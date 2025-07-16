from flask import current_app as app, jsonify, request
from application.database import db
from flask_security import auth_required ,roles_required, current_user, hash_password


@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Parking Management System!"

#ADMIN
@app.route('/api/admin/dashboard')
@auth_required('token')  # Ensure only admin users can access this route
@roles_required('admin')  # Ensure only users with the 'admin' role can access this route
def admin_home():
    return jsonify({
        "message": "Welcome to the Admin Dashboard!"
    })

#USER
@app.route('/api/user/dashboard')
@auth_required('token')  # Ensure only authenticated users can access this route
@roles_required('user')  # Ensure only users with the 'user' role can access this route
def user_home():
    user= current_user
    return jsonify({
        "username": current_user.uname,
        "email": current_user.email,
        "password": current_user.password
    })

#create_user    
@app.route('/api/register', methods=['POST'])
def register_user():
    credentials = request.get_json()
    if not app.security.datastore.find_user(email=credentials['email']):
        app.security.datastore.create_user(email=credentials['email'] ,uname=['username'] , password=hash_password(credentials['password']), roles = ['user'])
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    return jsonify({"message": "User already exists"}), 400 