from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
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


def auth_client(user=None, is_staff=False):
    if user is None:
        user = baker.make("users.User", is_staff=is_staff)
    c = APIClient()
    c.force_authenticate(user=user)
    return c, user


def make_book(copies_total=1, copies_available=None):
    a = baker.make("library.Author")
    if copies_available is None:
        copies_available = copies_total
    b = baker.make(
        "library.Book",
        author=a,
        copies_total=copies_total,
        copies_available=copies_available,
    )
    return b


def test_issue_decrements_available_for_self_user():
    c, u = auth_client()
    b = make_book(copies_total=2)
    resp = c.post(reverse("loans-issue"), {"book_id": b.id}, format="json")
    assert resp.status_code == 201
    b.refresh_from_db()
    assert b.copies_available == 1


def test_issue_for_other_requires_staff():
    c, u1 = auth_client()
    u2 = baker.make("users.User")
    b = make_book(copies_total=1)
    resp = c.post(
        reverse("loans-issue"), {"book_id": b.id, "user_id": u2.id}, format="json"
    )
    assert resp.status_code in (400, 403)


def test_staff_can_issue_for_anyone():
    c, staff = auth_client(is_staff=True)
    u = baker.make("users.User")
    b = make_book(copies_total=1)
    resp = c.post(
        reverse("loans-issue"), {"book_id": b.id, "user_id": u.id}, format="json"
    )
    assert resp.status_code == 201


def test_cannot_issue_when_no_available():
    c, u = auth_client()
    b = make_book(copies_total=1, copies_available=0)
    resp = c.post(reverse("loans-issue"), {"book_id": b.id}, format="json")
    assert resp.status_code == 400
    assert "Все копии этой книги недоступны" in resp.data["detail"]


def test_unique_active_loan_per_user_book():
    c, u = auth_client()
    b = make_book(copies_total=2)
    r1 = c.post(reverse("loans-issue"), {"book_id": b.id}, format="json")
    assert r1.status_code == 201
    r2 = c.post(reverse("loans-issue"), {"book_id": b.id}, format="json")
    assert r2.status_code == 400


def test_return_increases_available_and_sets_status():
    c, u = auth_client()
    b = make_book(copies_total=1)
    r = c.post(reverse("loans-issue"), {"book_id": b.id}, format="json")
    loan_id = r.data["id"]
    r2 = c.post(reverse("loans-return-book"), {"loan_id": loan_id}, format="json")
    assert r2.status_code == 200
    b.refresh_from_db()
    assert b.copies_available == 1
    assert r2.data["status"] == "RETURNED"


def test_list_filter_by_owner_for_user_and_all_for_staff():
    c1, u1 = auth_client()
    c2, u2 = auth_client()
    staff_client, staff = auth_client(is_staff=True)
    b1 = make_book(copies_total=2)
    b2 = make_book(copies_total=2)
    c1.post(reverse("loans-issue"), {"book_id": b1.id}, format="json")
    c2.post(reverse("loans-issue"), {"book_id": b2.id}, format="json")

    r_user = c1.get(reverse("loans-list"))
    assert r_user.status_code == 200
    assert r_user.data["count"] == 1

    r_staff = staff_client.get(reverse("loans-list"))
    assert r_staff.status_code == 200
    assert r_staff.data["count"] == 2


def test_effective_status_overdue_calculated_on_the_fly():
    c, u = auth_client()
    b = make_book(copies_total=1)
    loan = baker.make(
        "library.Loan",
        user=u,
        book=b,
        issued_at=timezone.now() - timedelta(days=15),
        due_at=timezone.now() - timedelta(days=1),
        returned_at=None,
        status="ISSUED",
    )
    r = c.get(reverse("loans-detail", args=[loan.id]))
    assert r.status_code == 200
    assert r.data["effective_status"] == "OVERDUE"
