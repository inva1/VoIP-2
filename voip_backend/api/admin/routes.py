# voip_backend/api/admin/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from functools import wraps

from voip_backend.models.user_models import User
from voip_backend.models.kyc_models import KYCRecord
from voip_backend.models.subscription_models import SubscriptionPlan, UserSubscription
from voip_backend.models.did_models import DIDNumber
from voip_backend.models.call_sms_models import CallRecord, SMSRecord
from voip_backend.schemas.user_schemas import UserSchema
from voip_backend.schemas.subscription_schemas import SubscriptionPlanSchema, CreatePlanSchema
from voip_backend.extensions import db

admin_bp = Blueprint('admin_api', __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
plan_schema = SubscriptionPlanSchema()
create_plan_schema = CreatePlanSchema()


def admin_required(fn):
    """Decorator to enforce admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"error": "Forbidden", "message": "Admin access required."}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users with search and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')
    status = request.args.get('status')  # active, inactive

    query = User.query
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                User.username.ilike(search_filter),
                User.email.ilike(search_filter),
                User.first_name.ilike(search_filter),
                User.last_name.ilike(search_filter),
            )
        )
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        "users": users_schema.dump(pagination.items),
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages,
    }), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Activate or deactivate a user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not found", "message": "User not found."}), 404

    json_data = request.get_json()
    if not json_data or 'is_active' not in json_data:
        return jsonify({"error": "Invalid input", "messages": "is_active field required"}), 400

    try:
        user.is_active = bool(json_data['is_active'])
        db.session.commit()
        action = "activated" if user.is_active else "deactivated"
        current_app.logger.info(f"Admin {get_jwt_identity()} {action} user {user_id}")
        return jsonify({"message": f"User {action}.", "user": user_schema.dump(user)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": "Could not update user."}), 500


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def system_stats():
    """Get system statistics dashboard data."""
    return jsonify({
        "total_users": User.query.count(),
        "active_users": User.query.filter_by(is_active=True).count(),
        "pending_kyc": KYCRecord.query.filter_by(verification_status='pending').count(),
        "active_subscriptions": UserSubscription.query.filter_by(status='active').count(),
        "total_dids": DIDNumber.query.count(),
        "assigned_dids": DIDNumber.query.filter_by(status='assigned').count(),
        "available_dids": DIDNumber.query.filter_by(status='available').count(),
        "total_calls": CallRecord.query.count(),
        "total_sms": SMSRecord.query.count(),
        "active_plans": SubscriptionPlan.query.filter_by(is_active=True).count(),
    }), 200


@admin_bp.route('/plans', methods=['POST'])
@admin_required
def create_plan():
    """Create a new subscription plan."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = create_plan_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    if SubscriptionPlan.query.filter_by(plan_code=data['plan_code']).first():
        return jsonify({"error": "Conflict", "messages": {"plan_code": ["Plan code already exists."]}}), 409

    try:
        plan = SubscriptionPlan(**data)
        db.session.add(plan)
        db.session.commit()

        current_app.logger.info(f"Plan {plan.plan_code} created by admin {get_jwt_identity()}")
        return jsonify({"message": "Plan created.", "plan": plan_schema.dump(plan)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": "Could not create plan."}), 500


@admin_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@admin_required
def update_plan(plan_id):
    """Update a subscription plan."""
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({"error": "Not found", "message": "Plan not found."}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No data provided"}), 400

    try:
        for field in ['plan_name', 'description', 'target_country', 'monthly_fee',
                       'included_minutes', 'included_messages', 'overage_rate_voice',
                       'overage_rate_sms', 'is_active']:
            if field in json_data:
                setattr(plan, field, json_data[field])

        db.session.commit()
        current_app.logger.info(f"Plan {plan.plan_code} updated by admin {get_jwt_identity()}")
        return jsonify({"message": "Plan updated.", "plan": plan_schema.dump(plan)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": "Could not update plan."}), 500
