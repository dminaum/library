import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_authors_search_and_pagination():
    baker.make("library.Author", first_name="John", last_name="Doe", _quantity=30)
    client = APIClient()
    resp = client.get(reverse("authors-list"), {"search": "John", "page_size": 25})
    assert resp.status_code == 200
    assert resp.data["count"] == 30
    assert len(resp.data["results"]) == 20
