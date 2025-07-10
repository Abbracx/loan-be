import logging
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.users.paginations import UserPagination

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            email = request.data.get("email")
            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return Response({"error": "No active account found with the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            if serializer.is_valid():
                if user.is_locked:
                    logger.warning(f"Login attempt on locked account - User: {user.id}")
                    return Response(
                        {"error": "Account is locked due to too many failed login attempts."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                
                user.failed_login_attempts = 0
                user.save()
                logger.info(f"Successful login - User: {user.id}")
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 3:
                    user.is_locked = True
                    logger.warning(f"Account locked due to failed attempts - User: {user.id}")
                user.save()
                logger.warning(f"Failed login attempt - User: {user.id}, Attempts: {user.failed_login_attempts}")
                return Response({"error": "No active account found with the given credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        cache_key = f"user_list_{hash(str(request.query_params))}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info("Cache hit for users list")
            return Response(cached_response, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=settings.CACHE_TIMEOUT)
        logger.info("Users list cached")
        return Response(response.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        
        cache_key = f"user_detail_{user.id}"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            logger.info(f"Cache hit for user detail - User: {user.id}")
            return Response(cached_response, status=status.HTTP_200_OK)

        response_data = serializer.data
        cache.set(cache_key, response_data, timeout=settings.CACHE_TIMEOUT)
        logger.info(f"User detail cached - User: {user.id}")
        
        return Response(response_data, status=status.HTTP_200_OK)