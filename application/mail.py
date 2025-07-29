import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SMTP_SERVER_HOST = 'localhost'  # or your SMTP server address 
SMTP_SERVER_PORT = 1025                     # 465 for SSL, 587 for TLS
SENDER_ADDRESS = 'parkingapp@donotreply.in'     
SENDER_PASSWORD = ''      

def send_email(subject, recipient, html_content, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = SENDER_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject

    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Attach file if provided
    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=attachment_path.split('/')[-1])
        part['Content-Disposition'] = f'attachment; filename="{attachment_path.split("/")[-1]}"'
        msg.attach(part)

    # Send email
    with smtplib.SMTP_SSL(SMTP_SERVER_HOST, SMTP_SERVER_PORT) as server:
        server.login(SENDER_ADDRESS, SENDER_PASSWORD)
        server.send_message(msg)