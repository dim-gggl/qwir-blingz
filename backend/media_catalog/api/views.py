"""REST API endpoints for queer-forward media discovery."""

from django.db.models import Count, QuerySet
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from media_catalog.models import IdentityTag, MediaList
from media_catalog.services import generate_media_list_for_identity

from .serializers import (
    IdentityTagSerializer,
    MediaListDetailSerializer,
    MediaListGenerateSerializer,
    MediaListSummarySerializer,
    MediaListUpdateSerializer,
)


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "on"}


class IdentityTagViewSet(viewsets.ReadOnlyModelViewSet):
    """Expose curated identity tags members can explore."""

    serializer_class = IdentityTagSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self) -> QuerySet[IdentityTag]:  # type: ignore[override]
        qs = IdentityTag.objects.all()
        if self.request.query_params.get("curated", "true").lower() != "false":
            qs = qs.filter(is_curated=True)
        return qs.order_by("name")


class MediaListViewSet(viewsets.ModelViewSet):
    """Generate, manage, and share LGBTQIA+ media lists."""

    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self) -> QuerySet[MediaList]:  # type: ignore[override]
        qs = MediaList.objects.select_related("owner", "source_keyword")
        action = getattr(self, "action", None)
        if action == "retrieve":
            qs = qs.prefetch_related("items__media_item")
        if action == "list":
            qs = qs.annotate(item_count=Count("items"))
            if self.request.user.is_authenticated:
                qs = qs.filter(owner=self.request.user)
            else:
                qs = qs.filter(visibility=MediaList.VISIBILITY_PUBLIC)
        return qs

    def get_serializer_class(self):  # type: ignore[override]
        if self.action == "list":
            return MediaListSummarySerializer
        if self.action in {"retrieve", "create", "refresh", "partial_update"}:
            return MediaListDetailSerializer
        return MediaListDetailSerializer

    def get_permissions(self):  # type: ignore[override]
        if self.action in {"create", "partial_update", "destroy", "refresh"}:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    # default create uses ModelSerializer; override to call generator service.
    def create(self, request, *args, **kwargs) -> Response:
        if request.user.is_anonymous:
            raise NotAuthenticated()

        serializer = MediaListGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        media_list = generate_media_list_for_identity(
            tag=payload["identity_tag"],
            owner=request.user,
            limit=payload["limit"],
            include_adult=payload["include_adult"],
            language=payload.get("language"),
            visibility=payload["visibility"],
            title=payload.get("title"),
            description=payload.get("description"),
        )

        output = MediaListDetailSerializer(media_list, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer_cls = self.get_serializer_class()
        context = {"request": request}
        if page is not None:
            serializer = serializer_cls(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = serializer_cls(queryset, many=True, context=context)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = MediaListDetailSerializer(instance, context={"request": request})
        return Response(serializer.data)

    def get_object(self) -> MediaList:  # type: ignore[override]
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)
        if lookup_value is None:
            raise Http404
        media_list = queryset.filter(slug=lookup_value).first()
        if not media_list:
            raise Http404
        if not self._user_can_view(media_list):
            raise Http404
        self.check_object_permissions(self.request, media_list)
        return media_list

    def partial_update(self, request, *args, **kwargs) -> Response:
        media_list = self.get_object()
        if media_list.owner_id != request.user.id:
            raise PermissionDenied(detail=_("Seul·e le propriétaire peut modifier cette liste."))

        serializer = MediaListUpdateSerializer(media_list, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        media_list.refresh_from_db()
        output = MediaListDetailSerializer(media_list, context={"request": request})
        return Response(output.data)

    def destroy(self, request, *args, **kwargs) -> Response:
        media_list = self.get_object()
        if media_list.owner_id != request.user.id:
            raise PermissionDenied(detail=_("Seul·e le propriétaire peut supprimer cette liste."))
        media_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="refresh")
    def refresh(self, request, slug: str | None = None) -> Response:
        media_list = self.get_object()
        if media_list.owner_id != request.user.id:
            raise PermissionDenied(detail=_("Seul·e le propriétaire peut régénérer cette liste."))
        if not media_list.source_keyword_id:
            return Response(
                {"detail": _("Cette liste n'est pas liée à une identité TMDb." )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = request.data.get("limit")
        try:
            limit_value = int(limit) if limit is not None else media_list.items.count() or 12
        except (TypeError, ValueError):
            return Response(
                {"detail": _("Le paramètre limit doit être un entier.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        include_adult = _as_bool(request.data.get("include_adult", False))
        language = request.data.get("language") or None

        refreshed = generate_media_list_for_identity(
            tag=media_list.source_keyword,
            owner=request.user,
            limit=limit_value,
            include_adult=include_adult,
            language=language,
            visibility=media_list.visibility,
            title=media_list.title,
            description=media_list.description,
        )

        refreshed.refresh_from_db()
        output = MediaListDetailSerializer(refreshed, context={"request": request})
        return Response(output.data)

    def _user_can_view(self, media_list: MediaList) -> bool:
        request = self.request
        if media_list.visibility == MediaList.VISIBILITY_PUBLIC:
            return True
        if request.user.is_authenticated and media_list.owner_id == request.user.id:
            return True
        if media_list.visibility == MediaList.VISIBILITY_UNLISTED:
            return True
        return False
