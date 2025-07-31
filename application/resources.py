#api
from flask_restful import Api, Resource
from flask import current_app as app, jsonify, request
from .models import User, Role, ParkingLot, ParkingSpot, Reservation, Payment, ActivityReport
from application.database import db
from flask_security import auth_required, roles_required, current_user, hash_password, verify_and_update_password, login_user
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
from sqlalchemy.orm import subqueryload, joinedload
from sqlalchemy import func, extract
import logging
import math
from application import cache


cache=  app.cache

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


# --- Admin Parking Lot Management ---
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
            db.session.flush()  

            for _ in range(data['spots']):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
            
            db.session.commit()
            return {"message": "Parking Lot created successfully", "lot_id": lot.id}, 201
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating parking lot: {e}")
            return {"message": "Could not create parking lot due to an internal error."}, 500

    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=5)  
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

api.add_resource(ParkingLotOps, '/admin/parking-lots')

# --- Admin Parking Lot Detail Management ---
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


#User Reservation Management 
class ReserveParking(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self):
      
        data = request.get_json()
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')

        if not vehicle_number:
            return {'message': 'Vehicle number is required'}, 400

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
                vehicle_number=vehicle_number,
                parking_timestamp=datetime.now(IST),
                parking_cost=lot.price
            )
            db.session.add(reservation)
            db.session.commit()

            
            update_activity_report(
                user_id=current_user.id,
                dt=reservation.parking_timestamp,
                lot_id=reservation.spot.lot_id,
                add_reservation=True
            )

            return {
                'message': 'Parking spot reserved successfully',
                'lot_id': lot.id,
                'spot_id': available_spot.id,
                'vehicle_number': reservation.vehicle_number, 
                'timestamp': reservation.parking_timestamp.isoformat()
            }, 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reserving parking for user {current_user.id}: {e}")
            return {"message": "Could not reserve spot due to an internal error."}, 500

api.add_resource(ReserveParking, '/user/reserve-parking')


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

        if not spot.lot:
            return {'message': f'Associated parking lot for spot {spot.id} not found.'}, 404

        try:
            now = datetime.now(IST)
            if active_reservation.parking_timestamp.tzinfo is None:
                active_reservation.parking_timestamp = active_reservation.parking_timestamp.replace(tzinfo=IST)
            duration = now - active_reservation.parking_timestamp
            hours = duration.total_seconds() / 3600

           
            final_cost = max(1, math.ceil(hours)) * spot.lot.price

            
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
                'vehicle_number': r.vehicle_number,  
                'parking_timestamp': r.parking_timestamp.isoformat(),
                'release_timestamp': r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
                'parking_cost': r.parking_cost,
                'status': 'Active' if not r.leaving_timestamp else 'Completed',
                'paid': paid
            })

        return {'reservations': result}, 200

api.add_resource(UserReservations, '/user/reservations')


class UserLots(Resource):
    @auth_required('token')
    @roles_required('user')
    @cache.cached(timeout=5)  
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

        if Payment.query.filter_by(reservation_id=reservation_id).first():
            return {'message': 'This reservation has already been paid for.'}, 400
            
        try:
            new_payment = Payment(
                reservation_id=reservation.id,
                user_id=current_user.id,
                amount=reservation.parking_cost,
                status='Success' 
            )
            db.session.add(new_payment)
            db.session.commit()
            

            update_activity_report(
                user_id=current_user.id,
                dt=reservation.leaving_timestamp or reservation.parking_timestamp,
                lot_id=reservation.spot.lot_id,
                amount=reservation.parking_cost or 0,
                add_spent=True
            )

            return {'message': 'Payment successful!', 'payment_id': new_payment.id}, 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing payment for reservation {reservation_id}: {e}")
            return {"message": "Could not process payment due to an internal error."}, 500

