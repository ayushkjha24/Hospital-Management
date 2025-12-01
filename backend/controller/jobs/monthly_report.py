# controller/jobs/monthly_report.py
from datetime import date, timedelta
import calendar
from controller.models import Appointment, Doctor, Patient
from controller.mailer import send_email_html, render_template_from_string
from controller.jobs_helpers import generate_filename, write_bytes_to_exports
from celery_app import celery

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><meta charset="utf-8"/><title>Monthly Report</title></head>
<body>
  <h2>Monthly Activity Report — {{ month_name }} {{ year }}</h2>
  <h3>Doctor: {{ doctor_name }}</h3>
  <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
    <thead>
      <tr><th>Date</th><th>Patient</th><th>Diagnosis</th><th>Treatment</th><th>Next Visit</th></tr>
    </thead>
    <tbody>
      {% for r in appointments %}
      <tr>
        <td>{{ r.date }}</td>
        <td>{{ r.patient }}</td>
        <td>{{ r.diagnosis }}</td>
        <td>{{ r.treatment }}</td>
        <td>{{ r.next_visit }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

def previous_month_range():
    today = date.today()
    first_this = today.replace(day=1)
    last_prev = first_this - timedelta(days=1)
    start = last_prev.replace(day=1)
    end = last_prev
    return start, end

@celery.task(bind=True)
def create_and_send_monthly_reports(self):
    start_date, end_date = previous_month_range()
    month_name = calendar.month_name[start_date.month]
    year = start_date.year

    doctors = Doctor.query.all()
    reports_sent = 0

    for doc in doctors:
        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.date >= start_date,
            Appointment.date <= end_date
        ).order_by(Appointment.date).all()

        rows = []
        for a in appts:
            patient = Patient.query.get(a.patient_id)
            rows.append({
                "date": getattr(a, "date", ""),
                "patient": patient.name if patient else "Unknown",
                "diagnosis": getattr(a, "diagnosis", "") or "",
                "treatment": getattr(a, "treatment", "") or "",
                "next_visit": getattr(a, "next_visit", "") or ""
            })

        html = render_template_from_string(
            HTML_TEMPLATE,
            month_name=month_name,
            year=year,
            doctor_name=doc.name,
            appointments=rows
        )

        # Save and attach HTML
        filename = generate_filename(f"monthly_report_doctor_{doc.id}", "html")
        path = write_bytes_to_exports(filename, html.encode("utf-8"))

        # Read bytes and send as attachment (prod: use S3 signed url instead)
        with open(path, "rb") as fh:
            data = fh.read()

        send_email_html(doc.email, f"Monthly Report — {month_name} {year}", html, attachments=[(filename, data, "text/html")])
        reports_sent += 1

    return {"reports_sent": reports_sent}
