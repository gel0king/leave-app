from flask import Flask

from app.routes import register_routes
from app.utils.config import get_database_uri

from .extensions import db
from . import models
from app.utils.security import get_or_create_secret

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = get_or_create_secret(
    "FLASK_SECRET_KEY"
    )
    
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)

    return app