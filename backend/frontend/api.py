from __future__ import annotations

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import fetch_random_queer_movie


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
