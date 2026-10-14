import pytest

from backend.services.financial_engine import (
    calculate_balance,
    calculate_savings_rate,
    category_totals,
    flag_deficit,
    monthly_summary,
    total_amount,
)


# TC-01: Normal month
def test_tc01_normal_month_balance():
    assert calculate_balance(25000, 18000) == 7000


def test_tc01_normal_month_savings_rate():
    assert calculate_savings_rate(25000, 18000) == 28.0


def test_tc01_normal_month_not_flagged():
    assert flag_deficit(calculate_balance(25000, 18000)) is False


# TC-02: Deficit month
def test_tc02_deficit_balance_is_negative():
    assert calculate_balance(20000, 22000) == -2000


def test_tc02_deficit_triggers_flag():
    assert flag_deficit(calculate_balance(20000, 22000)) is True


def test_tc02_deficit_savings_rate_is_negative():
    assert calculate_savings_rate(20000, 22000) == -10.0


# Edge cases
def test_zero_balance_is_not_a_deficit():
    assert flag_deficit(0) is False


def test_savings_rate_rejects_zero_income():
    with pytest.raises(ValueError):
        calculate_savings_rate(0, 1000)


def test_negative_income_rejected():
    with pytest.raises(ValueError):
        calculate_balance(-1, 100)


def test_negative_expenses_rejected():
    with pytest.raises(ValueError):
        calculate_balance(1000, -5)


def test_total_amount_sums_and_rounds():
    assert total_amount([0.1, 0.2]) == 0.3


def test_total_amount_rejects_negative():
    with pytest.raises(ValueError):
        total_amount([100, -50])


# Category totals and summary, using the worked example from section 7
LEDGER = [
    {"type": "income", "category": "Salary", "amount": 25000},
    {"type": "expense", "category": "Rent & Utilities", "amount": 7000},
    {"type": "expense", "category": "Food & Groceries", "amount": 4000},
    {"type": "expense", "category": "Transport", "amount": 1500},
    {"type": "expense", "category": "Family Support", "amount": 3000},
    {"type": "expense", "category": "Personal Spending", "amount": 2500},
]


def test_category_totals_ignores_income():
    totals = category_totals(LEDGER)
    assert "Salary" not in totals
    assert totals["Rent & Utilities"] == 7000


def test_category_totals_merges_same_category():
    rows = LEDGER + [{"type": "expense", "category": "Transport", "amount": 500}]
    assert category_totals(rows)["Transport"] == 2000


def test_monthly_summary_matches_worked_example():
    s = monthly_summary(LEDGER)
    assert s["income"] == 25000
    assert s["expenses"] == 18000
    assert s["balance"] == 7000
    assert s["savings_rate"] == 28.0
    assert s["deficit"] is False


def test_monthly_summary_with_no_income():
    rows = [{"type": "expense", "category": "Food", "amount": 500}]
    s = monthly_summary(rows)
    assert s["balance"] == -500
    assert s["savings_rate"] is None
    assert s["deficit"] is True
