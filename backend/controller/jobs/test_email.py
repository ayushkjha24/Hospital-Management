# controller/jobs/test_email.py
from celery_app import celery
from controller.mailer import send_email_html

@celery.task(name="test.send_test_email")
def send_test_email(to="ayushkjha.2004@gmail.com"):
    html = "<h3>This is a Celery test email from Medisphere</h3>"
    send_email_html(to, "Test Email from Celery", html)
    return "Sent"
