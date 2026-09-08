from flask import Flask

from app.routes import register_routes
from app.utils.config import get_database_uri, get_form_path

from .extensions import db
from . import models
from app.utils.security import get_or_create_secret
from make_form import generate_leave_form_template
from .models import LeaveType

import os

LEAVE_TYPE_ACCRUAL = {
    "Annual Leave": True,
    "Sick Leave": True,
    "Emergency Leave": False,
    "Military Leave": False,
    "Leave Without Pay": False,
    "Extended Sick Leave": False,
    "Jury Duty": False,
    "Holiday Leave": False,
    "Other": False,
}


def seed_leave_types():
    existing = {lt.name for lt in LeaveType.query.all()}

    for name, auto_accrual in LEAVE_TYPE_ACCRUAL.items():
        if name not in existing:
            db.session.add(LeaveType(name=name, auto_accrual=auto_accrual))

    db.session.commit()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = get_or_create_secret("FLASK_SECRET_KEY")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_leave_types()

        form_path = get_form_path()
        if form_path and not os.path.exists(form_path):
            generate_leave_form_template(form_path)

    register_routes(app)

    return app