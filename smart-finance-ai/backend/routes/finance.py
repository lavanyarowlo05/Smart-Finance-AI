"""Finance API route handlers."""

import logging
from math import isfinite
from typing import Any, Callable, TypeVar

from fastapi import APIRouter, HTTPException, Query

if __package__.startswith("backend."):
    from ..schemas.finance import (
        AmountsInput,
        BalanceInput,
        DeficitInput,
        SavingsRateInput,
        SurvivalInput,
        TransactionValidationInput,
        TransactionsInput,
    )
    from ..services.financial_engine import (
        calculate_balance,
        calculate_savings_rate,
        category_totals,
        flag_deficit,
        monthly_summary,
        total_amount,
    )
    from ..services.survival_engine import calculate_survival_months
else:
    from schemas.finance import (
        AmountsInput,
        BalanceInput,
        DeficitInput,
        SavingsRateInput,
        SurvivalInput,
        TransactionValidationInput,
        TransactionsInput,
    )
    from services.financial_engine import (
        calculate_balance,
        calculate_savings_rate,
        category_totals,
        flag_deficit,
        monthly_summary,
        total_amount,
    )
    from services.survival_engine import calculate_survival_months

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["finance"])
T = TypeVar("T")


def _calculate(calculation: Callable[..., T], *args: Any) -> T:
    """Run a calculation and translate business-rule errors to HTTP 422."""
    try:
        return calculation(*args)
    except ValueError as exc:
        logger.warning("Rejected %s request: %s", calculation.__name__, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/balance")
def balance(data: BalanceInput) -> dict[str, float]:
    """Calculate net balance from income and expenses in the JSON body."""
    return {"balance": calculate_balance(data.income, data.expenses)}


@router.get("/balance")
def get_balance(
    income: float = Query(ge=0, allow_inf_nan=False),
    expenses: float = Query(ge=0, allow_inf_nan=False),
) -> dict[str, float]:
    """Calculate net balance from income and expenses in URL query parameters."""
    return {"balance": calculate_balance(income, expenses)}


@router.post("/savings-rate")
def savings_rate(data: SavingsRateInput) -> dict[str, float]:
    """Calculate savings as a percentage of income from the JSON body."""
    return {
        "savings_rate": _calculate(
            calculate_savings_rate, data.income, data.expenses
        )
    }


@router.post("/deficit")
def deficit(data: DeficitInput) -> dict[str, bool]:
    """Return whether the supplied balance is below zero."""
    return {"deficit": flag_deficit(data.balance)}


@router.post("/total")
def total(data: AmountsInput) -> dict[str, float]:
    """Add the amount values supplied in the JSON body."""
    return {"total": total_amount(data.amounts)}


@router.post("/category-totals")
def expenses_by_category(data: TransactionsInput) -> dict[str, dict[str, float]]:
    """Group and total expense transactions by category."""
    transactions = [transaction.model_dump() for transaction in data.transactions]
    return {"category_totals": category_totals(transactions)}


@router.post("/monthly-summary")
def summary(data: TransactionsInput) -> dict[str, Any]:
    """Summarize income, expenses, balance, savings rate, and categories."""
    transactions = [transaction.model_dump() for transaction in data.transactions]
    return monthly_summary(transactions)


@router.post("/survival-months")
def survival_months(data: SurvivalInput) -> dict[str, float | None | bool]:
    """Estimate emergency-fund runway after monthly benefits."""
    months = calculate_survival_months(
        data.available_savings,
        data.monthly_essential_expenses,
        data.monthly_benefits,
    )
    unlimited = not isfinite(months)
    return {"months": None if unlimited else months, "unlimited": unlimited}


@router.post("/validate/transaction")
def validate_transaction(data: TransactionValidationInput) -> dict[str, Any]:
    """Return the transaction after validating and normalizing its fields."""
    return {
        "type": data.type,
        "category": data.category,
        "amount": data.amount,
        "transaction_date": data.transaction_date.isoformat(),
    }
