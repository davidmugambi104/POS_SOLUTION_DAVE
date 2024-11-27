# seed.py
from model import db, Employee, Product
from app import app
from werkzeug.security import generate_password_hash

with app.app_context():
    # Seed employees
    employee1 = Employee(name="John", role="cashier", password_hash=generate_password_hash("password"))
    employee2 = Employee(name="Alice", role="manager", password_hash=generate_password_hash("securepass"))
    
    # Seed products
    product1 = Product(name="Apple", price=1.2, stock_quantity=100)
    product2 = Product(name="Orange", price=0.8, stock_quantity=150)

    db.session.add_all([employee1, employee2, product1, product2])
    db.session.commit()
