"""Core deterministic financial calculations."""


def _check_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def calculate_balance(income: float, total_expenses: float) -> float:
    """Return monthly income minus total expenses."""
    _check_non_negative(income, "Income")
    _check_non_negative(total_expenses, "Expenses")
    return round(income - total_expenses, 2)


def calculate_savings_rate(income: float, expenses: float) -> float:
    """Return the savings rate as a percentage of income."""
    if income <= 0:
        raise ValueError("Income must be greater than zero to compute a savings rate.")
    _check_non_negative(expenses, "Expenses")
    return round((income - expenses) / income * 100, 2)


def flag_deficit(balance: float) -> bool:
    """Return whether the balance is below zero."""
    return balance < 0


def total_amount(amounts: list[float]) -> float:
    """Sum amounts, rejecting negative values."""
    for amount in amounts:
        _check_non_negative(amount, "Amount")
    return round(sum(amounts), 2)


def category_totals(transactions: list[dict]) -> dict[str, float]:
    """Return total expense amount for each category."""
    totals: dict[str, float] = {}
    for row in transactions:
        if row["type"] != "expense":
            continue
        category = row["category"]
        totals[category] = round(totals.get(category, 0.0) + row["amount"], 2)
    return totals


def monthly_summary(transactions: list[dict]) -> dict:
    """Return combined monthly income, expense, balance, and category metrics."""
    income = total_amount(
        [row["amount"] for row in transactions if row["type"] == "income"]
    )
    expenses = total_amount(
        [row["amount"] for row in transactions if row["type"] == "expense"]
    )
    balance = calculate_balance(income, expenses)
    return {
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "savings_rate": calculate_savings_rate(income, expenses) if income > 0 else None,
        "deficit": flag_deficit(balance),
        "category_totals": category_totals(transactions),
    }
