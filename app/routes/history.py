
from datetime import datetime, time

from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload

from app.models import Log
from app.utils.logging import parse_log_values

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
def history():

    order = request.args.get("order", "DESC").upper()

    if order not in ("ASC", "DESC"):
        order = "DESC"

    query = (
        Log.query
        .options(
            joinedload(Log.employee),
            joinedload(Log.leave_type)
        )
    )

    start_date_str = request.args.get("start_date", "")
    end_date_str = request.args.get("end_date", "")

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(
                start_date_str,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            start_date_str = ""

    if end_date_str:
        try:
            end_date = datetime.strptime(
                end_date_str,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            end_date_str = ""

    if start_date:
        query = query.filter(
            Log.time_created >= datetime.combine(
                start_date,
                time.min
            )
        )

    if end_date:
        query = query.filter(
            Log.time_created <= datetime.combine(
                end_date,
                time.max
            )
        )

    if order == "ASC":
        query = query.order_by(Log.time_created.asc())
    else:
        query = query.order_by(Log.time_created.desc())

    events = query.all()

    for event in events:

        old_values = parse_log_values(event.old_values)
        new_values = parse_log_values(event.new_values)

        event.old_values_display = old_values
        event.new_values_display = new_values

        changes = []

        fields = list(dict.fromkeys(
            list(old_values.keys()) +
            list(new_values.keys())
        ))

        for field in fields:

            old_value = old_values.get(field)
            new_value = new_values.get(field)

            if old_value != new_value:

                changes.append({
                    "field": field,
                    "old": old_value,
                    "new": new_value
                })

        leave_details = [
            ("leave_type", "Leave Type",
             event.leave_type.name if event.leave_type else None),

            ("start_date", "Start Date",
             event.start_date.strftime("%m/%d/%Y")
             if event.start_date else None),

            ("end_date", "End Date",
             event.end_date.strftime("%m/%d/%Y")
             if event.end_date else None),

            ("hours", "Hours",
             event.hours if event.hours is not None else None),
        ]

        for field, label, value in leave_details:

            if value is not None:

                changes.append({
                    "field": label,
                    "old": "—",
                    "new": value
                })

        event.changes_display = changes

    return render_template(
        "history.html",
        events=events,
        order=order,
        start_date=start_date_str,
        end_date=end_date_str,
    )
