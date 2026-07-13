import os

import csv

import time

from app.celery_worker import celery_app

@celery_app.task(name='app.tasks.export_csv.export_applications_csv', bind=True)

def export_applications_csv(self, student_id):

    from app import create_app

    app = create_app()

    with app.app_context():

        from flask import current_app

        from app.models import StudentProfile, Application

        from flask_mail import Message

        from app.extensions import mail

        student = StudentProfile.query.get(student_id)

        if not student:

            return {'status': 'error', 'message': 'Student not found'}

        applications = Application.query.filter_by(student_id=student_id)
                                        .order_by(Application.applied_at.desc()).all()

        export_folder = current_app.config['EXPORT_FOLDER']

        os.makedirs(export_folder, exist_ok=True)

        filename = f'applications_student_{student_id}_{int(time.time())}.csv'

        filepath = os.path.join(export_folder, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:

            writer = csv.writer(f)

            writer.writerow([

                'Application ID', 'Student ID', 'Student Name',

                'Department', 'CGPA',

                'Company', 'Drive', 'Job Title',

                'Status', 'Applied Date'

            ])

            for app_rec in applications:

                writer.writerow([

                    app_rec.id,

                    student.id,

                    student.full_name or student.user.username,

                    student.department or '',

                    student.cgpa or '',

                    app_rec.drive.company.company_name if app_rec.drive and app_rec.drive.company else '',

                    app_rec.drive.drive_name if app_rec.drive else '',

                    app_rec.drive.job_title if app_rec.drive else '',

                    app_rec.status,

                    app_rec.applied_at.strftime('%Y-%m-%d') if app_rec.applied_at else ''

                ])

        if student.user and student.user.email:

            try:

                html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {  font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; } 
        .card {  background: #f8f8ff; border-radius: 8px; padding: 24px; border-left: 4px solid #6c63ff; } 
        h2 {  color: #1a1a2e; } 
        .badge {  display:inline-block; background:#6c63ff; color:white; padding:4px 12px;
                  border-radius:20px; font-size:13px; } 
      </style>
    </head>
    <body>
      <div class="card">
        <h2>📥 Your CSV Export is Ready!</h2>
        <p>Hi <strong>{student.full_name or student.user.username}</strong>,</p>
        <p>Your application history has been exported successfully.</p>
        <p>
          <span class="badge">{len(applications)} application(s)</span>
        </p>
        <p>Log in to the PlaceMe dashboard and go to the <strong>History</strong> tab to download your CSV.</p>
        <p style="font-size:12px;color:#888;margin-top:20px;">
          This is an automated message from PlaceMe.
        </p>
      </div>
    </body>
    </html>
                """.strip()

                msg = Message(

                    subject='📥 [PlaceMe] Your application history export is ready',

                    recipients=[student.user.email],

                    html=html_body,

                    body=f'Hi {student.full_name},\n\nYour CSV export ({len(applications)} applications) is ready. Download it from the History tab on your dashboard.'

                )

                mail.send(msg)

            except Exception as e:

                print(f'[CSV Export] Email notification failed: {e}')

        print(f'[CSV Export] Created {filename} with {len(applications)} rows.')

        return {'status': 'success', 'filename': filename, 'total_rows': len(applications)}
