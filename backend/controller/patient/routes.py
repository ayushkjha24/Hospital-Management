from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from controller.security import RoleProtectedResource
from datetime import datetime, timedelta
from controller.database import db
from controller.models import User, Patient, Doctor, Department, Appointment, Availability, Treatment


APPOINTMENT_DURATION_MIN = 30  # minutes

# ----------------------------------------------------
# Patient Dashboard
# ----------------------------------------------------
class PatientDashboard(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = Patient.query.filter_by(user_id=user_id).first()

        if not patient or not user:
            return {"error": "Patient profile not found"}, 404

        now = datetime.now()

        # upcoming appointments
        upcoming_q = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_time >= now,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).order_by(Appointment.appointment_time.asc()).all()

        upcoming = []
        for appt in upcoming_q:
            upcoming.append({
                "id": appt.id,
                "doctor": appt.doctor.user.name if getattr(appt, "doctor", None) and getattr(appt.doctor, "user", None) else "N/A",
                "department": appt.doctor.department.name if getattr(appt, "doctor", None) and getattr(appt.doctor, "department", None) else "N/A",
                "date": appt.appointment_time.strftime("%Y-%m-%d"),
                "time": appt.appointment_time.strftime("%H:%M"),
                "status": appt.status
            })

        # departments
        depts_q = Department.query.order_by(Department.name.asc()).all()
        depts = []
        for d in depts_q:
            depts.append({
                "id": d.id,
                "name": d.name,
                "description": getattr(d, "description", "") or ""
            })

        return {
            "patient_name": user.name,
            "email": user.email,
            "departments": depts,
            "upcoming_appointments": upcoming,
            "stats": {
                "upcoming_appointments": len(upcoming_q),
                "total_departments": len(depts_q)
            }
        }, 200


# ----------------------------------------------------
# Departments List (public for patients)
# ----------------------------------------------------
class PatientDepartments(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        depts_q = Department.query.order_by(Department.name.asc()).all()
        depts = []
        for d in depts_q:
            depts.append({
                "id": d.id,
                "name": d.name,
                "description": getattr(d, "description", "") or ""
            })
        return {"departments": depts}, 200


# ----------------------------------------------------
# Book appointment
# ----------------------------------------------------
class BookAppointment(RoleProtectedResource):
    required_roles = ["patient"]

    def post(self):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return {"error": "Patient profile not found"}, 404

        data = request.get_json() or {}
        doctor_id = data.get("doctor_id")
        date_str = data.get("date")
        start_time_str = data.get("start_time")

        if not all([doctor_id, date_str, start_time_str]):
            return {"error": "Missing required fields"}, 400

        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            appt_dt = datetime.combine(appt_date, start_time)
        except ValueError:
            return {"error": "Invalid date/time format. Use YYYY-MM-DD and HH:MM"}, 400

        doctor = Doctor.query.get(doctor_id)
        if not doctor or not doctor.is_approved:
            return {"error": "Doctor not found or not approved"}, 404

        # check availability slot
        slot = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=appt_date,
            start_time=start_time,
            is_available=True
        ).first()
        if not slot:
            return {"error": "Selected slot is not available"}, 400

        # check conflicts using numeric duration
        duration = APPOINTMENT_DURATION_MIN
        appt_end = appt_dt + timedelta(minutes=duration)

        conflict = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_(["scheduled", "confirmed"]),
            Appointment.appointment_time < appt_end,
            (Appointment.appointment_time + timedelta(minutes=duration)) > appt_dt
        ).first()

        if conflict:
            return {"error": "Time slot conflict with existing appointment"}, 409

        # create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_time=appt_dt,
            status="scheduled"
        )
        # add optional notes if model supports it and provided
        if hasattr(Appointment, "notes") and "notes" in data:
            appointment.notes = data.get("notes", "")

        try:
            db.session.add(appointment)
            slot.is_available = False
            db.session.add(slot)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": "Could not create appointment: " + str(e)}, 500

        return {"message": "Appointment booked successfully", "appointment_id": appointment.id}, 201


# ----------------------------------------------------
# Upcoming appointments (patient)
# ----------------------------------------------------
class PatientAppointments(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return {"error": "Patient profile not found"}, 404

        now = datetime.now()
        appts = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_time >= now,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).order_by(Appointment.appointment_time.asc()).all()

        result = []
        for appt in appts:
            result.append({
                "id": appt.id,
                "doctor": appt.doctor.user.name if getattr(appt, "doctor", None) and getattr(appt.doctor, "user", None) else "N/A",
                "specialization": appt.doctor.specialization if getattr(appt, "doctor", None) else "N/A",
                "appointment_time": appt.appointment_time.strftime("%Y-%m-%d %H:%M"),
                "status": appt.status,
                "notes": getattr(appt, "notes", None)
            })

        return {"appointments": result}, 200


