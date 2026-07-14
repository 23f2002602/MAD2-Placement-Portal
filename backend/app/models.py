from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

class User(db.Model):

    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)

    username       = db.Column(db.String(80),  unique=True, nullable=False)

    email          = db.Column(db.String(120), unique=True, nullable=False)

    password_hash  = db.Column(db.String(256), nullable=False)

    role           = db.Column(db.String(20),  nullable=False)                                   

    is_active      = db.Column(db.Boolean, default=True)

    is_blacklisted = db.Column(db.Boolean, default=False)

    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship('StudentProfile', back_populates='user',

                                      uselist=False, cascade='all, delete-orphan')

    company_profile = db.relationship('CompanyProfile', back_populates='user',

                                      uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):

        return check_password_hash(self.password_hash, password)

    def to_dict(self):

        return {

            'id': self.id,

            'username': self.username,

            'email': self.email,

            'role': self.role,

            'is_active': self.is_active,

            'is_blacklisted': self.is_blacklisted,

            'created_at': self.created_at.isoformat()

        }

class StudentProfile(db.Model):

    __tablename__ = 'student_profiles'

    id              = db.Column(db.Integer, primary_key=True)

    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    full_name       = db.Column(db.String(120))

    department      = db.Column(db.String(100))                         

    cgpa            = db.Column(db.Float, default=0.0)

    graduation_year = db.Column(db.Integer)

    phone           = db.Column(db.String(20))

    resume_path     = db.Column(db.String(256))                               

    user         = db.relationship('User', back_populates='student_profile')

    applications = db.relationship('Application', back_populates='student',

                                   cascade='all, delete-orphan')

    def __init__(self, user_id: int, full_name: str = '', department: str = '',

                 cgpa: float = 0.0, graduation_year: int = 0,

                 phone: str = '', resume_path: str = '', **kwargs):

        super().__init__(user_id=user_id, full_name=full_name, department=department,

                         cgpa=cgpa, graduation_year=graduation_year,

                         phone=phone, resume_path=resume_path, **kwargs)

    def to_dict(self):

        return {

            'id': self.id,

            'user_id': self.user_id,

            'username': self.user.username if self.user else None,

            'email': self.user.email if self.user else None,

            'full_name': self.full_name,

            'department': self.department,

            'cgpa': self.cgpa,

            'graduation_year': self.graduation_year,

            'phone': self.phone,

            'resume_path': self.resume_path,

            'is_active': self.user.is_active if self.user else True,

            'is_blacklisted': self.user.is_blacklisted if self.user else False,

        }

class CompanyProfile(db.Model):

    __tablename__ = 'company_profiles'

    id              = db.Column(db.Integer, primary_key=True)

    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    company_name    = db.Column(db.String(120), nullable=False)

    hr_contact      = db.Column(db.String(120))

    website         = db.Column(db.String(200))

    description     = db.Column(db.Text)

    approval_status = db.Column(db.String(20), default='pending')                                       

    user   = db.relationship('User', back_populates='company_profile')

    drives = db.relationship('PlacementDrive', back_populates='company',

                             cascade='all, delete-orphan')

    def to_dict(self):

        return {

            'id': self.id,

            'user_id': self.user_id,

            'username': self.user.username if self.user else None,

            'email': self.user.email if self.user else None,

            'company_name': self.company_name,

            'hr_contact': self.hr_contact,

            'website': self.website,

            'description': self.description,

            'approval_status': self.approval_status,

            'is_active': self.user.is_active if self.user else True,

            'is_blacklisted': self.user.is_blacklisted if self.user else False,

        }

class PlacementDrive(db.Model):

    __tablename__ = 'placement_drives'

    id                   = db.Column(db.Integer, primary_key=True)

    company_id           = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False)

    drive_name           = db.Column(db.String(120), nullable=False)

    job_title            = db.Column(db.String(120), nullable=False)

    job_description      = db.Column(db.Text)

    eligibility_criteria = db.Column(db.Text, default='{}')

    application_deadline = db.Column(db.DateTime)

    salary               = db.Column(db.String(50))

    location             = db.Column(db.String(100))

    interview_type       = db.Column(db.String(50), default='In-person')

    status               = db.Column(db.String(20), default='pending')                                    

    created_at           = db.Column(db.DateTime, default=datetime.utcnow)

    company      = db.relationship('CompanyProfile', back_populates='drives')

    applications = db.relationship('Application', back_populates='drive',

                                   cascade='all, delete-orphan')

    def to_dict(self):

        import json

        try:

            eligibility = json.loads(self.eligibility_criteria) if self.eligibility_criteria else {}

        except Exception:

            eligibility = {}

        return {

            'id': self.id,

            'company_id': self.company_id,

            'company_name': self.company.company_name if self.company else None,

            'drive_name': self.drive_name,

            'job_title': self.job_title,

            'job_description': self.job_description,

            'eligibility_criteria': eligibility,

            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,

            'salary': self.salary,

            'location': self.location,

            'interview_type': self.interview_type,

            'status': self.status,

            'created_at': self.created_at.isoformat(),

            'applicant_count': len(self.applications)

        }

class Application(db.Model):

    __tablename__ = 'applications'

    id         = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)

    drive_id   = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    status     = db.Column(db.String(20), default='applied')

    __table_args__ = (

        db.UniqueConstraint('student_id', 'drive_id', name='uq_student_drive'),

    )

    student = db.relationship('StudentProfile', back_populates='applications')

    drive   = db.relationship('PlacementDrive', back_populates='applications')

    def to_dict(self):

        return {

            'id': self.id,

            'student_id': self.student_id,

            'student_name': self.student.full_name if self.student else None,

            'student_email': self.student.user.email if self.student and self.student.user else None,

            'student_department': self.student.department if self.student else None,

            'drive_id': self.drive_id,

            'drive_name': self.drive.drive_name if self.drive else None,

            'job_title': self.drive.job_title if self.drive else None,

            'company_name': self.drive.company.company_name if self.drive and self.drive.company else None,

            'applied_at': self.applied_at.isoformat(),

            'status': self.status,

        }
