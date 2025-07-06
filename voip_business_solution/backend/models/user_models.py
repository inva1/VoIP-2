from ..app import db # Importing db from the app module
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    country_code = db.Column(db.String(3)) # ISO 3166-1 alpha-3
    kyc_status = db.Column(db.String(20), default='pending') # e.g., pending, verified, rejected
    kyc_verified_at = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_login = db.Column(db.TIMESTAMP)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    kyc_records = db.relationship('KYCRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    subscriptions = db.relationship('UserSubscription', backref='user', lazy=True, cascade="all, delete-orphan")
    dids_assigned = db.relationship('DIDNumber', backref='assigned_user', lazy=True) # Nullable foreign key in DIDNumber
    call_records = db.relationship('CallDetailRecord', backref='user', lazy=True)
    sms_records = db.relationship('SMSRecord', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    # Add methods for password hashing and verification here
    # e.g., set_password, check_password using werkzeug.security


class KYCRecord(db.Model):
    __tablename__ = 'kyc_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50)) # e.g., passport, national_id, driver_license
    document_number = db.Column(db.String(100))
    document_country = db.Column(db.String(3)) # ISO 3166-1 alpha-3
    verification_status = db.Column(db.String(20), default='pending') # e.g., pending, approved, rejected, requires_review
    risk_score = db.Column(db.Integer) # Optional field for risk scoring
    submitted_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    verified_at = db.Column(db.TIMESTAMP)
    verified_by = db.Column(db.Integer) # Could be an admin user ID
    notes = db.Column(db.Text)
    document_front_url = db.Column(db.String(500))
    document_back_url = db.Column(db.String(500)) # For documents like ID cards
    selfie_url = db.Column(db.String(500))

    def __repr__(self):
        return f'<KYCRecord {self.id} for User {self.user_id}>'
