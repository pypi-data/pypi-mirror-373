"""
Foreva AI SDK Types and Enums
"""

from enum import Enum

class OrderMode(Enum):
    """How the AI should handle orders"""
    DEFAULT = "default"  # AI processes order, sends JSON via webhook
    SMS = "sms"          # AI sends ordering URL via SMS  
    STAFF = "staff"      # AI forwards call to staff


class Mode(Enum):
    """API modes - Test/Live pattern (like Stripe)"""
    TEST = "test"
    LIVE = "live"

# Routing numbers are now server-controlled via API
# No more hardcoded numbers in SDK!

# Common escalation event strings (for convenience - not required)
class EscalationEvents:
    """
    Common escalation event strings for convenience.
    
    These are just helpful constants - you can use any string you want.
    The AI handles most situations automatically, only set escalation events
    if you want to override the default behavior.
    """
    ORDERING = "ordering"
    DELIVERY = "delivery"
    CATERING = "catering"
    RESERVATION = "reservation"
    COMPLAINT = "complaint"
