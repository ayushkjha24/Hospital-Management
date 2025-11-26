from controller.security import RoleProtectedResource


class PatientDashboard(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        return {"message": "Welcome Patient"}
