from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users.paginations import UserPagination

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:

            if serializer.is_valid():
                # Check if the user is locked due to too many failed login attempts
                user = get_object_or_404(User, email=request.data.get("email"))
                if user.is_locked:
                    return Response(
                        {
                            "error": "Account is locked due to too many failed login attempts."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                user.failed_login_attempts = 0
                user.save()
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                user = get_object_or_404(User, email=request.data.get("email"))
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 3:
                    user.is_locked = True
                user.save()
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomTokenRefreshView(TokenRefreshView):
    pass


class CustomTokenVerifyView(TokenVerifyView):
    pass


class CustomUsersViewSet(UserViewSet):

    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["is_active", "is_staff", "is_superuser", "username", "email"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["date_joined"]
    ordering = ["date_joined"]

    lookup_field = "id"
    lookup_url_kwarg = "id"

    def list(self, request, *args, **kwargs):
        cache_key = f"user_list_{request.query_params}"

        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=settings.CACHE_TIMEOUT)
        return Response(response.data, status=status.HTTP_200_OK)