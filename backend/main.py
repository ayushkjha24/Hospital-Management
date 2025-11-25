from flask import Flask
from controller.database import db
from controller.config import Config
from controller.models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@gmail.com').first():
            admin_user = User(
                name = 'Admin',
                email =  'admin@gmail.com',
                password = 'admin123',
                role = 'admin'
            )
            db.session.add(admin_user)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
    