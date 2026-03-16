# voip_backend/api/auth/routes.py

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import datetime

from voip_backend.models.user_models import User
from voip_backend.schemas.user_schemas import UserRegistrationSchema, UserLoginSchema, UserSchema
from voip_backend.extensions import db, bcrypt

auth_bp = Blueprint('auth_api', __name__)

user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema()


@auth_bp.route('/register', methods=['POST'])
def register_user():
    """User registration endpoint."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = user_registration_schema.load(json_data)
    except ValidationError as err:
        current_app.logger.warning(f"Registration validation error: {err.messages}")
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Conflict", "messages": {"username": ["Username already exists."]}}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Conflict", "messages": {"email": ["Email already registered."]}}), 409

    try:
        new_user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            country_code=data.get('country_code')
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        current_app.logger.info(f"User registered successfully: {new_user.username}")
        return jsonify({
            "message": "User registered successfully.",
            "user": user_schema.dump(new_user)
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during registration: {str(e)}", exc_info=True)
        return jsonify({"error": "Server error", "messages": "Could not process your registration."}), 500


@auth_bp.route('/login', methods=['POST'])
def login_user():
    """User login endpoint. Returns access and refresh JWT tokens."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Invalid input", "messages": "No input data provided"}), 400

    try:
        data = user_login_schema.load(json_data)
    except ValidationError as err:
        current_app.logger.warning(f"Login validation error: {err.messages}")
        return jsonify({"error": "Validation error", "messages": err.messages}), 422

    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        if not user.is_active:
            current_app.logger.warning(f"Login attempt for inactive user: {user.username}")
            return jsonify({"error": "Unauthorized", "message": "Account is inactive."}), 401

        user.last_login = datetime.datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        current_app.logger.info(f"User logged in successfully: {user.username}")
        return jsonify(
            message="Login successful.",
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_schema.dump(user)
        ), 200
    else:
        current_app.logger.warning(f"Failed login attempt for email: {data['email']}")
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password."}), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Token refresh endpoint. Returns a new access token."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user or not user.is_active:
        current_app.logger.warning(f"Refresh attempt for non-existent or inactive user ID: {current_user_id}")
        return jsonify({"error": "Unauthorized", "message": "Invalid user for token refresh."}), 401

    new_access_token = create_access_token(identity=str(current_user_id))
    current_app.logger.info(f"Access token refreshed for user ID: {current_user_id}")
    return jsonify(access_token=new_access_token), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required(verify_type=False)
def logout_user():
    """User logout endpoint. Adds the JTI to the blocklist."""
    try:
        token = get_jwt()
        jti = token["jti"]
        token_type = token["type"]

        redis_client = current_app.extensions.get('redis_client')
        if not redis_client:
            current_app.logger.error("Redis client not available for logout.")
            return jsonify({"error": "Server configuration issue", "message": "Logout mechanism temporarily unavailable."}), 500

        expires_at = datetime.datetime.fromtimestamp(token['exp'])
        now = datetime.datetime.utcnow()
        if expires_at <= now:
            current_app.logger.info(f"Token {jti} already expired. Logout confirmed.")
            return jsonify(message="Logout successful (token already expired)."), 200

        if token_type == 'access':
            token_expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        elif token_type == 'refresh':
            token_expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
        else:
            current_app.logger.warning(f"Unknown token type '{token_type}' during logout for jti: {jti}")
            return jsonify(message="Logout successful (token type unknown, not blocklisted)."), 200

        if isinstance(token_expires_delta, datetime.timedelta):
            redis_client.setex(f"jti:{jti}", int(token_expires_delta.total_seconds()) + 60, "revoked")
        else:
            redis_client.setex(f"jti:{jti}", int(token_expires_delta) + 60, "revoked")

        current_app.logger.info(f"{token_type.capitalize()} token JTI {jti} blocklisted for user {get_jwt_identity()}.")
        return jsonify(message="Logout successful. Token has been invalidated."), 200

    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}", exc_info=True)
        return jsonify({"error": "Server error", "messages": "Could not process your logout."}), 500
