from .user_models import User, KYCRecord
from .subscription_models import SubscriptionPlan, UserSubscription
from .did_models import DIDNumber
from .call_models import CallDetailRecord, RegulatoryCDR
from .sms_models import SMSRecord

# This __all__ list is used by 'from .models import *'
# It's good practice to define it to control what gets imported.
__all__ = [
    'User',
    'KYCRecord',
    'SubscriptionPlan',
    'UserSubscription',
    'DIDNumber',
    'CallDetailRecord',
    'SMSRecord',
    'RegulatoryCDR'
]

# The actual model classes are now defined in their respective files (user_models.py, etc.)
# and imported above.
# The db instance from app.py will be used by these model definitions.
