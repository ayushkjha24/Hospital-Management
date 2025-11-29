from flask import request
from flask_restful import Resource
from datetime import datetime, timedelta, date
from controller.models import *
from controller.security import RoleProtectedResource
from controller.database import db


# -------------------------------------------------
# Doctor Dashboard - Welcome
# -------------------------------------------------
class DoctorDashboard(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        return {"message": "Welcome Doctor"}, 200


# -------------------------------------------------
# Upcoming Appointments (for doctor)
# -------------------------------------------------
class DoctorUpcomingAppointments(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        if not doctor:
            return {"message": "Doctor profile not found"}, 404

        now = datetime.now()

        appts = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "scheduled",
            Appointment.appointment_time >= now
        ).order_by(Appointment.appointment_time.asc()).all()

        result = []
        for a in appts:
            result.append({
                "id": a.id,
                "patient": a.patient.user.name,
                "time": a.appointment_time.strftime("%Y-%m-%d %H:%M"),
                "status": a.status
            })

        return result, 200


# -------------------------------------------------
# Mark Appointment Completed or Cancelled
# -------------------------------------------------
class UpdateAppointmentStatus(RoleProtectedResource):
    required_roles = ["doctor"]

    def patch(self, appointment_id):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()

        appt = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first()

        if not appt:
            return {"message": "Appointment not found"}, 404

        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["completed", "cancelled"]:
            return {"message": "Invalid status"}, 400

        appt.status = new_status
        db.session.commit()

        return {"message": "Status updated"}, 200


# -------------------------------------------------
# Assigned Patients
# -------------------------------------------------
class AssignedPatients(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()

        appts = Appointment.query.filter_by(doctor_id=doctor.id).all()
        patient_ids = {a.patient_id for a in appts}

        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

        result = []
        for p in patients:
            result.append({
                "id": p.id,
                "name": p.user.name,
                "email": p.user.email
            })

        return result, 200


# -------------------------------------------------
# View Patient History
# -------------------------------------------------
class DoctorPatientHistory(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self, patient_id):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()

        # ensure doctor treated this patient
        valid = Appointment.query.filter_by(
            patient_id=patient_id,
            doctor_id=doctor.id
        ).first()

        if not valid:
            return {"message": "You do not have access to this patient"}, 403

        treatments = Treatment.query.join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == doctor.id
        ).order_by(Treatment.created_at.desc()).all()

        result = []
        for t in treatments:
            result.append({
                "visit_date": t.appointment.appointment_time.strftime("%Y-%m-%d"),
                "diagnosis": t.diagnosis,
                "prescription": t.prescription,
                "notes": t.notes,
                "next_visit": t.next_visit.strftime("%Y-%m-%d %H:%M") if t.next_visit else None
            })

        patient = Patient.query.get(patient_id)

        return {
            "patient": patient.user.name,
            "history": result
        }, 200


# -------------------------------------------------
# Add Patient History (Update Patient History page)
# -------------------------------------------------
class AddPatientHistory(RoleProtectedResource):
    required_roles = ["doctor"]

    def post(self, patient_id):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()

        data = request.get_json()

        diagnosis = data.get("diagnosis")
        prescription = data.get("prescription")
        notes = data.get("notes")
        next_visit = data.get("next_visit")
        appointment_id = data.get("appointment_id")

        if not diagnosis:
            return {"message": "Diagnosis is required"}, 400

        # validate appointment
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor.id
        ).first()

        if not appointment:
            return {"message": "Appointment not found"}, 404

        # mark appointment completed when adding history
        appointment.status = "completed"

        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes,
            next_visit=datetime.fromisoformat(next_visit) if next_visit else None
        )

        db.session.add(treatment)
        db.session.commit()

        return {"message": "Patient history updated"}, 201


# -------------------------------------------------
# Doctor Availability (GET)
# -------------------------------------------------
class DoctorAvailability(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        today = date.today()
        next7 = [today + timedelta(days=i) for i in range(7)]

        avails = Availability.query.filter(
            Availability.doctor_id == doctor.id,
            Availability.date.in_(next7)
        ).order_by(Availability.date.asc()).all()

        result = []
        for a in avails:
            result.append({
                "date": a.date.strftime("%Y-%m-%d"),
                "start_time": a.start_time.strftime("%H:%M"),
                "end_time": a.end_time.strftime("%H:%M"),
                "is_available": a.is_available
            })

        return result, 200


# -------------------------------------------------
# Doctor Availability (POST) - Provide Availability
# -------------------------------------------------
class PublishAvailability(RoleProtectedResource):
    required_roles = ["doctor"]

    def post(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        data = request.get_json()

        slots = data.get("slots")
        if not slots:
            return {"message": "Slots are required"}, 400

        try:
            doctor.publish_availability(slots)
        except ValueError as e:
            return {"message": str(e)}, 400

        return {"message": "Availability published"}, 201