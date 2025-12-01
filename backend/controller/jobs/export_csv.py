# controller/jobs/export_csv.py
from celery_app import celery
from controller.models import Appointment, Patient, Doctor
from controller.jobs_helpers import generate_filename, write_bytes_to_exports
from controller.mailer import send_email_html
import csv
import io

@celery.task(bind=True)
def generate_patient_csv(self, patient_id, requester_email=None):
    # fetch appointments for the patient
    appts = Appointment.query.filter(Appointment.patient_id == patient_id).order_by(Appointment.date).all()
    patient = Patient.query.get(patient_id)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["user_id", "username", "consulting_doctor", "appointment_date", "diagnosis", "treatment", "next_visit"])

    for a in appts:
        doctor = Doctor.query.get(a.doctor_id) if getattr(a, "doctor_id", None) else None
        writer.writerow([
            a.patient_id,
            patient.name if patient else "",
            doctor.name if doctor else "",
            getattr(a, "date", ""),
            getattr(a, "diagnosis", "") or "",
            getattr(a, "treatment", "") or "",
            getattr(a, "next_visit", "") or ""
        ])

    csv_bytes = buf.getvalue().encode("utf-8")
    filename = generate_filename(f"patient_{patient_id}_history", "csv")
    path = write_bytes_to_exports(filename, csv_bytes)

    if requester_email:
        with open(path, "rb") as fh:
            csv_data = fh.read()
        send_email_html(requester_email, "Your Patient History Export is Ready", "<p>Your export is attached.</p>", attachments=[(filename, csv_data, "text/csv")])

    return {"path": path, "filename": filename}
