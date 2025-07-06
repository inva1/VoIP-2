from ..app import db # Importing db from the app module
import datetime

class DIDNumber(db.Model):
    __tablename__ = 'did_numbers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(20), unique=True, nullable=False) # E.164 format recommended
    country_code = db.Column(db.String(3)) # ISO 3166-1 alpha-3 of the number's country
    area_code = db.Column(db.String(10)) # Optional, for easier searching/filtering
    number_type = db.Column(db.String(20)) # e.g., local, toll-free, mobile, virtual
    provider = db.Column(db.String(100)) # Name of the DID provider
    monthly_cost = db.Column(db.Numeric(8, 2)) # Cost to acquire/maintain this number

    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # A DID can be unassigned
    status = db.Column(db.String(20), default='available') # e.g., available, assigned, reserved, ported_out

    assigned_at = db.Column(db.TIMESTAMP, nullable=True)
    expires_at = db.Column(db.TIMESTAMP, nullable=True) # Expiry from provider, or assigned period

    # Relationships
    # assigned_user is defined in User model via backref

    def __repr__(self):
        return f'<DIDNumber {self.number} ({self.status})>'
