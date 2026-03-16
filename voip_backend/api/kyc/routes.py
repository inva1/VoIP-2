# voip_backend/api/kyc/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import datetime

from voip_backend.models.user_models import User
from voip_backend.models.kyc_models import KYCRecord
from voip_backend.schemas.kyc_schemas import KYCSubmitSchema, KYCRecordSchema, KYCReviewSchema
from voip_backend.extensions import db

kyc_bp = Blueprint('kyc_api', __name__)

kyc_submit_schema = KYCSubmitSchema()
kyc_record_schema = KYCRecordSchema()
kyc_records_schema = KYCRecordSchema(many=True)
kyc_review_schema = KYCReviewSchema()


@kyc_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_kyc():
    """Submit KYC verification documents."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Forbidden", "message": "User not found or inactive."}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = kyc_submit_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    # Check for existing pending KYC
    existing = KYCRecord.query.filter_by(
        user_id=current_user_id, verification_status='pending'
    ).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "You already have a pending KYC submission."}), 409

    try:
        record = KYCRecord(
            user_id=current_user_id,
            document_type=data['document_type'],
            document_number=data['document_number'],
            document_country=data['document_country'],
            document_front_url=data.get('document_front_url'),
            document_back_url=data.get('document_back_url'),
            selfie_url=data.get('selfie_url'),
            verification_status='pending'
        )
        db.session.add(record)
        db.session.commit()

        current_app.logger.info(f"KYC submitted for user {current_user_id}")
        return jsonify({
            "message": "KYC documents submitted successfully.",
            "kyc_record": kyc_record_schema.dump(record)
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"KYC submission error: {e}", exc_info=True)
        return jsonify({"error": "Server error", "message": "Could not submit KYC."}), 500


@kyc_bp.route('/status', methods=['GET'])
@jwt_required()
def get_kyc_status():
    """Get current user's KYC status."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "Not found", "message": "User not found."}), 404

    return jsonify({
        "kyc_status": user.kyc_status,
        "kyc_verified_at": user.kyc_verified_at.isoformat() if user.kyc_verified_at else None,
    }), 200


@kyc_bp.route('/records', methods=['GET'])
@jwt_required()
def get_kyc_records():
    """List current user's KYC records."""
    current_user_id = int(get_jwt_identity())
    records = KYCRecord.query.filter_by(user_id=current_user_id).order_by(
        KYCRecord.submitted_at.desc()
    ).all()
    return jsonify(kyc_records_schema.dump(records)), 200


@kyc_bp.route('/review/<int:record_id>', methods=['PUT'])
@jwt_required()
def review_kyc(record_id):
    """Admin: review/approve/reject a KYC submission."""
    current_user_id = int(get_jwt_identity())
    admin = User.query.get(current_user_id)
    if not admin or not admin.is_admin:
        return jsonify({"error": "Forbidden", "message": "Admin access required."}), 403

    record = KYCRecord.query.get(record_id)
    if not record:
        return jsonify({"error": "Not found", "message": "KYC record not found."}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = kyc_review_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    try:
        record.verification_status = data['verification_status']
        record.risk_score = data.get('risk_score')
        record.notes = data.get('notes')
        record.verified_by = current_user_id
        record.verified_at = datetime.datetime.utcnow()

        # Update user's KYC status if approved
        if data['verification_status'] == 'approved':
            user = User.query.get(record.user_id)
            if user:
                user.kyc_status = 'verified'
                user.kyc_verified_at = datetime.datetime.utcnow()
        elif data['verification_status'] == 'rejected':
            user = User.query.get(record.user_id)
            if user:
                user.kyc_status = 'rejected'

        db.session.commit()
        current_app.logger.info(f"KYC {record_id} reviewed by admin {current_user_id}: {data['verification_status']}")
        return jsonify({
            "message": f"KYC record {data['verification_status']}.",
            "kyc_record": kyc_record_schema.dump(record)
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"KYC review error: {e}", exc_info=True)
        return jsonify({"error": "Server error", "message": "Could not review KYC."}), 500
