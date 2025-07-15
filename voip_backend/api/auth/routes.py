# voip_backend/api/auth/routes.py

from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import datetime

from voip_backend.models.user_models import User
from voip_backend.schemas.user_schemas import UserRegistrationSchema, UserLoginSchema, UserSchema
from voip_backend.extensions import db, bcrypt, jwt

auth_bp = Blueprint('auth_api', __name__)

user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_schema = UserSchema() # For dumping user info

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    User registration endpoint.
    Expects JSON payload with username, email, password, and optional profile fields.
    """
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
    """
    User login endpoint.
    Expects JSON payload with email and password.
    Returns access and refresh JWT tokens upon successful authentication.
    """
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

        # Update last_login timestamp
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        current_app.logger.info(f"User logged in successfully: {user.username}")
        return jsonify(
            message="Login successful.",
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_schema.dump(user) # Optionally return user info
        ), 200
    else:
        current_app.logger.warning(f"Failed login attempt for email: {data['email']}")
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password."}), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Requires a valid refresh token
def refresh_token():
    """
    Token refresh endpoint.
    Requires a valid JWT refresh token in the Authorization header (Bearer <token>).
    Returns a new access token.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_active:
        # This case should ideally be caught by JWT blocklisting if user is deactivated after token issuance
        current_app.logger.warning(f"Refresh attempt for non-existent or inactive user ID: {current_user_id}")
        return jsonify({"error": "Unauthorized", "message": "Invalid user for token refresh."}), 401

    new_access_token = create_access_token(identity=current_user_id)
    current_app.logger.info(f"Access token refreshed for user ID: {current_user_id}")
    return jsonify(access_token=new_access_token), 200


# TODO: Implement JWT blocklisting for logout if needed.
# This requires configuring JWTManager with a blocklist loader and store (e.g., Redis).
# @jwt.token_in_blocklist_loader
# def check_if_token_in_blocklist(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     # Check if jti is in Redis blocklist
#     token_is_revoked = redis_client.get(jti) # Example
#     return token_is_revoked is not None

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(verify_type=False) # Allow access and refresh tokens, verify_type=False means token type is not checked by decorator itself
def logout_user():
    """
    User logout endpoint.
    Adds the JTI of the provided token (access or refresh) to the blocklist.
    Requires a valid JWT in the Authorization header.
    """
    try:
        token = get_jwt() # Get the full token data
        jti = token["jti"]
        token_type = token["type"]

        redis_client = current_app.extensions.get('redis_client')
        if not redis_client:
            current_app.logger.error("Redis client not available for logout.")
            # Depending on policy, you might still return 200 to client
            # but log that token couldn't be blocklisted.
            return jsonify({"error": "Server configuration issue", "message": "Logout mechanism temporarily unavailable."}), 500

        # Get token expiry to set an expiry for the blocklist entry in Redis
        # For access tokens, this is 'exp'. For refresh tokens, it's also 'exp'.
        # The timedelta should be from now until expiry.
        expires_at = datetime.datetime.fromtimestamp(token['exp'])
        now = datetime.datetime.utcnow()
        # If token already expired, no need to add to blocklist, but client might send it.
        # timedelta will be negative if expired. Redis EXPIRE handles positive seconds.
        # If already expired, just confirm logout.
        if expires_at <= now:
            current_app.logger.info(f"Token {jti} already expired. Logout confirmed.")
            return jsonify(message="Logout successful (token already expired)."), 200

        # Time until token expires, in seconds. Max for safety if already near expiry.
        # Add a small buffer to ensure it's stored past expiry.
        # redis_client.set(f"jti:{jti}", "revoked", ex=int((expires_at - now).total_seconds()) + 60)
        # Or, more simply, use the remaining time from the token itself, if available as a config
        # Flask-JWT-Extended uses app.config['JWT_ACCESS_TOKEN_EXPIRES'] which is a timedelta
        # We need to calculate remaining time.

        # Simpler: just store it with the original expiry time of the token type.
        # This ensures it's cleared from Redis eventually.
        if token_type == 'access':
            token_expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        elif token_type == 'refresh':
            token_expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
        else:
            # Should not happen if verify_type=False is used carefully with other checks
            current_app.logger.warning(f"Unknown token type '{token_type}' during logout for jti: {jti}")
            return jsonify(message="Logout successful (token type unknown, not blocklisted)."), 200

        if isinstance(token_expires_delta, datetime.timedelta):
            redis_client.setex(f"jti:{jti}", int(token_expires_delta.total_seconds()) + 60, "revoked") # Add 60s buffer
            current_app.logger.info(f"{token_type.capitalize()} token JTI {jti} blocklisted for user {get_jwt_identity()}.")
        else: # If expiry is not timedelta (e.g. integer seconds)
             redis_client.setex(f"jti:{jti}", int(token_expires_delta) + 60, "revoked")
             current_app.logger.info(f"{token_type.capitalize()} token JTI {jti} blocklisted for user {get_jwt_identity()} (using direct expiry).")


        return jsonify(message="Logout successful. Token has been invalidated."), 200

    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}", exc_info=True)
        return jsonify({"error": "Server error", "messages": "Could not process your logout."}), 500

# Note: The @jwt_required(verify_type=False) allows either an access or a refresh token
# to be sent for logout. If you want to force only access tokens for logout, use @jwt_required().
# If you want separate /logout-access and /logout-refresh, create two endpoints.
# The current approach blocklists whatever token is provided.
# A more robust logout might involve blocklisting *both* associated access and refresh tokens
# if possible (e.g., if their JTIs are linked or if refresh token is sent to logout all sessions).
# For simplicity, this logs out the provided token.
# If `get_jwt()` is used, it must be inside a @jwt_required decorated function.
# We also need to import `get_jwt`
from flask_jwt_extended import get_jwt
