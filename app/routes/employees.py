from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.extensions import db
from app.models import Employee
from app.utils.encryption import encrypt, decrypt
from app.utils.logging import create_log

from datetime import datetime

employees_bp = Blueprint("employees", __name__)

@employees_bp.route("/employees")
def employees():
    employees = Employee.query.order_by(Employee.name).all()

    return render_template("employees.html", employees=employees)

@employees_bp.route("/employees/new")
def new_employee():
    return render_template("new_employee.html")

@employees_bp.route("/employees/new", methods=["POST"])
def add_employee_submit():

    # Required fields
    employee_number = request.form.get("employee_number", "").strip()
    name = request.form.get("name", "").strip()
    start_date_string = request.form.get("start_date", "").strip()

    # Defaults
    employment_status = (
        request.form.get("employment_status", "").strip()
        or "Seasonal"
    )

    employment_history = (
        request.form.get("employment_history", "").strip()
        or "New Hire"
    )

    annual_hours = request.form.get("annual_balance", "0").strip()
    sick_hours = request.form.get("sick_balance", "0").strip()

    # Validate required fields
    if not employee_number:
        flash("Employee number is required.", "error")
        return redirect(request.url)

    if not name:
        flash("Employee name is required.", "error")
        return redirect(request.url)

    if not start_date_string:
        flash("Start date is required.", "error")
        return redirect(request.url)

    # Convert start date
    try:
        start_date = datetime.strptime(
            start_date_string,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        flash("Invalid start date.", "error")
        return redirect(request.url)

    # Convert leave hours to 30-minute intervals
    try:
        annual_leave = int(float(annual_hours) * 2)
        sick_leave = int(float(sick_hours) * 2)
    except ValueError:
        flash("Leave balances must be valid numbers.", "error")
        return redirect(request.url)

    # Encrypt sensitive fields
    ssn = encrypt(request.form.get("ssn", "").strip())

    date_of_birth = encrypt(
        request.form.get("date_of_birth", "").strip()
    )

    license_number = encrypt(
        request.form.get("license_number", "").strip()
    )

    other_id_number = encrypt(
        request.form.get("other_id_number", "").strip()
    )

    address = encrypt(
        request.form.get("address", "").strip()
    )

    # Create employee
    employee = Employee(
        employee_number=int(employee_number),
        name=name,
        office=request.form.get("office", "").strip() or None,

        starting_annual_leave=annual_leave,
        starting_sick_leave=sick_leave,

        start_date=start_date,

        employment_status=employment_status,
        employment_date=parse_date(
            request.form.get("employment_date")
        ),
        employment_history=employment_history,
        probation_end_date=parse_date(
            request.form.get("probation_end_date")
        ),

        departure_date=parse_date(
            request.form.get("departure_date")
        ),
        return_date=parse_date(
            request.form.get("return_date")
        ),

        driver_license_state=(
            request.form.get("driver_license_state", "")
            .strip()
            .upper()
            or None
        ),

        license_number=license_number,

        driver_license_expire_date=parse_date(
            request.form.get("driver_license_expire_date")
        ),

        other_id=request.form.get("other_id", "").strip() or None,
        other_id_number=other_id_number,

        ssn=ssn,
        date_of_birth=date_of_birth,

        insurance_expires=parse_date(
            request.form.get("insurance_expires")
        ),

        address=address,
        city=request.form.get("city", "").strip() or None,

        state=(
            request.form.get("state", "")
            .strip()
            .upper()
            or None
        ),

        zip=request.form.get("zip", "").strip() or None,
    )

    db.session.add(employee)
    create_log(
        employee=employee,
        action="CREATE",
        description="Employee created",
        new_values={
            "employee_number": employee.employee_number,
            "name": employee.name,
            "office": employee.office,

            "starting_annual_leave": employee.starting_annual_leave,
            "starting_sick_leave": employee.starting_sick_leave,

            "start_date": employee.start_date,
            "employment_status": employee.employment_status,
            "employment_date": employee.employment_date,
            "employment_history": employee.employment_history,
            "probation_end_date": employee.probation_end_date,

            "departure_date": employee.departure_date,
            "return_date": employee.return_date,

            "driver_license_state": employee.driver_license_state,
            "license_number": employee.license_number,
            "driver_license_expire_date": employee.driver_license_expire_date,

            "other_id": employee.other_id,
            "other_id_number": employee.other_id_number,

            "ssn": employee.ssn,
            "date_of_birth": employee.date_of_birth,

            "insurance_expires": employee.insurance_expires,

            "address": employee.address,
            "city": employee.city,
            "state": employee.state,
            "zip": employee.zip,
        },
    )

    db.session.commit()

    flash("Employee added.", "success")

    return redirect(
        url_for("employees.employees")
    )


@employees_bp.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
def edit_employee(emp_id):
    employee = Employee.query.get_or_404(emp_id)

    if request.method == "GET":
        return render_template(
            "edit_employee.html",
            employee=employee,
            ssn=decrypt(employee.ssn) if employee.ssn else "",
            date_of_birth=decrypt(employee.date_of_birth)
            if employee.date_of_birth else "",
            license_number=decrypt(employee.license_number)
            if employee.license_number else "",
            other_id_number=decrypt(employee.other_id_number)
            if employee.other_id_number else "",
            address=decrypt(employee.address)
            if employee.address else "",
        )
    
    old_values = {
        "employee_number": employee.employee_number,
        "name": employee.name,
        "office": employee.office,

        "starting_annual_leave": employee.starting_annual_leave,
        "starting_sick_leave": employee.starting_sick_leave,

        "start_date": employee.start_date,

        "employment_status": employee.employment_status,
        "employment_date": employee.employment_date,
        "employment_history": employee.employment_history,
        "probation_end_date": employee.probation_end_date,

        "departure_date": employee.departure_date,
        "return_date": employee.return_date,

        "driver_license_state": employee.driver_license_state,
        "license_number": (
            decrypt(employee.license_number)
            if employee.license_number
            else ""
        ),
        "driver_license_expire_date": employee.driver_license_expire_date,

        "other_id": employee.other_id,
        "other_id_number": (
            decrypt(employee.other_id_number)
            if employee.other_id_number
            else ""
        ),

        "ssn": (
            decrypt(employee.ssn)
            if employee.ssn
            else ""
        ),
        "date_of_birth": (
            decrypt(employee.date_of_birth)
            if employee.date_of_birth
            else ""
        ),

        "insurance_expires": employee.insurance_expires,

        "address": (
            decrypt(employee.address)
            if employee.address
            else ""
        ),
        "city": employee.city,
        "state": employee.state,
        "zip": employee.zip,
    }

    employee_number_string = request.form.get("employee_number","").strip()
    name = request.form.get("name", "").strip()
    start_date_string = request.form.get("start_date", "").strip()
    employment_status = (request.form.get("employment_status", "").strip() or "Seasonal")
    employment_history = (request.form.get("employment_history", "").strip() or "New Hire")
    annual_hours = request.form.get("annual_balance", "0").strip()
    sick_hours = request.form.get("sick_balance", "0").strip()

    if not employee_number_string:
        flash("Employee number is required.", "error")
        return redirect(request.url)

    if not name:
        flash("Employee name is required.", "error")
        return redirect(request.url)

    if not start_date_string:
        flash("Start date is required.", "error")
        return redirect(request.url)

    try:
        employee_number = int(employee_number_string)
    except ValueError:
        flash("Employee number must be a valid number.", "error")
        return redirect(request.url)

    try:
        start_date = datetime.strptime(
            start_date_string,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        flash("Invalid start date.", "error")
        return redirect(request.url)

    try:
        annual_leave = int(float(annual_hours) * 2)
        sick_leave = int(float(sick_hours) * 2)
    except ValueError:
        flash(
            "Leave balances must be valid numbers.",
            "error"
        )
        return redirect(request.url)

    ssn = request.form.get("ssn", "").strip()
    date_of_birth = request.form.get("date_of_birth", "").strip()
    license_number = request.form.get("license_number", "").strip()
    other_id_number = request.form.get("other_id_number", "").strip()
    address = request.form.get("address", "").strip()

    employee.employee_number = employee_number
    employee.name = name
    employee.office = (request.form.get("office", "").strip() or None)
    employee.starting_annual_leave = annual_leave
    employee.starting_sick_leave = sick_leave
    employee.start_date = start_date
    employee.employment_status = employment_status
    employee.employment_date = parse_date(request.form.get("employment_date"))
    employee.employment_history = employment_history
    employee.probation_end_date = parse_date(request.form.get("probation_end_date"))

    employee.departure_date = parse_date(request.form.get("departure_date"))
    employee.return_date = parse_date(request.form.get("return_date"))

    employee.driver_license_state = (request.form.get("driver_license_state", "").strip().upper() or None)
    employee.license_number = (encrypt(license_number) if license_number else None)
    employee.driver_license_expire_date = parse_date(request.form.get("driver_license_expire_date"))

    employee.other_id = (request.form.get("other_id","").strip() or None)
    employee.other_id_number = (encrypt(other_id_number) if other_id_number else None)
    employee.ssn = (encrypt(ssn) if ssn else None)
    employee.date_of_birth = (encrypt(date_of_birth) if date_of_birth else None)
    employee.insurance_expires = parse_date(request.form.get("insurance_expires"))

    employee.address = (encrypt(address) if address else None)
    employee.city = (request.form.get("city", "").strip() or None)
    employee.state = (request.form.get("state", "").strip().upper() or None)
    employee.zip = (request.form.get("zip", "").strip() or None)

    new_values = {
        "employee_number": employee.employee_number,
        "name": employee.name,
        "office": employee.office,

        "starting_annual_leave": employee.starting_annual_leave,
        "starting_sick_leave": employee.starting_sick_leave,

        "start_date": employee.start_date,

        "employment_status": employee.employment_status,
        "employment_date": employee.employment_date,
        "employment_history": employee.employment_history,
        "probation_end_date": employee.probation_end_date,

        "departure_date": employee.departure_date,
        "return_date": employee.return_date,

        "driver_license_state": employee.driver_license_state,
        "license_number": license_number,
        "driver_license_expire_date": employee.driver_license_expire_date,

        "other_id": employee.other_id,
        "other_id_number": other_id_number,

        "ssn": ssn,
        "date_of_birth": date_of_birth,

        "insurance_expires": employee.insurance_expires,

        "address": address,
        "city": employee.city,
        "state": employee.state,
        "zip": employee.zip,
    }

    # Only add changed fields
    changed_old_values = {}
    changed_new_values = {}

    for field in old_values:
        if old_values.get(field) != new_values.get(field):
            changed_old_values[field] = old_values.get(field)
            changed_new_values[field] = new_values.get(field)

    if changed_old_values:
        create_log(
            employee=employee,
            action="UPDATE",
            description="Employee information updated",
            old_values=changed_old_values,
            new_values=changed_new_values,
        )

    db.session.commit()

    flash("Employee updated.", "success")

    return redirect(url_for("employees.employees"))

# TODO: Implement soft delete for employees.
@employees_bp.route(
    "/employees/<int:emp_id>/remove",
    methods=["POST"]
)
def remove_employee(emp_id):
    return render_template("employees.html")


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