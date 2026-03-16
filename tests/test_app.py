import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test GET /activities returns all activities"""
    # Arrange - TestClient is set up

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    email = "test@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]

    # Verify added to participants
    resp = client.get("/activities")
    activities = resp.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    """Test signup fails when student is already signed up"""
    # Arrange
    email = "duplicate@mergington.edu"
    activity = "Programming Class"

    # First signup
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act - attempt duplicate signup
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity():
    """Test signup fails for non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity"""
    # Arrange
    email = "unregister@mergington.edu"
    activity = "Gym Class"

    # First signup
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email in data["message"]

    # Verify removed from participants
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up():
    """Test unregister fails when student is not signed up"""
    # Arrange
    email = "notsigned@mergington.edu"
    activity = "Art Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity():
    """Test unregister fails for non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    activity = "Invalid Activity"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test GET / redirects to static index.html"""
    # Arrange - TestClient is set up

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"