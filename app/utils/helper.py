from decimal import Decimal, InvalidOperation
from flask import flash
from datetime import datetime, date
import calendar
from app.extensions import db
from sqlalchemy import func
from app.models import Log, LeaveType

ANNUAL_LEAVE_TIERS = [
    # min_years, hours_per_month, max_carryover
    (Decimal("0"),  Decimal("8"),  Decimal("180")),
    (Decimal("2"),  Decimal("9"),  Decimal("244")),
    (Decimal("5"),  Decimal("10"), Decimal("268")),
    (Decimal("10"), Decimal("11"), Decimal("292")),
    (Decimal("15"), Decimal("13"), Decimal("340")),
    (Decimal("20"), Decimal("15"), Decimal("388")),
    (Decimal("25"), Decimal("17"), Decimal("436")),
    (Decimal("30"), Decimal("19"), Decimal("484")),
    (Decimal("35"), Decimal("21"), Decimal("532")),
]

SICK_LEAVE_MONTHLY_ACCRUAL = Decimal("8")
FISCAL_YEAR_START_MONTH = 9  # September 1

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

def get_months_of_service(employee, as_of_date=None, full_time_only=False):
    if as_of_date is None:
        as_of_date = date.today()

    total_months = 0

    for period in employee.employment_periods:
        if period.start_date > as_of_date:
            continue

        if full_time_only and not (
            period.employment_status == "Full Time"
            and period.employment_date is not None
        ):
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

    period = get_current_employment_period(employee, as_of_date)

    if period is None:
        return 0

    return (
        (as_of_date.year - period.start_date.year) * 12
        + (as_of_date.month - period.start_date.month)
        + 1
    )

def get_annual_leave_tier(years_of_service):
    hours_per_month, max_carryover = ANNUAL_LEAVE_TIERS[0][1], ANNUAL_LEAVE_TIERS[0][2]

    for min_years, hpm, mc in ANNUAL_LEAVE_TIERS:
        if years_of_service >= min_years:
            hours_per_month, max_carryover = hpm, mc
        else:
            break

    return hours_per_month, max_carryover

def _add_months(d, months):
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def _is_on_unpaid_leave(period, month_start):
    if not period.departure_date:
        return False

    if month_start < period.departure_date:
        return False

    if period.return_date and month_start >= period.return_date:
        return False

    return True

def calculate_leave_balance(employee, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()

    period = get_current_employment_period(employee, as_of_date)

    if period is None:
        return {
            "annual": Decimal("0"),
            "annual_available": Decimal("0"),
            "sick": Decimal("0"),
        }

    annual = Decimal(period.starting_annual_leave or 0)
    sick = Decimal(period.starting_sick_leave or 0)

    is_full_time = (
        period.employment_status == "Full Time"
        and period.employment_date is not None
    )

    if is_full_time:
        baseline = period.leave_balance_date or period.employment_date

        # Assumes credit for this month was applied
        cursor = _add_months(date(baseline.year, baseline.month, 1), 1)
        last_month = date(as_of_date.year, as_of_date.month, 1)

        while cursor <= last_month:
            if cursor.month == FISCAL_YEAR_START_MONTH:
                years_of_service = Decimal(
                    get_months_of_service(employee, cursor, full_time_only=True)
                ) / Decimal("12")
                _, max_carryover = get_annual_leave_tier(years_of_service)

                if annual > max_carryover:
                    sick += annual - max_carryover
                    annual = max_carryover

            in_period = period.end_date is None or cursor <= period.end_date

            if in_period and not _is_on_unpaid_leave(period, cursor):
                years_of_service = Decimal(
                    get_months_of_service(employee, cursor, full_time_only=True)
                ) / Decimal("12")
                hours_per_month, _ = get_annual_leave_tier(years_of_service)

                annual += hours_per_month
                sick += SICK_LEAVE_MONTHLY_ACCRUAL

            cursor = _add_months(cursor, 1)

    annual -= get_used_hours(employee, "Annual Leave", as_of_date)
    sick -= get_used_hours(employee, "Sick Leave", as_of_date)

    if period.probation_end_date and as_of_date < period.probation_end_date:
        annual_available = Decimal("0")
    else:
        annual_available = annual

    return {
        "annual": annual,
        "annual_available": annual_available,
        "sick": sick,
    }

def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

def get_used_hours(employee, leave_type_name, as_of_date=None):

    if as_of_date is None:
        as_of_date = date.today()

    total = (
        db.session.query(func.coalesce(func.sum(Log.hours), 0))
        .join(LeaveType, Log.leave_type_id == LeaveType.id)
        .filter(
            Log.employee_id == employee.id,
            Log.action == "USED",
            LeaveType.name == leave_type_name,
            Log.start_date <= as_of_date,
        )
        .scalar()
    )
    return Decimal(total or 0)