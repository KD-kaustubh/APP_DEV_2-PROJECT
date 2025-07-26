#api
from flask_restful import Api, Resource
from flask import current_app as app, jsonify, request
from .models import User, Role, ParkingLot, ParkingSpot, Reservation, Payment, ActivityReport
from application.database import db
from flask_security import auth_required, roles_required, current_user, hash_password, verify_and_update_password, login_user
from flask_security.utils import get_token
from datetime import datetime, timezone
from sqlalchemy.orm import subqueryload, joinedload
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = Api(prefix='/api')

def roles_list(roles):
    return [role.name for role in roles]


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = app.security.datastore.find_user(email=email)
        if user and verify_and_update_password(password, user):
            login_user(user)
            token = get_token(user)
            return {
                "response": {
                    "user": {
                        "email": user.email,
                        "roles": roles_list(user.roles),
                        "authentication_token": token
                    }
                }
            }, 200
        return {"message": "Invalid email or password"}, 401

api.add_resource(Login, '/loginn')

# --- Authentication & Dashboard Resources ---

class UserDashboard(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        return {
            'username': current_user.uname,
            'email': current_user.email,
            'roles': roles_list(current_user.roles)
        }, 200
    
class AdminDashboard(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        return {
            'message': 'Welcome to the Admin Dashboard!',
            'username': current_user.uname,
            'email': current_user.email,
            'roles': roles_list(current_user.roles)
        }, 200

class RegisterUser(Resource):
    def post(self):
        credentials = request.get_json()
        if not credentials or not all(k in credentials for k in ('email', 'username', 'password')):
            return {"message": "Missing email, username, or password"}, 400

        if app.security.datastore.find_user(email=credentials['email']):
            return {"message": "User with this email already exists"}, 409 # 409 Conflict is more specific

        try:
            app.security.datastore.create_user(
                email=credentials['email'],
                uname=credentials['username'],
                password=hash_password(credentials['password']),
                roles=['user']
            )
            db.session.commit()
            return {"message": "User registered successfully"}, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}")
            return {"message": "Could not create user due to an internal error."}, 500

api.add_resource(UserDashboard, '/user/dashboard')
api.add_resource(AdminDashboard, '/admin/dashboard')
api.add_resource(RegisterUser, '/register')


# --- Admin Parking Lot Management ---

# REFACTORED: To ensure creating a lot and its spots is an atomic operation.
class ParkingLotOps(Resource):
    @auth_required('token')
    @roles_required('admin')
    def post(self):
        data = request.get_json()
        try:
            lot = ParkingLot(
                prime_location_name=data['location'],
                price=data['price'],
                address=data['address'],
                pin_code=data['pin'],
                number_of_spots=data['spots']
            )
            db.session.add(lot)
            db.session.flush()  # Flushes to get the lot.id without committing

            for _ in range(data['spots']):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
            
            db.session.commit()
            return {"message": "Parking Lot created successfully", "lot_id": lot.id}, 201
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating parking lot: {e}")
            return {"message": "Could not create parking lot due to an internal error."}, 500

    # REFACTORED: To fix the N+1 query problem for better performance.
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        lots = ParkingLot.query.options(subqueryload(ParkingLot.spots)).all()
        result = []
        for lot in lots:
            # lot.spots is now pre-loaded, so this loop does not cause new DB queries.
            available = sum(1 for s in lot.spots if s.status == 'A')
            result.append({
                'id': lot.id,
                'location': lot.prime_location_name,
                'address': lot.address,
                'pin': lot.pin_code,
                'price': lot.price,
                'total_spots': lot.number_of_spots,
                'available_spots': available,
                'occupied_spots': lot.number_of_spots - available
            })
        return {'parking_lots': result}, 200

api.add_resource(ParkingLotOps, '/admin/parking-lots')


# REFACTORED: To ensure updates and deletions are atomic operations.
class ParkingLotDetailOps(Resource):
    @auth_required('token')
    @roles_required('admin')
    def put(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'message': 'Parking lot not found'}, 404

        data = request.get_json()
        try:
            lot.prime_location_name = data.get('location', lot.prime_location_name)
            lot.price = data.get('price', lot.price)
            lot.address = data.get('address', lot.address)
            lot.pin_code = data.get('pin', lot.pin_code)

            new_spots_count = data.get('spots')
            if new_spots_count is not None and isinstance(new_spots_count, int):
                diff = new_spots_count - lot.number_of_spots
                if diff > 0:
                    for _ in range(diff):
                        db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
                elif diff < 0:
                    removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(abs(diff)).all()
                    if len(removable_spots) < abs(diff):
                        return {'message': 'Cannot reduce spots. Not enough available spots to remove.'}, 400
                    for spot in removable_spots:
                        db.session.delete(spot)
                lot.number_of_spots = new_spots_count
            
            db.session.commit()
            return {'message': 'Parking lot updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating parking lot {lot_id}: {e}")
            return {"message": "Could not update parking lot due to an internal error."}, 500

    @auth_required('token')
    @roles_required('admin')
    def delete(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'message': 'Parking lot not found'}, 404

        if ParkingSpot.query.filter_by(lot_id=lot.id, status='O').first():
            return {'message': 'Cannot delete parking lot. Some spots are still occupied.'}, 400
        
        try:
            ParkingSpot.query.filter_by(lot_id=lot.id).delete()
            db.session.delete(lot)
            db.session.commit()
            return {'message': 'Parking lot and its spots deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting parking lot {lot_id}: {e}")
            return {"message": "Could not delete parking lot due to an internal error."}, 500

api.add_resource(ParkingLotDetailOps, '/admin/parking-lots/<int:lot_id>')


# --- User Reservation Management ---

# REFACTORED: To use atomic transactions and consistent UTC time.
class ReserveParking(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self):
        lot_id = request.get_json().get('lot_id')
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'message': 'Parking lot not found'}, 404

        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            return {'message': 'No available parking spots in this lot'}, 400

        try:
            available_spot.status = 'O'
            reservation = Reservation(
                spot_id=available_spot.id,
                user_id=current_user.id,
                parking_timestamp=datetime.now(timezone.utc), # Use timezone-aware UTC
                parking_cost=lot.price
            )
            db.session.add(reservation)
            db.session.commit()

            return {
                'message': 'Parking spot reserved successfully',
                'lot_id': lot.id,
                'spot_id': available_spot.id,
                'timestamp': reservation.parking_timestamp.isoformat(),
                'cost': lot.price
            }, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reserving parking for user {current_user.id}: {e}")
            return {"message": "Could not reserve spot due to an internal error."}, 500

api.add_resource(ReserveParking, '/user/reserve-parking')

# REFACTORED: To use atomic transactions and consistent UTC time.
class VacateParking(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self):
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            leaving_timestamp=None
        ).order_by(Reservation.parking_timestamp.desc()).first()

        if not active_reservation:
            return {'message': 'No active parking reservation found'}, 404
        
        spot = ParkingSpot.query.get(active_reservation.spot_id)
        if not spot:
             return {'message': f'Associated spot {active_reservation.spot_id} not found.'}, 404

        try:
            spot.status = 'A'
            active_reservation.leaving_timestamp = datetime.now(timezone.utc) # Use timezone-aware UTC
            db.session.commit()

            return {
                'message': 'Spot vacated successfully',
                'spot_id': spot.id,
                'vacated_at': active_reservation.leaving_timestamp.isoformat()
            }, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error vacating parking for user {current_user.id}: {e}")
            return {"message": "Could not vacate spot due to an internal error."}, 500

api.add_resource(VacateParking, '/user/vacate-parking')


# REFACTORED: To fix the N+1 query problem for better performance.
class UserReservations(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        # Use joinedload to fetch related spot in the same query.
        reservations = Reservation.query.options(
            joinedload(Reservation.spot)
        ).filter_by(user_id=current_user.id).order_by(Reservation.parking_timestamp.desc()).all()

        result = []
        for r in reservations:
            result.append({
                'reservation_id': r.id,
                'spot_id': r.spot_id,
                # r.spot is pre-loaded, so r.spot.lot_id causes no new query.
                'lot_id': r.spot.lot_id if r.spot else None,
                'parking_timestamp': r.parking_timestamp.isoformat(),
                'leaving_timestamp': r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
                'parking_cost': r.parking_cost,
                'status': 'Active' if not r.leaving_timestamp else 'Completed'
            })

        return {'reservations': result}, 200

api.add_resource(UserReservations, '/user/reservations')


