import copy

from fastapi.testclient import TestClient

from src.app import activities, app


ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    # Arrange
    reset_activities()
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_adds_student_to_activity():
    # Arrange
    reset_activities()
    client = TestClient(app)
    activity_name = "Chess Club"
    student_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": student_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"
    assert student_email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_registration():
    # Arrange
    reset_activities()
    client = TestClient(app)
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": student_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity():
    # Arrange
    reset_activities()
    client = TestClient(app)

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_student_from_activity():
    # Arrange
    reset_activities()
    client = TestClient(app)
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": student_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {student_email} from {activity_name}"
    assert student_email not in activities[activity_name]["participants"]


def test_unregister_rejects_missing_student():
    # Arrange
    reset_activities()
    client = TestClient(app)
    activity_name = "Chess Club"
    student_email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": student_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
