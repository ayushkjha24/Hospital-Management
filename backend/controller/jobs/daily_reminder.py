# controller/jobs/daily_reminder.py
from controller.database import db
from controller.models import Appointment, Patient, Doctor
from controller.mailer import send_email_html, render_template_from_string
from celery_app import celery
from datetime import date

TEMPLATE = """
<p>Hi {{ patient_name }},</p>
<p>This is a reminder for your appointment today with Dr. {{ doctor_name }} at {{ time }}.</p>
<p>Please arrive 10 minutes early.</p>
"""

@celery.task(bind=True, max_retries=3)
def send_daily_reminders(self):
    today = date.today()
    # query appointments scheduled for today and still 'scheduled'
    appts = Appointment.query.filter(
        Appointment.date == today,
        Appointment.status == "scheduled"
    ).all()

    sent = 0
    for a in appts:
        try:
            patient = Patient.query.get(a.patient_id)
            doctor = Doctor.query.get(a.doctor_id) if getattr(a, "doctor_id", None) else None
            if not patient or not patient.email:
                continue

            body = render_template_from_string(
                TEMPLATE,
                patient_name=patient.name,
                doctor_name=(doctor.name if doctor else "your doctor"),
                time=getattr(a, "time", "")
            )

            send_email_html(patient.email, "Appointment Reminder", body)
            sent += 1
        except Exception as exc:
            # task should not stop; log and continue
            print("Failed to send reminder for appt", getattr(a, "id", None), exc)
            continue

    return {"sent": sent}
