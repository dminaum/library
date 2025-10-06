import json

import pytest
import yaml
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_schema_has_main_endpoints():
    client = APIClient()
    r = client.get(reverse("schema"))
    assert (
        r.status_code == 200
    ), f"schema status={r.status_code}, body={r.content[:200]!r}"

    raw = r.content.decode("utf-8").strip()
    assert raw, "Empty schema response"

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = yaml.safe_load(raw)

    assert isinstance(data, dict), f"Schema is not a dict, got {type(data)}"
    paths = data.get("paths", {})
    assert "/api/auth/register" in paths
    assert "/api/auth/token" in paths
    assert "/api/users/me/" in paths
    assert "/api/books/" in paths
    assert "/api/authors/" in paths
    assert "/api/loans/issue/" in paths
    assert "/api/loans/return/" in paths
