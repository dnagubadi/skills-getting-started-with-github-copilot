import copy
from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of the initial activities and restore after each test
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data


def test_signup_and_unregister_participant():
    email = "test.user@example.com"

    # Sign up
    r = client.post(f"/activities/Chess Club/signup?email={email}")
    assert r.status_code == 200
    assert f"Signed up {email} for Chess Club" in r.json()["message"]

    # Confirm participant present
    r2 = client.get("/activities")
    assert email in r2.json()["Chess Club"]["participants"]

    # Unregister
    r3 = client.delete(f"/activities/Chess Club/participants?email={email}")
    assert r3.status_code == 200
    assert f"Unregistered {email} from Chess Club" in r3.json()["message"]

    # Confirm removal
    r4 = client.get("/activities")
    assert email not in r4.json()["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    # michael@mergington.edu is already signed up in the fixture data
    existing = "michael@mergington.edu"
    r = client.post(f"/activities/Chess Club/signup?email={existing}")
    assert r.status_code == 400


def test_signup_nonexistent_activity():
    r = client.post("/activities/NoSuchActivity/signup?email=a@b.c")
    assert r.status_code == 404


def test_unregister_nonexistent_participant():
    r = client.delete("/activities/Chess Club/participants?email=notfound@example.com")
    assert r.status_code == 404
