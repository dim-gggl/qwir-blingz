from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import build_feed_carousel, fetch_random_queer_movie


class QueerFilmTeaserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs) -> Response:
        movie = fetch_random_queer_movie()
        if not movie:
            return Response(
                {"detail": "No film available right now."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(movie)


class FeedCarouselRefreshView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug: str, *args, **kwargs) -> Response:
        limit = request.data.get("limit")
        try:
            limit_value = int(limit) if limit is not None else 12
        except (TypeError, ValueError):
            return Response(
                {"detail": "Le paramètre limit doit être un entier."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        carousel = build_feed_carousel(
            slug,
            user=request.user,
            limit=limit_value,
            language=request.data.get("language"),
        )
        if carousel is None:
            return Response(
                {"detail": "Thème introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"carousel": carousel})
