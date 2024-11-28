import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')  #Use a strong key
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default_jwt_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///pos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
