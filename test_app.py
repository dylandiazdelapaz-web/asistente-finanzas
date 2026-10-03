from fastapi.testclient import TestClient

from app import app, get_connection

client = TestClient(app)


def setup_function() -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM expenses")


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
