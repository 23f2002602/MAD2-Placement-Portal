import json

from datetime import datetime

from flask import Blueprint, request, jsonify

from flask_jwt_extended import get_jwt_identity

from app.extensions import db, cache

from app.models import User, CompanyProfile, PlacementDrive, Application

from app.api.decorators import role_required

company_bp = Blueprint('company', __name__)

def _get_company():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user or not user.company_profile:

        return None, jsonify({'error': 'Company profile not found'}), 404

    return user.company_profile, None, None

@company_bp.route('/dashboard', methods=['GET'])

@role_required('company')

def dashboard():

    company, err, code = _get_company()

    if err:

        return err, code

    drives      = PlacementDrive.query.filter_by(company_id=company.id).all()

    drives_data = []

    for d in drives:

        dd = d.to_dict()

        dd['applicant_count'] = Application.query.filter_by(drive_id=d.id).count()

        drives_data.append(dd)

    return jsonify({

        'company': company.to_dict(),

        'drives': drives_data,

        'total_drives': len(drives),

        'total_applicants': sum(d['applicant_count'] for d in drives_data),

    }), 200

@company_bp.route('/profile', methods=['GET'])

@role_required('company')

def get_profile():

    company, err, code = _get_company()

    if err:

        return err, code

    return jsonify(company.to_dict()), 200

@company_bp.route('/profile', methods=['PUT'])

@role_required('company')

def update_profile():

    company, err, code = _get_company()

    if err:

        return err, code

    data = request.get_json()

    company.company_name = data.get('company_name', company.company_name)

    company.hr_contact   = data.get('hr_contact',   company.hr_contact)

    company.website      = data.get('website',      company.website)

    company.description  = data.get('description',  company.description)

    db.session.commit()

    cache.delete(f'company_{company.id}')

    return jsonify({'message': 'Profile updated', 'company': company.to_dict()}), 200

@company_bp.route('/drives', methods=['POST'])

@role_required('company')

def create_drive():

    company, err, code = _get_company()

    if err:

        return err, code

    if company.approval_status != 'approved':

        return jsonify({'error': 'Your company must be approved by admin before creating drives'}), 403

    data = request.get_json()

    if not data:

        return jsonify({'error': 'No data provided'}), 400

    drive_name = data.get('drive_name', '').strip()

    job_title  = data.get('job_title', '').strip()

    if not drive_name or not job_title:

        return jsonify({'error': 'drive_name and job_title are required'}), 400

    eligibility = {

        'min_cgpa': float(data.get('min_cgpa', 0.0)),

        'branches': data.get('branches', []),                         

        'grad_years': data.get('grad_years', [])                      

    }

    deadline = None

    deadline_str = data.get('application_deadline')

    if deadline_str:

        try:

            deadline = datetime.fromisoformat(deadline_str)

        except ValueError:

            return jsonify({'error': 'Invalid date format for application_deadline'}), 400

    drive = PlacementDrive(

        company_id=company.id,

        drive_name=drive_name,

        job_title=job_title,

        job_description=data.get('job_description', ''),

        eligibility_criteria=json.dumps(eligibility),

        application_deadline=deadline,

        salary=data.get('salary', ''),

        location=data.get('location', ''),

        interview_type=data.get('interview_type', 'In-person'),

        status='pending'                                                         

    )

    db.session.add(drive)

    db.session.commit()

    cache.delete('admin_stats')

    return jsonify({'message': 'Drive submitted for admin approval.', 'drive': drive.to_dict()}), 201

@company_bp.route('/drives', methods=['GET'])

@role_required('company')

def list_drives():

    company, err, code = _get_company()

    if err:

        return err, code

    drives = PlacementDrive.query.filter_by(company_id=company.id)
                                 .order_by(PlacementDrive.created_at.desc()).all()

    return jsonify([d.to_dict() for d in drives]), 200

@company_bp.route('/drives/<int:drive_id>', methods=['GET'])

@role_required('company')

def get_drive(drive_id):

    company, err, code = _get_company()

    if err:

        return err, code

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    return jsonify(drive.to_dict()), 200

@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])

@role_required('company')

