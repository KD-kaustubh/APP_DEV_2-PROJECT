from .database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime, timezone

class User(db.Model,UserMixin):
    __tablename__ = 'user'
    #req for flask security
    id=db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    uname = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)

    roles= db.relationship('Role', backref = 'bearer', secondary='users_roles')
    reservations = db.relationship('Reservation', backref='user', cascade="all, delete-orphan")
    

class Role(db.Model,RoleMixin):
    __tablename__ = 'role'
    #req for flask security
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

#many to many (1-1) relationship becoz of flask sequrity
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    #req for flask security
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)


class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    
    spots = db.relationship('ParkingSpot', backref='lot', cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # 'A' = Available, 'O' = Occupied

    reservations = db.relationship('Reservation', backref='spot', cascade="all, delete-orphan")

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)

    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)
    remarks = db.Column(db.Text, nullable=True)

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')  
    payment_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reservation = db.relationship('Reservation', backref='payment')
    user = db.relationship('User', backref='payments')


class ActivityReport(db.Model):
    __tablename__ = 'activity_report'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)  # e.g., "2025-04"
    total_reservations = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    most_used_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=True)

    most_used_lot = db.relationship('ParkingLot', backref='reports')
