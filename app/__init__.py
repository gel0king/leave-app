from flask import Flask
from app.routes import register_routes
from app.db import init_db, close_db
from utils.config import get_db_path
import json


def create_app():
    app = Flask(__name__)

    db_path = get_db_path()
    init_db(db_path)

    app.teardown_appcontext(close_db)

    register_routes(app)

    return app