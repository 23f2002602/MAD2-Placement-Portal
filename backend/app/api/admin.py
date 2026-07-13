"""
admin.py — Admin-only API routes

All routes here require a valid JWT token with role = 'admin'.
The @role_required('admin') decorator enforces this.

Routes:
    GET    /api/admin/dashboard                      → Stats overview

    GET    /api/admin/companies                      → List all companies
    GET    /api/admin/companies/<id>                 → Get single company
    PUT    /api/admin/companies/<id>                 → Update company details
    DELETE /api/admin/companies/<id>                 → Delete company + user
    PATCH  /api/admin/companies/<id>/approve         → Approve or reject company
    PATCH  /api/admin/companies/<id>/blacklist       → Blacklist/reinstate company

    GET    /api/admin/students                       → List all students
    GET    /api/admin/students/<id>                  → Get single student
    PUT    /api/admin/students/<id>                  → Update student details
    DELETE /api/admin/students/<id>                  → Delete student + user
    PATCH  /api/admin/students/<id>/blacklist        → Blacklist/reinstate student

    GET    /api/admin/drives                         → List all drives
    GET    /api/admin/drives/<id>                    → Get single drive
    PUT    /api/admin/drives/<id>                    → Update drive details
    DELETE /api/admin/drives/<id>                    → Delete drive
    PATCH  /api/admin/drives/<id>/approve            → Approve or reject a drive

    GET    /api/admin/applications                   → View all applications
    DELETE /api/admin/applications/<id>              → Delete an application
"""

from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from app.extensions import db, cache, mail
from app.models import User, StudentProfile, CompanyProfile, PlacementDrive, Application
from app.api.decorators import role_required

admin_bp = Blueprint('admin', __name__)


# ── Dashboard ──────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    """Return summary statistics for the admin overview page."""
    # Try to get cached stats first (avoids hitting the database every time)
    cached = cache.get('admin_stats')
    if cached:
        return jsonify(cached), 200

    # Count records from the database
    stats = {
        'total_students':    User.query.filter_by(role='student').count(),
        'total_companies':   User.query.filter_by(role='company').count(),
        'total_drives':      PlacementDrive.query.count(),
        'pending_companies': CompanyProfile.query.filter_by(approval_status='pending').count(),
        'pending_drives':    PlacementDrive.query.filter_by(status='pending').count(),
        'total_applications': Application.query.count(),
    }

    # Cache for 5 minutes so repeated refreshes don't spam the database
    cache.set('admin_stats', stats, timeout=300)
    return jsonify(stats), 200


# ── Companies ──────────────────────────────────────────────────────────────────

@admin_bp.route('/companies', methods=['GET'])
@role_required('admin')
def list_companies():
    """List all companies. Use ?search=name to filter."""
    search = request.args.get('search', '').strip()
    query  = CompanyProfile.query.join(User)

    if search:
        # ilike = case-insensitive LIKE search
        query = query.filter(
            db.or_(
                CompanyProfile.company_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
            )
        )
    return jsonify([c.to_dict() for c in query.all()]), 200


@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@role_required('admin')
def get_company(company_id):
    """Get a single company's full profile."""
    company = CompanyProfile.query.get_or_404(company_id)
    return jsonify(company.to_dict()), 200


@admin_bp.route('/companies/<int:company_id>', methods=['PUT'])
@role_required('admin')
def update_company(company_id):
    """Update a company's profile details (admin can edit any field)."""
    company = CompanyProfile.query.get_or_404(company_id)
    data    = request.get_json()

    # Update profile fields
    company.company_name = data.get('company_name', company.company_name)
    company.hr_contact   = data.get('hr_contact',   company.hr_contact)
    company.website      = data.get('website',       company.website)
    company.description  = data.get('description',   company.description)

    # Allow admin to update the login email/username too
    new_email    = data.get('email')
    new_username = data.get('username')
    if new_email and new_email != company.user.email:
        if User.query.filter(User.email == new_email, User.id != company.user_id).first():
            return jsonify({'error': 'Email already in use'}), 409
        company.user.email = new_email
    if new_username and new_username != company.user.username:
        if User.query.filter(User.username == new_username, User.id != company.user_id).first():
            return jsonify({'error': 'Username already in use'}), 409
        company.user.username = new_username

    db.session.commit()
    cache.delete('admin_stats')
    return jsonify({'message': 'Company updated', 'company': company.to_dict()}), 200


