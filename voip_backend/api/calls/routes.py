# voip_backend/api/calls/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from voip_backend.models.call_sms_models import CallRecord
from voip_backend.schemas.call_sms_schemas import CallRecordSchema

calls_bp = Blueprint('calls_api', __name__)

call_schema = CallRecordSchema()
calls_schema = CallRecordSchema(many=True)


@calls_bp.route('/history', methods=['GET'])
@jwt_required()
def call_history():
    """List call records for the current user with pagination."""
    current_user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    direction = request.args.get('direction')  # inbound, outbound

    query = CallRecord.query.filter_by(user_id=current_user_id)
    if direction:
        query = query.filter_by(call_direction=direction)

    pagination = query.order_by(CallRecord.start_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "calls": calls_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    }), 200


@calls_bp.route('/<int:call_id>', methods=['GET'])
@jwt_required()
def get_call_detail(call_id):
    """Get a specific call record."""
    current_user_id = int(get_jwt_identity())
    record = CallRecord.query.get(call_id)
    if not record:
        return jsonify({"error": "Not found", "message": "Call record not found."}), 404
    if record.user_id != current_user_id:
        return jsonify({"error": "Forbidden", "message": "Access denied."}), 403

    return jsonify(call_schema.dump(record)), 200
