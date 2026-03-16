# voip_backend/models/subscription_models.py

from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from voip_backend.extensions import db


class SubscriptionPlan(db.Model):
    """Subscription plan definitions."""
    __tablename__ = 'subscription_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_code = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    description = Column(Text)
    target_country = Column(String(3))  # ISO alpha-3 — primary market
    monthly_fee = Column(Numeric(10, 2))
    included_minutes = Column(Integer)
    included_messages = Column(Integer)
    overage_rate_voice = Column(Numeric(6, 4))  # per minute
    overage_rate_sms = Column(Numeric(6, 4))    # per message
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="plan")

    def __repr__(self):
        return f'<SubscriptionPlan {self.plan_code} "{self.plan_name}">'


class UserSubscription(db.Model):
    """User subscription instance linking user to a plan."""
    __tablename__ = 'user_subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'), nullable=False)
    status = Column(String(20), default='active', index=True)  # active, expired, cancelled
    subscribed_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    usage_minutes = Column(Integer, default=0)
    usage_messages = Column(Integer, default=0)
    last_reset_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="user_subscriptions")

    def __repr__(self):
        return f'<UserSubscription {self.id} user={self.user_id} plan={self.plan_id}>'
