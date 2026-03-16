# voip_backend/schemas/did_schemas.py

from marshmallow import fields, validate
from voip_backend.extensions import ma


class DIDNumberSchema(ma.Schema):
    """Schema for serializing DID number data."""
    id = fields.Int(dump_only=True)
    number = fields.Str()
    country_code = fields.Str(allow_none=True)
    area_code = fields.Str(allow_none=True)
    number_type = fields.Str(allow_none=True)
    provider = fields.Str(allow_none=True)
    monthly_cost = fields.Float(allow_none=True)
    assigned_to = fields.Int(allow_none=True)
    status = fields.Str()
    assigned_at = fields.DateTime(allow_none=True)
    expires_at = fields.DateTime(allow_none=True)

    class Meta:
        ordered = True


class DIDAssignSchema(ma.Schema):
    """Schema for assigning a DID to a user."""
    did_id = fields.Int(required=True)

    class Meta:
        ordered = True