@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@role_required('admin')
def delete_company(company_id):
    """Permanently delete a company and its associated user account."""
    company = CompanyProfile.query.get_or_404(company_id)
    user    = company.user
    db.session.delete(user)   # cascade deletes company_profile and drives
    db.session.commit()
    cache.delete('admin_stats')
    return jsonify({'message': 'Company deleted successfully'}), 200


@admin_bp.route('/companies/<int:company_id>/approve', methods=['PATCH'])
@role_required('admin')
def approve_company(company_id):
    """Approve or reject a company registration."""
    data   = request.get_json()
    action = data.get('action')   # 'approved' or 'rejected'

    if action not in ('approved', 'rejected'):
        return jsonify({'error': 'action must be "approved" or "rejected"'}), 400

    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = action
    db.session.commit()
    cache.delete('admin_stats')   # refresh the stats cache

    # ── Send email to company HR on approval ──────────────────────────────────
    if action == 'approved':
        hr_email = company.user.email  # registered email of the company account
        try:
            msg = Message(
                subject='🎉 Your Company Registration Has Been Approved!',
                recipients=[hr_email],
                html=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px;
                            border: 1px solid #e0e0e0; border-radius: 8px; background-color: #f9f9f9;">
                    <h2 style="color: #2e7d32;">Congratulations! Your Company is Approved ✅</h2>
                    <p>Dear <strong>{company.company_name}</strong> Team,</p>
                    <p>
                        We are pleased to inform you that your company registration on the
                        <strong>Placement Portal</strong> has been <strong style="color:#2e7d32;">approved</strong>
                        by the admin.
                    </p>
                    <p>You can now log in to the portal and:</p>
                    <ul>
                        <li>Post new placement drives</li>
                        <li>Review student applications</li>
                        <li>Update your company profile</li>
                    </ul>
                    <p style="margin-top: 24px;">
                        If you have any questions, please contact the placement cell.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ccc; margin: 24px 0;" />
                    <p style="font-size: 12px; color: #888;">
                        This is an automated message from the Placement Portal. Please do not reply to this email.
                    </p>
                </div>
                """,
            )
            mail.send(msg)
            current_app.logger.info(f"Approval email sent to {hr_email}")
        except Exception as e:
            # Log the error but don't block the approval response
            current_app.logger.error(f"Failed to send approval email to {hr_email}: {e}")

    return jsonify({'message': f'Company {action}', 'company': company.to_dict()}), 200


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_company(company_id):
    """Blacklist (or reinstate) a company. Blacklisting also closes their drives."""
    data      = request.get_json()
    blacklist = data.get('blacklist', True)   # True = blacklist, False = reinstate

    company = CompanyProfile.query.get_or_404(company_id)
    company.user.is_blacklisted = blacklist
    company.user.is_active      = not blacklist

    # Close all this company's open drives when blacklisting
    if blacklist:
        for drive in company.drives:
            if drive.status in ('pending', 'approved'):
                drive.status = 'closed'

    db.session.commit()
    cache.delete('admin_stats')
    status = 'blacklisted' if blacklist else 'reinstated'
    return jsonify({'message': f'Company {status}'}), 200


# ── Students ───────────────────────────────────────────────────────────────────

@admin_bp.route('/students', methods=['GET'])
@role_required('admin')
def list_students():
    """List all students. Use ?search=name to filter."""
    search = request.args.get('search', '').strip()
    query  = StudentProfile.query.join(User)

    if search:
        query = query.filter(
            db.or_(
                StudentProfile.full_name.ilike(f'%{search}%'),
                StudentProfile.department.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
            )
        )
    return jsonify([s.to_dict() for s in query.all()]), 200


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@role_required('admin')
def get_student(student_id):
    """Get a single student's full profile."""
    student = StudentProfile.query.get_or_404(student_id)
    return jsonify(student.to_dict()), 200


@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@role_required('admin')
def update_student(student_id):
    """Update a student's profile details (admin can edit any field)."""
    student = StudentProfile.query.get_or_404(student_id)
    data    = request.get_json()

    # Update profile fields
    student.full_name       = data.get('full_name',       student.full_name)
    student.department      = data.get('department',      student.department)
    student.phone           = data.get('phone',           student.phone)
    student.graduation_year = int(data.get('graduation_year', student.graduation_year or 0))

    cgpa = data.get('cgpa')
    if cgpa is not None:
        cgpa = float(cgpa)
        if not (0.0 <= cgpa <= 10.0):
            return jsonify({'error': 'CGPA must be between 0.0 and 10.0'}), 400
        student.cgpa = cgpa

    # Allow admin to update login email/username
    new_email    = data.get('email')
    new_username = data.get('username')
    if new_email and new_email != student.user.email:
        if User.query.filter(User.email == new_email, User.id != student.user_id).first():
            return jsonify({'error': 'Email already in use'}), 409
        student.user.email = new_email
    if new_username and new_username != student.user.username:
        if User.query.filter(User.username == new_username, User.id != student.user_id).first():
            return jsonify({'error': 'Username already in use'}), 409
        student.user.username = new_username

    db.session.commit()
    cache.delete(f'student_{student.id}')
    cache.delete('admin_stats')
    return jsonify({'message': 'Student updated', 'student': student.to_dict()}), 200


@admin_bp.route('/students/<int:student_id>', methods=['DELETE'])
@role_required('admin')
def delete_student(student_id):
    """Permanently delete a student and their user account."""
    student = StudentProfile.query.get_or_404(student_id)
    user    = student.user
    db.session.delete(user)   # cascade deletes student_profile and applications
    db.session.commit()
    cache.delete('admin_stats')
    return jsonify({'message': 'Student deleted successfully'}), 200


@admin_bp.route('/students/<int:student_id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_student(student_id):
    """Blacklist or reinstate a student."""
    data      = request.get_json()
    blacklist = data.get('blacklist', True)

    student = StudentProfile.query.get_or_404(student_id)
    student.user.is_blacklisted = blacklist
    student.user.is_active      = not blacklist
    db.session.commit()
    cache.delete('admin_stats')
    status = 'blacklisted' if blacklist else 'reinstated'
    return jsonify({'message': f'Student {status}'}), 200


# ── Drives ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/drives', methods=['GET'])
@role_required('admin')
def list_drives():
    """List all drives. Filter by ?status=pending and/or ?search=name."""
    status = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    query  = PlacementDrive.query

    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(PlacementDrive.drive_name.ilike(f'%{search}%'))

    drives = query.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drives]), 200


