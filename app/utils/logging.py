import json

from app.extensions import db
from app.models import Log


# Dont send raw values to create log
SENSITIVE_FIELDS = {
    "ssn",
    "date_of_birth",
    "license_number",
    "other_id_number",
    "address",
}


def serialize_value(value):
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def clean_values(values, side=None):
    # Change sensitive values to generic updates
    if not values:
        return {}

    cleaned = {}

    for field, value in values.items():

        if field in SENSITIVE_FIELDS:

            if value is None or value == "":
                cleaned[field] = None

            elif side == "new":
                cleaned[field] = "[CREATED]"

            else:
                cleaned[field] = "[EXISTS]"

        else:
            cleaned[field] = serialize_value(value)

    return cleaned


def create_log(
    employee,
    action,
    description=None,
    old_values=None,
    new_values=None,
    notes=None,
    leave_type=None,
    start_date=None,
    end_date=None,
    hours=None,
):
    raw_old_values = old_values or {}
    raw_new_values = new_values or {}

    old_values = clean_values(
        raw_old_values,
        side="old"
    )

    new_values = clean_values(
        raw_new_values,
        side="new"
    )

    # Check what kind of change was made
    for field in SENSITIVE_FIELDS:

        if field not in raw_old_values and field not in raw_new_values:
            continue

        old_exists = (
            raw_old_values.get(field) not in (None, "")
        )

        new_exists = (
            raw_new_values.get(field) not in (None, "")
        )

        if old_exists and new_exists:
            old_values[field] = "[EXISTS]"
            new_values[field] = "[UPDATED]"

        elif old_exists and not new_exists:
            old_values[field] = "[EXISTS]"
            new_values[field] = "[CLEARED]"

        elif not old_exists and new_exists:
            old_values[field] = None
            new_values[field] = "[CREATED]"

    log = Log(
        employee=employee,
        action=action,
        description=description,

        old_values=(
            json.dumps(old_values)
            if old_values
            else None
        ),

        new_values=(
            json.dumps(new_values)
            if new_values
            else None
        ),

        notes=notes,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        hours=hours,
    )

    db.session.add(log)

    return log


def parse_log_values(value):
    if not value:
        return {}

    try:
        return json.loads(value)

    except (json.JSONDecodeError, TypeError):
        return {
            "value": value
        }
