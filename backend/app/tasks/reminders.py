from datetime import datetime, timedelta

from app.celery_worker import celery_app

@celery_app.task(name='app.tasks.reminders.send_daily_reminders', bind=True)

def send_daily_reminders(self):

    from app import create_app

    app = create_app()

    with app.app_context():

        from app.models import PlacementDrive, Application, StudentProfile

        from flask_mail import Message

        from app.extensions import mail

        now  = datetime.utcnow()

        soon = now + timedelta(days=3)

        upcoming = PlacementDrive.query.filter(

            PlacementDrive.status == 'approved',

            PlacementDrive.application_deadline >= now,

            PlacementDrive.application_deadline <= soon

        ).all()

        if not upcoming:

            print('[Reminders] No upcoming deadlines.')

            return {'sent': 0, 'message': 'No upcoming deadlines in the next 3 days.'}

        students = StudentProfile.query.join(StudentProfile.user)
                                       .filter(StudentProfile.user.has(is_active=True, is_blacklisted=False)).all()

        sent = 0

        for student in students:

            if not student.user.email:

                continue

            applied_ids    = {a.drive_id for a in student.applications}

            pending_drives = [d for d in upcoming if d.id not in applied_ids]

            if not pending_drives:

                continue

            drive_list = '\n'.join([

                f'  • {d.drive_name} at {d.company.company_name} (Deadline: {d.application_deadline.strftime("%d %b %Y")})'

                for d in pending_drives

            ])

            html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {  font-family: Arial, sans-serif; line-height: 1.6; color: #333; } 
    .container {  max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; } 
    .header {  font-size: 18px; font-weight: bold; margin-bottom: 20px; color: #6c63ff; } 
    .list {  background: #f9f9f9; padding: 15px; border-radius: 4px; font-family: monospace; margin: 15px 0; white-space: pre-wrap; } 
    .footer {  font-size: 12px; color: #777; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; } 
  </style>
</head>
<body>
  <div class="container">
    <div class="header">⏳ Upcoming Application Deadlines</div>
    <p>Dear {student.full_name or student.user.username},</p>
    <p>This is a friendly reminder that the deadline to apply for the following placement drives is approaching within the next 3 days:</p>
    <div class="list">{drive_list}</div>
    <p>Please log in to the Placement Portal to submit your application before the deadline passes.</p>
    <p>Good luck!</p>
    <div class="footer">
      This is an automated notification from the Placement Portal. Please do not reply.
    </div>
  </div>
</body>
</html>
"""

            try:

                msg = Message(

                    subject='⏳ Placement Portal: Upcoming Application Deadlines',

                    recipients=[student.user.email],

                    html=html_body

                )

                mail.send(msg)

                sent += 1

            except Exception as e:

                print(f'[Reminders] Failed to send email to {student.user.email}: {e}')

        print(f'[Reminders] Sent {sent} reminders.')

        return {'sent': sent, 'total_students_checked': len(students), 'message': f'Sent {sent} reminder emails.'}
