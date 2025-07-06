from ..app import db # Importing db from the app module
import datetime

class CallDetailRecord(db.Model):
    __tablename__ = 'call_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable if system calls or unauthenticated calls are possible
    call_id = db.Column(db.String(100), unique=True) # Unique ID from VoIP system (e.g., Asterisk UniqueID)

    caller_number = db.Column(db.String(20)) # Originating number
    called_number = db.Column(db.String(20)) # Destination number

    call_direction = db.Column(db.String(10)) # e.g., inbound, outbound, internal
    call_type = db.Column(db.String(20)) # e.g., voice, video, conference

    start_time = db.Column(db.TIMESTAMP, nullable=False)
    end_time = db.Column(db.TIMESTAMP)
    duration = db.Column(db.Integer) # In seconds

    call_status = db.Column(db.String(20)) # e.g., answered, busy, failed, no_answer
    termination_reason = db.Column(db.String(50)) # More specific reason for call end

    cost = db.Column(db.Numeric(10, 4)) # Cost of the call
    carrier_used = db.Column(db.String(100)) # PSTN carrier or internal route
    quality_score = db.Column(db.Integer) # e.g., MOS score, or internal quality metric

    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<CallDetailRecord {self.call_id}>'


class RegulatoryCDR(db.Model):
    __tablename__ = 'regulatory_cdr'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    call_id = db.Column(db.String(100), unique=True, nullable=False) # Could FK to call_records.call_id if always linked

    calling_party = db.Column(db.String(20), nullable=False)
    called_party = db.Column(db.String(20), nullable=False)

    call_start_time = db.Column(db.TIMESTAMP, nullable=False)
    call_end_time = db.Column(db.TIMESTAMP)
    call_duration = db.Column(db.Integer) # In seconds

    originating_carrier = db.Column(db.String(100))
    terminating_carrier = db.Column(db.String(100))

    call_type = db.Column(db.String(20)) # e.g., local, long_distance, international, emergency
    billing_number = db.Column(db.String(20)) # Number to which the call is billed

    charge_amount = db.Column(db.Numeric(10, 4))
    tax_amount = db.Column(db.Numeric(10, 4))
    regulatory_fees = db.Column(db.Numeric(10, 4))

    jurisdiction = db.Column(db.String(10)) # e.g., US-NY, GBR, NGA. Country or specific region.
    emergency_service_flag = db.Column(db.Boolean, default=False)
    lawful_intercept_flag = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    retention_until = db.Column(db.TIMESTAMP) # For data retention policies

    # Compliance flags
    e911_capable = db.Column(db.Boolean, default=False)
    calea_compliant = db.Column(db.Boolean, default=False) # Communications Assistance for Law Enforcement Act (US)
    stir_shaken_verified = db.Column(db.Boolean, default=False) # STIR/SHAKEN verification status (US)

    def __repr__(self):
        return f'<RegulatoryCDR {self.call_id}>'
