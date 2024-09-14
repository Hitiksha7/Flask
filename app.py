from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import traceback
import re


######################### Setup #########################

# Initialize app
app = Flask(__name__)


# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:001478@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)


######################### Model & Schema #########################

# User Class/Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

######################### APIs #########################
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_phone(phone):
    phone_regex = r'^\d{10,15}$'
    return re.match(phone_regex, phone) is not None

# Create a user
@app.route('/user/create', methods=['POST'])
def create_user():
    try:
        user_dict = {
            'firstname': request.json['firstname'],
            'lastname': request.json['lastname'],
            'email': request.json['email'],
            'password': request.json['password'],
            'address': request.json['address'],
            'phone': request.json['phone']
            }
        # Email validation
        if not is_valid_email(user_dict['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Phone number validation
        if not is_valid_phone(user_dict['phone']):
            return jsonify({'error': 'Invalid phone number format'}), 400

        new_user = User(**user_dict)
        db.session.add(new_user)
        db.session.commit()
        user_dict['id'] = new_user.id
        return jsonify(user_dict), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# Get all users
@app.route('/user/all', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    user_list = []
    for user in all_users:
        user_list.append({
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'address': user.address,
            'phone': user.phone
        })
    return jsonify(user_list)

# Get single user
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'error': f'No user found with the id {id}'}), 404
    user_dict = {
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email,
        'address': user.address,
        'phone': user.phone
    }
    return jsonify(user_dict)

# Update a user
@app.route('/user/update/<id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'error': f'No user found with the id {id}'}), 404

        user.firstname = request.json['firstname']
        user.lastname = request.json['lastname']
        user.email = request.json['email']
        user.password = request.json['password']
        user.address = request.json['address']
        user.phone = request.json['phone']
        db.session.commit()

        user_dict = {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'password': user.password,
            'address': user.address,
            'phone': user.phone
        }
        return jsonify(user_dict)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

# Delete a user
@app.route('/user/delete/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': f'No user found with the id {id}'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {id} deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
