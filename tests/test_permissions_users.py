import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_users_list_admin_only():
    u = baker.make("users.User")
    client = APIClient()
    client.force_authenticate(user=u)
    resp = client.get(reverse("users-list"))
    assert resp.status_code == 403


def test_users_me_ok():
    u = baker.make("users.User", username="u1")
    client = APIClient()
    client.force_authenticate(user=u)
    resp = client.get(reverse("users-me"))
    assert resp.status_code == 200
    assert resp.data["username"] == "u1"
