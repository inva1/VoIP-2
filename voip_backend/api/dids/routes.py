# voip_backend/api/dids/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import datetime

from voip_backend.models.user_models import User
from voip_backend.models.did_models import DIDNumber
from voip_backend.schemas.did_schemas import DIDNumberSchema, DIDAssignSchema
from voip_backend.extensions import db

dids_bp = Blueprint('dids_api', __name__)

did_schema = DIDNumberSchema()
dids_schema = DIDNumberSchema(many=True)
did_assign_schema = DIDAssignSchema()


@dids_bp.route('/available', methods=['GET'])
@jwt_required()
def list_available_dids():
    """List available DID numbers. Filter by country or type."""
    country = request.args.get('country')
    number_type = request.args.get('type')

    query = DIDNumber.query.filter_by(status='available')
    if country:
        query = query.filter_by(country_code=country.upper())
    if number_type:
        query = query.filter_by(number_type=number_type)

    dids = query.order_by(DIDNumber.monthly_cost).all()
    return jsonify(dids_schema.dump(dids)), 200


@dids_bp.route('/my-numbers', methods=['GET'])
@jwt_required()
def get_my_dids():
    """List DIDs assigned to the current user."""
    current_user_id = int(get_jwt_identity())
    dids = DIDNumber.query.filter_by(assigned_to=current_user_id).all()
    return jsonify(dids_schema.dump(dids)), 200


@dids_bp.route('/assign', methods=['POST'])
@jwt_required()
def assign_did():
    """Assign an available DID to the current user."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Forbidden", "message": "User not found or inactive."}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = did_assign_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    did = DIDNumber.query.get(data['did_id'])
    if not did:
        return jsonify({"error": "Not found", "message": "DID not found."}), 404
    if did.status != 'available':
        return jsonify({"error": "Conflict", "message": "DID is not available for assignment."}), 409

    try:
        did.assigned_to = current_user_id
        did.status = 'assigned'
        did.assigned_at = datetime.datetime.utcnow()
        db.session.commit()

        current_app.logger.info(f"DID {did.number} assigned to user {current_user_id}")
        return jsonify({
            "message": f"DID {did.number} assigned successfully.",
            "did": did_schema.dump(did)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": "Could not assign DID."}), 500


@dids_bp.route('/release/<int:did_id>', methods=['DELETE'])
@jwt_required()
def release_did(did_id):
    """Release a DID assigned to the current user."""
    current_user_id = int(get_jwt_identity())
    did = DIDNumber.query.get(did_id)
    if not did:
        return jsonify({"error": "Not found", "message": "DID not found."}), 404
    if did.assigned_to != current_user_id:
        return jsonify({"error": "Forbidden", "message": "This DID is not assigned to you."}), 403

    try:
        did.assigned_to = None
        did.status = 'available'
        did.assigned_at = None
        db.session.commit()

        current_app.logger.info(f"DID {did.number} released by user {current_user_id}")
        return jsonify({"message": f"DID {did.number} released successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": "Could not release DID."}), 500
