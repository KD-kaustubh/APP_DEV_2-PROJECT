from celery import shared_task
from application.models import User, ActivityReport, Reservation, Payment
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
        # Count reservations for this user
        reservation_count = db.session.query(Reservation).filter_by(user_id=user.id).count()
        
        # Calculate total spent from payments
        total_spent = db.session.query(db.func.sum(Payment.amount)).filter_by(user_id=user.id).scalar() or 0
        
        user_data = {
            'username': user.uname,
            'email': user.email,
            'reservations': reservation_count,
            'total_spent': total_spent,
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
    # Get all users
    users = User.query.all()
    
    for user in users:
        # Check if user has any active reservations (not yet completed)
        active_reservations = db.session.query(Reservation).filter_by(
            user_id=user.id, 
            leaving_timestamp=None
        ).all()
        
        if active_reservations:
            # Send reminder for active parking sessions
            reservation_details = []
            for res in active_reservations:
                reservation_details.append({
                    'vehicle_number': res.vehicle_number,
                    'parking_time': res.parking_timestamp.strftime('%Y-%m-%d %H:%M'),
                    'spot_id': res.spot_id
                })
            
            html_content = f"""
            <h2>Daily Parking Reminder</h2>
            <p>Dear {user.uname},</p>
            <p>You have {len(active_reservations)} active parking session(s):</p>
            <ul>
            """
            
            for detail in reservation_details:
                html_content += f"""
                <li>Vehicle: {detail['vehicle_number']} - Parked since: {detail['parking_time']} (Spot #{detail['spot_id']})</li>
                """
            
            html_content += """
            </ul>
            <p>Please remember to complete your parking session when you leave.</p>
            <p>Thank you for using our parking service!</p>
            """
            
            send_email(
                subject="Daily Parking Reminder - Active Sessions",
                recipient=user.email,
                html_content=html_content
            )
    
    return f"Daily reminders sent to users with active parking sessions."