# seed.py
from model import db, Employee, Product, Category
from app import app
from werkzeug.security import generate_password_hash

#WITH-APP
with app.app_context():
    # Ensure that the database tables exist before seeding
    db.create_all()

    # Seed categories (add if needed)
    category1 = Category(name="Fruits")
    category2 = Category(name="Vegetables")

    # Seed employees
    employee1 = Employee(name="John", role="cashier", password_hash=generate_password_hash("password"))
    employee2 = Employee(name="Alice", role="manager", password_hash=generate_password_hash("securepass"))

    # Seed products with category relationships
    product1 = Product(name="Apple", price=1.2, stock_quantity=100, category=category1)
    product2 = Product(name="Orange", price=0.8, stock_quantity=150, category=category1)
    product3 = Product(name="Carrot", price=0.5, stock_quantity=200, category=category2)

    # Add all seed data to the session
    db.session.add_all([category1, category2, employee1, employee2, product1, product2, product3])
    db.session.commit()

    print("Database seeded successfully!")
