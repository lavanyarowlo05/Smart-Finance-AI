import math

import pytest

from backend.services.survival_engine import calculate_survival_months


# TC-03: Standard survival
def test_tc03_standard_survival_is_four_months():
    assert calculate_survival_months(60000, 15000) == 4.0


# TC-04: Negative savings
def test_tc04_negative_savings_raises():
    with pytest.raises(ValueError, match="Savings cannot be negative"):
        calculate_survival_months(-1000, 12000)


# Scenarios from section 7 of the document (Rs 60,000 fund)
@pytest.mark.parametrize(
    "burn, expected",
    [(12000, 5.0), (15000, 4.0), (20000, 3.0)],
)
def test_runway_scenarios(burn, expected):
    assert calculate_survival_months(60000, burn) == expected


def test_zero_essential_expenses_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_survival_months(60000, 0)


def test_negative_benefits_raises():
    with pytest.raises(ValueError, match="Benefits cannot be negative"):
        calculate_survival_months(60000, 15000, -100)


def test_benefits_reduce_burn():
    # burn = 15000 - 5000 = 10000 -> 6 months
    assert calculate_survival_months(60000, 15000, 5000) == 6.0


def test_benefits_cover_essentials_gives_infinity():
    assert math.isinf(calculate_survival_months(60000, 15000, 15000))
    assert math.isinf(calculate_survival_months(60000, 15000, 20000))


def test_zero_savings_gives_zero_months():
    assert calculate_survival_months(0, 15000) == 0.0


def test_result_rounded_to_two_decimals():
    assert calculate_survival_months(10000, 3000) == 3.33
