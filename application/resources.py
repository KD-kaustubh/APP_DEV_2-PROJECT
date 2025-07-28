#api
from flask_restful import Api, Resource
from flask import current_app as app, jsonify, request
from .models import User, Role, ParkingLot, ParkingSpot, Reservation, Payment, ActivityReport
from application.database import db
from flask_security import auth_required, roles_required, current_user, hash_password, verify_and_update_password, login_user
from datetime import datetime, timezone
from sqlalchemy.orm import subqueryload, joinedload
from sqlalchemy import func
import logging
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = Api(prefix='/api')

def roles_list(roles):
    return [role.name for role in roles]


class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return {"message": "Email and password are required"}, 400

            user = app.security.datastore.find_user(email=email)
            if user and verify_and_update_password(password, user):
                login_user(user)
                token = user.get_auth_token()
                return {
                    "response": {
                        "user": {
                            "email": user.email,
                            "uname": user.uname,  
                            "roles": roles_list(user.roles),
                            "authentication_token": token
                        }
                    }
                }, 200

            return {"message": "Invalid email or password"}, 401

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return {"message": "Internal server error"}, 500

api.add_resource(Login, '/login')

# # --- Authentication & Dashboard Resources ---

# class UserDashboard(Resource):
#     @auth_required('token')
#     @roles_required('user')
#     def get(self):
#         return {
#             'username': current_user.uname,
#             'email': current_user.email,
#             'roles': roles_list(current_user.roles)
#         }, 200
    
# class AdminDashboard(Resource):
#     @auth_required('token')
#     @roles_required('admin')
#     def get(self):
#         return {
#             'message': 'Welcome to the Admin Dashboard!',
#             'username': current_user.uname,
#             'email': current_user.email,
#             'roles': roles_list(current_user.roles)
#         }, 200

# class RegisterUser(Resource):
#     def post(self):
#         credentials = request.get_json()
#         if not credentials or not all(k in credentials for k in ('email', 'username', 'password')):
#             return {"message": "Missing email, username, or password"}, 400

#         if app.security.datastore.find_user(email=credentials['email']):
#             return {"message": "User with this email already exists"}, 409 # 409 Conflict is more specific

#         try:
#             app.security.datastore.create_user(
#                 email=credentials['email'],
#                 uname=credentials['username'],
#                 password=hash_password(credentials['password']),
#                 roles=['user']
#             )
#             db.session.commit()
#             return {"message": "User registered successfully"}, 201
#         except Exception as e:
#             db.session.rollback()
#             logger.error(f"Error creating user: {e}")
#             return {"message": "Could not create user due to an internal error."}, 500

