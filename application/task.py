from celery import shared_task
from application.models import User,ActivityReport
from application.database import db
from datetime import datetime
import time
import csv
from application.utilis import format_report
from application.mail import send_email

@shared_task(ignore_result=False, name='csv_report')
def csv_report():
    activity = ActivityReport.query.all()
    csv_file_name = "activity_report_{}.csv".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    with open(f'static/{csv_file_name}', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "User ID", "User Name", "Month", "Total Reservations", "Total Spent", "Most Used Lot ID"])
        for act in activity:
            user = User.query.get(act.user_id)
            writer.writerow([
                act.id,
                act.user_id,
                user.uname if user else "N/A",
                act.month,
                act.total_reservations,
                act.total_spent,
                act.most_used_lot_id or "N/A"
            ])
    
    return csv_file_name



@shared_task(ignore_result=False, name='monthly_report')
def monthly_report():
    users = User.query.all()
    for user in users:
        user_data = {
            'username': user.uname,
            'email': user.email,
            'reservations': user.reservations.count(),
            'total_spent': sum(res.amount for res in user.reservations),
        }
        html_content = format_report('templates/monthly_report.html', user_data)
        html_file_path = f'static/monthly_report_{user.id}.html'
        with open(html_file_path, 'w') as f:
            f.write(html_content)
        send_email(
            subject="Your Monthly Parking Report",
            recipient=user.email,
            html_content=html_content,
            attachment_path=html_file_path
        )
    return "Monthly reports sent."

@shared_task(ignore_result=False, name='daily_reminder')

def daily_reminder():
    # Logic for daily reminder goes here
    return "Sending daily reminder..."