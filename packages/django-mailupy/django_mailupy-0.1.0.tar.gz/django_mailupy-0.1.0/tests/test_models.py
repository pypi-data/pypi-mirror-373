# tests/test_models.py
import pytest
from django_mailupy.models import MailupyCredential


@pytest.mark.django_db
def test_mailupy_credential_manager_get():
    obj = MailupyCredential.objects.get()
    assert isinstance(obj, MailupyCredential)
    assert obj.pk == 1


@pytest.mark.django_db
def test_mailupy_credential_str_and_save():
    cred = MailupyCredential(username="foo", mailup_password="bar")
    cred.save()
    assert str(cred) == "MailUp: foo"
    assert cred.pk == 1
