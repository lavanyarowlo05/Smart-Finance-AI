"""Unemployment survival (emergency runway) calculations."""


def calculate_survival_months(
    available_savings: float,
    monthly_essential_expenses: float,
    monthly_benefits: float = 0.0,
) -> float:
    """Return how many months savings last after benefits offset expenses."""
    if available_savings < 0:
        raise ValueError("Savings cannot be negative.")
    if monthly_essential_expenses <= 0:
        raise ValueError("Essential expenses must be greater than zero.")
    if monthly_benefits < 0:
        raise ValueError("Benefits cannot be negative.")

    net_monthly_burn = monthly_essential_expenses - monthly_benefits
    if net_monthly_burn <= 0:
        return float("inf")
    return round(available_savings / net_monthly_burn, 2)
