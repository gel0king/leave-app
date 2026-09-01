from flask import Blueprint, render_template
from app.models import Employee

employees_bp = Blueprint("employees", __name__)

@employees_bp.route("/employees")
def employees():
    employees = Employee.query.order_by(Employee.name).all()

    return render_template("employees.html", employees=employees)

@employees_bp.route("/employees/new")
def new_employee():
    return render_template("new_employee.html")

@employees_bp.route("/employees/add", methods=["POST"])
def add_employee_submit():
    pass