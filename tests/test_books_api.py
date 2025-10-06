import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_books_list_public_can_read():
    a = baker.make("library.Author")
    baker.make(
        "library.Book", author=a, title="Python 101", published_year=2020, _quantity=2
    )
    client = APIClient()
    resp = client.get(reverse("books-list"))
    assert resp.status_code == 200
    assert resp.data["count"] == 2


def test_books_filter_search_ordering_pagination():
    a1 = baker.make("library.Author", first_name="Ray", last_name="Bradbury")
    a2 = baker.make("library.Author", first_name="Andy", last_name="Weir")
    baker.make(
        "library.Book",
        author=a1,
        title="Fahrenheit 451",
        description="dystopia",
        genre="fiction",
        published_year=1953,
        isbn="I1",
    )
    baker.make(
        "library.Book",
        author=a2,
        title="The Martian",
        description="mars, astronaut",
        genre="science",
        published_year=2011,
        isbn="I2",
    )
    client = APIClient()
    resp = client.get(
        reverse("books-list"),
        {
            "author": a2.id,
            "search": "astronaut",
            "ordering": "-published_year",
            "page_size": 10,
        },
    )
    assert resp.status_code == 200
    titles = [i["title"] for i in resp.data["results"]]
    assert titles == ["The Martian"]


def test_books_create_requires_staff():
    a = baker.make("library.Author")
    client = APIClient()
    payload = {
        "title": "New Book",
        "isbn": "ISBN-1",
        "description": "",
        "genre": "fiction",
        "published_year": 2024,
        "author": a.id,
        "copies_total": 2,
    }
    resp = client.post(reverse("books-list"), payload, format="json")
    assert resp.status_code in (401, 403)


def test_books_create_as_staff_and_patch():
    a = baker.make("library.Author")
    staff = baker.make("users.User", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)
    payload = {
        "title": "API Design",
        "isbn": "ISBN-2",
        "description": "good",
        "genre": "science",
        "published_year": 2023,
        "author": a.id,
        "copies_total": 3,
    }
    resp = client.post(reverse("books-list"), payload, format="json")
    assert resp.status_code == 201
    book_id = resp.data["id"]
    # PATCH
    resp2 = client.patch(
        reverse("books-detail", args=[book_id]),
        {"title": "API Design 2"},
        format="json",
    )
    assert resp2.status_code == 200
    assert resp2.data["title"] == "API Design 2"
