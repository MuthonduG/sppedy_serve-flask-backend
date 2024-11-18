from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import db

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    phone_number = Column(String)
    created_at = Column(DateTime, default=func.now())

class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    phone_number = Column(String)
    notifications = relationship('Notification', back_populates='customer', cascade='all, delete-orphan')
    created_at = Column(DateTime, default=func.now())

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String, default='KES', nullable=False)
    image_path = Column(String)
    created_at = Column(DateTime, default=func.now())

class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default='Pending')
    created_at = Column(DateTime, default=func.now())

    customer = relationship('Customer')
    menu_item = relationship('MenuItem')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    customer = relationship('Customer', back_populates='notifications')
