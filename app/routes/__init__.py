from .base import base_bp
from .employees import employees_bp
from .history import history_bp

def register_routes(app):
    app.register_blueprint(base_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(history_bp)