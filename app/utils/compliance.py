
from datetime import date

from app.extensions import db
from app.models import (
    Employee,
    EmploymentPeriod,
    CompanyInsurancePolicy,
)


def get_expiration_status(expiration_date, today=None):
    if expiration_date is None:
        return "unknown"

    today = today or date.today()
    days_remaining = (expiration_date - today).days

    if days_remaining < 0:
        return "expired"
    elif days_remaining <= 30:
        return "expiring_soon"
    elif days_remaining <= 90:
        return "upcoming"

    return "current"


def get_days_remaining(expiration_date, today=None):
    if expiration_date is None:
        return None

    today = today or date.today()
    return (expiration_date - today).days






def get_active_employees():
    employees = (
        db.session.query(Employee, EmploymentPeriod)
        .join(
            EmploymentPeriod,
            EmploymentPeriod.employee_id == Employee.id
        )
        .filter(
            EmploymentPeriod.id == (
                db.session.query(
                    db.func.max(EmploymentPeriod.id)
                )
                .filter(
                    EmploymentPeriod.employee_id == Employee.id
                )
                .correlate(Employee)
                .scalar_subquery()
            )
        )
        .filter(
            db.func.lower(
                db.func.trim(EmploymentPeriod.employment_status)
            ) != "inactive"
        )
        .order_by(Employee.name)
        .all()
    )

    return employees




def get_employee_document_expirations(today=None):
    if today is None:
        today = date.today()

    records = []

    employees = get_active_employees()

    for employee, period in employees:

        documents = [
            (
                "Driver's License",
                employee.driver_license_expire_date
            ),
            (
                "Vehicle Insurance",
                employee.insurance_expires
            ),
        ]

        for document_type, expiration_date in documents:

            if expiration_date is None:
                continue

            records.append({
                "employee_id": employee.id,
                "employee_name": employee.name,
                "office": employee.office,
                "category": document_type,
                "expiration_date": expiration_date,
                "days_remaining": get_days_remaining(
                    expiration_date, today
                ),
                "status": get_expiration_status(
                    expiration_date, today
                ),
            })

    return records



def get_company_insurance_expirations(today=None):
    if today is None:
        today = date.today()

    records = []

    policies = CompanyInsurancePolicy.query.order_by(
        CompanyInsurancePolicy.expiration_date
    ).all()

    for policy in policies:

        records.append({
            "policy_id": policy.id,
            "employee_id": None,
            "employee_name": policy.policy_name,
            "office": "Company-wide",
            "category": "Company Insurance Policy",
            "expiration_date": policy.expiration_date,
            "days_remaining": get_days_remaining(
                policy.expiration_date,
                today
            ),
            "status": get_expiration_status(
                policy.expiration_date,
                today
            ),
        })

    return records



def get_compliance_summary(records):
    return {
        "expired": sum(
            1 for r in records if r["status"] == "expired"
        ),
        "expiring_soon": sum(
            1 for r in records if r["status"] == "expiring_soon"
        ),
        "upcoming": sum(
            1 for r in records if r["status"] == "upcoming"
        ),
        "current": sum(
            1 for r in records if r["status"] == "current"
        ),
    }


def get_all_document_expirations(today=None):
    records = []

    records.extend(
        get_employee_document_expirations(today)
    )

    records.extend(
        get_company_insurance_expirations(today)
    )

    records.sort(
        key=lambda r: r["expiration_date"]
    )

    return records
