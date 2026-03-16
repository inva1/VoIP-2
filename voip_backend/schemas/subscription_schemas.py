# voip_backend/schemas/subscription_schemas.py

from marshmallow import fields, validate
from voip_backend.extensions import ma


class SubscriptionPlanSchema(ma.Schema):
    """Schema for serializing subscription plan data."""
    id = fields.Int(dump_only=True)
    plan_code = fields.Str()
    plan_name = fields.Str()
    description = fields.Str(allow_none=True)
    target_country = fields.Str(allow_none=True)
    monthly_fee = fields.Float()
    included_minutes = fields.Int()
    included_messages = fields.Int()
    overage_rate_voice = fields.Float()
    overage_rate_sms = fields.Float()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        ordered = True


class CreatePlanSchema(ma.Schema):
    """Schema for admin creating a new subscription plan."""
    plan_code = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    plan_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(allow_none=True)
    target_country = fields.Str(validate=validate.Length(min=2, max=3), allow_none=True)
    monthly_fee = fields.Float(required=True, validate=validate.Range(min=0))
    included_minutes = fields.Int(required=True, validate=validate.Range(min=0))
    included_messages = fields.Int(required=True, validate=validate.Range(min=0))
    overage_rate_voice = fields.Float(validate=validate.Range(min=0), load_default=0.0)
    overage_rate_sms = fields.Float(validate=validate.Range(min=0), load_default=0.0)

    class Meta:
        ordered = True


class SubscribeSchema(ma.Schema):
    """Schema for subscribing to a plan."""
    plan_id = fields.Int(required=True)

    class Meta:
        ordered = True


class UserSubscriptionSchema(ma.Schema):
    """Schema for serializing user subscription data."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    plan_id = fields.Int()
    status = fields.Str()
    subscribed_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime(allow_none=True)
    auto_renew = fields.Bool()
    usage_minutes = fields.Int()
    usage_messages = fields.Int()
    last_reset_at = fields.DateTime(dump_only=True)
    plan = fields.Nested(SubscriptionPlanSchema, dump_only=True)

    class Meta:
        ordered = True
