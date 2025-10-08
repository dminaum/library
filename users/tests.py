import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def auth_client(user=None, is_staff=False):
    if user is None:
        user = baker.make("users.User", is_staff=is_staff)
    c = APIClient()
    c.force_authenticate(user=user)
    return c, user


def test_register_ok():
    client = APIClient()
    payload = {
        "username": "u1",
        "email": "u1@example.com",
        "password": "Str0ngPass!",
        "first_name": "U",
        "last_name": "One",
    }
    resp = client.post(reverse("register"), payload, format="json")
    assert resp.status_code == 201
    assert resp.data["username"] == "u1"
    assert "password" not in resp.data


def test_register_weak_password_rejected():
    client = APIClient()
    resp = client.post(
        reverse("register"),
        {"username": "weak", "email": "weak@example.com", "password": "12345678"},
        format="json",
    )
    assert resp.status_code == 400
    assert "password" in resp.data


def test_register_duplicate_email_rejected():
    baker.make("users.User", email="dup@example.com")
    client = APIClient()
    resp = client.post(
        reverse("register"),
        {"username": "dupuser", "email": "dup@example.com", "password": "Str0ngPass!"},
        format="json",
    )
    assert resp.status_code == 400
    assert "email" in resp.data


def test_users_list_admin_only():
    # обычный
    c, u = auth_client()
    resp = c.get(reverse("users-list"))
    assert resp.status_code == 403
    # админ
    c_admin, _ = auth_client(is_staff=True)
    resp2 = c_admin.get(reverse("users-list"))
    assert resp2.status_code == 200
    assert "results" in resp2.data or isinstance(resp2.data, list)


def test_users_me_and_retrieve_privacy():
    c1, u1 = auth_client()
    c2, u2 = auth_client()
    # me
    r1 = c1.get(reverse("users-me"))
    assert r1.status_code == 200
    assert r1.data["id"] == u1.id
    # retrieve self ok
    r2 = c1.get(reverse("users-detail", args=[u1.id]))
    assert r2.status_code == 200
    # retrieve чужого — запрет
    r3 = c1.get(reverse("users-detail", args=[u2.id]))
    assert r3.status_code in (403, 404)


def test_users_me_ok():
    u = baker.make("users.User", username="u1")
    client = APIClient()
    client.force_authenticate(user=u)
    resp = client.get(reverse("users-me"))
    assert resp.status_code == 200
    assert resp.data["username"] == "u1"
