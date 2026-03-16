# voip_backend/schemas/call_sms_schemas.py

from marshmallow import fields, validate
from voip_backend.extensions import ma


class CallRecordSchema(ma.Schema):
    """Schema for serializing call record data."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    call_id = fields.Str()
    caller_number = fields.Str()
    called_number = fields.Str()
    call_direction = fields.Str()
    call_type = fields.Str()
    start_time = fields.DateTime()
    end_time = fields.DateTime(allow_none=True)
    duration = fields.Int(allow_none=True)
    call_status = fields.Str()
    termination_reason = fields.Str(allow_none=True)
    cost = fields.Float(allow_none=True)
    carrier_used = fields.Str(allow_none=True)
    quality_score = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        ordered = True


class SMSRecordSchema(ma.Schema):
    """Schema for serializing SMS record data."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    message_id = fields.Str()
    from_number = fields.Str()
    to_number = fields.Str()
    message_text = fields.Str()
    message_type = fields.Str()
    direction = fields.Str()
    status = fields.Str()
    sent_at = fields.DateTime(allow_none=True)
    delivered_at = fields.DateTime(allow_none=True)
    cost = fields.Float(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        ordered = True


class SendSMSSchema(ma.Schema):
    """Schema for sending an SMS."""
    to_number = fields.Str(required=True, validate=validate.Length(min=5, max=20))
    message_text = fields.Str(required=True, validate=validate.Length(min=1, max=1600))
    from_did_id = fields.Int(required=False)  # Optional: use a specific DID

    class Meta:
        ordered = True
