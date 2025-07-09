from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework import routers

from apps.users import views

app_name = "apps.users"


router = routers.DefaultRouter()
router.register("", views.CustomUsersViewSet, basename="users")

urlpatterns = [
    path("users/", include(router.urls)),

]
