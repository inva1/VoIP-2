# voip_backend/models/call_sms_models.py

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from voip_backend.extensions import db


class CallRecord(db.Model):
    """Call detail records (CDR)."""
    __tablename__ = 'call_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    call_id = Column(String(100), unique=True)  # From Asterisk/Kamailio
    caller_number = Column(String(20))
    called_number = Column(String(20))
    call_direction = Column(String(10))  # inbound, outbound
    call_type = Column(String(20))       # voice, video
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration = Column(Integer)  # seconds
    call_status = Column(String(20))  # completed, failed, busy
    termination_reason = Column(String(50))
    cost = Column(Numeric(10, 4))
    carrier_used = Column(String(100))
    quality_score = Column(Integer)  # MOS score
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="call_records")

    def __repr__(self):
        return f'<CallRecord {self.call_id}>'


class SMSRecord(db.Model):
    """SMS message records."""
    __tablename__ = 'sms_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    message_id = Column(String(100), unique=True)
    from_number = Column(String(20))
    to_number = Column(String(20))
    message_text = Column(Text)
    message_type = Column(String(20))  # sms, mms
    direction = Column(String(10))     # inbound, outbound
    status = Column(String(20))        # sent, delivered, failed
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    cost = Column(Numeric(8, 4))
    carrier_used = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="sms_records")

    def __repr__(self):
        return f'<SMSRecord {self.message_id}>'


class RegulatoryCDR(db.Model):
    """Regulatory-compliant CDR records for telecom compliance."""
    __tablename__ = 'regulatory_cdr'

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String(100), unique=True, nullable=False)
    calling_party = Column(String(20), nullable=False)
    called_party = Column(String(20), nullable=False)
    call_start_time = Column(DateTime, nullable=False, index=True)
    call_end_time = Column(DateTime)
    call_duration = Column(Integer)
    originating_carrier = Column(String(100))
    terminating_carrier = Column(String(100))
    call_type = Column(String(20))  # local, long_distance, international
    billing_number = Column(String(20))
    charge_amount = Column(Numeric(10, 4))
    tax_amount = Column(Numeric(10, 4))
    regulatory_fees = Column(Numeric(10, 4))
    jurisdiction = Column(String(10), index=True)
    emergency_service_flag = Column(Boolean, default=False, index=True)
    lawful_intercept_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    retention_until = Column(DateTime)
    e911_capable = Column(Boolean, default=False)
    calea_compliant = Column(Boolean, default=False)
    stir_shaken_verified = Column(Boolean, default=False)

    def __repr__(self):
        return f'<RegulatoryCDR {self.call_id}>'
