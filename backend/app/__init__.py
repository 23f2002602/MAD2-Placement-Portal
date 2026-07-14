import os

from flask import Flask

from app.config import Config

from app.extensions import db, jwt, cache, mail, cors

def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    db.init_app(app)

    jwt.init_app(app)

    cache.init_app(app)

    mail.init_app(app)

    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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

    with app.app_context():

        db.create_all()                                           

        _seed_admin(app)                                             

    return app

def _seed_admin(app):

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
