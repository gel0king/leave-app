from datetime import date
from io import BytesIO

from flask import Blueprint, jsonify, render_template, request, send_file

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from app.utils.compliance import get_all_document_expirations, get_compliance_summary, get_active_employees

from app.utils.bribery import (
    get_certification_roster,
    create_certification_cycle,
    complete_certification,
    complete_onboarding_certification
)

from app.models import Employee, BriberyCertification, BriberyCertificationCycle, CompanyInsurancePolicy
from app.extensions import db


notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/summary")
def notification_summary():

    records = get_all_document_expirations()
    summary = get_compliance_summary(records)

    attention_records = [
        record for record in records
        if record["status"] in (
            "expired",
            "expiring_soon",
            "upcoming"
        )
    ]

    attention_records.sort(
        key=lambda r: (
            0 if r["status"] == "expired" else
            1 if r["status"] == "expiring_soon" else 2,
            r["expiration_date"]
        )
    )

    return jsonify({
        "summary": summary,
        "records": [
            {
                **record,
                "expiration_date": (
                    record["expiration_date"].isoformat()
                )
            }
            for record in attention_records
        ],
        "attention_count": (
            summary["expired"] + summary["expiring_soon"]
        )
    })


@notifications_bp.route("/compliance")
def compliance():

    records = get_all_document_expirations()

    summary = get_compliance_summary(records)

    document_type = request.args.get("type", "all")
    selected_statuses = request.args.getlist("status")

    if document_type != "all":
        records = [
            r for r in records
            if r["category"] == document_type
        ]

    if selected_statuses:
        records = [
            r for r in records
            if r["status"] in selected_statuses
        ]

    return render_template(
        "compliance.html",
        records=records,
        summary=summary
    )


@notifications_bp.route("/export")
def export_compliance():

    records = get_all_document_expirations()

    document_type = request.args.get("type", "all")
    statuses = request.args.getlist("status")

    if document_type != "all":
        records = [
            r for r in records
            if r["category"] == document_type
        ]

    if statuses:
        records = [
            r for r in records
            if r["status"] in statuses
        ]

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Compliance Report"

    headers = [
        "Employee / Policy",
        "Office",
        "Document Type",
        "Expiration Date",
        "Days Remaining",
        "Status"
    ]

    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            "solid",
            fgColor="1E3F3D"
        )

    for record in records:
        sheet.append([
            record["employee_name"],
            record["office"] or "",
            record["category"],
            record["expiration_date"],
            record["days_remaining"],
            record["status"].replace("_", " ").title()
        ])

    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )

        sheet.column_dimensions[
            get_column_letter(column[0].column)
        ].width = max_length + 3

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="compliance_report.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )



@notifications_bp.route("/bribery")
def bribery_compliance():

    year = request.args.get(
        "year",
        date.today().year,
        type=int
    )

    roster = get_certification_roster(year)

    cycles = BriberyCertificationCycle.query.order_by(
        BriberyCertificationCycle.year.desc()
    ).all()

    # Find active employees who still need onboarding.
    active_employees = get_active_employees()

    onboarding_employees = []

    for employee, period in active_employees:

        existing = BriberyCertification.query.filter_by(
            employee_id=employee.id,
            certification_type="ONBOARDING"
        ).first()

        if not existing:
            onboarding_employees.append(employee)

    return render_template(
        "bribery_compliance.html",
        roster=roster,
        year=year,
        cycles=cycles,
        onboarding_employees=onboarding_employees,
        today=date.today().isoformat()
    )

@notifications_bp.route("/bribery/create-cycle", methods=["POST"])
def create_bribery_cycle():
    year = request.form.get("year", type=int)

    scheduled_date_string = request.form.get(
        "scheduled_date"
    )

    if not year:
        return jsonify({
            "success": False,
            "message": "Please enter a valid year."
        }), 400

    try:

        scheduled_date = (
            date.fromisoformat(scheduled_date_string)
            if scheduled_date_string
            else date(year, 1, 1)
        )

        if scheduled_date.year != year:
            raise ValueError(
                "The scheduled date must belong to the selected year."
            )

        cycle = create_certification_cycle(
            year,
            scheduled_date
        )

        return jsonify({
            "success": True,
            "message": f"Created the {cycle.year} certification cycle."
        })

    except ValueError as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

@notifications_bp.route("/bribery/complete", methods=["POST"])
def record_bribery_certification():
    employee_id = request.form.get(
        "employee_id",
        type=int
    )

    cycle_id = request.form.get(
        "cycle_id",
        type=int
    )

    method = request.form.get(
        "completion_method",
        "INDIVIDUAL"
    )

    try:
        if not employee_id or not cycle_id:
            raise ValueError(
                "Employee and certification cycle are required."
            )

        complete_certification(
            employee_id=employee_id,
            cycle_id=cycle_id,
            completed_date=date.today(),
            completion_method=method,
            notes=request.form.get("notes")
        )

        return jsonify({
            "success": True,
            "message": "Annual certification recorded."
        })

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


