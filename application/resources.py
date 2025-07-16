#api
from flask_restful import Api, Resource, reqparse
from flask import current_app as app, jsonify, request
from .models import User, Role, ParkingLot, ParkingSpot, Reservation, Payment, ActivityReport
from application.database import db
from flask_security import auth_required, roles_required,roles_accepted, current_user, hash_password

api=Api(prefix='/api')

def roles_list(roles):
    role_list=[]
    for role in roles:
        role_list.append(role.name)
    return role_list


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
            
api.add_resource(UserDashboard, '/user/dashboard')
api.add_resource(AdminDashboard, '/admin/dashboard')

class RegisterUser(Resource):
    def post(self):
        credentials = request.get_json()
        if not app.security.datastore.find_user(email=credentials['email']):
            app.security.datastore.create_user(
                email=credentials['email'],
                uname=credentials['username'],
                password=hash_password(credentials['password']),
                roles=['user']
            )
            db.session.commit()
            return jsonify({"message": "User registered successfully"}), 201
        return jsonify({"message": "User already exists"}), 400
    
api.add_resource(RegisterUser, '/register')


class ParkingLotCreate(Resource):
    @auth_required('token')
    @roles_required('admin')
    def post(self):
        data = request.get_json()

        # 1. Create Parking Lot
        lot = ParkingLot(
            prime_location_name=data['location'],
            price=data['price'],
            address=data['address'],
            pin_code=data['pin'],
            number_of_spots=data['spots']
        )
        db.session.add(lot)
        db.session.commit()

        # 2. Create Parking Spots for the lot
        for _ in range(data['spots']):
            spot = ParkingSpot(lot_id=lot.id, status='A')  # 'A' for Available
            db.session.add(spot)
        db.session.commit()

        return {
            "message": "Parking Lot created with spots",
            "lot_id": lot.id,
            "total_spots": data['spots']
        }, 201

api.add_resource(ParkingLotCreate, '/admin/parking-lots')


class ParkingLotList(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        lots = ParkingLot.query.all()
        result = []

        for lot in lots:
            spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            available = sum(1 for s in spots if s.status == 'A')
            occupied = sum(1 for s in spots if s.status == 'O')

            result.append({
                'id': lot.id,
                'location': lot.prime_location_name,
                'address': lot.address,
                'pin': lot.pin_code,
                'price': lot.price,
                'total_spots': lot.number_of_spots,
                'available_spots': available,
                'occupied_spots': occupied
            })

        return {'parking_lots': result}, 200
api.add_resource(ParkingLotList, '/admin/parking-lots/list')

class ParkingLotUpdate(Resource):
    @auth_required('token')
    @roles_required('admin')
    def put(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'message': 'Parking lot not found'}, 404

        data = request.get_json()

        # Update basic info
        lot.prime_location_name = data.get('location', lot.prime_location_name)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin', lot.pin_code)

        # Handle spot changes
        new_spots = data.get('spots')
        if new_spots and isinstance(new_spots, int):
            diff = new_spots - lot.number_of_spots

            if diff > 0:
                # Add new spots
                for _ in range(diff):
                    new_spot = ParkingSpot(lot_id=lot.id, status='A')
                    db.session.add(new_spot)

            elif diff < 0:
                # Try to remove empty spots only
                removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(abs(diff)).all()
                if len(removable_spots) < abs(diff):
                    return {'message': 'Cannot reduce spots. Not enough available spots to remove.'}, 400
                for spot in removable_spots:
                    db.session.delete(spot)

            lot.number_of_spots = new_spots

        db.session.commit()
        return {'message': 'Parking lot updated successfully'}, 200
api.add_resource(ParkingLotUpdate, '/admin/parking-lots/<int:lot_id>')

class ParkingLotDelete(Resource):
    @auth_required('token')
    @roles_required('admin')
    def delete(self, lot_id):
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'message': 'Parking lot not found'}, 404

        # Check for occupied spots
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        if occupied_spots > 0:
            return {'message': 'Cannot delete parking lot. Some spots are still occupied.'}, 400

        # Delete all spots
        ParkingSpot.query.filter_by(lot_id=lot.id).delete()

        # Delete the lot
        db.session.delete(lot)
        db.session.commit()

        return {'message': 'Parking lot and its spots deleted successfully'}, 200
api.add_resource(ParkingLotDelete, '/admin/parking-lots/<int:lot_id>/delete')


#user reservation
from datetime import datetime

class ReserveParking(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self):
        data = request.get_json()
        lot_id = data.get('lot_id')

        # Check if lot exists
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'message': 'Parking lot not found'}, 404

        # Find first available spot in that lot
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            return {'message': 'No available parking spots in this lot'}, 400

        # Reserve the spot
        available_spot.status = 'O'  # Occupied
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=current_user.id,
            parking_timestamp=datetime.now(),
            parking_cost=lot.price
        )

        db.session.add(reservation)
        db.session.commit()

        return {
            'message': 'Parking spot reserved successfully',
            'lot_id': lot.id,
            'spot_id': available_spot.id,
            'timestamp': str(reservation.parking_timestamp),
            'cost': lot.price
        }, 201
api.add_resource(ReserveParking, '/user/reserve-parking')

from datetime import datetime

class VacateParking(Resource):
    @auth_required('token')
    @roles_required('user')
    def post(self):
        # Find the latest active reservation (no leaving time)
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            leaving_timestamp=None
        ).order_by(Reservation.parking_timestamp.desc()).first()

        if not active_reservation:
            return {'message': 'No active parking reservation found'}, 404

        # Update the spot to available
        spot = ParkingSpot.query.get(active_reservation.spot_id)
        spot.status = 'A'

        # Update leaving timestamp
        active_reservation.leaving_timestamp = datetime.now()

        db.session.commit()

        return {
            'message': 'Spot vacated successfully',
            'spot_id': spot.id,
            'vacated_at': str(active_reservation.leaving_timestamp)
        }, 200
api.add_resource(VacateParking, '/user/vacate-parking')

class UserReservations(Resource):
    @auth_required('token')
    @roles_required('user')
    def get(self):
        user_id = current_user.id
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()

        result = []
        for r in reservations:
            result.append({
                'reservation_id': r.id,
                'spot_id': r.spot_id,
                'lot_id': ParkingSpot.query.get(r.spot_id).lot_id,
                'parking_timestamp': str(r.parking_timestamp),
                'leaving_timestamp': str(r.leaving_timestamp) if r.leaving_timestamp else None,
                'parking_cost': r.parking_cost,
                'status': 'Active' if not r.leaving_timestamp else 'Completed'
            })

        return {'reservations': result}, 200
api.add_resource(UserReservations, '/user/reservations')

