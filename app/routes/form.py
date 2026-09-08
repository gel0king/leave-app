import os
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file

from app.extensions import db
from app.models import Employee, EmploymentPeriod, LeaveType, Log
from app.utils.helper import calculate_leave_balance, parse_leave_hours, parse_date
from app.utils.logging import create_log
from app.utils.leave_form import fill_leave_request_pdf

form_bp = Blueprint("form", __name__)

LEAVE_TYPE_OPTIONS = [
    "Annual Leave",
    "Sick Leave",
    "Emergency Leave",
    "Military Leave",
    "Leave Without Pay",
    "Extended Sick Leave",
    "Jury Duty",
    "Holiday Leave",
    "Other",
]

BALANCE_DEDUCTING_TYPES = {"Annual Leave", "Sick Leave"}


@form_bp.route("/form")
def form():
    latest_period_id = (
        db.session.query(db.func.max(EmploymentPeriod.id))
        .filter(EmploymentPeriod.employee_id == Employee.id)
        .correlate(Employee).scalar_subquery()
    )
    employees = (
        db.session.query(Employee)
        .join(EmploymentPeriod, EmploymentPeriod.id == latest_period_id)
        .filter(EmploymentPeriod.employment_status != "Inactive")
        .order_by(Employee.name)
        .all()
    )
    return render_template(
        "form.html",
        employees=employees,
        leave_types=LEAVE_TYPE_OPTIONS,
    )


@form_bp.route("/form", methods=["POST"])
def form_submit():
    employee_id = request.form.get("employee_id", "").strip()
    leave_type_name = request.form.get("leave_type", "").strip()
    other_specify = request.form.get("leave_other_specify", "").strip()
    total_hours_raw = request.form.get("total_hours", "").strip()
    from_date_str = request.form.get("from_date", "").strip()
    from_time = request.form.get("from_time", "").strip()
    to_date_str = request.form.get("to_date", "").strip()
    to_time = request.form.get("to_time", "").strip()
    comments = request.form.get("comments", "").strip()

    if not employee_id:
        flash("Select an employee.", "error")
        return redirect(request.url)

    employee = Employee.query.get_or_404(int(employee_id))

    if leave_type_name not in LEAVE_TYPE_OPTIONS:
        flash("Select a valid leave type.", "error")
        return redirect(request.url)

    if leave_type_name == "Other" and not other_specify:
        flash('Please specify the leave type for "Other".', "error")
        return redirect(request.url)

    total_hours = parse_leave_hours(total_hours_raw)
    if total_hours is None:
        return redirect(request.url)

    if total_hours <= 0:
        flash("Total hours must be greater than 0.", "error")
        return redirect(request.url)

    from_date_val = parse_date(from_date_str)
    to_date_val = parse_date(to_date_str)

    if not from_date_val:
        flash("From date is required.", "error")
        return redirect(request.url)

    if to_date_val and to_date_val < from_date_val:
        flash("To date cannot be before from date.", "error")
        return redirect(request.url)

    if leave_type_name in BALANCE_DEDUCTING_TYPES:
        balance = calculate_leave_balance(employee)
        available = (
            balance["annual_available"]
            if leave_type_name == "Annual Leave"
            else balance["sick"]
        )
        if total_hours > available:
            kind = "annual" if leave_type_name == "Annual Leave" else "sick"
            flash(
                f"{employee.name} only has {available} hours of {kind} leave available.",
                "error"
            )
            return redirect(request.url)

    leave_type = LeaveType.query.filter_by(name=leave_type_name).first()

    log = create_log(
        employee=employee,
        action="USED",
        description=f"{leave_type_name} request",
        notes=comments or None,
        leave_type=leave_type,
        start_date=from_date_val,
        end_date=to_date_val,
        hours=total_hours,
    )

    db.session.flush()

    pdf_path = fill_leave_request_pdf(
        employee=employee,
        leave_type_name=leave_type_name,
        other_specify=other_specify,
        total_hours=total_hours,
        from_date=from_date_val,
        from_time=from_time,
        to_date=to_date_val,
        to_time=to_time,
        comments=comments,
        log_id=log.id,
    )

    log.attachment_path = pdf_path

    db.session.commit()

    flash("Leave request submitted.", "success")

    return redirect(url_for("form.view_request", log_id=log.id))


@form_bp.route("/form/<int:log_id>/view")
def view_request(log_id):
    log = Log.query.get_or_404(log_id)
    return render_template("form_confirmation.html", log=log)


@form_bp.route("/form/<int:log_id>/pdf")
def download_request_pdf(log_id):
    log = Log.query.get_or_404(log_id)

    if not log.attachment_path or not os.path.exists(log.attachment_path):
        flash("PDF not found.", "error")
        return redirect(url_for("employees.employees"))

    return send_file(log.attachment_path, mimetype="application/pdf", as_attachment=False)