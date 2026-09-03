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

    # Leave is stored as 30-minute intervals
    starting_annual_leave = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    starting_sick_leave = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    employment_status = db.Column(db.String(100))
    employment_date = db.Column(db.Date)
    employment_history = db.Column(db.Text)
    probation_end_date = db.Column(db.Date)

    departure_date = db.Column(db.Date)
    return_date = db.Column(db.Date)

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
        back_populates="employee"
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

    time_created = db.Column(
    db.DateTime,
    server_default=db.func.current_timestamp(),
    nullable=False,
    index=True
    )

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    hours = db.Column(db.Float)

