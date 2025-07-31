import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SMTP_SERVER_HOST = 'localhost'
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = 'parkingapp@donotreply.in'
SENDER_PASSWORD = ''

def send_email(subject, recipient, html_content, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = SENDER_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=attachment_path.split('/')[-1])
        part['Content-Disposition'] = f'attachment; filename="{attachment_path.split("/")[-1]}"'
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER_HOST, SMTP_SERVER_PORT) as server:
        server.send_message(msg)

# send_email(
#     subject="Test Email",
#     recipient="test@example.com",
#     html_content="<h1>This is a test email</h1>"
# )