# ----------------------------------------------------
# Profile get/update
# ----------------------------------------------------
class PatientProfile(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient or not user:
            return {"error": "Patient profile not found"}, 404

        return {
            "id": patient.id,
            "name": user.name,
            "email": user.email,
            "phone": getattr(user, "phone", ""),
            "medical_history": getattr(patient, "medical_history", "") or ""
        }, 200

    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient or not user:
            return {"error": "Patient profile not found"}, 404

        data = request.get_json() or {}
        if "name" in data:
            user.name = data["name"]
        if "phone" in data:
            user.phone = data["phone"]
        if "medical_history" in data:
            patient.medical_history = data["medical_history"]
        db.session.commit()
        return {"message": "Profile updated"}, 200


# ----------------------------------------------------
# Reschedule appointment
# ----------------------------------------------------
class RescheduleAppointment(RoleProtectedResource):
    required_roles = ["patient"]

    def post(self, appt_id):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return {"error": "Patient profile not found"}, 404

        appointment = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first()
        if not appointment:
            return {"error": "Appointment not found"}, 404

        data = request.get_json() or {}
        date_str = data.get("date")
        start_time_str = data.get("start_time")
        if not all([date_str, start_time_str]):
            return {"error": "Missing date or time"}, 400

        try:
            new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            new_time = datetime.strptime(start_time_str, "%H:%M").time()
            new_dt = datetime.combine(new_date, new_time)
        except ValueError:
            return {"error": "Invalid date/time format"}, 400

        # check new slot availability
        slot = Availability.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=new_date,
            start_time=new_time,
            is_available=True
        ).first()
        if not slot:
            return {"error": "Selected slot not available"}, 400

        # free old slot if exists
        old_slot = Availability.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=appointment.appointment_time.date(),
            start_time=appointment.appointment_time.time()
        ).first()
        if old_slot:
            old_slot.is_available = True

        # update appointment and mark new slot unavailable
        appointment.appointment_time = new_dt
        slot.is_available = False

        db.session.commit()
        return {"message": "Appointment rescheduled"}, 200


# ----------------------------------------------------
# Cancel appointment
# ----------------------------------------------------
class CancelAppointment(RoleProtectedResource):
    required_roles = ["patient"]

    def post(self, appt_id):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return {"error": "Patient profile not found"}, 404

        appointment = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first()
        if not appointment:
            return {"error": "Appointment not found"}, 404

        # release slot if exists
        slot = Availability.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=appointment.appointment_time.date(),
            start_time=appointment.appointment_time.time()
        ).first()
        if slot:
            slot.is_available = True

        appointment.status = "cancelled"
        db.session.commit()
        return {"message": "Appointment cancelled"}, 200


# ----------------------------------------------------
# Past appointments
# ----------------------------------------------------
class PatientAllAppointments(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return {"error": "Patient profile not found"}, 404
        #list all appointments
        appts = Appointment.query.filter(
            Appointment.patient_id == patient.id
        ).order_by(Appointment.appointment_time.desc()).all()

        result = []
        for appt in appts:
            result.append({
                "id": appt.id,
                "doctor": appt.doctor.user.name if getattr(appt, "doctor", None) and getattr(appt.doctor, "user", None) else "N/A",
                "specialization": appt.doctor.specialization if getattr(appt, "doctor", None) else "N/A",
                "appointment_time": appt.appointment_time.strftime("%Y-%m-%d %H:%M"),
                "status": appt.status,
                "notes": getattr(appt, "notes", None)
            })
        return {"appointments": result}, 200
    
# endpoint to retrieve medicines and diagnosis report for a given appointment
class PatientAppointmentReport(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self, appt_id):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            return {"error": "Patient profile not found"}, 404

        appointment = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first()
        if not appointment:
            return {"error": "Appointment not found"}, 404

        treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()
        if not treatment:
            return {"error": "No treatment record found for this appointment"}, 404

        return {
            "diagnosis": treatment.diagnosis,
            "test_done": treatment.test_done,
            "prescription": treatment.prescription,
            "notes": treatment.notes,
            "next_visit": treatment.next_visit.strftime("%Y-%m-%d %H:%M") if treatment.next_visit else None
        }, 200
