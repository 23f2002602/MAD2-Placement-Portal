"""
student.py — Student API routes

Routes:
    GET  /api/student/dashboard             → Student info + available drives + applications
    GET  /api/student/profile               → Get student profile
    PUT  /api/student/profile               → Update profile (incl. email change)
    POST /api/student/profile/resume        → Upload resume file
    GET  /api/student/drives                → List drives (with search/filter)
    GET  /api/student/drives/<id>           → Get drive detail + eligibility check
    POST /api/student/drives/<id>/apply     → Apply to a drive
    GET  /api/student/applications          → My applications
    GET  /api/student/applications/<id>     → Get a single application
    DELETE /api/student/applications/<id>   → Withdraw application (only if status='applied')
    GET  /api/student/history               → Full placement history
    POST /api/student/export/csv            → Trigger async CSV export
    GET  /api/student/export/status/<id>    → Check export job status
    GET  /api/student/export/download/<f>   → Download the exported CSV
"""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db, cache
from app.models import User, StudentProfile, PlacementDrive, Application
from app.api.decorators import role_required

student_bp = Blueprint('student', __name__)

# Only these file types are allowed for resume upload
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def _allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_student():
    """Helper: look up the student profile for whoever is logged in."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.student_profile:
        return None, jsonify({'error': 'Student profile not found'}), 404
    return user.student_profile, None, None


def _check_eligibility(student, drive):
    """
    Check if a student meets ALL of a drive's eligibility criteria.
    Returns a list of error messages. Empty list = eligible.
    """
    try:
        criteria = json.loads(drive.eligibility_criteria) if drive.eligibility_criteria else {}
    except Exception:
        criteria = {}

    errors = []

    # Check CGPA requirement
    min_cgpa = float(criteria.get('min_cgpa', 0.0))
    if min_cgpa > 0 and student.cgpa < min_cgpa:
        errors.append(f'Min CGPA required: {min_cgpa} (yours: {student.cgpa})')

    # Check branch/department requirement
    branches = criteria.get('branches', [])
    if branches and student.department not in branches:
        errors.append(f'Branch required: {", ".join(branches)} (yours: {student.department})')

    # Check graduation year requirement
    grad_years = criteria.get('grad_years', [])
    if grad_years and student.graduation_year not in [int(y) for y in grad_years]:
        errors.append(f'Grad year required: {grad_years} (yours: {student.graduation_year})')

    return errors


# ── Dashboard ──────────────────────────────────────────────────────────────────

@student_bp.route('/dashboard', methods=['GET'])
@role_required('student')
def dashboard():
    """All-in-one endpoint: student info + available drives + my applications."""
    student, err, code = _get_student()
    if err:
        return err, code

    # Get all approved drives, sorted by nearest deadline first
    drives = PlacementDrive.query.filter_by(status='approved')\
                                 .order_by(PlacementDrive.application_deadline.asc()).all()

    # Build a set of drive IDs the student has already applied to
    applied_ids = {a.drive_id for a in Application.query.filter_by(student_id=student.id).all()}

    drives_data = []
    for d in drives:
        dd = d.to_dict()
        dd['already_applied']    = d.id in applied_ids
        dd['eligible']           = len(_check_eligibility(student, d)) == 0
        dd['eligibility_errors'] = _check_eligibility(student, d)
        drives_data.append(dd)

    # My applications (newest first)
    apps = Application.query.filter_by(student_id=student.id)\
                            .order_by(Application.applied_at.desc()).all()

    return jsonify({
        'student': student.to_dict(),
        'available_drives': drives_data,
        'my_applications': [a.to_dict() for a in apps],
    }), 200


# ── Profile ────────────────────────────────────────────────────────────────────

@student_bp.route('/profile', methods=['GET'])
@role_required('student')
def get_profile():
    student, err, code = _get_student()
    if err:
        return err, code
    # Cache the profile for 5 minutes (reduces DB queries)
    key    = f'student_{student.id}'
    cached = cache.get(key)
    if cached:
        return jsonify(cached), 200
    data = student.to_dict()
    cache.set(key, data, timeout=300)
    return jsonify(data), 200


@student_bp.route('/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    """
    Update student profile fields.
    Students may also change their login email — uniqueness is enforced.
    """
    student, err, code = _get_student()
    if err:
        return err, code

    data = request.get_json()

    # ── Email change ─────────────────────────────────────────────────────────
    new_email = data.get('email', '').strip()
    if new_email and new_email != student.user.email:
        # Check that the new email isn't already registered
        if User.query.filter(User.email == new_email, User.id != student.user_id).first():
            return jsonify({'error': 'Email already in use by another account'}), 409
        student.user.email = new_email

    # ── Profile fields ───────────────────────────────────────────────────────
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

    db.session.commit()
    cache.delete(f'student_{student.id}')   # clear cache so next GET is fresh
    return jsonify({'message': 'Profile updated', 'student': student.to_dict()}), 200


@student_bp.route('/profile/resume', methods=['POST'])
@role_required('student')
def upload_resume():
    """Upload a resume file (PDF/DOC/DOCX, max 5 MB)."""
    student, err, code = _get_student()
    if err:
        return err, code

    if 'resume' not in request.files:
        return jsonify({'error': 'No file part named "resume" in the request'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not _allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: pdf, doc, docx'}), 400

    # secure_filename removes dangerous characters from the filename
    filename = secure_filename(f'resume_{student.id}_{file.filename}')
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))

    student.resume_path = filename
    db.session.commit()
    cache.delete(f'student_{student.id}')
    return jsonify({'message': 'Resume uploaded', 'filename': filename}), 200


@student_bp.route('/resume/<filename>', methods=['GET'])
def download_resume(filename):
    """Serve a resume file for download/viewing."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# ── Drives ─────────────────────────────────────────────────────────────────────

