from .extensions import db

class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)

    employee_number = db.Column(
        db.Integer,
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    office = db.Column(db.String(255))

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    driver_license_state = db.Column(db.String(2))
    license_number = db.Column(db.Text)
    driver_license_expire_date = db.Column(db.Date)

    other_id = db.Column(db.String(100))
    other_id_number = db.Column(db.Text)

    ssn = db.Column(db.Text)
    date_of_birth = db.Column(db.Text)

    insurance_expires = db.Column(db.Date)

    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp() 
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    logs = db.relationship(
        "Log",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

    employment_periods = db.relationship(
        "EmploymentPeriod",
        back_populates="employee",
        cascade="all, delete-orphan",
        order_by="EmploymentPeriod.start_date",
    )

    bribery_certifications = db.relationship(
        "BriberyCertification",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

class LeaveType(db.Model):
    __tablename__ = "leave_types"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    auto_accrual = db.Column(
        db.Boolean,
        default=False
    )

    logs = db.relationship(
        "Log",
        back_populates="leave_type"
    )

class Log(db.Model):
    __tablename__ = "log"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )

    leave_type_id = db.Column(
        db.Integer,
        db.ForeignKey("leave_types.id")
    )

    employee = db.relationship(
        "Employee",
        back_populates="logs"
    )

    leave_type = db.relationship(
        "LeaveType",
        back_populates="logs"
    )

    action = db.Column(db.String(100))
    description = db.Column(db.Text)
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    notes = db.Column(db.Text)
    attachment_path = db.Column(db.Text)

    time_created = db.Column(
    db.DateTime,
    server_default=db.func.current_timestamp(),
    nullable=False,
    index=True
    )

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    hours = db.Column(db.Numeric(6, 1))

class EmploymentPeriod(db.Model):
    __tablename__ = "employment_periods"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    employment_date = db.Column(
        db.Date,
        nullable=True
    )

    employment_status = db.Column(
        db.String(100),
        nullable=False,
        default="Seasonal"
    )

    employment_history = db.Column(
        db.Text,
        nullable=True
    )

    probation_end_date = db.Column(
        db.Date,
        nullable=True
    )

    starting_annual_leave = db.Column(
        db.Numeric(6, 1),
        nullable=False,
        default=0
    )

    starting_sick_leave = db.Column(
        db.Numeric(6, 1),
        nullable=False,
        default=0
    )

    leave_balance_date = db.Column(
        db.Date,
        nullable=True
    )

    end_date = db.Column(
        db.Date,
        nullable=True
    )

    departure_date = db.Column(
        db.Date,
        nullable=True
    )

    return_date = db.Column(
        db.Date,
        nullable=True
    )

    employee = db.relationship(
        "Employee",
        back_populates="employment_periods"
    )


class BriberyCertificationCycle(db.Model):
    __tablename__ = "bribery_certification_cycles"

    id = db.Column(db.Integer, primary_key=True)

    year = db.Column(
        db.Integer,
        unique=True,
        nullable=False
    )

    scheduled_date = db.Column(db.Date)

    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    certifications = db.relationship(
        "BriberyCertification",
        back_populates="cycle",
        cascade="all, delete-orphan"
    )




class BriberyCertification(db.Model):
    __tablename__ = "bribery_certifications"

    __table_args__ = (
        db.UniqueConstraint(
            "employee_id",
            "cycle_id",
            name="uq_employee_bribery_cycle"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=False,
        index=True
    )

    cycle_id = db.Column(
        db.Integer,
        db.ForeignKey("bribery_certification_cycles.id"),
        nullable=True,
        index=True
    )

    certification_type = db.Column(
        db.String(50),
        nullable=False
    )

    certification_year = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    completion_method = db.Column(
        db.String(50),
        nullable=True
    )

    completed_date = db.Column(
        db.Date,
        nullable=True
    )

    notes = db.Column(db.Text)

    employee = db.relationship(
        "Employee",
        back_populates="bribery_certifications"
    )

    cycle = db.relationship(
        "BriberyCertificationCycle",
        back_populates="certifications"
    )



class CompanyInsurancePolicy(db.Model):
    __tablename__ = "company_insurance_policies"

    id = db.Column(db.Integer, primary_key=True)

    policy_name = db.Column(
        db.String(255),
        nullable=False
    )

    policy_number = db.Column(db.String(100))

    expiration_date = db.Column(
        db.Date,
        nullable=False
    )

    notes = db.Column(db.Text)

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
