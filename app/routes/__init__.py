from .base import base_bp

def register_routes(app):
    app.register_blueprint(base_bp)
