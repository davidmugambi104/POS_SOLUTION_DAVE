# app.py
from flask import Flask
from flask_migrate import Migrate
from model import db
from config import Config
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # Add this line to set up Flask-Migrate

with app.app_context():
    db.create_all()  # Ensure tables are created
app.config['JWT_SECRET_KEY'] = 'MKpkvui1436nKL'  # Replace with a strong secret key
jwt = JWTManager(app)
import routes  # Import your application routes

if __name__ == '__main__':
    app.run(debug=True)
