from flask import request, send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from controller.models import *
from controller.security import RoleProtectedResource
import csv, io
from datetime import datetime, timedelta


# ----------------------------------------------------
# Patient Dashboard
# ----------------------------------------------------
class PatientDashboard(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()

        departments = Department.query.all()
        dept_list = [{"id": d.id, "name": d.name} for d in departments]

        upcoming = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == "scheduled",
            Appointment.appointment_time >= datetime.now(),
        ).all()

        upcoming_list = [{
            "id": a.id,
            "doctor": a.doctor.user.name,
            "department": a.doctor.department.name if a.doctor.department else None,
            "date": a.appointment_time.strftime("%Y-%m-%d"),
            "time": a.appointment_time.strftime("%I:%M %p"),
        } for a in upcoming]

        return {
            "patient_name": patient.user.name,
            "departments": dept_list,
            "upcoming_appointments": upcoming_list
        }, 200


# ----------------------------------------------------
# Departments List
# ----------------------------------------------------
class PatientDepartments(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        d = Department.query.all()
        return [{"id": d.id, "name": d.name, "description": d.description}] , 200


# ----------------------------------------------------
# Department Details + Doctor List
# ----------------------------------------------------
class DepartmentDetails(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self, dept_id):
        dept = Department.query.get_or_404(dept_id)

        doctors = [{
            "id": d.id,
            "name": d.user.name,
            "specialization": d.specialization,
            "experience_years": d.experience_years
        } for d in dept.doctors]

        return {
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "doctors": doctors
        }, 200


# ----------------------------------------------------
# Doctor Profile
# ----------------------------------------------------
class DoctorDetails(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self, doctor_id):
        d = Doctor.query.get_or_404(doctor_id)
        return {
            "id": d.id,
            "name": d.user.name,
            "specialization": d.specialization,
            "experience_years": d.experience_years,
            "department": d.department.name if d.department else None,
            "approved": d.is_approved
        }, 200


# ----------------------------------------------------
# Doctor Availability
# ----------------------------------------------------
class DoctorAvailabilityPublic(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        slots = []

        for av in doctor.availabilities:
            slots.append({
                "date": av.date.strftime("%Y-%m-%d"),
                "start": av.start_time.strftime("%H:%M"),
                "end": av.end_time.strftime("%H:%M")
            })

        return slots, 200


# ----------------------------------------------------
# Book Appointment
# ----------------------------------------------------
class BookAppointment(RoleProtectedResource):
    required_roles = ["patient"]

    def post(self):
        data = request.get_json()
        doctor_id = data.get("doctor_id")
        date_str = data.get("date")
        start_time = data.get("start_time")

        if not all([doctor_id, date_str, start_time]):
            return {"message": "Missing required fields"}, 400

        patient = Patient.query.filter_by(user_id=get_jwt_identity()).first()
        doctor = Doctor.query.get_or_404(doctor_id)

        appt_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
        duration = 30
        appt_end = appt_dt + timedelta(minutes=duration)

        # Check for overlapping appointments with same doctor
        overlap = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "scheduled",
            Appointment.appointment_time < appt_end,
            Appointment.appointment_time + timedelta(minutes=Appointment.duration_minutes or 30) > appt_dt
        ).first()

        if overlap:
            return {"message": "Doctor not available at this time"}, 400

        # Check availability slot
        slot = Availability.query.filter_by(
            doctor_id=doctor_id,
            date=appt_dt.date(),
            is_available=True
        ).filter(
            Availability.start_time <= appt_dt.time(),
            Availability.end_time >= appt_end.time()
        ).first()

        if not slot:
            return {"message": "Selected time slot not available"}, 400

        appt = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            appointment_time=appt_dt,
            duration_minutes=duration,
            status="scheduled"
        )

        db.session.add(appt)
        db.session.commit()

        return {"message": "Appointment booked successfully"}, 201


# ----------------------------------------------------
# Cancel Appointment
# ----------------------------------------------------
class CancelAppointment(RoleProtectedResource):
    required_roles = ["patient"]

    def delete(self, appt_id):
        appt = Appointment.query.get_or_404(appt_id)

        if appt.status != "scheduled":
            return {"message": "Only scheduled appointments can be cancelled"}, 400

        appt.status = "cancelled"
        db.session.commit()

        return {"message": "Appointment cancelled"}, 200


# ----------------------------------------------------
# Patient History
# ----------------------------------------------------
class PatientMedicalHistory(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        patient = Patient.query.filter_by(user_id=get_jwt_identity()).first()
        history = []

        for a in patient.appointments:
            for t in a.treatments:
                history.append({
                    "visit_date": a.appointment_time.strftime("%Y-%m-%d"),
                    "doctor": a.doctor.user.name,
                    "department": a.doctor.department.name if a.doctor.department else None,
                    "visit_type": "In-person",
                    "tests_done": "ECG",
                    "diagnosis": t.diagnosis,
                    "prescription": t.prescription,
                    "notes": t.notes
                })

        return history, 200


# ----------------------------------------------------
# Export CSV
# ----------------------------------------------------
class ExportPatientHistoryCSV(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        patient = Patient.query.filter_by(user_id=get_jwt_identity()).first()
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Date", "Doctor", "Department", "Diagnosis", "Prescription", "Notes"])

        for a in patient.appointments:
            for t in a.treatments:
                writer.writerow([
                    a.appointment_time.strftime("%Y-%m-%d"),
                    a.doctor.user.name,
                    a.doctor.department.name if a.doctor.department else None,
                    t.diagnosis,
                    t.prescription,
                    t.notes
                ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.read().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="patient_history.csv"
        )


# ----------------------------------------------------
# Patient Profile
# ----------------------------------------------------
class PatientProfile(RoleProtectedResource):
    required_roles = ["patient"]

    def get(self):
        patient = Patient.query.filter_by(user_id=get_jwt_identity()).first()
        return {
            "id": patient.id,
            "name": patient.user.name,
            "email": patient.user.email,
            "phone": patient.user.phone,
            "medical_history": patient.medical_history
        }, 200

    def put(self):
        patient = Patient.query.filter_by(user_id=get_jwt_identity()).first()
        data = request.get_json()
        
        patient.user.name = data.get("name", patient.user.name)
        patient.user.phone = data.get("phone", patient.user.phone)
        patient.medical_history = data.get("medical_history", patient.medical_history)
        
        db.session.commit()
        return {"message": "Profile updated"}, 200


# ----------------------------------------------------
# Reschedule Appointment
# ----------------------------------------------------
class RescheduleAppointment(RoleProtectedResource):
    required_roles = ["patient"]

    def post(self, appt_id):
        data = request.get_json()
        new_date = data.get("date")
        new_time = data.get("start_time")

        appt = Appointment.query.get_or_404(appt_id)
        patient = Patient.query.filter_by(user_id=get_jwt_identity()).first()

        if appt.patient_id != patient.id:
            return {"message": "Unauthorized"}, 403

        if appt.status != "scheduled":
            return {"message": "Only scheduled appointments can be rescheduled"}, 400

        new_dt = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
        new_end = new_dt + timedelta(minutes=30)

        # Validate new slot
        slot = Availability.query.filter_by(
            doctor_id=appt.doctor_id,
            date=new_dt.date(),
            is_available=True
        ).filter(
            Availability.start_time <= new_dt.time(),
            Availability.end_time >= new_end.time()
        ).first()

        if not slot:
            return {"message": "Selected slot not available"}, 400

        appt.appointment_time = new_dt
        db.session.commit()

        return {"message": "Appointment rescheduled"}, 200