def update_drive(drive_id):

    company, err, code = _get_company()

    if err:

        return err, code

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    if drive.status not in ('pending', 'rejected'):

        return jsonify({'error': 'Only pending or rejected drives can be edited'}), 403

    data = request.get_json()

    drive.drive_name      = data.get('drive_name',      drive.drive_name)

    drive.job_title       = data.get('job_title',       drive.job_title)

    drive.job_description = data.get('job_description', drive.job_description)

    drive.salary          = data.get('salary',          drive.salary)

    drive.location        = data.get('location',        drive.location)

    drive.interview_type  = data.get('interview_type',  drive.interview_type)

    if drive.status == 'rejected':

        drive.status = 'pending'

    if 'eligibility_criteria' in data:

        drive.eligibility_criteria = json.dumps(data['eligibility_criteria'])

    elif any(k in data for k in ('min_cgpa', 'branches', 'grad_years')):

        try:

            existing = json.loads(drive.eligibility_criteria) if drive.eligibility_criteria else {}

        except Exception:

            existing = {}

        existing['min_cgpa']   = float(data.get('min_cgpa',   existing.get('min_cgpa', 0.0)))

        existing['branches']   = data.get('branches',          existing.get('branches', []))

        existing['grad_years'] = data.get('grad_years',        existing.get('grad_years', []))

        drive.eligibility_criteria = json.dumps(existing)

    deadline_str = data.get('application_deadline')

    if deadline_str:

        try:

            drive.application_deadline = datetime.fromisoformat(deadline_str)

        except ValueError:

            return jsonify({'error': 'Invalid date format for application_deadline'}), 400

    db.session.commit()

    cache.delete('admin_stats')

    return jsonify({'message': 'Drive updated', 'drive': drive.to_dict()}), 200

@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])

@role_required('company')

def delete_drive(drive_id):

    company, err, code = _get_company()

    if err:

        return err, code

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    if drive.status not in ('pending', 'rejected'):

        return jsonify({'error': 'Only pending or rejected drives can be deleted. Contact admin to remove approved drives.'}), 403

    db.session.delete(drive)

    db.session.commit()

    cache.delete('admin_stats')

    return jsonify({'message': 'Drive deleted successfully'}), 200

@company_bp.route('/drives/<int:drive_id>/close', methods=['PATCH'])

@role_required('company')

def close_drive(drive_id):

    company, err, code = _get_company()

    if err:

        return err, code

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    drive.status = 'closed'

    db.session.commit()

    cache.delete('approved_drives')

    return jsonify({'message': 'Drive closed', 'drive': drive.to_dict()}), 200

@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])

@role_required('company')

def drive_applications(drive_id):

    company, err, code = _get_company()

    if err:

        return err, code

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first_or_404()

    apps  = Application.query.filter_by(drive_id=drive.id).all()

    return jsonify({

        'drive': drive.to_dict(),

        'applications': [a.to_dict() for a in apps]

    }), 200

@company_bp.route('/applications/<int:app_id>', methods=['GET'])

@role_required('company')

def get_application(app_id):

    company, err, code = _get_company()

    if err:

        return err, code

    application = Application.query.get_or_404(app_id)

    if application.drive.company_id != company.id:

        return jsonify({'error': 'Not authorized'}), 403

    return jsonify(application.to_dict()), 200

@company_bp.route('/applications/<int:app_id>/status', methods=['PATCH'])

@role_required('company')

def update_application_status(app_id):

    company, err, code = _get_company()

    if err:

        return err, code

    application = Application.query.get_or_404(app_id)

    if application.drive.company_id != company.id:

        return jsonify({'error': 'Not authorized'}), 403

    data       = request.get_json()

    new_status = data.get('status')

    valid_statuses = ('shortlisted', 'selected', 'rejected', 'waiting', 'applied')

    if new_status not in valid_statuses:

        return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400

    application.status = new_status

    db.session.commit()

    return jsonify({'message': 'Status updated', 'application': application.to_dict()}), 200

@company_bp.route('/export/stats', methods=['GET'])

@role_required('company')

def export_stats_csv():

    import csv

    import io

    from datetime import datetime as dt

    from flask import make_response

    company, err, code = _get_company()

    if err:

        return err, code

    drives = PlacementDrive.query.filter_by(company_id=company.id)
                                 .order_by(PlacementDrive.created_at.desc()).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(['Company', company.company_name])

    writer.writerow(['HR Contact', company.hr_contact or ''])

    writer.writerow(['Generated', dt.utcnow().strftime('%Y-%m-%d %H:%M UTC')])

    writer.writerow([])               

    writer.writerow([

        'Drive ID', 'Drive Name', 'Job Title', 'Status',

        'Location', 'Salary', 'Deadline',

        'Total Applicants', 'Applied', 'Shortlisted', 'Selected', 'Rejected', 'Waiting',

        'Created At'

    ])

    grand_total = grand_applied = grand_shortlisted = 0

    grand_selected = grand_rejected = grand_waiting = 0

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

        grand_total       += len(apps)

        grand_applied     += counts['applied']

        grand_shortlisted += counts['shortlisted']

        grand_selected    += counts['selected']

        grand_rejected    += counts['rejected']

        grand_waiting     += counts['waiting']

    writer.writerow([])

    writer.writerow([

        'TOTAL', f'{len(drives)} drives', '', '', '', '', '',

        grand_total, grand_applied, grand_shortlisted,

        grand_selected, grand_rejected, grand_waiting, ''

    ])

    csv_content = output.getvalue()

    output.close()

    filename = f'{company.company_name.replace(" ", "_")}_stats_{dt.utcnow().strftime("%Y%m%d_%H%M")}.csv'

    response = make_response(csv_content)

    response.headers['Content-Type']        = 'text/csv; charset=utf-8'

    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
