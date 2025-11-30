from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from controller.database import db
from controller.config import Config
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # JWT Config
    app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY", "dev-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)
    
    api = Api(app)
    
    with app.app_context():
        # public endpoints
        from controller.routes import DepartmentsList, DepartmentResource, DoctorsList, DoctorRes
        api.add_resource(DepartmentsList, '/departments')
        api.add_resource(DepartmentResource, '/departments/<int:department_id>')
        api.add_resource(DoctorsList, '/doctors')
        api.add_resource(DoctorRes, '/doctors/<int:doctor_id>')
        
        # auth endpoints
        from controller.auth import Login, Register
        api.add_resource(Login, '/auth/login')
        api.add_resource(Register, '/auth/register')
        
        # admin endpoints
        from controller.admin.routes import (
            AdminDashboard, DoctorListResource, DoctorResource, DoctorBlacklistResource,
            PatientListResource, PatientResource, PatientBlacklistResource,
            SearchDoctors, SearchPatients, UpcomingAppointments
        )
        api.add_resource(AdminDashboard, '/admin/dashboard')
        api.add_resource(DoctorListResource, '/admin/doctors')             # list & add
        api.add_resource(DoctorResource, '/admin/doctors/<int:doctor_id>') # get, put, delete
        api.add_resource(DoctorBlacklistResource, '/admin/doctors/<int:doctor_id>/blacklist')
        api.add_resource(PatientListResource, '/admin/patients')
        api.add_resource(PatientResource, '/admin/patients/<int:patient_id>')
        api.add_resource(PatientBlacklistResource, '/admin/patients/<int:patient_id>/blacklist')
        api.add_resource(SearchDoctors, '/admin/search/doctors')
        api.add_resource(SearchPatients, '/admin/search/patients')
        api.add_resource(UpcomingAppointments, '/admin/appointments')
        
        # doctor endpoints
        from controller.doctor.routes import (
            DoctorDashboard, DoctorUpcomingAppointments, UpdateAppointmentStatus,
            AssignedPatients, DoctorAvailability as DoctorAvailabilityResource
        )
        api.add_resource(DoctorDashboard, '/doctor/dashboard')
        api.add_resource(DoctorUpcomingAppointments, '/doctor/appointments/upcoming')
        api.add_resource(UpdateAppointmentStatus, '/doctor/appointment/<int:appt_id>/status')
        api.add_resource(AssignedPatients, '/doctor/assigned-patients')
        api.add_resource(DoctorAvailabilityResource, '/doctor/availability')
        
        # patient endpoints
        from controller.patient.routes import (
            PatientDashboard, BookAppointment,
            PatientAppointments, PatientProfile, RescheduleAppointment,
            CancelAppointment, PatientAllAppointments
        )
        api.add_resource(PatientDashboard, '/patient/dashboard')
        #api.add_resource(SearchAvailableDoctors, '/patient/search/doctors')
        api.add_resource(BookAppointment, '/patient/book-appointment')
        api.add_resource(PatientAppointments, '/patient/appointments/upcoming')
        api.add_resource(PatientProfile, '/patient/profile')
        api.add_resource(RescheduleAppointment, '/patient/appointment/<int:appt_id>/reschedule')
        api.add_resource(CancelAppointment, '/patient/appointment/<int:appt_id>/cancel')
        api.add_resource(PatientAllAppointments, '/patient/appointments')
        
        # create tables if needed
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)