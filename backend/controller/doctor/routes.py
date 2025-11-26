from controller.security import RoleProtectedResource


class DoctorDashboard(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        return {"message": "Welcome Doctor"}