@student_bp.route('/drives', methods=['GET'])
@role_required('student')
def list_drives():
    """
    List all approved drives with search and eligibility filter.
    Query params: ?search=keyword  ?eligible_only=true
    """
    student, err, code = _get_student()
    if err:
        return err, code

    search        = request.args.get('search', '').strip()
    eligible_only = request.args.get('eligible_only', 'false').lower() == 'true'

    query = PlacementDrive.query.filter_by(status='approved')
    if search:
        query = query.filter(
            db.or_(
                PlacementDrive.drive_name.ilike(f'%{search}%'),
                PlacementDrive.job_title.ilike(f'%{search}%'),
            )
        )

    drives     = query.order_by(PlacementDrive.application_deadline.asc()).all()
    applied_ids = {a.drive_id for a in Application.query.filter_by(student_id=student.id).all()}

    result = []
    for d in drives:
        errors = _check_eligibility(student, d)
        if eligible_only and errors:
            continue   # skip ineligible drives if filter is on
        dd = d.to_dict()
        dd['already_applied']    = d.id in applied_ids
        dd['eligible']           = len(errors) == 0
        dd['eligibility_errors'] = errors
        result.append(dd)

    return jsonify(result), 200


@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@role_required('student')
def get_drive(drive_id):
    """Get full details of one drive, including the student's eligibility status."""
    student, err, code = _get_student()
    if err:
        return err, code

    drive  = PlacementDrive.query.filter_by(id=drive_id, status='approved').first_or_404()
    errors = _check_eligibility(student, drive)
    app    = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()

    data = drive.to_dict()
    data['already_applied']    = app is not None
    data['eligible']           = len(errors) == 0
    data['eligibility_errors'] = errors
    if app:
        data['application_status'] = app.status
    return jsonify(data), 200


# ── Applying ───────────────────────────────────────────────────────────────────

@student_bp.route('/drives/<int:drive_id>/apply', methods=['POST'])
@role_required('student')
def apply_drive(drive_id):
    """Apply to a placement drive."""
    student, err, code = _get_student()
    if err:
        return err, code

    if student.user.is_blacklisted:
        return jsonify({'error': 'Your account is blacklisted'}), 403

    drive = PlacementDrive.query.filter_by(id=drive_id, status='approved').first_or_404()

    # Check if deadline has passed
    if drive.application_deadline and datetime.utcnow() > drive.application_deadline:
        return jsonify({'error': 'Application deadline has passed'}), 400

    # Check eligibility
    errors = _check_eligibility(student, drive)
    if errors:
        return jsonify({'error': 'Eligibility not met', 'details': errors}), 400

    # Check for duplicate application
    if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
        return jsonify({'error': 'You have already applied to this drive'}), 409

    application = Application(student_id=student.id, drive_id=drive.id)
    db.session.add(application)
    db.session.commit()
    cache.delete('admin_stats')
    return jsonify({'message': 'Applied successfully!', 'application': application.to_dict()}), 201


# ── My Applications / History ──────────────────────────────────────────────────

