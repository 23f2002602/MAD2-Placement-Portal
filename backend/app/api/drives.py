from flask import Blueprint, request, jsonify

from flask_jwt_extended import jwt_required

from app.extensions import db, cache

from app.models import PlacementDrive

drives_bp = Blueprint('drives', __name__)

@drives_bp.route('/', methods=['GET'])

@jwt_required()

def list_approved_drives():

    search    = request.args.get('search', '').strip()

    cache_key = f'approved_drives_{search}'

    cached = cache.get(cache_key)

    if cached:

        return jsonify(cached), 200

    query = PlacementDrive.query.filter_by(status='approved')

    if search:

        query = query.filter(

            db.or_(

                PlacementDrive.drive_name.ilike(f'%{search}%'),

                PlacementDrive.job_title.ilike(f'%{search}%'),

            )

        )

    drives = query.order_by(PlacementDrive.application_deadline.asc()).all()

    result = [d.to_dict() for d in drives]

    cache.set(cache_key, result, timeout=120)                        

    return jsonify(result), 200

@drives_bp.route('/<int:drive_id>', methods=['GET'])

@jwt_required()

def get_drive(drive_id):

    drive = PlacementDrive.query.get_or_404(drive_id)

    return jsonify(drive.to_dict()), 200
