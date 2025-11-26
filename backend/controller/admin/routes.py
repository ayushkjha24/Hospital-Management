from flask import request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from controller.models import *
from controller.security import RoleProtectedResource

class AdminDashboard(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        return {"message": "Welcome Admin"}


class AddDoctor(RoleProtectedResource):
    required__roles = ["admin"]
    def post(self):
        data = request.get_json()
        doc_name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        if not all([doc_name, email, password]):
            return {"message": "Name, email and password are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 400

        hashed = generate_password_hash(password)

        new_user = User(
            name=doc_name,
            email=email,
            password=hashed,
            role="doctor"
        )

        db.session.add(new_user)
        db.session.commit()        
        return {"message": "Doctor added successfully"}, 201