# --- Report Viewing ---
class UserActivityAPI(Resource):
    @auth_required('token')
    @roles_required('user')
    @cache.cached(timeout=5)  # <-- .
    def get(self):
        reports = ActivityReport.query.filter_by(user_id=current_user.id).order_by(ActivityReport.month.desc()).all()
        result = []
        for r in reports:
            result.append({
                'month': r.month,
                'total_reservations': r.total_reservations,
                'total_spent': r.total_spent,
                'most_used_lot': r.most_used_lot.prime_location_name if r.most_used_lot else 'N/A'
            })
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


class AdminSpotDetails(Resource):
    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=5)  
    def get(self, lot_id):
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        result = []
        for spot in spots:
            spot_data = {
                'id': spot.id,
                'status': 'Available' if spot.status == 'A' else 'Occupied'
            }
            if spot.status == 'O':
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
    @cache.cached(timeout=5)  
    def get(self):
        total_spots = db.session.query(db.func.count(ParkingSpot.id)).scalar()
        occupied_spots = db.session.query(db.func.count(ParkingSpot.id)).filter(ParkingSpot.status == 'O').scalar()
        
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

api.add_resource(AdminSpotDetails, '/admin/parking-lots/<int:lot_id>/spots')
api.add_resource(AdminSummary, '/admin/summary')


class AdminRevenueSummary(Resource):
    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=5)  # <-- .
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


def update_activity_report(user_id, dt, lot_id=None, amount=0, add_reservation=False, add_spent=False):
    month_str = dt.strftime('%Y-%m')
    report = ActivityReport.query.filter_by(user_id=user_id, month=month_str).first()
    if not report:
        report = ActivityReport(user_id=user_id, month=month_str)
        db.session.add(report)
    if add_reservation:
        report.total_reservations = (report.total_reservations or 0) + 1
    if add_spent:
        report.total_spent = (report.total_spent or 0) + (amount or 0)
    if lot_id:
        report.most_used_lot_id = lot_id 
    report.last_updated = datetime.utcnow()
    db.session.commit()

# --- Admin User Activity Report ---
class AdminUserActivityAPI(Resource):
    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=5)  # <-- .
    def get(self, user_id):
        reports = ActivityReport.query.filter_by(user_id=user_id).order_by(ActivityReport.month.desc()).all()
        result = []
        for r in reports:
            result.append({
                'month': r.month,
                'total_reservations': r.total_reservations,
                'total_spent': r.total_spent,
                'most_used_lot': r.most_used_lot.prime_location_name if r.most_used_lot else 'N/A',
                'last_updated': r.last_updated.isoformat() if r.last_updated else None
            })
        return {'reports': result}, 200

api.add_resource(AdminUserActivityAPI, '/admin/user/<int:user_id>/activity')


class UserMonthlyLotSpending(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        results = (
            db.session.query(
                func.strftime('%Y-%m', Reservation.parking_timestamp).label('month'),
                ParkingLot.prime_location_name.label('lot_name'),
                func.sum(Reservation.parking_cost).label('amount_spent'),
                func.count(Reservation.id).label('reservations_count')
            )
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
            .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)
            .filter(
                Reservation.user_id == current_user.id,
                Reservation.parking_cost != None
            )
            .group_by('month', 'lot_name')
            .order_by('month')
            .all()
        )
        month_dict = {}
        for row in results:
            if row.month not in month_dict:
                month_dict[row.month] = {'lots': [], 'total_reservations': 0}
            month_dict[row.month]['lots'].append({
                'lot_name': row.lot_name,
                'amount_spent': float(row.amount_spent),
                'reservations_count': row.reservations_count
            })
            month_dict[row.month]['total_reservations'] += row.reservations_count
        response = []
        for month, data in month_dict.items():
            response.append({
                'month': month,
                'lots': data['lots'],
                'total_reservations': data['total_reservations']
            })
        return {'reports': response}, 200

api.add_resource(UserMonthlyLotSpending, '/user/reports-lotwise')