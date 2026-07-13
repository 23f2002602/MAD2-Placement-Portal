import os
from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cache, mail, cors


def create_app(config_class=Config):
    """
    Application Factory Pattern.
    Instead of creating the Flask app at module level, we create it inside
    a function. This makes testing easier and avoids circular imports.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create folders for file uploads and CSV exports if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    # ── Initialize Extensions ──────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)

    # Allow requests from the Vue frontend (runs on port 5173 during development)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # ── Register API Blueprints ────────────────────────────────
    # Each blueprint groups related routes into its own file.
    from app.api.auth    import auth_bp
    from app.api.admin   import admin_bp
    from app.api.company import company_bp
    from app.api.student import student_bp
    from app.api.drives  import drives_bp

    app.register_blueprint(auth_bp,    url_prefix='/api/auth')
    app.register_blueprint(admin_bp,   url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(drives_bp,  url_prefix='/api/drives')

    # ── Create Database Tables & Seed Admin ───────────────────
    with app.app_context():
        db.create_all()       # Creates tables if they don't exist
        _seed_admin(app)      # Creates the admin user if not present

    return app


def _seed_admin(app):
    """
    Create the one and only admin user on first run.
    Admin credentials come from the .env file.
    This is intentional — there is no admin registration endpoint.
    """
    from app.models import User
    existing_admin = User.query.filter_by(role='admin').first()

    if not existing_admin:
        admin = User(
            username=app.config['ADMIN_USERNAME'],
            email=app.config['ADMIN_EMAIL'],
            role='admin'
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f"[+] Admin created: {app.config['ADMIN_EMAIL']}")
    else:
        print("[*] Admin already exists, skipping.")
