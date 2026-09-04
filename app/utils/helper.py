from decimal import Decimal, InvalidOperation
from flask import flash


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
