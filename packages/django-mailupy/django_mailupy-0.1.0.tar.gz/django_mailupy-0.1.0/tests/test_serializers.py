# tests/test_serializers.py
import pytest
from django_mailupy.serializers import MailupyCredentialSerializer
from django_mailupy.models import MailupyCredential


@pytest.mark.django_db
def test_mailupycredential_serializer():
    cred = MailupyCredential.objects.create(username="foo", mailup_password="bar")
    data = MailupyCredentialSerializer(cred).data
    assert data["username"] == "foo"
    assert data["mailup_password"] == "bar"