# api.add_resource(UserDashboard, '/user/dashboard')
# api.add_resource(AdminDashboard, '/admin/dashboard')
# api.add_resource(RegisterUser, '/register')


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
                occupied_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
                if diff > 0:
                    for _ in range(diff):
                        db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
                elif diff < 0:
                    if new_spots_count < occupied_count:
                        return {"message": f"Cannot reduce spots below number of occupied spots ({occupied_count})."}, 400
                    removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(abs(diff)).all()
                    if len(removable_spots) < abs(diff):
                        return {'message': 'Cannot reduce spots. Not enough available spots to remove.'}, 400
                    for spot in removable_spots:
                        db.session.delete(spot)
                lot.number_of_spots = new_spots_count
            
            db.session.commit()
            return {"message": "Parking lot updated successfully."}, 200
        except Exception as e:
            logger.error(f"Error updating parking lot: {e}")
            db.session.rollback()
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
        # --- GET VEHICLE NUMBER FROM REQUEST ---
        data = request.get_json()
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')

        if not vehicle_number:
            return {'message': 'Vehicle number is required'}, 400
        # ----------------------------------------

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
                # --- ADD VEHICLE NUMBER HERE ---
                vehicle_number=vehicle_number,
                # -------------------------------
                parking_timestamp=datetime.now(timezone.utc),
                parking_cost=lot.price
            )
            db.session.add(reservation)
            db.session.commit()

            return {
                'message': 'Parking spot reserved successfully',
                'lot_id': lot.id,
                'spot_id': available_spot.id,
                'vehicle_number': reservation.vehicle_number, # Also return it in the response
                'timestamp': reservation.parking_timestamp.isoformat()
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
        # Find the active reservation for the current user
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            leaving_timestamp=None
        ).order_by(Reservation.parking_timestamp.desc()).first()

        if not active_reservation:
            return {'message': 'No active parking reservation found'}, 404
        
        spot = ParkingSpot.query.get(active_reservation.spot_id)
        if not spot:
            return {'message': f'Associated spot {active_reservation.spot_id} not found.'}, 404

        if not spot.lot:
            return {'message': f'Associated parking lot for spot {spot.id} not found.'}, 404

        try:
            now = datetime.now(timezone.utc)
            if active_reservation.parking_timestamp.tzinfo is None:
                active_reservation.parking_timestamp = active_reservation.parking_timestamp.replace(tzinfo=timezone.utc)
            duration = now - active_reservation.parking_timestamp
            hours = duration.total_seconds() / 3600

            # Always round up to the next hour, minimum 1 hour
            final_cost = max(1, math.ceil(hours)) * spot.lot.price

            # Update the records
            spot.status = 'A'
            active_reservation.leaving_timestamp = now
            active_reservation.parking_cost = final_cost
            db.session.commit()

            return {
                'message': 'Spot vacated successfully. Please complete payment.',
                'reservation_id': active_reservation.id,
                'final_cost': final_cost,
                'vacated_at': now.isoformat()
            }, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error vacating parking for user {current_user.id}: {e}", exc_info=True)
            return {"message": "Could not vacate spot due to an internal error."}, 500

api.add_resource(VacateParking, '/user/vacate-parking')


