from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    Bootstrap(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.project_routes import project_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)

    with app.app_context():
        db.create_all()

    return app