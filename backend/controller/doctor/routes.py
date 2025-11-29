from flask import request
from controller.security import RoleProtectedResource
from controller.database import db
from controller.models import Doctor, Appointment, Patient, Availability, Treatment
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity


# -------------------------------------------------
# Doctor Dashboard - Welcome
# -------------------------------------------------
class DoctorDashboard(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        upcoming = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "scheduled",
            Appointment.appointment_time >= datetime.now()
        ).count()

        patients = Patient.query.filter(
            Patient.id.in_(
                db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct()
            )
        ).count()

        return {
            "upcoming_appointments": upcoming,
            "total_patients": patients
        }, 200


# -------------------------------------------------
# Upcoming Appointments (for doctor)
# -------------------------------------------------
class DoctorUpcomingAppointments(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        appts = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == "scheduled",
            Appointment.appointment_time >= datetime.now()
        ).order_by(Appointment.appointment_time.asc()).all()

        result = []
        for a in appts:
            result.append({
                "id": a.id,
                "patient_name": a.patient.user.name,
                "appointment_time": a.appointment_time.strftime("%Y-%m-%d %H:%M"),
                "status": a.status
            })

        return result, 200


# -------------------------------------------------
# Mark Appointment Completed or Cancelled
# -------------------------------------------------
class UpdateAppointmentStatus(RoleProtectedResource):
    required_roles = ["doctor"]

    def patch(self, appt_id):
        appt = Appointment.query.get_or_404(appt_id)
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()

        if appt.doctor_id != doctor.id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json() or {}
        status = data.get("status")

        if status not in ["scheduled", "completed", "cancelled"]:
            return {"error": "Invalid status"}, 400

        appt.status = status
        db.session.commit()

        return {"message": "Status updated"}, 200


# -------------------------------------------------
# Assigned Patients
# -------------------------------------------------
class AssignedPatients(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        patients = Patient.query.filter(
            Patient.id.in_(
                db.session.query(Appointment.patient_id).filter_by(doctor_id=doctor.id).distinct()
            )
        ).all()

        result = []
        for p in patients:
            result.append({
                "id": p.id,
                "name": p.user.name,
                "email": p.user.email,
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
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        today = datetime.now().date()
        end = today + timedelta(days=6)

        slots = Availability.query.filter(
            Availability.doctor_id == doctor.id,
            Availability.date >= today,
            Availability.date <= end
        ).order_by(Availability.date.asc(), Availability.start_time.asc()).all()

        out = []
        for s in slots:
            out.append({
                "id": s.id,
                "date": s.date.isoformat(),
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M"),
                "is_available": bool(s.is_available)
            })

        return {"slots": out}, 200

    def post(self):
        doctor = Doctor.query.filter_by(user_id=self.current_user.id).first()
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        data = request.get_json() or {}
        slots = data.get("slots")

        if not isinstance(slots, list):
            return {"error": "Slots must be a list"}, 400

        try:
            doctor.publish_availability(slots)
        except ValueError as e:
            return {"error": str(e)}, 400

        return {"message": "Availability saved"}, 200