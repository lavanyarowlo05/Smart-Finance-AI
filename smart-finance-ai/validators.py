"""Input validation for Smart Finance AI.

All business-rule checks live here so the UI and the database layer
never receive bad data. Every function raises ValueError on invalid input.
"""

from datetime import date, datetime

VALID_TYPES = ("income", "expense")


def validate_amount(amount: float) -> float:
    """Amount must be a real number greater than zero."""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("Amount must be a number.")
    if amount != amount or amount in (float("inf"), float("-inf")):
        raise ValueError("Amount must be a finite number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return float(amount)


def validate_category(category: str | None) -> str:
    """Category must be a non-empty string (TC-05)."""
    if category is None or not isinstance(category, str) or not category.strip():
        raise ValueError("Category is required.")
    return category.strip()


def validate_transaction_type(transaction_type: str) -> str:
    """Type must be 'income' or 'expense' (case-insensitive)."""
    if not isinstance(transaction_type, str):
        raise ValueError("Transaction type must be 'income' or 'expense'.")
    cleaned = transaction_type.strip().lower()
    if cleaned not in VALID_TYPES:
        raise ValueError("Transaction type must be 'income' or 'expense'.")
    return cleaned


def validate_date(value: str | date) -> date:
    """Accepts a date object or an ISO string (YYYY-MM-DD)."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError:
            pass
    raise ValueError("Date must be in YYYY-MM-DD format.")


def validate_transaction(
    transaction_type: str, category: str | None, amount: float, transaction_date: str | date
) -> dict:
    """Validate a full ledger row and return a clean payload."""
    return {
        "type": validate_transaction_type(transaction_type),
        "category": validate_category(category),
        "amount": validate_amount(amount),
        "transaction_date": validate_date(transaction_date).isoformat(),
    }
