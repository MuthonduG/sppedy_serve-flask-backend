from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

# Create an explicit Base
Base = declarative_base()

def init_db(app: Flask):
    """Initializes the database."""
    app.config.from_object('config.Config')
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()  # Create tables if they don't exist
            print("Database initialized successfully!")
        except SQLAlchemyError as e:
            print(f"Error initializing database: {e}")
