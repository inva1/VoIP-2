# voip_backend/api/sms/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import datetime
import uuid

from voip_backend.models.user_models import User
from voip_backend.models.did_models import DIDNumber
from voip_backend.models.call_sms_models import SMSRecord
from voip_backend.models.subscription_models import UserSubscription
from voip_backend.schemas.call_sms_schemas import SMSRecordSchema, SendSMSSchema
from voip_backend.extensions import db

sms_bp = Blueprint('sms_api', __name__)

sms_schema = SMSRecordSchema()
sms_list_schema = SMSRecordSchema(many=True)
send_sms_schema = SendSMSSchema()


@sms_bp.route('/send', methods=['POST'])
@jwt_required()
def send_sms():
    """Send an SMS message."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Forbidden", "message": "User not found or inactive."}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = send_sms_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    # Get a DID for the from_number
    if data.get('from_did_id'):
        did = DIDNumber.query.get(data['from_did_id'])
        if not did or did.assigned_to != current_user_id:
            return jsonify({"error": "Forbidden", "message": "DID not assigned to you."}), 403
        from_number = did.number
    else:
        did = DIDNumber.query.filter_by(assigned_to=current_user_id, status='assigned').first()
        if not did:
            return jsonify({"error": "Precondition failed", "message": "No DID assigned. Assign a number first."}), 412
        from_number = did.number

    # Check subscription usage
    sub = UserSubscription.query.filter_by(user_id=current_user_id, status='active').first()
    if sub:
        sub.usage_messages += 1

    try:
        record = SMSRecord(
            user_id=current_user_id,
            message_id=f"sms-{uuid.uuid4().hex[:16]}",
            from_number=from_number,
            to_number=data['to_number'],
            message_text=data['message_text'],
            message_type='sms',
            direction='outbound',
            status='sent',
            sent_at=datetime.datetime.utcnow(),
        )
        db.session.add(record)
        db.session.commit()

        current_app.logger.info(f"SMS sent by user {current_user_id} to {data['to_number']}")
        return jsonify({
            "message": "SMS sent successfully.",
            "sms": sms_schema.dump(record)
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"SMS send error: {e}", exc_info=True)
        return jsonify({"error": "Server error", "message": "Could not send SMS."}), 500


@sms_bp.route('/history', methods=['GET'])
@jwt_required()
def sms_history():
    """List SMS records for the current user with pagination."""
    current_user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    direction = request.args.get('direction')

    query = SMSRecord.query.filter_by(user_id=current_user_id)
    if direction:
        query = query.filter_by(direction=direction)

    pagination = query.order_by(SMSRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "messages": sms_list_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    }), 200