@admin_bp.route('/drives/<int:drive_id>', methods=['GET'])
@role_required('admin')
def get_drive(drive_id):
    """Get a single drive's full details."""
    drive = PlacementDrive.query.get_or_404(drive_id)
    return jsonify(drive.to_dict()), 200


@admin_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@role_required('admin')
def update_drive(drive_id):
    """Update any field of a placement drive."""
    import json
    from datetime import datetime

    drive = PlacementDrive.query.get_or_404(drive_id)
    data  = request.get_json()

    drive.drive_name      = data.get('drive_name',      drive.drive_name)
    drive.job_title       = data.get('job_title',       drive.job_title)
    drive.job_description = data.get('job_description', drive.job_description)
    drive.salary          = data.get('salary',          drive.salary)
    drive.location        = data.get('location',        drive.location)
    drive.interview_type  = data.get('interview_type',  drive.interview_type)
    drive.status          = data.get('status',          drive.status)

    # Update eligibility criteria if provided
    if 'eligibility_criteria' in data:
        drive.eligibility_criteria = json.dumps(data['eligibility_criteria'])

    # Update deadline if provided
    deadline_str = data.get('application_deadline')
    if deadline_str:
        try:
            drive.application_deadline = datetime.fromisoformat(deadline_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format for application_deadline'}), 400

    db.session.commit()
    cache.delete('admin_stats')
    cache.delete('approved_drives')
    return jsonify({'message': 'Drive updated', 'drive': drive.to_dict()}), 200


@admin_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@role_required('admin')
def delete_drive(drive_id):
    """Permanently delete a placement drive and all its applications."""
    drive = PlacementDrive.query.get_or_404(drive_id)
    db.session.delete(drive)   # cascade deletes applications
    db.session.commit()
    cache.delete('admin_stats')
    cache.delete('approved_drives')
    return jsonify({'message': 'Drive deleted successfully'}), 200


@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PATCH'])
@role_required('admin')
def approve_drive(drive_id):
    """Approve or reject a placement drive."""
    data   = request.get_json()
    action = data.get('action')

    if action not in ('approved', 'rejected'):
        return jsonify({'error': 'action must be "approved" or "rejected"'}), 400

    drive = PlacementDrive.query.get_or_404(drive_id)

    # Can only approve drives from already-approved companies
    if action == 'approved' and drive.company.approval_status != 'approved':
        return jsonify({'error': 'Company is not approved yet'}), 400

    drive.status = action
    db.session.commit()
    cache.delete('admin_stats')
    cache.delete('approved_drives')
    return jsonify({'message': f'Drive {action}', 'drive': drive.to_dict()}), 200


# ── Applications ───────────────────────────────────────────────────────────────

@admin_bp.route('/applications', methods=['GET'])
@role_required('admin')
def list_applications():
    """View all student applications across all drives."""
    apps = Application.query.order_by(Application.applied_at.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200


@admin_bp.route('/applications/<int:app_id>', methods=['DELETE'])
@role_required('admin')
def delete_application(app_id):
    """Permanently delete a student application record."""
    application = Application.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    cache.delete('admin_stats')
    return jsonify({'message': 'Application deleted successfully'}), 200


# ── Statistics CSV Download ────────────────────────────────────────────────────

@admin_bp.route('/export/stats', methods=['GET'])
@role_required('admin')
def export_stats_csv():
    """
    Download a full placement statistics CSV on demand.
    Includes one row per drive with applicant counts + status breakdowns,
    plus a summary row at the bottom.
    Streamed directly — no file saved to disk.
    """
    import csv
    import io
    from datetime import datetime as dt
    from flask import make_response

    drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # ── Header ────────────────────────────────────────────────────────────────
    writer.writerow([
        'Drive ID', 'Drive Name', 'Company', 'Job Title',
        'Status', 'Location', 'Salary', 'Deadline',
        'Total Applicants', 'Applied', 'Shortlisted', 'Selected', 'Rejected', 'Waiting',
        'Created At'
    ])

    # ── Per-drive rows ────────────────────────────────────────────────────────
    total_drives = 0
    grand_applied = grand_shortlisted = grand_selected = grand_rejected = grand_waiting = 0

    for d in drives:
        apps = Application.query.filter_by(drive_id=d.id).all()
        counts = {
            'applied':     sum(1 for a in apps if a.status == 'applied'),
            'shortlisted': sum(1 for a in apps if a.status == 'shortlisted'),
            'selected':    sum(1 for a in apps if a.status == 'selected'),
            'rejected':    sum(1 for a in apps if a.status == 'rejected'),
            'waiting':     sum(1 for a in apps if a.status == 'waiting'),
        }
        writer.writerow([
            d.id,
            d.drive_name,
            d.company.company_name if d.company else '',
            d.job_title,
            d.status,
            d.location or '',
            d.salary or '',
            d.application_deadline.strftime('%Y-%m-%d') if d.application_deadline else '',
            len(apps),
            counts['applied'],
            counts['shortlisted'],
            counts['selected'],
            counts['rejected'],
            counts['waiting'],
            d.created_at.strftime('%Y-%m-%d'),
        ])

        total_drives      += 1
        grand_applied     += counts['applied']
        grand_shortlisted += counts['shortlisted']
        grand_selected    += counts['selected']
        grand_rejected    += counts['rejected']
        grand_waiting     += counts['waiting']

    # ── Summary row ───────────────────────────────────────────────────────────
    writer.writerow([])   # blank separator
    writer.writerow([
        'TOTAL', f'{total_drives} drives', '', '', '', '', '', '',
        grand_applied + grand_shortlisted + grand_selected + grand_rejected + grand_waiting,
        grand_applied, grand_shortlisted, grand_selected, grand_rejected, grand_waiting,
        f'Generated {dt.utcnow().strftime("%Y-%m-%d %H:%M")} UTC'
    ])

    csv_content = output.getvalue()
    output.close()

    filename = f'admin_stats_{dt.utcnow().strftime("%Y%m%d_%H%M")}.csv'
    response = make_response(csv_content)
    response.headers['Content-Type']        = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ── On-demand Job Triggers ──────────────────────────────────────────────────────

@admin_bp.route('/jobs/send-reminders', methods=['POST'])
@role_required('admin')
def trigger_reminders():
    """
    Trigger the daily student reminder emails on demand.
    Returns the Celery task ID so the frontend can optionally poll for completion.
    """
    from app.tasks.reminders import send_daily_reminders
    task = send_daily_reminders.delay()
    return jsonify({
        'message': 'Daily reminder job started. Emails will be sent to eligible students.',
        'task_id': task.id
    }), 202


@admin_bp.route('/jobs/monthly-report', methods=['POST'])
@role_required('admin')
def trigger_monthly_report():
    """
    Trigger the monthly placement activity report email on demand.
    Returns the Celery task ID so the frontend can optionally poll for completion.
    """
    from app.tasks.monthly_report import send_monthly_report
    task = send_monthly_report.delay()
    return jsonify({
        'message': 'Monthly report job started. The report will be emailed to the admin.',
        'task_id': task.id
    }), 202
