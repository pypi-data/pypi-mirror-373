from django.urls import path, include

try:
    from rest_framework.routers import DefaultRouter
    from .viewsets import MailupyCredentialViewSet

    router = DefaultRouter()
    router.register(r"mailupy-credentials", MailupyCredentialViewSet)

    urlpatterns = [
        path("api/", include(router.urls)),
    ]
except ImportError:
    urlpatterns = []
