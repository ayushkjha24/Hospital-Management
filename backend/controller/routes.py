from controller.admin.routes import AdminDashboard, AddDoctor
from controller.doctor.routes import DoctorDashboard
from controller.patient.routes import PatientDashboard

def initialize_routes(api):
    # Admin
    api.add_resource(AdminDashboard, "/admin/dashboard")
    api.add_resource(AddDoctor, "/admin/add-doctor")

    # Doctor
    api.add_resource(DoctorDashboard, "/doctor/dashboard")

    # Patient
    api.add_resource(PatientDashboard, "/patient/dashboard")
