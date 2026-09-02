from datetime import datetime, time

from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload

from app.models import Log

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

    # Date filters
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

    # Sorting
    if order == "ASC":
        query = query.order_by(Log.time_created.asc())
    else:
        query = query.order_by(Log.time_created.desc())

    events = query.all()

    return render_template(
        "history.html",
        events=events,
        order=order,
        start_date=start_date_str,
        end_date=end_date_str,
    )
