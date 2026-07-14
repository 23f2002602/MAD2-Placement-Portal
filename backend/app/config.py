import os

from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY     = os.getenv('SECRET_KEY', 'dev-secret-key')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')

    JWT_ACCESS_TOKEN_EXPIRES  = 900                   

    JWT_REFRESH_TOKEN_EXPIRES = 604800            

    SQLALCHEMY_DATABASE_URI       = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///placement.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False                                   

    CACHE_TYPE          = os.getenv('CACHE_TYPE', 'SimpleCache')

    CACHE_REDIS_URL     = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/1')

    CACHE_DEFAULT_TIMEOUT = 300            

    CACHE_THRESHOLD     = 500                                

    CELERY_BROKER_URL    = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2')

    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')

    MAIL_SERVER         = os.getenv('MAIL_SERVER', 'smtp.gmail.com')

    MAIL_PORT           = int(os.getenv('MAIL_PORT', 587))

    MAIL_USE_TLS        = os.getenv('MAIL_USE_TLS', 'True') == 'True'

    MAIL_USERNAME       = os.getenv('MAIL_USERNAME', '')

    MAIL_PASSWORD       = os.getenv('MAIL_PASSWORD', '')

    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')

    UPLOAD_FOLDER      = os.getenv('UPLOAD_FOLDER', 'uploads')                    

    EXPORT_FOLDER      = os.getenv('EXPORT_FOLDER', 'exports')                

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024                         

    ADMIN_EMAIL    = os.getenv('ADMIN_EMAIL', 'admin@placement.com')

    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin@123')

    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
