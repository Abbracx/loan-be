from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# from apps.users.views import CustomTokenCreateView

schema_view = get_schema_view(
    openapi.Info(
        title="Loan Management System API",
        default_version="v1",
        description="API endpoints for Loan Management System",
        contact=openapi.Contact(email="tankoraphael@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("", RedirectView.as_view(url="api/v1/auth/redoc/", permanent=False)),
    path("admin/", admin.site.urls),
    # path("api/v1/auth/", include("djoser.urls")),
    # path("api/v1/auth/", include("djoser.urls.jwt")),
    path("api/v1/auth/", include("apps.users.urls.jwt", namespace="usersauth")),
    path("api/v1/auth/", include("apps.users.urls.base", namespace="usersapi")),
    path("api/v1/loans/", include("apps.loans.urls", namespace="loans")),
    path(
        "api/v1/auth/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/v1/auth/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path(
        "api/v1/auth/swagger.json/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Loan Management Admin Portal"
admin.site.site_title = "Loan Management Admin Portal"
admin.site.index_title = "Welcome to Loan Management Admin Portal"