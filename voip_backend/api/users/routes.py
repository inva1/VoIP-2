# voip_backend/api/users/routes.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from voip_backend.models.user_models import User
from voip_backend.schemas.user_schemas import UserSchema, UserUpdateSchema
from voip_backend.extensions import db

users_bp = Blueprint('users_api', __name__)

user_schema = UserSchema()
user_update_schema = UserUpdateSchema()

@users_bp.route('/me', methods=['GET'])
@jwt_required() # Requires a valid access token
def get_current_user_profile():
    """
    Get the profile of the currently authenticated user.
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        current_app.logger.warning(f"User profile request for non-existent user ID: {current_user_id}")
        return jsonify({"error": "Not found", "message": "User not found."}), 404

    if not user.is_active:
        current_app.logger.warning(f"User profile request for inactive user ID: {current_user_id}")
        return jsonify({"error": "Forbidden", "message": "User account is inactive."}), 403

    current_app.logger.info(f"User profile retrieved for user ID: {current_user_id}")
    return jsonify(user_schema.dump(user)), 200


@users_bp.route('/me', methods=['PUT'])
@jwt_required() # Requires a valid access token
def update_current_user_profile():
    """
    Update the profile of the currently authenticated user.
    Accepts JSON payload with fields to update (e.g., first_name, last_name).
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        current_app.logger.warning(f"User profile update attempt for non-existent user ID: {current_user_id}")
        return jsonify({"error": "Not found", "message": "User not found."}), 404

    if not user.is_active:
        current_app.logger.warning(f"User profile update attempt for inactive user ID: {current_user_id}")
        return jsonify({"error": "Forbidden", "message": "User account is inactive."}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        # Validate input data using the update schema
        # partial=True allows for partial updates (not all fields required)
        data_to_update = user_update_schema.load(json_data, partial=True)
    except ValidationError as err:
        current_app.logger.warning(f"User profile update validation error for user ID {current_user_id}: {err.messages}")
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    if not data_to_update:
        return jsonify({"message": "No updatable fields provided.", "user": user_schema.dump(user)}), 200

    try:
        # Update user fields if they are provided in the validated data
        if 'first_name' in data_to_update:
            user.first_name = data_to_update['first_name']
        if 'last_name' in data_to_update:
            user.last_name = data_to_update['last_name']
        if 'phone_number' in data_to_update:
            user.phone_number = data_to_update['phone_number']
        if 'country_code' in data_to_update:
            user.country_code = data_to_update['country_code']

        # Note: Email and username changes are typically more complex (e.g., requiring verification)
        # and are not included in this simple profile update. Password change should be a separate endpoint.

        db.session.commit()
        current_app.logger.info(f"User profile updated for user ID: {current_user_id}. Fields updated: {list(data_to_update.keys())}")
        return jsonify({"message": "Profile updated successfully.", "user": user_schema.dump(user)}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile for user ID {current_user_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Server error", "messages": "Could not update your profile."}), 500

# To use this blueprint, it needs to be registered in the main app factory (create_app in run.py)
# from voip_backend.api.users.routes import users_bp
# app.register_blueprint(users_bp, url_prefix='/api/users')
