from flask import current_app as app, jsonify, request, render_template
from application.database import db
from flask_security import auth_required ,roles_required, current_user, hash_password
from application.models import User, Role


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

#ADMIN
@app.route('/admin/dashboard')
@auth_required('token')  # Ensure only admin users can access this route
@roles_required('admin')  # Ensure only users with the 'admin' role can access this route
def admin_home():
    return render_template('admin_dashboard.html')

#USER
@app.route('/user/dashboard')
@auth_required('token')  # Ensure only authenticated users can access this route
@roles_required('user')  # Ensure only users with the 'user' role can access this route
def user_home():
    user= current_user
    return render_template('user_dashboard.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    hashed_password = hash_password(password)
    new_user = User(email=email, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.verify_password(password):
        # Generate a token for the user
        token = user.get_auth_token()
        return jsonify({"token": token}), 200
    
    return jsonify({"message": "Invalid email or password"}), 401

