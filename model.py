# model.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy(metadata=MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}))

# Employee Table
class Employee(db.Model):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., 'cashier', 'manager'
    password_hash = Column(String, nullable=False)

    # Add this relationship to fix the error
    transactions = relationship('Transaction', back_populates='employee')

    def __repr__(self):
        return f"<Employee {self.name}>"


# Product Table
class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=5)

    def __repr__(self):
        return f"<Product {self.name} - {self.stock_quantity}>"

# Transaction Table
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    total_amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime)

    employee = relationship('Employee', back_populates='transactions')
    sale_items = relationship('SaleItem', back_populates='transaction')

    def __repr__(self):
        return f"<Transaction {self.id} - {self.total_amount}>"

# SaleItem Table
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
