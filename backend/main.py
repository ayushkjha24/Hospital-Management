from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from controller.routes import TestCache,TestCelery
from controller.database import db
from controller.config import Config
from datetime import timedelta
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from controller.cache import init_cache

# ✅ Import celery here (safe – outside create_app)
from celery_app import celery, init_celery
from dotenv import load_dotenv
load_dotenv()




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT config
    app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY", "dev-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app)
    Migrate(app, db)
    init_celery(app)
    init_cache(app)

    api = Api(app)

    with app.app_context():

        # -----------------------------------------------------
        # PUBLIC ENDPOINTS
        # -----------------------------------------------------
        from controller.routes import (
            DepartmentsList, DepartmentResource,
            DoctorsList, DoctorRes, SearchDoctors, SearchDepartments,
        )
        api.add_resource(DepartmentsList, '/departments')
        api.add_resource(DepartmentResource, '/departments/<int:department_id>')
        api.add_resource(DoctorsList, '/doctors')
        api.add_resource(DoctorRes, '/doctors/<int:doctor_id>')
        api.add_resource(SearchDoctors, '/search/doctors')
        api.add_resource(SearchDepartments, '/search/departments')
        api.add_resource(TestCache, '/test-cache')
        api.add_resource(TestCelery, '/test-celery/<int:a>/<int:b>')
        # AUTH ENDPOINTS
        from controller.auth import Login, Register
        api.add_resource(Login, '/auth/login')
        api.add_resource(Register, '/auth/register')

        # ADMIN ENDPOINTS
        from controller.admin.routes import (
            AdminDashboard, DoctorListResource, DoctorResource, DoctorBlacklistResource,
            PatientListResource, PatientResource, PatientBlacklistResource,
            SearchPatients, UpcomingAppointments, AdminPatientHistory, DepartmentListResource
        )
        api.add_resource(AdminDashboard, '/admin/dashboard')
        api.add_resource(DoctorListResource, '/admin/doctors')
        api.add_resource(DoctorResource, '/admin/doctors/<int:doctor_id>')
        api.add_resource(DoctorBlacklistResource, '/admin/doctors/<int:doctor_id>/blacklist')
        api.add_resource(PatientListResource, '/admin/patients')
        api.add_resource(PatientResource, '/admin/patients/<int:patient_id>')
        api.add_resource(PatientBlacklistResource, '/admin/patients/<int:patient_id>/blacklist')
        api.add_resource(SearchPatients, '/admin/search/patients')
        api.add_resource(UpcomingAppointments, '/admin/appointments')
        api.add_resource(AdminPatientHistory, '/admin/patients/<int:patient_id>/history')
        api.add_resource(DepartmentListResource, '/admin/add-department')

        # DOCTOR ENDPOINTS
        from controller.doctor.routes import (
            DoctorDashboard, DoctorUpcomingAppointments, UpdateAppointmentStatus,
            AssignedPatients, DoctorAvailability, UpdatePatientHistory, PatientHistory
        )
        api.add_resource(DoctorDashboard, '/doctor/dashboard')
        api.add_resource(DoctorUpcomingAppointments, '/doctor/appointments/upcoming')
        api.add_resource(UpdateAppointmentStatus, '/doctor/appointment/<int:appt_id>/status')
        api.add_resource(AssignedPatients, '/doctor/assigned-patients')
        api.add_resource(DoctorAvailability, '/doctor/availability')
        api.add_resource(UpdatePatientHistory, '/doctor/patient/<int:patient_id>/history')
        api.add_resource(PatientHistory, '/doctor/patient/<int:patient_id>/history')

        # PATIENT ENDPOINTS
        from controller.patient.routes import (
            PatientDashboard, BookAppointment, PatientAppointments,
            PatientProfile, RescheduleAppointment,
            CancelAppointment, PatientAllAppointments,PatientAppointmentReport
        )
        api.add_resource(PatientDashboard, '/patient/dashboard')
        api.add_resource(BookAppointment, '/patient/book-appointment')
        api.add_resource(PatientAppointments, '/patient/appointments/upcoming')
        api.add_resource(PatientProfile, '/patient/profile')
        api.add_resource(RescheduleAppointment, '/patient/appointment/<int:appt_id>/reschedule')
        api.add_resource(CancelAppointment, '/patient/appointment/<int:appt_id>/cancel')
        api.add_resource(PatientAllAppointments, '/patient/appointments')
        api.add_resource(PatientAppointmentReport,'/patient/appointment/<int:appt_id>/report')

        # -----------------------------------------------------------------
        # AUTOMATIC ADMIN CREATION
        # -----------------------------------------------------------------
        from controller.models import User

        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@gmail.com",
                role="admin",
                password=generate_password_hash("admin123")
            )
            db.session.add(admin)
            db.session.commit()
            print("🚀 Default Admin created automatically.")

        # -----------------------------------------------------------------
        # JOB ENDPOINTS (NO CELERY TASK IMPORTS HERE)
        # -----------------------------------------------------------------
        from controller.jobs_helpers import EXPORT_DIR

        @app.route("/jobs/export/patient", methods=["POST"])
        def trigger_patient_export():
            data = request.json or {}
            patient_id = data.get("patient_id")
            requester_email = data.get("email")

            if not patient_id:
                return jsonify({"error": "patient_id is required"}), 400

            # 🔥 trigger task by name (avoids circular imports)
            task = celery.send_task(
                "controller.jobs.export_csv.generate_patient_csv",
                args=[patient_id, requester_email]
            )

            return jsonify({"task_id": task.id}), 202

        @app.route("/jobs/status/<task_id>", methods=["GET"])
        def job_status(task_id):
            async_res = celery.AsyncResult(task_id)
            return jsonify({
                "task_id": task_id,
                "status": async_res.status,
                "result": async_res.result
            })

        @app.route("/jobs/download/<filename>", methods=["GET"])
        def download_export(filename):
            return send_from_directory(EXPORT_DIR, filename, as_attachment=True)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
