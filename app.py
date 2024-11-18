from flask import Flask, request, jsonify, session
from flask_cors import CORS
from database import init_db, db
from models import AdminUser, Customer, MenuItem, Order, Notification
import bcrypt

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize the database
init_db(app)

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



if __name__ == '__main__':
    app.run(debug=True, port=5000)