@student_bp.route('/applications', methods=['GET'])
@role_required('student')
def my_applications():
    """View all of the student's applications."""
    student, err, code = _get_student()
    if err:
        return err, code
    apps = Application.query.filter_by(student_id=student.id)\
                            .order_by(Application.applied_at.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200


@student_bp.route('/applications/<int:app_id>', methods=['GET'])
@role_required('student')
def get_application(app_id):
    """Get full details of a single application (must belong to the logged-in student)."""
    student, err, code = _get_student()
    if err:
        return err, code

    application = Application.query.get_or_404(app_id)

    # Security check: application must belong to this student
    if application.student_id != student.id:
        return jsonify({'error': 'Not authorized'}), 403

    return jsonify(application.to_dict()), 200


@student_bp.route('/applications/<int:app_id>', methods=['DELETE'])
@role_required('student')
def withdraw_application(app_id):
    """
    Withdraw (delete) an application.
    Only allowed when the status is still 'applied' —
    once the company has shortlisted/selected/rejected the student,
    withdrawal is no longer permitted.
    """
    student, err, code = _get_student()
    if err:
        return err, code

    application = Application.query.get_or_404(app_id)

    # Security check: must be the student's own application
    if application.student_id != student.id:
        return jsonify({'error': 'Not authorized'}), 403

    # Business rule: can only withdraw before the company acts
    if application.status != 'applied':
        return jsonify({
            'error': f'Cannot withdraw — your application status is already "{application.status}"'
        }), 400

    db.session.delete(application)
    db.session.commit()
    cache.delete('admin_stats')
    return jsonify({'message': 'Application withdrawn successfully'}), 200


@student_bp.route('/history', methods=['GET'])
@role_required('student')
def placement_history():
    """View complete placement history."""
    student, err, code = _get_student()
    if err:
        return err, code
    apps = Application.query.filter_by(student_id=student.id)\
                            .order_by(Application.applied_at.desc()).all()
    return jsonify({'student': student.to_dict(), 'history': [a.to_dict() for a in apps]}), 200


# ── CSV Export (uses Celery for async processing) ──────────────────────────────

@student_bp.route('/export/csv', methods=['POST'])
@role_required('student')
def export_csv():
    """Start an async Celery task to export this student's application history as CSV."""
    student, err, code = _get_student()
    if err:
        return err, code
    from app.tasks.export_csv import export_applications_csv
    task = export_applications_csv.delay(student.id)
    return jsonify({'message': 'Export started.', 'task_id': task.id}), 202


@student_bp.route('/export/status/<task_id>', methods=['GET'])
@role_required('student')
def export_status(task_id):
    """Poll the status of the CSV export task."""
    from app.celery_worker import celery_app
    task = celery_app.AsyncResult(task_id)
    return jsonify({
        'task_id': task_id,
        'status': task.status,                               # PENDING / STARTED / SUCCESS / FAILURE
        'result': task.result if task.ready() else None      # filename when done
    }), 200


@student_bp.route('/export/download/<filename>', methods=['GET'])
@role_required('student')
def download_export(filename):
    """Download the generated CSV file."""
    return send_from_directory(current_app.config['EXPORT_FOLDER'], filename)


@student_bp.route('/export/direct-csv', methods=['GET'])
@role_required('student')
def direct_csv_download():
    """
    Synchronous single-click CSV download — no Celery needed.
    Streams the student's full application history directly as a CSV file.
    Ideal for quick exports; use the async /export/csv for large histories
    that also send an email notification.
    """
    import csv
    import io
    from flask import make_response

    student, err, code = _get_student()
    if err:
        return err, code

    applications = Application.query.filter_by(student_id=student.id)\
                                    .order_by(Application.applied_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'Application ID', 'Student ID', 'Student Name',
        'Department', 'CGPA',
        'Company Name', 'Drive Title', 'Job Title',
        'Application Status', 'Applied Date'
    ])

    for app in applications:
        writer.writerow([
            app.id,
            student.id,
            student.full_name or student.user.username,
            student.department or '',
            student.cgpa or '',
            app.drive.company.company_name if app.drive and app.drive.company else '',
            app.drive.drive_name if app.drive else '',
            app.drive.job_title if app.drive else '',
            app.status,
            app.applied_at.strftime('%Y-%m-%d') if app.applied_at else ''
        ])

    csv_content = output.getvalue()
    output.close()

    filename = f'my_applications_{student.id}_{datetime.utcnow().strftime("%Y%m%d_%H%M")}.csv'
    response = make_response(csv_content)
    response.headers['Content-Type']        = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
