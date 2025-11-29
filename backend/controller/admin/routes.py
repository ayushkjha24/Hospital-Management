from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from controller.models import *
from controller.security import RoleProtectedResource

# ------------------------
# Admin Dashboard Welcome
# ------------------------
class AdminDashboard(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        upcoming_appts = Appointment.query.filter(
            Appointment.appointment_time >= datetime.now(),
            Appointment.status == "scheduled"
        ).count()
        
        return {
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_appointments": upcoming_appts
        }, 200


# ------------------------
# Get All Doctors
# ------------------------
class GetDoctors(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        doctors = Doctor.query.all()
        result = []
        for d in doctors:
            result.append({
                "id": d.id,
                "name": d.user.name,
                "email": d.user.email,
                "specialization": d.specialization,
                "experience_years": d.experience_years,
                "department": d.department.name if d.department else None,
                "is_approved": d.is_approved
            })
        return result, 200


# ------------------------
# Add Doctor
# ------------------------
class AddDoctor(RoleProtectedResource):
    required_roles = ["admin"]

    def post(self):
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        specialization = data.get("specialization")
        experience = data.get("experience_years", 0)
        department_id = data.get("department_id")

        if not all([name, email, password, specialization]):
            return {"message": "Missing required fields"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 409

        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed, role="doctor")

        db.session.add(user)
        db.session.commit()

        doctor = Doctor(
            user_id=user.id,
            specialization=specialization,
            experience_years=experience,
            department_id=department_id
        )
        db.session.add(doctor)
        db.session.commit()

        return {"message": "Doctor added successfully"}, 201


# ------------------------
# Edit Doctor
# ------------------------
class EditDoctor(RoleProtectedResource):
    required_roles = ["admin"]

    def put(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        data = request.get_json()

        doctor.user.name = data.get("name", doctor.user.name)
        doctor.specialization = data.get("specialization", doctor.specialization)
        doctor.experience_years = data.get("experience_years", doctor.experience_years)
        doctor.department_id = data.get("department_id", doctor.department_id)

        db.session.commit()
        return {"message": "Doctor updated"}, 200


# ------------------------
# Delete Doctor
# ------------------------
class DeleteDoctor(RoleProtectedResource):
    required_roles = ["admin"]

    def delete(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)

        db.session.delete(doctor)
        db.session.commit()
        return {"message": "Doctor deleted"}, 200


# ------------------------
# Blacklist Doctor
# ------------------------
class BlacklistDoctor(RoleProtectedResource):
    required_roles = ["admin"]

    def post(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        user = doctor.user

        user.role = "blacklisted"
        db.session.commit()

        return {"message": "Doctor blacklisted"}, 200


# ------------------------------------------------------
# -------- PATIENT CONTROLS ----------------------------
# ------------------------------------------------------

class GetPatients(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        patients = Patient.query.all()
        result = []

        for p in patients:
            result.append({
                "id": p.id,
                "name": p.user.name,
                "email": p.user.email,
                "history_count": len(p.appointments)
            })
        return result, 200


class EditPatient(RoleProtectedResource):
    required_roles = ["admin"]

    def put(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()

        patient.user.name = data.get("name", patient.user.name)
        db.session.commit()

        return {"message": "Patient updated"}, 200


class DeletePatient(RoleProtectedResource):
    required_roles = ["admin"]

    def delete(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        return {"message": "Patient deleted"}, 200


class BlacklistPatient(RoleProtectedResource):
    required_roles = ["admin"]

    def post(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        user = patient.user
        user.role = "blacklisted"
        db.session.commit()
        return {"message": "Patient blacklisted"}, 200


# ------------------------
# Upcoming Appointments
# ------------------------
class UpcomingAppointments(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        today = datetime.now()
        appts = Appointment.query.filter(
            Appointment.appointment_time >= today,
            Appointment.status == "scheduled"
        ).all()

        result = []
        for a in appts:
            result.append({
                "id": a.id,
                "patient": a.patient.user.name,
                "doctor": a.doctor.user.name,
                "department": a.doctor.department.name if a.doctor.department else None,
                "time": a.appointment_time.strftime("%Y-%m-%d %H:%M")
            })
        return result, 200


# ------------------------
# Patient History (Treatment Table)
# ------------------------
class PatientHistory(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        appts = patient.appointments

        history = []
        for a in appts:
            history.append({
                "visit_date": a.appointment_time.strftime("%Y-%m-%d"),
                "type": "In-person",
                "tests_done": "ECG",
                "diagnosis": a.treatments[0].diagnosis if a.treatments else None,
                "prescription": a.treatments[0].prescription if a.treatments else None,
                "medicines": a.treatments[0].notes if a.treatments else None,
            })

        return {
            "patient": patient.user.name,
            "doctor": history[0]["doctor"] if history else None,
            "history": history
        }, 200


class SearchDoctors(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        query = request.args.get("q", "").lower()
        doctors = Doctor.query.join(User).filter(
            (User.name.ilike(f"%{query}%")) | 
            (Doctor.specialization.ilike(f"%{query}%"))
        ).all()
        
        result = []
        for d in doctors:
            result.append({
                "id": d.id,
                "name": d.user.name,
                "specialization": d.specialization,
                "department": d.department.name if d.department else None
            })
        return result, 200

class SearchPatients(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        query = request.args.get("q", "").lower()
        patients = Patient.query.join(User).filter(
            (User.name.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%"))
        ).all()
        
        result = []
        for p in patients:
            result.append({
                "id": p.id,
                "name": p.user.name,
                "email": p.user.email,
                "appointments_count": len(p.appointments)
            })
        return result, 200

class AddDepartment(RoleProtectedResource):
    required_roles = ["admin"]

    def post(self):
        data = request.get_json()
        name = data.get("name")
        description = data.get("description", "")

        if not name:
            return {"message": "Department name is required"}, 400

        if Department.query.filter_by(name=name).first():
            return {"message": "Department already exists"}, 409
        print(name, description)
        department = Department(name=name, description=description)
        db.session.add(department)
        db.session.commit()

        return {"message": "Department added successfully"}, 201

class GetDepartments(RoleProtectedResource):
    required_roles = ["admin"]

    def get(self):
        departments = Department.query.all()
        result = []
        for d in departments:
            result.append({
                "id": d.id,
                "name": d.name,
                "description": d.description
            })
        return result, 200
    