# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///pos.db')
    # config.py
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_strong_secret_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_strong_jwt_secret_key')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
