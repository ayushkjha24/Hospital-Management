from flask import request
from flask_restful import Resource, Api
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt
)
from controller.models import User, TokenBlocklist
from controller.database import db
from werkzeug.security import generate_password_hash, check_password_hash


class Register(Resource):
    def post(self):
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not all([name, email, password]):
            return {"message": "Name, email and password are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 400

        hashed = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed,
            role="patient"
        )

        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully"}, 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return {"message": "Invalid email or password"}, 401

        if not user.is_active:
            return {"message": "User account is disabled"}, 403

        # Identity as string (fixes JWT "sub must be string" error)
        identity = str(user.id)

        access_token = create_access_token(identity=identity, additional_claims={
            "role": user.role,
            "name": user.name
        })

        return {
            "username": user.name,
            "role": user.role,
            "message": "Login successful",
            "access_token": access_token
        }, 200


class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()

        return {"message": "Successfully logged out"}, 200
    
class CheckEmail(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        if not email:
            return {"message": "Email parameter is required"}, 400

        user = User.query.filter_by(email=email).first()
        if user:
            return {"exists": True}, 200
        else:
            return {"exists": False}, 200


def initialize_auth_routes(api: Api):
    api.add_resource(Register, "/register")
    api.add_resource(CheckEmail, "/check_email")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
