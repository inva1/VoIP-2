# voip_backend/schemas/kyc_schemas.py

from marshmallow import fields, validate
from voip_backend.extensions import ma


class KYCSubmitSchema(ma.Schema):
    """Schema for submitting KYC verification documents."""
    document_type = fields.Str(required=True, validate=validate.OneOf(
        ['passport', 'national_id', 'driver_license']
    ))
    document_number = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    document_country = fields.Str(required=True, validate=validate.Length(min=2, max=3))
    document_front_url = fields.Str(validate=validate.Length(max=500))
    document_back_url = fields.Str(validate=validate.Length(max=500), allow_none=True)
    selfie_url = fields.Str(validate=validate.Length(max=500))

    class Meta:
        ordered = True


class KYCRecordSchema(ma.Schema):
    """Schema for serializing KYC record data."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    document_type = fields.Str()
    document_number = fields.Str()
    document_country = fields.Str()
    verification_status = fields.Str()
    risk_score = fields.Int(allow_none=True)
    submitted_at = fields.DateTime(dump_only=True)
    verified_at = fields.DateTime(dump_only=True, allow_none=True)
    notes = fields.Str(dump_only=True, allow_none=True)

    class Meta:
        ordered = True


class KYCReviewSchema(ma.Schema):
    """Schema for admin reviewing KYC submissions."""
    verification_status = fields.Str(required=True, validate=validate.OneOf(
        ['approved', 'rejected', 'requires_review']
    ))
    risk_score = fields.Int(validate=validate.Range(min=0, max=100), allow_none=True)
    notes = fields.Str(validate=validate.Length(max=1000), allow_none=True)

    class Meta:
        ordered = True
