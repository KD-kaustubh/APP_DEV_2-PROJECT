from flask import current_app as app, jsonify, request, render_template
from application.database import db
from flask_security import auth_required ,roles_required, current_user, hash_password


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

