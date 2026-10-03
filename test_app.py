from fastapi.testclient import TestClient

from app import app, get_connection

client = TestClient(app)


def setup_function() -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM expenses")
        connection.execute("DELETE FROM quiz_results")
        connection.execute("DELETE FROM quiz_leaderboard")


def test_register_and_summarize_expenses_per_user() -> None:
    response = client.post(
        "/expenses",
        json={
            "user_id": "user-a",
            "amount": "4500",
            "category": "transporte",
            "description": "Metro",
            "spent_on": "2026-09-30",
        },
    )
    assert response.status_code == 201

    client.post(
        "/expenses",
        json={
            "user_id": "user-a",
            "amount": "12000",
            "category": "alimentacion",
            "spent_on": "2026-09-15",
        },
    )
    client.post(
        "/expenses",
        json={
            "user_id": "user-b",
            "amount": "999999",
            "category": "otro",
            "spent_on": "2026-09-15",
        },
    )

    summary = client.get("/users/user-a/summary?year=2026&month=9")
    assert summary.status_code == 200
    assert summary.json()["total"] == "16500"
    assert summary.json()["by_category"] == {"alimentacion": "12000", "transporte": "4500"}


def test_webhook_registers_spanish_message() -> None:
    response = client.post(
        "/webhooks/whatsapp",
        json={"user_id": "+56900000000", "message": "Gasté 3.500 en transporte"},
    )
    assert response.status_code == 200
    assert response.json()["expense"]["amount"] == "3500"
    assert response.json()["expense"]["category"] == "transporte"


def test_quiz_results_are_opt_in_and_admin_protected(monkeypatch) -> None:
    monkeypatch.setenv("ADMIN_PASSWORD", "test-secret")
    submitted = client.post(
        "/quiz-results",
        json={"alias": "  Ana  ", "answers": [1, 0, 1, 1, 0, 1, 1, 0]},
    )

    assert submitted.status_code == 201
    assert submitted.json()["alias"] == "Ana"
    assert submitted.json()["level"] == "Avanzado"
    assert client.get("/admin/quiz-results").status_code == 401

    results = client.get("/admin/quiz-results", auth=("admin", "test-secret"))
    assert results.status_code == 200
    assert results.json()["count"] == 1
    assert results.json()["by_level"]["Avanzado"] == 1
    assert results.json()["results"][0]["alias"] == "Ana"


def test_quiz_result_requires_eight_valid_answers() -> None:
    response = client.post("/quiz-results", json={"answers": [1, 0]})

    assert response.status_code == 422


def test_quiz_admin_panel_fails_closed_without_password(monkeypatch) -> None:
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    response = client.get("/admin/quiz-results", auth=("admin", "anything"))

    assert response.status_code == 503


def test_quiz_script_is_served() -> None:
    response = client.get("/quiz.js")

    assert response.status_code == 200
    assert b"quizQuestions" in response.content


def test_daily_leaderboard_weights_scores_and_keeps_daily_best() -> None:
    first = client.post(
        "/leaderboard",
        json={"player_name": "  Ana Sol  ", "level": "medio", "correct_count": 3, "question_count": 5},
    )
    lower_retry = client.post(
        "/leaderboard",
        json={"player_name": "ana sol", "level": "medio", "correct_count": 2, "question_count": 5},
    )
    higher = client.post(
        "/leaderboard",
        json={"player_name": "Beto", "level": "medio", "correct_count": 4, "question_count": 5},
    )

    assert first.status_code == 201
    assert first.json()["score"] == 6
    assert lower_retry.json()["score"] == 6
    assert higher.json()["score"] == 8

    board = client.get("/leaderboard?level=medio")
    assert board.status_code == 200
    assert [row["player_name"] for row in board.json()["results"]] == ["Beto", "Ana Sol"]
    assert board.json()["results"][1]["rank"] == 2


def test_leaderboard_validates_level_question_count_and_alias() -> None:
    wrong_question_count = client.post(
        "/leaderboard",
        json={"player_name": "Carla", "level": "basico", "correct_count": 5, "question_count": 10},
    )
    invalid_alias = client.post(
        "/leaderboard",
        json={"player_name": "<script>", "level": "basico", "correct_count": 3, "question_count": 5},
    )

    assert wrong_question_count.status_code == 422
    assert invalid_alias.status_code == 422


def test_leaderboard_cors_allows_public_site_origin() -> None:
    response = client.options(
        "/leaderboard?level=basico",
        headers={
            "Origin": "https://deluxe-strudel-b85556.netlify.app",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://deluxe-strudel-b85556.netlify.app"
