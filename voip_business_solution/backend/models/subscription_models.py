from ..app import db # Importing db from the app module
import datetime

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_code = db.Column(db.String(50), unique=True, nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_country = db.Column(db.String(3)) # ISO 3166-1 alpha-3, e.g., NGA, USA, GBR. Identifies primary market for this plan.
    destination_countries = db.Column(db.ARRAY(db.String(3))) # Array of ISO 3166-1 alpha-3 country codes this plan allows calling TO
    monthly_fee = db.Column(db.Numeric(10, 2))
    included_minutes = db.Column(db.Integer)
    included_messages = db.Column(db.Integer) # For SMS
    overage_rate_voice = db.Column(db.Numeric(6, 4)) # Cost per minute after included minutes
    overage_rate_sms = db.Column(db.Numeric(6, 4))   # Cost per message after included messages
    features = db.Column(db.JSONB) # For additional plan features, e.g., {"caller_id": true, "call_recording": false}
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    # updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) # Add if needed

    # Relationship
    user_subscriptions = db.relationship('UserSubscription', backref='plan', lazy=True)

    def __repr__(self):
        return f'<SubscriptionPlan {self.plan_name}>'


class UserSubscription(db.Model):
    __tablename__ = 'user_subscriptions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.String(20), default='active') # e.g., active, expired, cancelled, pending_payment
    subscribed_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.TIMESTAMP) # Can be null for non-expiring or manually managed subscriptions
    auto_renew = db.Column(db.Boolean, default=True)
    usage_minutes = db.Column(db.Integer, default=0)
    usage_messages = db.Column(db.Integer, default=0) # For SMS
    last_reset_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow) # When usage was last reset (e.g., start of billing cycle)

    def __repr__(self):
        return f'<UserSubscription {self.id} for User {self.user_id} - Plan {self.plan_id}>'
