import os
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import timedelta
from flask_cors import CORS

from model import db, Employee, Product, Transaction, SaleItem, Category, InventoryTransaction

# Load environment variables
load_dotenv()

# Create the Flask app instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
CORS(app)

# Initialize the database, migrations, JWT, and API
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)

# JWT blacklist for token revocation
blacklist = set()
expires = timedelta(hours=24)

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blacklist

# Login route for generating tokens
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return {'message': 'Missing username or password'}, 400
    
    employee = Employee.query.filter_by(name=username).first()
    if employee and employee.check_password(password):
        access_token = create_access_token(identity=employee.id, expires_delta=expires)
        refresh_token = create_refresh_token(identity=employee.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200
    else:
        return {'message': 'Invalid credentials'}, 401

# Logout route for revoking the token
@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'message': 'Logged out successfully'}), 200

# Employee Resource for managing employees
class EmployeeResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'name' not in data or 'role' not in data or 'password' not in data:
            return {'message': 'Missing required fields'}, 400

        if Employee.query.filter_by(name=data['name']).first():
            return {'message': 'Employee already exists'}, 400

        hashed_password = generate_password_hash(data['password'])
        employee = Employee(
            name=data['name'],
            role=data['role']
        )
        employee.set_password(data['password'])
        db.session.add(employee)
        db.session.commit()
        return jsonify({'message': 'Employee created', 'employee': employee.id}), 201

    @jwt_required()
    def get(self):
        employees = Employee.query.all()
        return jsonify([{'id': e.id, 'name': e.name, 'role': e.role} for e in employees]), 200

class SpecificEmployee(Resource):
    @jwt_required()
    def get(self, id):
        employee = Employee.query.get_or_404(id)
        return jsonify({'id': employee.id, 'name': employee.name, 'role': employee.role}), 200

api.add_resource(EmployeeResource, '/employees')
api.add_resource(SpecificEmployee, '/employees/<int:id>')

# Product Resource for managing products
class ProductResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'name' not in data or 'price' not in data:
            return {'message': 'Missing required fields'}, 400

        product = Product(
            name=data['name'],
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            min_stock_level=data.get('min_stock_level', 5)
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created', 'product_id': product.id}), 201

    @jwt_required()
    def get(self):
        products = Product.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'stock_quantity': p.stock_quantity} for p in products]), 200

class SpecificProduct(Resource):
    @jwt_required()
    def get(self, id):
        product = Product.query.get_or_404(id)
        return jsonify({'id': product.id, 'name': product.name, 'price': product.price, 'stock_quantity': product.stock_quantity}), 200

api.add_resource(ProductResource, '/products')
api.add_resource(SpecificProduct, '/products/<int:id>')

# Transaction Resource for managing transactions
class TransactionResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        if not data or 'employee_id' not in data or 'total_amount' not in data:
            return {'message': 'Missing required fields'}, 400

        transaction = Transaction(
            employee_id=data['employee_id'],
            total_amount=data['total_amount'],
            discount=data.get('discount', 0)
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction created', 'transaction_id': transaction.id}), 201

    @jwt_required()
    def get(self):
        transactions = Transaction.query.all()
        return jsonify([{'id': t.id, 'employee_id': t.employee_id, 'total_amount': t.total_amount} for t in transactions]), 200

api.add_resource(TransactionResource, '/transactions')

# Initialize the app
if __name__ == '__main__':
    app.run(debug=True)
