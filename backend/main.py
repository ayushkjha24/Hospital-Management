from flask import Flask
from controller.database import db
from controller.config import Config
from controller.models import User, TokenBlocklist
from flask_restful import Api
from flask_jwt_extended import JWTManager
from controller.auth import initialize_auth_routes
from controller.routes import initialize_routes
from werkzeug.security import generate_password_hash


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- JWT CONFIG ---
    jwt = JWTManager(app)

    # Check token against blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlocklist.query.filter_by(jti=jti).first() is not None

    db.init_app(app)
    api = Api(app)

    # ---- AUTO CREATE ADMIN USER ----
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email='admin@gmail.com').first():
            admin_user = User(
                name='Admin',
                email='admin@gmail.com',
                password=generate_password_hash('admin123'),  # TODO: hash this
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

    # Register routes
    initialize_auth_routes(api)
    initialize_routes(api)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)