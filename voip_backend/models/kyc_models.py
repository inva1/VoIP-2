# voip_backend/models/kyc_models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from voip_backend.extensions import db


class KYCRecord(db.Model):
    """KYC identity verification records."""
    __tablename__ = 'kyc_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    document_type = Column(String(50))  # passport, national_id, driver_license
    document_number = Column(String(100))
    document_country = Column(String(3))  # ISO 3166-1 alpha-3
    verification_status = Column(String(20), default='pending', index=True)  # pending, approved, rejected
    risk_score = Column(Integer)
    submitted_at = Column(DateTime, server_default=func.now())
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(Integer, nullable=True)  # Admin user ID
    notes = Column(Text)
    document_front_url = Column(String(500))
    document_back_url = Column(String(500))
    selfie_url = Column(String(500))

    # Relationship
    user = relationship("User", back_populates="kyc_records")

    def __repr__(self):
        return f'<KYCRecord {self.id} user={self.user_id} status={self.verification_status}>'
