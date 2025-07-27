from flask import Blueprint, render_template, jsonify, request, current_app
from application.database import db
from flask_security import auth_required, roles_required, current_user, hash_password
from application.models import User, Role

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@main_bp.route('/api/home')
@auth_required('token')
@roles_required('user')
def user_home():
    user = current_user
    return jsonify({
        "message": "Welcome to the Vehicle Parking App",
        "user": {
            "email": user.email,
            "uname": user.uname,
            "roles": [role.name for role in user.roles]
        }
    })

@main_bp.route('/api/register', methods=['POST'])
def create_user():
    data = request.get_json()
    if not current_app.security.datastore.find_user(email=data.get('email')):
        current_app.security.datastore.create_user(
            email=data.get('email'),
            uname=data.get('uname'),
            password=hash_password(data.get('password')),
            roles=['user'])
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    return jsonify({"message": "User already exists"}), 400



