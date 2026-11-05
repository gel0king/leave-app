from app.extensions import db
from app.models import Employee, EmploymentPeriod
from datetime import date

# check for expiring drivers license and insurance
# checks once a day (8:00 am)
def check_expirations():
    print("Notification")
    today = date.today()
    latest_period_id = (
            db.session.query(db.func.max(EmploymentPeriod.id))
            .filter(EmploymentPeriod.employee_id == Employee.id)
            .correlate(Employee).scalar_subquery()
        )
    employees = (
        db.session.query(Employee, EmploymentPeriod)
        .join(
            EmploymentPeriod,
            EmploymentPeriod.id == latest_period_id)
            .filter(EmploymentPeriod.employment_status != "Inactive")
            .order_by(Employee.name)
            .all()
    )

    for e, p in employees:
        print(e.driver_license_expire_date)
        print(e.insurance_expire_date)

# update leave balances
# runs on the 1st of every month (8:00 am)
def driver_policy_renewal():
    ...
    