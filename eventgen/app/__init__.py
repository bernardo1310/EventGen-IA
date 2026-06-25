from flask import Flask
from .models.database import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = 'eventgen-ai-secret-key-2024'

    init_db()

    from .routes.event_routes import event_bp
    from .routes.area_routes import area_bp
    from .routes.optimization_routes import optimization_bp

    app.register_blueprint(event_bp)
    app.register_blueprint(area_bp)
    app.register_blueprint(optimization_bp)

    return app