# REFACTORED: To fix the N+1 query problem for better performance.
class UserReservations(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        reservations = Reservation.query.options(
            joinedload(Reservation.spot).joinedload(ParkingSpot.lot)
        ).filter_by(user_id=current_user.id).order_by(Reservation.parking_timestamp.desc()).all()

        result = []
        for r in reservations:
            paid = Payment.query.filter_by(reservation_id=r.id).first() is not None
            result.append({
                'reservation_id': r.id,
                'spot_id': r.spot_id,
                'lot_id': r.spot.lot_id if r.spot else None,
                'lot_location': r.spot.lot.prime_location_name if r.spot and r.spot.lot else None,  # <-- Add this
                'vehicle_number': r.vehicle_number,  # <-- Add this
                'parking_timestamp': r.parking_timestamp.isoformat(),
                'release_timestamp': r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
                'parking_cost': r.parking_cost,
                'status': 'Active' if not r.leaving_timestamp else 'Completed',
                'paid': paid
            })

        return {'reservations': result}, 200

api.add_resource(UserReservations, '/user/reservations')


# REFACTORED: To fix the N+1 query problem for better performance.
class UserLots(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        lots = ParkingLot.query.options(subqueryload(ParkingLot.spots)).all()
        result = []
        for lot in lots:
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

api.add_resource(UserLots, '/user/parking-lots')


# --- Payment Processing ---
class ProcessPayment(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self, reservation_id):
        reservation = Reservation.query.filter_by(id=reservation_id, user_id=current_user.id).first()

        if not reservation:
            return {'message': 'Reservation not found or does not belong to user'}, 404
        
        if reservation.leaving_timestamp is None:
            return {'message': 'Cannot pay for a reservation that is still active.'}, 400

        # Check if already paid
        if Payment.query.filter_by(reservation_id=reservation_id).first():
            return {'message': 'This reservation has already been paid for.'}, 400
            
        try:
            # Create a fake successful payment record
            new_payment = Payment(
                reservation_id=reservation.id,
                user_id=current_user.id,
                amount=reservation.parking_cost,
                status='Success' 
            )
            db.session.add(new_payment)
            db.session.commit()
            
            return {'message': 'Payment successful!', 'payment_id': new_payment.id}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing payment for reservation {reservation_id}: {e}")
            return {"message": "Could not process payment due to an internal error."}, 500

# --- Report Viewing ---
class UserActivityAPI(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        # Group by year and month, count reservations, sum spent
        stats = db.session.query(
            func.strftime('%Y-%m', Reservation.parking_timestamp).label('month'),
            func.count(Reservation.id).label('total_reservations'),
            func.sum(Reservation.parking_cost).label('total_spent')
        ).filter(
            Reservation.user_id == current_user.id
        ).group_by(
            func.strftime('%Y-%m', Reservation.parking_timestamp)
        ).order_by(
            func.strftime('%Y-%m', Reservation.parking_timestamp).desc()
        ).all()

        result = []
        for row in stats:
            result.append({
                'month': row.month,
                'total_reservations': row.total_reservations,
                'total_spent': float(row.total_spent or 0),
                'most_used_lot': 'N/A'  # Optional: add logic if you want
            })

        # If no data, return a dummy row for UI
        if not result:
            result = [{'month': datetime.now().strftime('%Y-%m'), 'total_reservations': 0, 'total_spent': 0.0, 'most_used_lot': 'N/A'}]

        return {'reports': result}, 200

api.add_resource(ProcessPayment, '/user/payment/<int:reservation_id>')
api.add_resource(UserActivityAPI, '/user/reports')


# --- Admin User Management ---
class AdminUsers(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        users = [u for u in User.query.all() if any(role.name == 'user' for role in u.roles)]
        result = []
        for u in users:
            # Find active reservation (if any)
            active_res = Reservation.query.filter_by(user_id=u.id, leaving_timestamp=None).first()
            result.append({
                'id': u.id,
                'uname': u.uname,
                'email': u.email,
                'current_spot': active_res.spot_id if active_res else None,
                'status': 'Active' if active_res else 'Idle'
            })
        return {'users': result}, 200

api.add_resource(AdminUsers, '/admin/users')

# In application/resources.py
# Add these new resources anywhere before the api.add_resource calls

class AdminSpotDetails(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self, lot_id):
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        result = []
        for spot in spots:
            spot_data = {
                'id': spot.id,
                'status': 'Available' if spot.status == 'A' else 'Occupied'
            }
            if spot.status == 'O':
                # Find the active reservation for this spot
                reservation = Reservation.query.filter_by(
                    spot_id=spot.id, 
                    leaving_timestamp=None
                ).first()
                if reservation:
                    spot_data['vehicle_number'] = reservation.vehicle_number
                    spot_data['user_email'] = reservation.user.email
                    spot_data['parked_since'] = reservation.parking_timestamp.isoformat()
            result.append(spot_data)
        return {'spots': result}, 200

class AdminSummary(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        total_spots = db.session.query(db.func.count(ParkingSpot.id)).scalar()
        occupied_spots = db.session.query(db.func.count(ParkingSpot.id)).filter(ParkingSpot.status == 'O').scalar()
        
        # Data for lots breakdown chart
        lots = ParkingLot.query.options(subqueryload(ParkingLot.spots)).all()
        lots_data = []
        for lot in lots:
            available = sum(1 for s in lot.spots if s.status == 'A')
            lots_data.append({
                'name': lot.prime_location_name,
                'occupied': lot.number_of_spots - available,
                'available': available
            })

        return {
            'overall_occupancy': {
                'total': total_spots,
                'occupied': occupied_spots,
                'available': total_spots - occupied_spots
            },
            'lots_breakdown': lots_data
        }, 200

# Now, register these new resources at the end of your file
api.add_resource(AdminSpotDetails, '/admin/parking-lots/<int:lot_id>/spots')
api.add_resource(AdminSummary, '/admin/summary')


class AdminRevenueSummary(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        lots = ParkingLot.query.all()
        result = []
        for lot in lots:
            revenue = db.session.query(db.func.sum(Reservation.parking_cost)).filter(
                Reservation.spot_id.in_([s.id for s in lot.spots]),
                Reservation.parking_cost != None
            ).scalar() or 0
            result.append({
                'name': lot.prime_location_name,
                'revenue': float(revenue)
            })
        return {'lots': result}, 200

api.add_resource(AdminRevenueSummary, '/admin/revenue-summary')