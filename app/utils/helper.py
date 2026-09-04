from decimal import Decimal, InvalidOperation
from flask import flash
from datetime import datetime, date

ANNUAL_LEAVE_TIERS = [
    # min_years, max_years, hours_per_month, max_carryover
    (Decimal("0"), Decimal("1.916"), Decimal("8"), Decimal("180")),
    (Decimal("2"), Decimal("4.916"), Decimal("9"), Decimal("244")),
    (Decimal("5"), Decimal("9.916"), Decimal("10"), Decimal("268")),
    (Decimal("10"), Decimal("14.916"), Decimal("11"), Decimal("292")),
    (Decimal("15"), Decimal("19.916"), Decimal("13"), Decimal("340")),
    (Decimal("20"), Decimal("24.916"), Decimal("15"), Decimal("388")),
    (Decimal("25"), Decimal("29.916"), Decimal("17"), Decimal("436")),
    (Decimal("30"), Decimal("34.916"), Decimal("19"), Decimal("484")),
    (Decimal("35"), Decimal("99"), Decimal("21"), Decimal("532")),
]

def parse_leave_hours(value):
    try:
        hours = Decimal(value)
        if hours < 0:
            raise ValueError

        if hours % Decimal("0.5") != 0:
            raise ValueError

        return hours

    except (InvalidOperation, ValueError):
        flash(
            "Leave balances must be in 0.5 hour increments.",
            "error"
        )
        return None

def get_months_between(start_date, end_date):
    if not start_date or not end_date:
        return 0

    if end_date < start_date:
        return 0

    return (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
    )

def get_months_of_service(employee, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()

    total_months = 0

    for period in employee.employment_periods:
        if period.start_date > as_of_date:
            continue

        period_end = period.end_date or as_of_date

        if period_end > as_of_date:
            period_end = as_of_date

        total_months += get_months_between(
            period.start_date,
            period_end
        )

    return total_months

def get_current_employment_period(employee, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()

    for period in employee.employment_periods:
        if period.start_date > as_of_date:
            continue

        if period.end_date is None:
            return period

        if period.start_date <= as_of_date <= period.end_date:
            return period

    return None

def get_accrual_months(employee, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()

    period = get_current_employment_period(
        employee,
        as_of_date
    )

    if period is None:
        return 0

    return (
        (as_of_date.year - period.start_date.year) * 12
        + (as_of_date.month - period.start_date.month)
        + 1
    )

def calculate_leave_balance(employee, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()

    # Starting balances
    annual = Decimal(employee.starting_annual_leave or 0)
    sick = Decimal(employee.starting_sick_leave or 0)

    # TODO:
    # Add accruals from employment periods
    # Subtract approved/taken leave logs
    # Handle fiscal-year carryover
    # Handle separation resets
    # Handle probation restrictions

    return {
        "annual": annual,
        "sick": sick,
    }

def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return None