# voip_backend/models/did_models.py

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from voip_backend.extensions import db


class DIDNumber(db.Model):
    """DID (Direct Inward Dialing) phone number inventory."""
    __tablename__ = 'did_numbers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(20), unique=True, nullable=False)  # E.164 format
    country_code = Column(String(3))  # ISO 3166-1 alpha-3
    area_code = Column(String(10))
    number_type = Column(String(20))  # local, toll-free, mobile, virtual
    provider = Column(String(100))
    monthly_cost = Column(Numeric(8, 2))

    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    status = Column(String(20), default='available', index=True)  # available, assigned, reserved

    assigned_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationship
    assigned_user = relationship("User", back_populates="assigned_dids")

    def __repr__(self):
        return f'<DIDNumber {self.number} ({self.status})>'
