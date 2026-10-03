import os
import re
import sqlite3
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Asistente Finanzas",
    description="Registra gastos y genera resúmenes mensuales por usuario.",
    version="0.1.0",
)

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", Path(__file__).with_name("finanzas.db")))


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                spent_on TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


initialize_database()


@app.get("/", include_in_schema=False)
def serve_homepage() -> FileResponse:
    index_path = Path(__file__).with_name("index.html")
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="No existe la página principal.")
    return FileResponse(index_path)


class ExpenseIn(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0)
    category: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=200)
    spent_on: date = Field(default_factory=date.today)


@app.get("/health", summary="Comprobar estado de la aplicación")
def health() -> dict[str, str]:
    return {"estado": "operativa"}


@app.post("/expenses", status_code=201, summary="Registrar un gasto")
def add_expense(expense: ExpenseIn) -> dict:
    record = expense.model_dump()
    record["amount"] = str(record["amount"])
    record["spent_on"] = record["spent_on"].isoformat()
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO expenses (user_id, amount, category, description, spent_on) VALUES (?, ?, ?, ?, ?)",
            (expense.user_id, record["amount"], expense.category, expense.description, record["spent_on"]),
        )
    return {"message": "Gasto registrado", "expense": record}


@app.get("/users/{user_id}/summary", summary="Consultar resumen mensual")
def monthly_summary(user_id: str, year: int, month: int) -> dict:
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="El mes debe estar entre 1 y 12.")

    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    with get_connection() as connection:
        matching = connection.execute(
            "SELECT amount, category FROM expenses WHERE user_id = ? AND strftime('%Y-%m', spent_on) = ?",
            (user_id, f"{year:04d}-{month:02d}"),
        ).fetchall()
    for item in matching:
        try:
            by_category[item["category"]] += Decimal(item["amount"])
        except InvalidOperation as error:
            raise HTTPException(status_code=500, detail="Monto invalido almacenado") from error

    total = sum(by_category.values(), Decimal("0"))
    return {
        "user_id": user_id,
        "period": f"{year:04d}-{month:02d}",
        "total": str(total),
        "by_category": {category: str(amount) for category, amount in sorted(by_category.items())},
        "count": len(matching),
    }


def parse_expense_message(user_id: str, message: str) -> ExpenseIn:
    match = re.search(r"(?:\$\s*)?([0-9][0-9.,]*)", message)
    if not match:
        raise HTTPException(status_code=400, detail="No encontré un monto. Ejemplo: gasté 4500 en transporte.")

    normalized_amount = match.group(1).replace(".", "").replace(",", ".")
    category_match = re.search(r"\ben\s+([a-záéíóúñ ]+)", message.lower())
    category = category_match.group(1).strip() if category_match else "otros"
    category = category[:80]
    return ExpenseIn(user_id=user_id, amount=Decimal(normalized_amount), category=category, description=message)


@app.post("/webhooks/whatsapp", summary="Recibir mensaje de WhatsApp")
def whatsapp_webhook(payload: dict) -> dict:
    # Acepta un formato simple de prueba; Meta Cloud API se conectará aquí después.
    user_id = str(payload.get("user_id", "")).strip()
    message = str(payload.get("message", "")).strip()
    if not user_id or not message:
        raise HTTPException(status_code=400, detail="Se requieren user_id y message.")
    expense = parse_expense_message(user_id, message)
    return add_expense(expense)
