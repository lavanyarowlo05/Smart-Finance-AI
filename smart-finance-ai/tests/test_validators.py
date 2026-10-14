from datetime import date

import pytest

from backend.services.validators import (
    validate_amount,
    validate_category,
    validate_date,
    validate_transaction,
    validate_transaction_type,
)


# TC-05: Missing category
def test_tc05_none_category_rejected():
    with pytest.raises(ValueError, match="Category is required"):
        validate_category(None)


def test_tc05_blank_category_rejected():
    with pytest.raises(ValueError):
        validate_category("   ")


def test_tc05_full_row_with_missing_category_rejected_before_db():
    with pytest.raises(ValueError, match="Category is required"):
        validate_transaction("expense", None, 1500, "2026-10-13")


def test_category_is_trimmed():
    assert validate_category("  Food  ") == "Food"


# Amount rules
@pytest.mark.parametrize("bad", [0, -1, -0.01, float("inf"), float("nan"), "100", None, True])
def test_invalid_amounts_rejected(bad):
    with pytest.raises(ValueError):
        validate_amount(bad)


def test_valid_amount_accepted():
    assert validate_amount(1500) == 1500.0
    assert validate_amount(99.5) == 99.5


# Type rules
def test_type_is_normalised():
    assert validate_transaction_type(" Expense ") == "expense"
    assert validate_transaction_type("INCOME") == "income"


@pytest.mark.parametrize("bad", ["", "spend", None, 5])
def test_invalid_type_rejected(bad):
    with pytest.raises(ValueError):
        validate_transaction_type(bad)


# Date rules
def test_date_accepts_iso_string_and_date_object():
    assert validate_date("2026-10-13") == date(2026, 10, 13)
    assert validate_date(date(2026, 10, 13)) == date(2026, 10, 13)


@pytest.mark.parametrize("bad", ["13-10-2026", "2026-13-01", "", "abc", None, 20261013])
def test_invalid_date_rejected(bad):
    with pytest.raises(ValueError):
        validate_date(bad)


# Full row
def test_valid_transaction_returns_clean_payload():
    payload = validate_transaction("Expense", " Rent ", 7000, "2026-10-01")
    assert payload == {
        "type": "expense",
        "category": "Rent",
        "amount": 7000.0,
        "transaction_date": "2026-10-01",
    }
