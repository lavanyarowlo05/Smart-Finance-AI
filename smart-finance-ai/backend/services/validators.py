"""Input validation for Smart Finance AI transactions."""

from datetime import date, datetime

VALID_TYPES = ("income", "expense")


def validate_amount(amount: float) -> float:
    """Require an amount to be a finite number greater than zero."""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("Amount must be a number.")
    if amount != amount or amount in (float("inf"), float("-inf")):
        raise ValueError("Amount must be a finite number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return float(amount)


def validate_category(category: str | None) -> str:
    """Require and trim a non-empty category."""
    if category is None or not isinstance(category, str) or not category.strip():
        raise ValueError("Category is required.")
    return category.strip()


def validate_transaction_type(transaction_type: str) -> str:
    """Normalize and validate income or expense transaction types."""
    if not isinstance(transaction_type, str):
        raise ValueError("Transaction type must be 'income' or 'expense'.")
    cleaned = transaction_type.strip().lower()
    if cleaned not in VALID_TYPES:
        raise ValueError("Transaction type must be 'income' or 'expense'.")
    return cleaned


def validate_date(value: str | date) -> date:
    """Parse a date object or ISO-formatted date string."""
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
    """Validate and normalize a complete transaction row."""
    return {
        "type": validate_transaction_type(transaction_type),
        "category": validate_category(category),
        "amount": validate_amount(amount),
        "transaction_date": validate_date(transaction_date).isoformat(),
    }
