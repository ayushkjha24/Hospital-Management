from flask_restful import Resource
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from flask import abort
from controller.models import User


class RoleProtectedResource(Resource):
    required_roles = []   # override in child classes

    def dispatch_request(self, *args, **kwargs):
        try:
            verify_jwt_in_request()
        except:
            abort(401)
        
        claims = get_jwt()
        role = claims.get("role")
        
        if self.required_roles and role not in self.required_roles:
            abort(403)
        
        # Set current_user for use in handlers
        user_id = get_jwt_identity()
        try:
            uid = int(user_id)
        except:
            uid = user_id
        
        self.current_user = User.query.get(uid)
        if not self.current_user:
            abort(401)
        
        return super().dispatch_request(*args, **kwargs)
