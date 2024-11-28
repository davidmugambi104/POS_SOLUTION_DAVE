from flask import Flask
import os
from flask_migrate import Migrate
from model import db
from config import Config
from flask_jwt_extended import JWTManager

# Initialize the Flask app
app = Flask(__name__)

# Load configuration from config.py or environment variables
app.config.from_object(Config)

# Ensure SQLAlchemy uses the database URI from environment variables (if set)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pos.db')  # Use environment variable or fallback to SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set secret keys (for JWT and Flask)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_strong_secret_key')  # Replace with a strong key for production
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_strong_jwt_secret_key')  # Replace with a strong key for production

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # Flask-Migrate setup
jwt = JWTManager(app)

# Import routes
import routes  # Ensure your routes are in the routes.py file

# Only create the tables if necessary; use migrations for changes
# db.create_all() is not needed if you're using Flask-Migrate

if __name__ == '__main__':
    app.run(debug=True)
