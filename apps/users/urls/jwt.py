from django.urls import path

from apps.users.views import (CustomTokenObtainPairView,
                              CustomTokenRefreshView, CustomTokenVerifyView)

app_name = "apps.users"

urlpatterns = [
    path("jwt/create/", CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", CustomTokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", CustomTokenVerifyView.as_view(), name="jwt-verify"),
]