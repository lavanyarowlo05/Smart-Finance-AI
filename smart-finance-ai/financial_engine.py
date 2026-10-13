"""Core deterministic financial calculations.

Pure functions only: no database, no UI, no LLM. Same input, same output.
"""


def _check_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def calculate_balance(income: float, total_expenses: float) -> float:
    """Monthly net balance = income - total expenses. Can be negative."""
    _check_non_negative(income, "Income")
    _check_non_negative(total_expenses, "Expenses")
    return round(income - total_expenses, 2)


def calculate_savings_rate(income: float, expenses: float) -> float:
    """Savings rate as a percentage of income.

    Example: income 25000, expenses 18000 -> 28.0
    A deficit month gives a negative rate. Income must be above zero.
    """
    if income <= 0:
        raise ValueError("Income must be greater than zero to compute a savings rate.")
    _check_non_negative(expenses, "Expenses")
    return round((income - expenses) / income * 100, 2)


def flag_deficit(balance: float) -> bool:
    """True when spending exceeds income (balance below zero)."""
    return balance < 0


def total_amount(amounts: list[float]) -> float:
    """Sum a list of amounts, rejecting negatives."""
    for a in amounts:
        _check_non_negative(a, "Amount")
    return round(sum(amounts), 2)


def category_totals(transactions: list[dict]) -> dict[str, float]:
    """Total expense per category from ledger rows.

    Each row needs 'type', 'category' and 'amount'. Income rows are ignored.
    """
    totals: dict[str, float] = {}
    for row in transactions:
        if row["type"] != "expense":
            continue
        totals[row["category"]] = round(totals.get(row["category"], 0.0) + row["amount"], 2)
    return totals


def monthly_summary(transactions: list[dict]) -> dict:
    """One-shot summary used later by the dashboard and the AI layer."""
    income = total_amount([r["amount"] for r in transactions if r["type"] == "income"])
    expenses = total_amount([r["amount"] for r in transactions if r["type"] == "expense"])
    balance = calculate_balance(income, expenses)
    return {
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "savings_rate": calculate_savings_rate(income, expenses) if income > 0 else None,
        "deficit": flag_deficit(balance),
        "category_totals": category_totals(transactions),
    }
