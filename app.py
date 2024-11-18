from flask import Flask, request, jsonify, session
from flask_cors import CORS
from database import init_db, db
from models import AdminUser, Customer, MenuItem, Order, Notification
import bcrypt
import os
from sqlalchemy.exc import SQLAlchemyError

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the database
init_db(app)

# User Registration for Customers
@app.route('/register_customer', methods=['POST'])
def register_customer():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        user_name = data.get('user_name')

        if not email or not password or not user_name:
            return jsonify({"message": "Missing required fields!"}), 400

        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "User already exists!"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = Customer(email=email, password=hashed_password.decode('utf-8'), user_name=user_name)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Customer registered successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error occurred!", "error": str(e)}), 500

# other endpoints
# User Registration for Admins
@app.route('/register_admin', methods=['POST'])
def register_admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"message": "Unauthorized"}), 401

    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        user_name = data.get('user_name')

        if not email or not password or not user_name:
            return jsonify({"message": "Missing required fields!"}), 400

        existing_user = db.query(AdminUser).filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "User  already exists!"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = AdminUser(email=email, password=hashed_password, user_name=user_name, role='admin')
        db.add(new_user)
        db.commit()

        return jsonify({"message": "Admin registered successfully!"}), 201
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"message": "Database error occurred!"}), 500

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    
    user = db.query(Customer).filter_by(email=email).first()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        session['user_id'] = user.id
        session['role'] = user.role  # Store user role in session
        return jsonify({"message": "Login successful!"})
    return jsonify({"message": "Invalid credentials!"}), 401

# User Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('role', None)  # Clear role from session
    return jsonify({"message": "Logged out successfully!"})

# Menu Management (Admin Panel)
@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    item_name = data['name']
    item_price = data['price']
    item_description = data['description']
    item_category = data['category']
    item_available = data['available']
    
    # Handle image upload
    item_image = request.files['image']
    item_image.save(f'path/to/save/{item_image.filename}')  # Save the image
    image_path = os.path.join('path/to/save', item_image.filename)

    db.add(MenuItem(name=item_name, price=item_price, description=item_description, category=item_category, image=item_image.filename, available=item_available))
    db.commit()
    
    return jsonify({"message": "Menu item added successfully!"})

# Fetch Menu
@app.route('/menu', methods=['GET'])
def get_menu():
    menu_items = db.query(MenuItem).all()
    menu_list = [{"id": item.id, "name": item.name, "price": item.price, "description": item.description, "category": item.category, "image": item.image, "available": item.available} for item in menu_items]
    return jsonify(menu_list)

# Order Management
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    user_id = session['user_id']
    item_id = data['item_id']
    quantity = data['quantity']
    
    # Fetch item price logic
    item = db.query(MenuItem).filter_by(id=item_id).first()
    if not item:
        return jsonify({"message": "Menu item not found!"}), 404

    total_price = item.price * quantity

    # Insert into orders table logic
    db.add(Order(user_id=user_id, item_id=item_id, quantity=quantity, total_price=total_price, status='pending'))
    db.commit()

    return jsonify({"message": "Order placed successfully!"})

@app.route('/notify', methods=['POST'])
def create_notification():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    user_id = data['user_id']
    message = data['message']

    notification = Notification(user_id=user_id, message=message)
    db.add(notification)
    db.commit()

    return jsonify({"message": "Notification created!"}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5000)
