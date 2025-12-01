# controller/mailer.py
import smtplib
from email.message import EmailMessage
from jinja2 import Template
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")   # your SMTP username
SMTP_PASS = os.getenv("SMTP_PASS", "")   # your SMTP password (app password for Gmail)
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "no-reply@medisphere.local")

def send_email_html(to_email, subject, html_body, attachments=None):
    """
    Send an HTML email with optional attachments (list of (filename, bytes, mimetype)).
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content("This email requires an HTML capable client.")
    msg.add_alternative(html_body, subtype="html")

    if attachments:
        for fname, data_bytes, mime in attachments:
            maintype, subtype = mime.split("/", 1)
            msg.add_attachment(data_bytes, maintype=maintype, subtype=subtype, filename=fname)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        if SMTP_PORT == 587:
            smtp.starttls()
        if SMTP_USER and SMTP_PASS:
            smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

def render_template_from_string(template_str, **ctx):
    return Template(template_str).render(**ctx)
