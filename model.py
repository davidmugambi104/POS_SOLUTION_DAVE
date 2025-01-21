from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(metadata=MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}))
# Employee Table with password hashing
class Employee(db.Model):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., 'cashier', 'manager'
    password_hash = Column(String, nullable=False)

    # Relationship with transactions
    transactions = relationship(
        'Transaction',
        back_populates='employee',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Employee {self.name}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Product Table with category and stock management
class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # Added category

    category = relationship('Category', back_populates='products')

    def __repr__(self):
        return f"<Product {self.name} - {self.stock_quantity}>"

    # Validate that stock levels do not go negative
    @validates('stock_quantity')
    def validate_stock_quantity(self, key, value):
        if value < 0:
            raise ValueError("Stock quantity cannot be negative.")
        return value

# Transaction Table with history tracking
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    total_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime)
    discount = Column(Float, default=0.0)  # Discount on the transaction

    employee = relationship('Employee', back_populates='transactions')
    sale_items = relationship(
        'SaleItem',
        back_populates='transaction',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Transaction {self.id} - {self.total_amount}>"

# SaleItem Table with price capture at sale
class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    transaction = relationship('Transaction', back_populates='sale_items')
    product = relationship('Product')

    def __repr__(self):
        return f"<SaleItem {self.product.name} - {self.quantity}>"

# Category Table for product organization
class Category(db.Model):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    # Relationship with products
    products = relationship(
        'Product',
        back_populates='category',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Category {self.name}>"

# InventoryTransaction Table to manage stock additions/removals
class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    change_quantity = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'add' or 'remove'
    reason = Column(String, nullable=True)
    timestamp = Column(DateTime, default=db.func.current_timestamp())

    product = relationship('Product')

    def __repr__(self):
        return f"<InventoryTransaction {self.id} - {self.product.name} - {self.transaction_type}>"

    # Validation to ensure that a removal does not set stock below 0
    @validates('change_quantity')
    def validate_change_quantity(self, key, value):
        if self.transaction_type == 'remove' and self.product.stock_quantity - value < 0:
            raise ValueError("Insufficient stock to remove.")
        return value
