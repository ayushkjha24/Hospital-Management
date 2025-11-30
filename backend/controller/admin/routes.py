from flask import request
from controller.security import RoleProtectedResource
from controller.database import db
from controller.models import User, Doctor, Patient, Department, Appointment
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class AdminDashboard(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self):
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        upcoming = Appointment.query.filter(
            Appointment.appointment_time >= datetime.now(),
            Appointment.status == "scheduled"
        ).count()
        
        return {
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "upcoming_appointments": upcoming
        }, 200

class DoctorListResource(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self):
        doctors = Doctor.query.join(User).filter(User.is_active == True).all()
        out = []
        for d in doctors:
            out.append({
                "id": d.id,
                "name": d.user.name,
                "email": d.user.email,
                "specialization": d.specialization,
                "experience_years": d.experience_years,
                "department": d.department.name if d.department else None,
                "is_approved": bool(d.is_approved)
            })
        return {"doctors": out}, 200
    def post(self):
        # Create a new doctor
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")  # <-- Ensure password is captured
        specialization = data.get("specialization")
        experience_years = data.get("experience_years")
        department_id = data.get("department_id")
        
        if not all([name, email, password, specialization, experience_years]):
            return {"message": "Missing required fields"}, 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"message": "Email already registered"}, 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role="doctor",
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        
        new_doctor = Doctor(
            user_id=new_user.id,
            specialization=specialization,
            experience_years=experience_years,
            department_id=department_id,
            is_approved=False
        )
        db.session.add(new_doctor)
        db.session.commit()
        
        return {"message": "Doctor created", "doctor_id": new_doctor.id}, 201    

class DoctorResource(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self, doctor_id):
        d = Doctor.query.get_or_404(doctor_id)
        return {
            "id": d.id,
            "name": d.user.name,
            "email": d.user.email,
            "specialization": d.specialization,
            "experience_years": d.experience_years,
            "department_id": d.department_id,
            "is_approved": bool(d.is_approved),
            "is_active": bool(d.user.is_active)
        }, 200
    
    def put(self, doctor_id):
        d = Doctor.query.get_or_404(doctor_id)
        data = request.get_json() or {}
        
        if "name" in data:
            d.user.name = data["name"]
        if "email" in data:
            d.user.email = data["email"]
        if "specialization" in data:
            d.specialization = data["specialization"]
        if "experience_years" in data:
            d.experience_years = data["experience_years"]
        if "department_id" in data:
            d.department_id = data["department_id"]
        if "is_approved" in data:
            d.is_approved = bool(data["is_approved"])
        
        db.session.commit()
        return {"message": "Doctor updated"}, 200
    
    def delete(self, doctor_id):
        d = Doctor.query.get_or_404(doctor_id)
        d.user.is_active = False
        db.session.commit()
        return {"message": "Doctor deactivated"}, 200
    
class AddDoctor(RoleProtectedResource):
    required_roles = ["admin"]



class DoctorBlacklistResource(RoleProtectedResource):
    required_roles = ["admin"]
    
    def post(self, doctor_id):
        d = Doctor.query.get_or_404(doctor_id)
        d.user.is_active = False
        db.session.commit()
        return {"message": "Doctor blacklisted"}, 200

class PatientListResource(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self):
        patients = Patient.query.join(User).filter(User.is_active == True).all()
        out = []
        for p in patients:
            out.append({
                "id": p.id,
                "name": p.user.name,
                "email": p.user.email,
                "appointments_count": len(p.appointments)
            })
        return {"patients": out}, 200

class PatientResource(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self, patient_id):
        p = Patient.query.get_or_404(patient_id)
        return {
            "id": p.id,
            "name": p.user.name,
            "email": p.user.email,
            "medical_history": p.medical_history,
            "is_active": bool(p.user.is_active)
        }, 200
    
    def put(self, patient_id):
        p = Patient.query.get_or_404(patient_id)
        data = request.get_json() or {}
        
        if "name" in data:
            p.user.name = data["name"]
        if "email" in data:
            p.user.email = data["email"]
        if "phone" in data:
            p.user.phone = data["phone"]
        if "medical_history" in data:
            p.medical_history = data["medical_history"]
        
        db.session.commit()
        return {"message": "Patient updated"}, 200
    
    def delete(self, patient_id):
        p = Patient.query.get_or_404(patient_id)
        p.user.is_active = False
        db.session.commit()
        return {"message": "Patient deactivated"}, 200

class PatientBlacklistResource(RoleProtectedResource):
    required_roles = ["admin"]
    
    def post(self, patient_id):
        p = Patient.query.get_or_404(patient_id)
        p.user.is_active = False
        db.session.commit()
        return {"message": "Patient blacklisted"}, 200

class SearchDoctors(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self):
        q = request.args.get("q", "").lower()
        doctors = Doctor.query.join(User).filter(
            (User.name.ilike(f"%{q}%")) | (Doctor.specialization.ilike(f"%{q}%"))
        ).all()
        
        result = []
        for d in doctors:
            result.append({
                "id": d.id,
                "name": d.user.name,
                "specialization": d.specialization
            })
        return result, 200

class SearchPatients(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self):
        q = request.args.get("q", "").lower()
        patients = Patient.query.join(User).filter(
            (User.name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
        ).all()
        
        result = []
        for p in patients:
            result.append({
                "id": p.id,
                "name": p.user.name,
                "email": p.user.email
            })
        return result, 200
class UpcomingAppointments(RoleProtectedResource):
    required_roles = ["admin"]
    
    def get(self):
        now = datetime.now()
        appointments = Appointment.query.filter(
            Appointment.appointment_time >= now,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).order_by(Appointment.appointment_time.asc()).all()
        
        result = []
        for appt in appointments:
            patient_name = appt.patient.user.name if appt.patient and appt.patient.user else "N/A"
            doctor_name = appt.doctor.user.name if appt.doctor and appt.doctor.user else "N/A"
            department = appt.doctor.department.name if appt.doctor and appt.doctor.department else "N/A"
            
            result.append({
                "id": appt.id,
                "patient": patient_name,
                "doctor": doctor_name,
                "department": department,
                "date": appt.appointment_time.strftime("%Y-%m-%d"),
                "time": appt.appointment_time.strftime("%H:%M"),
                "status": appt.status
            })
        
        return {"appointments": result}, 200