@notifications_bp.route("/bribery/onboarding", methods=["POST"])
def record_onboarding_certification():
    employee_id = request.form.get(
        "employee_id",
        type=int
    )

    method = request.form.get(
        "completion_method",
        "INDIVIDUAL"
    )

    completed_date_string = request.form.get(
        "completed_date"
    )

    try:

        if not employee_id:
            raise ValueError("Please select an employee.")

        completed_date = (
            date.fromisoformat(completed_date_string)
            if completed_date_string
            else date.today()
        )

        complete_onboarding_certification(
            employee_id=employee_id,
            completed_date=completed_date,
            completion_method=method,
            notes=request.form.get("notes")
        )

        return jsonify({
            "success": True,
            "message": "Onboarding certification recorded."
        })

    except ValueError as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


@notifications_bp.route("/insurance")
def company_insurance():

    policies = CompanyInsurancePolicy.query.order_by(
        CompanyInsurancePolicy.expiration_date.asc()
    ).all()

    today = date.today()

    for policy in policies:
        policy.days_remaining = (
            policy.expiration_date - today
        ).days

        if policy.days_remaining < 0:
            policy.status = "expired"
        elif policy.days_remaining <= 30:
            policy.status = "expiring_soon"
        elif policy.days_remaining <= 90:
            policy.status = "upcoming"
        else:
            policy.status = "current"

    return render_template(
        "company_insurance.html",
        policies=policies
    )


@notifications_bp.route("/insurance/create", methods=["POST"])
def create_company_insurance():

    policy_name = request.form.get("policy_name", "").strip()
    policy_number = request.form.get("policy_number", "").strip()
    expiration_date_string = request.form.get("expiration_date")
    notes = request.form.get("notes", "").strip()

    if not policy_name or not expiration_date_string:
        return jsonify({
            "success": False,
            "message": "Policy name and expiration date are required."
        }), 400

    try:
        expiration_date = date.fromisoformat(
            expiration_date_string
        )
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid expiration date."
        }), 400

    policy = CompanyInsurancePolicy(
        policy_name=policy_name,
        policy_number=policy_number or None,
        expiration_date=expiration_date,
        notes=notes or None
    )

    db.session.add(policy)
    db.session.flush()

    return jsonify({
        "success": True,
        "message": "Company insurance policy created."
    })


@notifications_bp.route("/insurance/<int:policy_id>/update",methods=["POST"])
def update_company_insurance(policy_id):
    policy = db.session.get(
        CompanyInsurancePolicy,
        policy_id
    )

    if not policy:
        return jsonify({
            "success": False,
            "message": "Policy not found."
        }), 404

    policy_name = request.form.get("policy_name", "").strip()
    policy_number = request.form.get("policy_number", "").strip()
    expiration_date_string = request.form.get("expiration_date")
    notes = request.form.get("notes", "").strip()

    if not policy_name or not expiration_date_string:
        return jsonify({
            "success": False,
            "message": "Policy name and expiration date are required."
        }), 400

    try:
        expiration_date = date.fromisoformat(
            expiration_date_string
        )
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid expiration date."
        }), 400

    old_values = {
        "Policy Name": policy.policy_name,
        "Policy Number": policy.policy_number,
        "Expiration Date": (
            policy.expiration_date.strftime("%m/%d/%Y")
        )
    }

    new_values = {
        "Policy Name": policy_name,
        "Policy Number": policy_number or None,
        "Expiration Date": expiration_date.strftime("%m/%d/%Y")
    }

    policy.policy_name = policy_name
    policy.policy_number = policy_number or None
    policy.expiration_date = expiration_date
    policy.notes = notes or None

    db.session.add(policy)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Company insurance policy updated."
    })

@notifications_bp.route("/insurance/add", methods=["POST"])
def add_company_insurance():

    policy_name = request.form.get("policy_name", "").strip()
    policy_number = request.form.get("policy_number", "").strip()
    expiration_date_string = request.form.get("expiration_date")
    notes = request.form.get("notes", "").strip()

    if not policy_name or not expiration_date_string:
        return jsonify({
            "success": False,
            "message": "Policy name and expiration date are required."
        }), 400

    try:
        expiration_date = date.fromisoformat(expiration_date_string)

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid expiration date."
        }), 400

    policy = CompanyInsurancePolicy(
        policy_name=policy_name,
        policy_number=policy_number or None,
        expiration_date=expiration_date,
        notes=notes or None
    )

    db.session.add(policy)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Company insurance policy added successfully."
    })

@notifications_bp.route("/insurance/<int:policy_id>/edit", methods=["POST"])
def edit_company_insurance(policy_id):

    policy = db.session.get(
        CompanyInsurancePolicy,
        policy_id
    )

    if not policy:
        return jsonify({
            "success": False,
            "message": "Insurance policy not found."
        }), 404

    policy_name = request.form.get("policy_name", "").strip()
    expiration_date_string = request.form.get("expiration_date")

    if not policy_name or not expiration_date_string:
        return jsonify({
            "success": False,
            "message": "Policy name and expiration date are required."
        }), 400

    try:
        policy.expiration_date = date.fromisoformat(
            expiration_date_string
        )
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid expiration date."
        }), 400

    policy.policy_name = policy_name
    policy.policy_number = (
        request.form.get("policy_number", "").strip() or None
    )
    policy.notes = (
        request.form.get("notes", "").strip() or None
    )

    db.session.add(policy)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Insurance policy updated successfully."
    })