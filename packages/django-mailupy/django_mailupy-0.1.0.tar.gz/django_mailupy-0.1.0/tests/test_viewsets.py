# tests/test_viewsets.py
import pytest
from django_mailupy.models import MailupyCredential


@pytest.mark.django_db
def test_viewset_list(api_client, mailupy_credentials):
    resp = api_client.get("/api/mailupy-credentials/")
    assert resp.status_code == 200
    assert resp.json()[0]["username"] == "testuser"


@pytest.mark.django_db
def test_viewset_create(api_client):
    payload = {"username": "u2", "mailup_password": "pw2"}
    resp = api_client.post("/api/mailupy-credentials/", payload, format="json")
    assert resp.status_code == 201
    assert resp.json()["username"] == "u2"


@pytest.mark.django_db
def test_test_connection_success(api_client, mailupy_credentials, monkeypatch):
    class DummyMailupy:
        def __init__(self, **kwargs): pass
        def get_lists(self): return [{"id": 1}]

    monkeypatch.setattr("django_mailupy.viewsets.DjangoMailupy", DummyMailupy)

    resp = api_client.get("/api/mailupy-credentials/test_connection/")
    assert resp.status_code == 200
    assert "Connection successful" in resp.json()["status"]


@pytest.mark.django_db
def test_test_connection_failure(api_client, mailupy_credentials, monkeypatch):
    from mailupy import MailupyException

    class DummyMailupy:
        def __init__(self, **kwargs): pass
        def get_lists(self): raise MailupyException("Invalid creds")

    monkeypatch.setattr("django_mailupy.viewsets.DjangoMailupy", DummyMailupy)

    resp = api_client.get("/api/mailupy-credentials/test_connection/")
    assert resp.status_code == 400
    assert "Invalid creds" in resp.json()["error"]
