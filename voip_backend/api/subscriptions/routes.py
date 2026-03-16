# voip_backend/api/subscriptions/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from voip_backend.models.user_models import User
from voip_backend.models.subscription_models import SubscriptionPlan, UserSubscription
from voip_backend.schemas.subscription_schemas import (
    SubscriptionPlanSchema, SubscribeSchema, UserSubscriptionSchema
)
from voip_backend.extensions import db

subscriptions_bp = Blueprint('subscriptions_api', __name__)

plan_schema = SubscriptionPlanSchema()
plans_schema = SubscriptionPlanSchema(many=True)
subscribe_schema = SubscribeSchema()
user_sub_schema = UserSubscriptionSchema()
user_subs_schema = UserSubscriptionSchema(many=True)


@subscriptions_bp.route('/plans', methods=['GET'])
def list_plans():
    """List available subscription plans. Optionally filter by country."""
    country = request.args.get('country')
    query = SubscriptionPlan.query.filter_by(is_active=True)
    if country:
        query = query.filter_by(target_country=country.upper())
    plans = query.order_by(SubscriptionPlan.monthly_fee).all()
    return jsonify(plans_schema.dump(plans)), 200


@subscriptions_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    """Subscribe to a plan."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Forbidden", "message": "User not found or inactive."}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = subscribe_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    plan = SubscriptionPlan.query.get(data['plan_id'])
    if not plan or not plan.is_active:
        return jsonify({"error": "Not found", "message": "Plan not found or inactive."}), 404

    # Check for existing active subscription
    existing = UserSubscription.query.filter_by(
        user_id=current_user_id, status='active'
    ).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "You already have an active subscription. Cancel it first."}), 409

    try:
        subscription = UserSubscription(
            user_id=current_user_id,
            plan_id=plan.id,
            status='active'
        )
        db.session.add(subscription)
        db.session.commit()

        current_app.logger.info(f"User {current_user_id} subscribed to plan {plan.plan_code}")
        return jsonify({
            "message": "Subscription activated.",
            "subscription": user_sub_schema.dump(subscription)
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Subscribe error: {e}", exc_info=True)
        return jsonify({"error": "Server error", "message": "Could not subscribe."}), 500


@subscriptions_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get current user's active subscription with usage."""
    current_user_id = int(get_jwt_identity())
    sub = UserSubscription.query.filter_by(
        user_id=current_user_id, status='active'
    ).first()
    if not sub:
        return jsonify({"message": "No active subscription."}), 200

    return jsonify(user_sub_schema.dump(sub)), 200


@subscriptions_bp.route('/cancel', methods=['PUT'])
@jwt_required()
def cancel_subscription():
    """Cancel the current user's active subscription."""
    current_user_id = int(get_jwt_identity())
    sub = UserSubscription.query.filter_by(
        user_id=current_user_id, status='active'
    ).first()
    if not sub:
        return jsonify({"error": "Not found", "message": "No active subscription to cancel."}), 404

    try:
        sub.status = 'cancelled'
        db.session.commit()
        current_app.logger.info(f"User {current_user_id} cancelled subscription {sub.id}")
        return jsonify({"message": "Subscription cancelled.", "subscription": user_sub_schema.dump(sub)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Server error", "message": "Could not cancel subscription."}), 500


@subscriptions_bp.route('/usage', methods=['GET'])
@jwt_required()
def get_usage():
    """Get usage details for the current subscription."""
    current_user_id = int(get_jwt_identity())
    sub = UserSubscription.query.filter_by(
        user_id=current_user_id, status='active'
    ).first()
    if not sub:
        return jsonify({"message": "No active subscription.", "usage": None}), 200

    plan = sub.plan
    return jsonify({
        "plan": plan_schema.dump(plan),
        "usage_minutes": sub.usage_minutes,
        "usage_messages": sub.usage_messages,
        "included_minutes": plan.included_minutes,
        "included_messages": plan.included_messages,
        "remaining_minutes": max(0, plan.included_minutes - sub.usage_minutes),
        "remaining_messages": max(0, plan.included_messages - sub.usage_messages),
    }), 200
