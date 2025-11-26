from flask_restful import Resource
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import abort


class RoleProtectedResource(Resource):
    required_roles = []   # override in child classes

    def dispatch_request(self, *args, **kwargs):
        verify_jwt_in_request()

        role = get_jwt().get("role")

        if self.required_roles and role not in self.required_roles:
            abort(403)

        return super().dispatch_request(*args, **kwargs)
