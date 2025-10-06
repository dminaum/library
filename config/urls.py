from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from library.views import AuthorViewSet, BookViewSet, LoanViewSet
from users.views import RegisterView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"authors", AuthorViewSet, basename="authors")
router.register(r"books", BookViewSet, basename="books")
router.register(r"loans", LoanViewSet, basename="loans")


def health(_):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    # health / docs / Swagger / Redoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path(
        "api/schema.yaml",
        SpectacularAPIView.as_view(api_version="1.0.0"),
        name="schema-yaml",
    ),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/health/", health),
    # auth
    path("api/auth/register", RegisterView.as_view(), name="register"),
    path("api/auth/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    # users
    path("api/", include(router.urls)),
]
