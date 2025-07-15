# voip_backend/models/user_models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from voip_backend.extensions import db # Import db from extensions

# If you have a common Base model or timestamp mixins, define them or import them.
# class TimestampMixin:
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class User(db.Model): # Add TimestampMixin if you create it
    """
    User model for storing user account information.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country_code = Column(String(3), nullable=True)

    kyc_status = Column(String(20), default='pending', index=True)
    kyc_verified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    kyc_records = relationship("KYCRecord", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    call_records = relationship("CallRecord", back_populates="user", cascade="all, delete-orphan")
    sms_records = relationship("SMSRecord", back_populates="user", cascade="all, delete-orphan")
    assigned_dids = relationship("DIDNumber", back_populates="assigned_user")


    def __repr__(self):
        return f"<User id={self.id} username='{self.username}' email='{self.email}'>"

    def set_password(self, password_plaintext):
        from voip_backend.extensions import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password_plaintext).decode('utf-8')

    def check_password(self, password_plaintext):
        from voip_backend.extensions import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password_plaintext)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username

# Note: The relationships `KYCRecord`, `UserSubscription`, etc., refer to class names
# of other models that will be defined in their respective files.
# The import for bcrypt within methods is one way to handle it if bcrypt isn't used elsewhere in the model file top-level.
# Alternatively, bcrypt can be imported at the top of the file if preferred.
