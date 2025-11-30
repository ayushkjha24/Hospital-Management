from flask import request
from flask_jwt_extended import get_jwt_identity
from controller.security import RoleProtectedResource
from controller.database import db
from controller.models import User, Doctor, Patient, Appointment, Treatment, Availability
from datetime import datetime, date, timedelta, time as time_type

class DoctorDashboard(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        now = datetime.now()
        
        # Upcoming appointments
        upcoming = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_time >= now,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).count()
        
        # Assigned patients (unique patients from appointments)
        patients_count = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().count()
        
        return {
            "upcoming_appointments": upcoming,
            "total_patients": patients_count
        }, 200


class DoctorUpcomingAppointments(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        now = datetime.now()
        appts = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_time >= now,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).order_by(Appointment.appointment_time.asc()).all()

        result = []
        for appt in appts:
            patient_name = appt.patient.user.name if appt.patient and appt.patient.user else "N/A"
            result.append({
                "id": appt.id,
                "patient_id": appt.patient_id,
                "patient_name": patient_name,
                "appointment_time": appt.appointment_time.strftime("%Y-%m-%d %H:%M"),
                "status": appt.status
            })
        
        return {"appointments": result}, 200


class UpdateAppointmentStatus(RoleProtectedResource):
    required_roles = ["doctor"]

    def post(self, appt_id):
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        appointment = Appointment.query.filter_by(
            id=appt_id,
            doctor_id=doctor.id
        ).first()
        
        if not appointment:
            return {"error": "Appointment not found"}, 404

        data = request.get_json() or {}
        new_status = data.get("status")
        
        if new_status not in ["scheduled", "confirmed", "completed", "cancelled"]:
            return {"error": "Invalid status"}, 400
        if new_status == "completed" or new_status == "cancelled":
            # make the slot available again
            appointment_slot = Availability.query.filter_by(
                doctor_id=doctor.id,
                date=appointment.appointment_time.date(),
                start_time=appointment.appointment_time.time()
            ).first()
            if appointment_slot:
                appointment_slot.is_available = True
                db.session.commit()

        appointment.status = new_status
        db.session.commit()
        
        return {"message": "Appointment status updated", "status": new_status}, 200


class AssignedPatients(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        # Get unique patients who have appointments with this doctor
        patient_ids = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()

        patients = []
        for (pid,) in patient_ids:
            patient = Patient.query.get(pid)
            if patient and patient.user:
                patients.append({
                    "id": patient.id,
                    "name": patient.user.name,
                    "email": patient.user.email,
                    "phone": getattr(patient.user, "phone", "N/A")
                })

        return {"patients": patients}, 200


class DoctorAvailability(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self):
        """Get doctor's 7-day availability"""
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        today = date.today()
        end = today + timedelta(days=6)
        
        slots = Availability.query.filter(
            Availability.doctor_id == doctor.id,
            Availability.date >= today,
            Availability.date <= end
        ).order_by(
            Availability.date.asc(), 
            Availability.start_time.asc()
        ).all()

        result = []
        for slot in slots:
            result.append({
                "id": slot.id,
                "date": slot.date.isoformat(),
                "start_time": slot.start_time.strftime("%H:%M") if isinstance(slot.start_time, time_type) else str(slot.start_time),
                "end_time": slot.end_time.strftime("%H:%M") if isinstance(slot.end_time, time_type) else str(slot.end_time),
                "is_available": bool(slot.is_available)
            })

        return {"availability": result, "slots": result}, 200  # return both keys for compatibility

    def post(self):
        """Add or update doctor's availability"""
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        data = request.get_json() or {}
        slots_data = data.get("slots", [])

        if not slots_data or not isinstance(slots_data, list):
            return {"error": "Invalid slots format"}, 400

        try:
            added_count = 0
            for slot in slots_data:
                date_str = slot.get("date")
                start_time_str = slot.get("start_time")
                end_time_str = slot.get("end_time")

                if not all([date_str, start_time_str, end_time_str]):
                    continue

                try:
                    slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()
                except ValueError as e:
                    return {"error": f"Invalid date/time format: {str(e)}"}, 400

                # Validate times
                if start_time >= end_time:
                    return {"error": f"Start time must be before end time for {date_str}"}, 400

                # Check if slot already exists
                existing = Availability.query.filter_by(
                    doctor_id=doctor.id,
                    date=slot_date,
                    start_time=start_time
                ).first()

                if existing:
                    # Update existing
                    existing.end_time = end_time
                    existing.is_available = True
                else:
                    # Create new
                    new_slot = Availability(
                        doctor_id=doctor.id,
                        date=slot_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    db.session.add(new_slot)
                    added_count += 1

            db.session.commit()
            return {
                "message": "Availability saved successfully",
                "slots_added": added_count
            }, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class UpdatePatientHistory(RoleProtectedResource):
    required_roles = ["doctor"]

    def post(self, patient_id):
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        patient = Patient.query.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}, 404

        data = request.get_json() or {}
        appointment_id = data.get("appointment_id")
        tests_done = data.get("tests_done")
        diagnosis = data.get("diagnosis")
        prescription = data.get("prescription")
        notes = data.get("notes")
        next_visit = data.get("next_visit")

        if not all([appointment_id, diagnosis, prescription]):
            return {"error": "Missing required fields"}, 400

        # Verify appointment belongs to this doctor and patient
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id,
            patient_id=patient_id
        ).first()

        if not appointment:
            return {"error": "Appointment not found"}, 404

        # Create or update treatment record
        treatment = Treatment.query.filter_by(
            appointment_id=appointment_id
        ).first()

        if not treatment:
            treatment = Treatment(appointment_id=appointment_id)
            db.session.add(treatment)

        treatment.diagnosis = diagnosis
        treatment.prescription = prescription
        treatment.notes = notes
        treatment.test_done = tests_done
        if next_visit:
            try:
                treatment.next_visit = datetime.fromisoformat(next_visit)
            except ValueError:
                pass
        
        db.session.commit()

        return {
            "message": "Patient history updated",
            "treatment_id": treatment.id
        }, 201


class PatientHistory(RoleProtectedResource):
    required_roles = ["doctor"]

    def get(self, patient_id):
        user_id = get_jwt_identity()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return {"error": "Doctor profile not found"}, 404

        patient = Patient.query.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}, 404

        # Get all treatments for appointments with this doctor
        appointments = Appointment.query.filter_by(
            doctor_id=doctor.id,
            patient_id=patient_id
        ).all()

        result = []
        for appt in appointments:
            treatment = Treatment.query.filter_by(
                appointment_id=appt.id
            ).first()

            result.append({
                "id": appt.id,
                "date": appt.appointment_time.strftime("%Y-%m-%d %H:%M"),
                "status": appt.status,
                "diagnosis": treatment.diagnosis if treatment else "N/A",
                "prescription": treatment.prescription if treatment else "N/A",
                "notes": treatment.notes if treatment else "N/A",
                "next_visit": treatment.next_visit.strftime("%Y-%m-%d") if treatment and treatment.next_visit else "N/A"
            })

        return {"patient": {"id": patient.id, "name": patient.user.name}, "history": result}, 200