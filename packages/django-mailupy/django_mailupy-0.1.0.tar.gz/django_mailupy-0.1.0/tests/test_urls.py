# tests/test_urls.py
from django.urls import reverse, resolve


def test_urls_are_registered():
    resolver = resolve("/api/mailupy-credentials/")
    assert resolver.func.cls.__name__ == "MailupyCredentialViewSet"
