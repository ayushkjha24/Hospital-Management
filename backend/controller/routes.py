from controller.admin.routes import *
from controller.doctor.routes import *
from controller.patient.routes import *


def initialize_routes(api):
    # -------------------------
    # ADMIN ROUTES
    # -------------------------
    api.add_resource(AdminDashboard, "/admin/dashboard")
    api.add_resource(AddDoctor, "/admin/add-doctor")
    api.add_resource(GetDoctors, "/admin/doctors")
    api.add_resource(DeleteDoctor, "/admin/delete-doctor/<int:doctor_id>")
    api.add_resource(EditDoctor, "/admin/edit-doctor/<int:doctor_id>")
    api.add_resource(BlacklistDoctor, "/admin/blacklist-doctor/<int:doctor_id>")

    api.add_resource(GetPatients, "/admin/patients")
    api.add_resource(EditPatient, "/admin/edit-patient/<int:patient_id>")
    api.add_resource(DeletePatient, "/admin/delete-patient/<int:patient_id>")
    api.add_resource(BlacklistPatient, "/admin/blacklist-patient/<int:patient_id>")

    api.add_resource(UpcomingAppointments, "/admin/appointments/upcoming")
    api.add_resource(PatientHistory, "/admin/patient-history/<int:patient_id>")

    api.add_resource(SearchDoctors, "/admin/search/doctors")
    api.add_resource(SearchPatients, "/admin/search/patients")
    api.add_resource(AddDepartment, "/admin/add-department")
    api.add_resource(GetDepartments, "/admin/departments")

    # -------------------------
    # DOCTOR ROUTES
    # -------------------------
    api.add_resource(DoctorDashboard, "/doctor/dashboard")

    api.add_resource(DoctorUpcomingAppointments, "/doctor/appointments/upcoming")
    api.add_resource(UpdateAppointmentStatus, "/doctor/appointment/<int:appointment_id>/status")

    api.add_resource(AssignedPatients, "/doctor/assigned-patients")

    api.add_resource(DoctorPatientHistory, "/doctor/patient/<int:patient_id>/history")
    api.add_resource(AddPatientHistory, "/doctor/patient/<int:patient_id>/add-history")

    api.add_resource(DoctorAvailability, "/doctor/availability")
    api.add_resource(PublishAvailability, "/doctor/availability/publish")



    # -------------------------
    # PATIENT ROUTES
    # -------------------------
        # Patient
    api.add_resource(PatientDashboard, "/patient/dashboard")
    api.add_resource(PatientDepartments, "/patient/departments")
    api.add_resource(DepartmentDetails, "/patient/department/<int:dept_id>")
    api.add_resource(DoctorDetails, "/patient/doctor/<int:doctor_id>")
    api.add_resource(DoctorAvailabilityPublic, "/patient/doctor/<int:doctor_id>/availability")
    api.add_resource(BookAppointment, "/patient/appointment/book")
    api.add_resource(CancelAppointment, "/patient/appointment/<int:appt_id>/cancel")
    api.add_resource(PatientMedicalHistory, "/patient/history")
    api.add_resource(ExportPatientHistoryCSV, "/patient/history/export")
    api.add_resource(RescheduleAppointment, "/patient/appointment/<int:appt_id>/reschedule")
