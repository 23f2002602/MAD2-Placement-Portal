"""
auth.py — Authentication routes (Login & Register)

Routes:
    POST /api/auth/register  → Create student or company account
    POST /api/auth/login     → Login and get JWT tokens
    POST /api/auth/refresh   → Get a new access token using refresh token
    GET  /api/auth/me        → Get the currently logged-in user's info
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.extensions import db
from app.models import User, StudentProfile, CompanyProfile

# Blueprint groups all auth routes under a common prefix (/api/auth)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new student or company user.
    Expects JSON body with: username, email, password, role, + role-specific fields.
    Admin cannot register — admin is created programmatically.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract and clean required fields
    username = data.get('username', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role     = data.get('role', '').lower()   # must be 'student' or 'company'

    # --- Basic validation ---
    if not all([username, email, password, role]):
        return jsonify({'error': 'username, email, password, and role are required'}), 400

    if role not in ('student', 'company'):
        return jsonify({'error': 'Role must be "student" or "company"'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # --- Check for duplicates ---
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # --- Create the base User record ---
    user = User(username=username, email=email, role=role)
    user.set_password(password)    # hashes the password
    db.session.add(user)
    db.session.flush()             # assigns user.id before committing

    # --- Create the role-specific profile ---
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
            # approval_status defaults to 'pending' — admin must approve
        )
        db.session.add(profile)

    db.session.commit()
    return jsonify({'message': f'{role.capitalize()} registered successfully. Please login.'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login for admin, student, and company users.
    Returns JWT access_token and refresh_token on success.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # check_password() compares plain text against the stored hash
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Block blacklisted or deactivated accounts
    if user.is_blacklisted:
        return jsonify({'error': 'Your account is blacklisted. Contact admin.'}), 403
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

    # Companies must be approved by admin before they can login
    if user.role == 'company' and user.company_profile:
        status = user.company_profile.approval_status
        if status == 'pending':
            return jsonify({'error': 'Your company registration is pending admin approval.'}), 403
        if status == 'rejected':
            return jsonify({'error': 'Your company registration was rejected by admin.'}), 403

    # Create JWT tokens — we embed the user's role inside the token
    # so we don't need to query the database on every request
    additional_claims = {'role': user.role}
    access_token  = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)

    # Build user info to send back to the frontend
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
@jwt_required(refresh=True)   # requires the refresh token, not access token
def refresh():
    """Get a new access token using the refresh token (without logging in again)."""
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
    """Return current logged-in user's info. Useful to restore session on page reload."""
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200
