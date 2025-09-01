"""
Foreva AI SDK - Voice AI for restaurants

Usage:
    from foreva_ai import ForevaAgent, OrderMode
    
    # Create agent (mode auto-detected from API key)
    agent = ForevaAgent("YOUR_API_KEY_HERE", "+14155551234")
    agent.set_store("Tony's Pizza", "123 Main St")
    agent.set_menu(menu_data)
    agent.activate()  # Get setup instructions
"""

__version__ = "0.0.2"
__author__ = "Foreva AI"
__email__ = "support@foreva.ai"
__description__ = "Voice AI for restaurants - Python SDK"

# Import main classes
from .agent import ForevaAgent, quick_setup, quick_setup_both, MenuBuilder, MenuCustomization
from .types import OrderMode, EscalationEvents
from .exceptions import (
    ForevaError,
    ForevaAPIError, 
    ForevaValidationError,
    ForevaAuthenticationError,
    ForevaNotFoundError,
    ForevaTestLimitError,
    ForevaSubscriptionRequiredError
)

__all__ = [
    # Main classes
    "ForevaAgent",
    "OrderMode",
    "EscalationEvents",
    
    # Menu helpers
    "MenuBuilder",
    "MenuCustomization",
    
    # Exceptions
    "ForevaError",
    "ForevaAPIError",
    "ForevaValidationError", 
    "ForevaAuthenticationError",
    "ForevaNotFoundError",
    "ForevaTestLimitError",
    "ForevaSubscriptionRequiredError",
    
    # Convenience functions
    "quick_setup",
    "quick_setup_both",
    
    # Metadata
    "__version__",
]

# Set up logging
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())