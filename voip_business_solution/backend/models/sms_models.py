from ..app import db # Importing db from the app module
import datetime

class SMSRecord(db.Model):
    __tablename__ = 'sms_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable if system messages or unauthenticated messages are possible
    message_id = db.Column(db.String(100), unique=True) # Unique ID from SMS gateway or internal system

    from_number = db.Column(db.String(20)) # Sender's number
    to_number = db.Column(db.String(20))   # Recipient's number

    message_text = db.Column(db.Text)
    message_type = db.Column(db.String(20)) # e.g., sms, mms, notification
    direction = db.Column(db.String(10))    # e.g., inbound, outbound

    status = db.Column(db.String(20)) # e.g., sent, delivered, failed, pending, received
    sent_at = db.Column(db.TIMESTAMP)
    delivered_at = db.Column(db.TIMESTAMP)

    cost = db.Column(db.Numeric(8, 4)) # Cost of the SMS
    carrier_used = db.Column(db.String(100)) # SMS gateway or carrier

    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<SMSRecord {self.message_id}>'
