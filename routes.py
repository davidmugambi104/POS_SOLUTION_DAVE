# routes.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from model import db, Employee, Product, Transaction, SaleItem

from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change to a strong secret key
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # For JWT
jwt = JWTManager(app)

# Sign Up Route (Registration)
@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        existing_employee = Employee.query.filter_by(name=username).first()
        if existing_employee:
            return jsonify({'message': 'Username already taken'}), 400

        hashed_password = generate_password_hash(password, method='sha256')
        new_employee = Employee(name=username, password_hash=hashed_password, role=role)
        db.session.add(new_employee)
        db.session.commit()

        access_token = create_access_token(identity={'id': new_employee.id, 'role': new_employee.role})
        return jsonify({'message': 'Registration successful', 'token': access_token}), 201

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        employee = Employee.query.filter_by(name=username).first()
        if employee and check_password_hash(employee.password_hash, password):
            access_token = create_access_token(identity={'id': employee.id, 'role': employee.role})
            session['logged_in'] = True
            session['user_id'] = employee.id
            return jsonify({'message': 'Login successful', 'token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    return render_template('login.html')


# Logout Route (JWT does not require explicit logout, but included for flow clarity)
@app.route('/logout')
def logout():
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Product Lookup Route
@app.route('/products', methods=['GET', 'POST'])
@jwt_required()
def product_lookup():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        product_id = request.form['product_id']
        product = Product.query.get(product_id)
        if product:
            cart = request.cookies.get('cart', [])  # Example: replace with client-side cart management
            # Logic for adding product to cart
            return jsonify({'message': f'{product.name} added to cart'}), 200
        else:
            return jsonify({'message': 'Product not found'}), 404

    products = Product.query.all()
    return render_template('products.html', products=products)

# Cart Route
@app.route('/cart')
@jwt_required()
def cart():
    current_user = get_jwt_identity()
    # Logic for fetching and displaying cart details
    cart_items = []  # Replace with session/cart logic as needed
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total_amount=total_amount)

# Checkout Route
@app.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user = get_jwt_identity()
    employee_id = current_user['id']
    cart = request.cookies.get('cart', [])  # Example: replace with client-side cart management

    if not cart:
        return jsonify({'message': 'Cart is empty!'}), 400

    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    transaction = Transaction(employee_id=employee_id, total_amount=total_amount, transaction_date=datetime.now())
    db.session.add(transaction)
    db.session.commit()

    for item in cart:
        sale_item = SaleItem(transaction_id=transaction.id, product_id=item['id'], quantity=item['quantity'], price=item['price'])
        product = Product.query.get(item['id'])
        product.stock_quantity -= item['quantity']
        db.session.add(sale_item)

    db.session.commit()
    return jsonify({'message': 'Transaction completed successfully!', 'transaction_id': transaction.id}), 200

# Receipt Route
@app.route('/receipt/<int:transaction_id>')
@jwt_required()
def receipt(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404
    return render_template('receipt.html', transaction=transaction)

# Admin-Only Example Route
@app.route('/admin')
@jwt_required()
def admin_only():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    return jsonify({'message': 'Welcome, admin!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
