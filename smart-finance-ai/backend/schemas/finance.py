"""Validated request models for finance API endpoints."""

from datetime import date
from math import isfinite
from typing import Any

from pydantic import BaseModel, Field, field_validator

if __package__.startswith("backend."):
    from ..services.validators import (
        validate_amount,
        validate_category,
        validate_date,
        validate_transaction_type,
    )
else:
    from services.validators import (
        validate_amount,
        validate_category,
        validate_date,
        validate_transaction_type,
    )


class BalanceInput(BaseModel):
    """Non-negative income and expenses for a balance calculation."""

    income: float = Field(ge=0, allow_inf_nan=False)
    expenses: float = Field(ge=0, allow_inf_nan=False)


class SavingsRateInput(BaseModel):
    """Income and expenses for a savings-rate calculation."""

    income: float = Field(allow_inf_nan=False)
    expenses: float = Field(ge=0, allow_inf_nan=False)


class DeficitInput(BaseModel):
    """Balance value to check for a deficit."""

    balance: float = Field(allow_inf_nan=False)


class AmountsInput(BaseModel):
    """List of finite, non-negative amounts to add."""

    amounts: list[float]

    @field_validator("amounts")
    @classmethod
    def validate_amounts(cls, amounts: list[float]) -> list[float]:
        """Reject non-finite or negative values in the amount list."""
        if any(not isfinite(amount) or amount < 0 for amount in amounts):
            raise ValueError("Amounts must be finite numbers that are not negative.")
        return amounts


class TransactionInput(BaseModel):
    """Validated income or expense row."""

    type: str
    category: str
    amount: float = Field(allow_inf_nan=False)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        """Normalize the transaction type and allow only income or expense."""
        return validate_transaction_type(value)

    @field_validator("category")
    @classmethod
    def validate_category_value(cls, value: str) -> str:
        """Trim and require a non-empty transaction category."""
        return validate_category(value)

    @field_validator("amount")
    @classmethod
    def validate_amount_value(cls, value: float) -> float:
        """Require a positive finite transaction amount."""
        return validate_amount(value)


class TransactionsInput(BaseModel):
    """Collection of validated transactions for summaries."""

    transactions: list[TransactionInput]


class SurvivalInput(BaseModel):
    """Savings, essential monthly expenses, and optional benefit income."""

    available_savings: float = Field(ge=0, allow_inf_nan=False)
    monthly_essential_expenses: float = Field(gt=0, allow_inf_nan=False)
    monthly_benefits: float = Field(default=0, ge=0, allow_inf_nan=False)


class TransactionValidationInput(TransactionInput):
    """Transaction fields plus its ISO calendar date."""

    transaction_date: date

    @field_validator("transaction_date", mode="before")
    @classmethod
    def validate_transaction_date(cls, value: Any) -> date:
        """Parse and validate an ISO transaction date."""
        return validate_date(value)
