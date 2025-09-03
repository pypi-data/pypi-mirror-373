# tests/test_client.py
import pytest
from django_mailupy.client import DjangoMailupy
from django_mailupy.models import MailupyCredential
from mailupy.exceptions import MailupyRequestException


@pytest.mark.django_db
def test_django_mailupy_init_with_fake_credentials():

    MailupyCredential.objects.create(username="fake_user", mailup_password="fake_pass")

    with pytest.raises(MailupyRequestException) as excinfo:
        DjangoMailupy(client_id="id", client_secret="secret")

    msg = str(excinfo.value.args[0])

    assert msg.startswith("Error 400 -")
    assert "Invalid credentials" in msg
