from flask import Blueprint, request, jsonify

from flask_jwt_extended import (

    create_access_token, create_refresh_token,

    jwt_required, get_jwt_identity, get_jwt

)

from app.extensions import db

from app.models import User, StudentProfile, CompanyProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])

def register():

    data = request.get_json()

    if not data:

        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()

    email    = data.get('email', '').strip().lower()

    password = data.get('password', '')

    role     = data.get('role', '').lower()                                   

    if not all([username, email, password, role]):

        return jsonify({'error': 'username, email, password, and role are required'}), 400

    if role not in ('student', 'company'):

        return jsonify({'error': 'Role must be "student" or "company"'}), 400

    if len(password) < 6:

        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(username=username).first():

        return jsonify({'error': 'Username already taken'}), 409

    if User.query.filter_by(email=email).first():

        return jsonify({'error': 'Email already registered'}), 409

    user = User(username=username, email=email, role=role)

    user.set_password(password)                         

    db.session.add(user)

    db.session.flush()                                                

    if role == 'student':

        profile = StudentProfile(

            user_id=user.id,

            full_name=data.get('full_name', username),

            department=data.get('department', ''),

            cgpa=float(data.get('cgpa', 0.0)),

            graduation_year=int(data.get('graduation_year', 0)),

            phone=data.get('phone', '')

        )

        db.session.add(profile)

    elif role == 'company':

        company_name = data.get('company_name', '').strip()

        if not company_name:

            db.session.rollback()

            return jsonify({'error': 'company_name is required for company registration'}), 400

        profile = CompanyProfile(

            user_id=user.id,

            company_name=company_name,

            hr_contact=data.get('hr_contact', ''),

            website=data.get('website', ''),

            description=data.get('description', '')

        )

        db.session.add(profile)

    db.session.commit()

    return jsonify({'message': f'{role.capitalize()} registered successfully. Please login.'}), 201

@auth_bp.route('/login', methods=['POST'])

def login():

    data = request.get_json()

    if not data:

        return jsonify({'error': 'No data provided'}), 400

    email    = data.get('email', '').strip().lower()

    password = data.get('password', '')

    if not email or not password:

        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):

        return jsonify({'error': 'Invalid email or password'}), 401

    if user.is_blacklisted:

        return jsonify({'error': 'Your account is blacklisted. Contact admin.'}), 403

    if not user.is_active:

        return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

    if user.role == 'company' and user.company_profile:

        status = user.company_profile.approval_status

        if status == 'pending':

            return jsonify({'error': 'Your company registration is pending admin approval.'}), 403

        if status == 'rejected':

            return jsonify({'error': 'Your company registration was rejected by admin.'}), 403

    additional_claims = {'role': user.role}

    access_token  = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)

    user_info = {

        'id': user.id,

        'username': user.username,

        'email': user.email,

        'role': user.role,

    }

    if user.role == 'student' and user.student_profile:

        user_info['profile_id'] = user.student_profile.id

    elif user.role == 'company' and user.company_profile:

        user_info['profile_id']   = user.company_profile.id

        user_info['company_name'] = user.company_profile.company_name

    return jsonify({

        'access_token': access_token,

        'refresh_token': refresh_token,

        'user': user_info

    }), 200

@auth_bp.route('/refresh', methods=['POST'])

@jwt_required(refresh=True)                                                 

def refresh():

    identity = get_jwt_identity()

    claims   = get_jwt()

    new_access_token = create_access_token(

        identity=identity,

        additional_claims={'role': claims.get('role')}

    )

    return jsonify({'access_token': new_access_token}), 200

@auth_bp.route('/me', methods=['GET'])

@jwt_required()

def me():

    user_id = int(get_jwt_identity())

    user = User.query.get_or_404(user_id)

    return jsonify(user.to_dict()), 200
