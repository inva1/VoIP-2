# voip_backend/schemas/user_schemas.py

from marshmallow import Schema, fields, validate, ValidationError
# Assuming 'ma' is the Marshmallow instance from extensions.py
# from voip_backend.extensions import ma
# For now, to make this file parseable:
from flask_marshmallow import Marshmallow
ma = Marshmallow() # Placeholder for ma instance from extensions.py


# Custom validator for password strength (example)
def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit.")
    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter.")
    # Add more checks: uppercase, lowercase, special character if needed


class UserSchema(ma.Schema):
    """
    Schema for serializing User model data (output).
    Excludes sensitive information like password_hash.
    """
    id = fields.Int(dump_only=True) # dump_only means it's only for output, not input
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    first_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    country_code = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True) # ISO alpha-2 or alpha-3
    kyc_status = fields.Str(dump_only=True)
    kyc_verified_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True, allow_none=True)
    is_active = fields.Bool(dump_only=True)
    full_name = fields.Str(dump_only=True) # From User model's @property

    class Meta:
        # fields = (...) # Whitelist fields (alternative to dump_only on each field)
        # exclude = ("password_hash",) # Blacklist fields
        ordered = True


class UserRegistrationSchema(ma.Schema):
    """
    Schema for user registration input validation.
    """
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(
        required=True,
        validate=validate_password_strength,
        load_only=True # load_only means it's only for input, not output
    )
    first_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    country_code = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True)

    class Meta:
        ordered = True


class UserLoginSchema(ma.Schema):
    """
    Schema for user login input validation.
    """
    email = fields.Email(required=True) # Or username, or allow both
    # username = fields.Str(required=False) # If allowing username for login
    password = fields.Str(required=True, load_only=True)

    # @validates_schema
    # def validate_login_identifier(self, data, **kwargs):
    #     if not data.get('email') and not data.get('username'):
    #         raise ValidationError("Either email or username must be provided for login.", "_schema")

    class Meta:
        ordered = True


class UserUpdateSchema(ma.Schema):
    """
    Schema for updating user profile information.
    Fields are not required, only validated if provided.
    """
    first_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    country_code = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True)
    # Email change might require a verification process, so not included here for simple update.
    # Username change is often disallowed or complex, so also not included.

    class Meta:
        ordered = True

# Note: The actual `ma` instance will be imported from `voip_backend.extensions`.
# These schemas can be used in Flask views with `@use_args` (for input) and `dump` method (for output).
# Example usage in a Flask route:
#
# from .schemas.user_schemas import UserRegistrationSchema, UserSchema
# from .models.user_models import User
# from ..extensions import db
#
# @auth_bp.route('/register', methods=['POST'])
# @use_args(UserRegistrationSchema())
# def register(args):
#     # args contains validated data from UserRegistrationSchema
#     if User.query.filter_by(email=args['email']).first() or \
#        User.query.filter_by(username=args['username']).first():
#         return {"message": "User already exists"}, 409
#
#     user = User(**args) # Create User instance (need to handle password separately)
#     user.set_password(args['password']) # Assuming User model has set_password
#     db.session.add(user)
#     db.session.commit()
#
#     return UserSchema().dump(user), 201
#
# (This is just an illustrative example of how schemas might be used)
