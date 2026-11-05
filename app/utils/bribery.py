from datetime import date

from app.extensions import db
from app.models import (
    Employee,
    BriberyCertification,
    BriberyCertificationCycle,
    EmploymentPeriod,
    Log,
)
from app.utils.compliance import get_active_employees
import json


def get_certification_roster(year):
    cycle = BriberyCertificationCycle.query.filter_by(
        year=year
    ).first()

    if not cycle:
        return None

    active_employees = get_active_employees()

    certifications = {
        certification.employee_id: certification
        for certification in BriberyCertification.query.filter_by(
            cycle_id=cycle.id,
            certification_type="ANNUAL"
        ).all()
    }

    roster = []

    for employee, period in active_employees:

        if (
            cycle.scheduled_date
            and period.start_date > cycle.scheduled_date
        ):
            continue

        certification = certifications.get(employee.id)

        roster.append({
            "employee_id": employee.id,
            "employee_number": employee.employee_number,
            "employee_name": employee.name,
            "office": employee.office,
            "employment_status": period.employment_status,
            "status": (
                "completed" if certification else "pending"
            ),
            "completed_date": (
                certification.completed_date
                if certification else None
            ),
            "completion_method": (
                certification.completion_method
                if certification else None
            ),
            "certification_id": (
                certification.id if certification else None
            ),
        })

    return {
        "cycle": cycle,
        "employees": roster,
        "total": len(roster),
        "completed": sum(
            1 for employee in roster
            if employee["status"] == "completed"
        ),
        "pending": sum(
            1 for employee in roster
            if employee["status"] == "pending"
        ),
    }


def get_onboarding_roster():

    active_employees = get_active_employees()

    completed_ids = {
        certification.employee_id
        for certification in BriberyCertification.query.filter_by(
            certification_type="ONBOARDING"
        ).all()
    }

    roster = []

    for employee, period in active_employees:

        certification = next(
            (
                c for c in employee.bribery_certifications
                if c.certification_type == "ONBOARDING"
            ),
            None
        )

        roster.append({
            "employee_id": employee.id,
            "employee_number": employee.employee_number,
            "employee_name": employee.name,
            "office": employee.office,
            "employment_status": period.employment_status,
            "status": (
                "completed"
                if employee.id in completed_ids
                else "pending"
            ),
            "completed_date": (
                certification.completed_date
                if certification else None
            ),
        })

    return {
        "employees": roster,
        "total": len(roster),
        "completed": sum(
            1 for employee in roster
            if employee["status"] == "completed"
        ),
        "pending": sum(
            1 for employee in roster
            if employee["status"] == "pending"
        ),
    }


def create_certification_cycle(year, scheduled_date=None):

    existing = BriberyCertificationCycle.query.filter_by(
        year=year
    ).first()

    if existing:
        raise ValueError(
            f"The {year} certification cycle already exists."
        )

    if scheduled_date is None:
        scheduled_date = date(year, 1, 1)

    if scheduled_date.year != year:
        raise ValueError(
            "Scheduled date must belong to the selected year."
        )

    cycle = BriberyCertificationCycle(
        year=year,
        scheduled_date=scheduled_date
    )

    db.session.add(cycle)
    db.session.commit()

    return cycle



def complete_certification(employee_id, cycle_id, completed_date=None, completion_method="INDIVIDUAL", notes=None):
    if completed_date is None:
        completed_date = date.today()

    cycle = db.session.get(
        BriberyCertificationCycle,
        cycle_id
    )

    employee = db.session.get(
        Employee,
        employee_id
    )

    if not cycle or not employee:
        raise ValueError(
            "Employee or certification cycle not found."
        )

    if completion_method not in ("GROUP", "INDIVIDUAL"):
        raise ValueError("Invalid completion method.")

    active_employee_ids = {
        emp.id
        for emp, period in get_active_employees()
    }

    if employee_id not in active_employee_ids:
        raise ValueError(
            "Employee is currently inactive or has no active employment period."
        )

    # Employees hired after the annual scheduled date
    # must complete onboarding certification instead.
    if (
        cycle.scheduled_date
        and employee.start_date > cycle.scheduled_date
    ):
        raise ValueError(
            "This employee joined after the annual certification date. "
            "Use onboarding certification instead."
        )

    existing = BriberyCertification.query.filter_by(
        employee_id=employee_id,
        cycle_id=cycle_id,
        certification_type="ANNUAL"
    ).first()

    if existing:
        raise ValueError(
            "This employee has already completed this cycle."
        )

    certification = BriberyCertification(
        employee_id=employee_id,
        cycle_id=cycle_id,
        certification_type="ANNUAL",
        certification_year=cycle.year,
        completion_method=completion_method,
        completed_date=completed_date,
        notes=notes
    )

    db.session.add(certification)
    db.session.commit()

    return certification



def complete_onboarding_certification(
    employee_id,
    completed_date=None,
    completion_method="INDIVIDUAL",
    notes=None
):
    if completed_date is None:
        completed_date = date.today()

    employee = db.session.get(Employee, employee_id)

    if not employee:
        raise ValueError("Employee not found.")

    if completion_method not in ("GROUP", "INDIVIDUAL"):
        raise ValueError("Invalid completion method.")

    existing = BriberyCertification.query.filter_by(
        employee_id=employee_id,
        certification_type="ONBOARDING"
    ).first()

    if existing:
        raise ValueError(
            "This employee already has an onboarding certification."
        )

    certification = BriberyCertification(
        employee_id=employee_id,
        cycle_id=None,
        certification_type="ONBOARDING",
        certification_year=completed_date.year,
        completion_method=completion_method,
        completed_date=completed_date,
        notes=notes
    )

    db.session.add(certification)

    # Create structured activity history
    log = Log(
        employee_id=employee.id,
        action="UPDATE",
        description="Bribery onboarding certification completed.",
        old_values=json.dumps({}),
        new_values=json.dumps({
            "Certification Type": "Onboarding",
            "Completion Method": completion_method.title(),
            "Completed Date": completed_date.strftime("%m/%d/%Y"),
            "Certification Year": completed_date.year,
        }),
        notes=notes
    )

    db.session.add(log)

    db.session.commit()

    return certification



