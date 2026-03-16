# voip_backend/schemas/user_schemas.py

from marshmallow import fields, validate, ValidationError, EXCLUDE
from voip_backend.extensions import ma


def validate_password_strength(password):
    """Custom validator for password strength."""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one digit.")
    if not any(char.isalpha() for char in password):
        raise ValidationError("Password must contain at least one letter.")


class UserSchema(ma.Schema):
    """Schema for serializing User model data (output). Excludes password_hash."""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    first_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    country_code = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True)
    kyc_status = fields.Str(dump_only=True)
    kyc_verified_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True, allow_none=True)
    is_active = fields.Bool(dump_only=True)
    full_name = fields.Str(dump_only=True)

    class Meta:
        ordered = True


class UserRegistrationSchema(ma.Schema):
    """Schema for user registration input validation."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.Str(
        required=True,
        validate=validate_password_strength,
        load_only=True
    )
    first_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    country_code = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True)

    class Meta:
        ordered = True


class UserLoginSchema(ma.Schema):
    """Schema for user login input validation."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

    class Meta:
        ordered = True


class UserUpdateSchema(ma.Schema):
    """Schema for updating user profile. Fields are optional, validated if provided."""
    first_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=100), allow_none=True)
    phone_number = fields.Str(validate=validate.Length(max=20), allow_none=True)
    country_code = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True)

    class Meta:
        ordered = True
        unknown = EXCLUDE

