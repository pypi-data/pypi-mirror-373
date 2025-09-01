"""
Foreva AI SDK - Main Agent Class
Professional implementation of the original draft design
"""

from typing import Dict, Any, List, Optional, Union
import re
from .client import ForevaAPIClient
from .types import OrderMode
from .exceptions import ForevaAPIError, ForevaValidationError, ForevaNotFoundError
from .config import is_debug_build, should_show_internal_logs, should_show_urls

def time_to_minutes(time_str: str) -> int:
    """Convert time string HH:MM to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def validate_store_hours(hours_data) -> bool:
    """
    Validate store hours format.
    
    Expected format: [{"weekday": 0, "open": "11:30", "close": "21:00"}, ...]
    - weekday: 0-6 (Monday=0, Sunday=6)
    - open/close: HH:MM format in 24-hour time
    - open time must be before close time
    - no duplicate weekdays
    
    Args:
        hours_data: Hours data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(hours_data, list):
        return False
    
    if not hours_data:  # Empty list is valid (store closed all week)
        return True
    
    seen_weekdays = set()
    time_pattern = re.compile(r'^([01]?\d|2[0-3]):([0-5]\d)$')
    
    for entry in hours_data:
        # Must be a dictionary
        if not isinstance(entry, dict):
            return False
        
        # Must have required fields
        required_fields = {'weekday', 'open', 'close'}
        if not all(field in entry for field in required_fields):
            return False
        
        # Must have only the required fields (no extra fields)
        if set(entry.keys()) != required_fields:
            return False
        
        weekday = entry['weekday']
        open_time = entry['open']
        close_time = entry['close']
        
        # Weekday validation
        if not isinstance(weekday, int) or weekday < 0 or weekday > 6:
            return False
        
        # No duplicate weekdays
        if weekday in seen_weekdays:
            return False
        seen_weekdays.add(weekday)
        
        # Time format validation
        if not isinstance(open_time, str) or not isinstance(close_time, str):
            return False
        
        if not time_pattern.match(open_time) or not time_pattern.match(close_time):
            return False
        
        # Logical validation: open < close (no overnight hours for now)
        open_minutes = time_to_minutes(open_time)
        close_minutes = time_to_minutes(close_time)
        
        if open_minutes >= close_minutes:
            return False
    
    return True


def validate_e164_phone_number(phone_number: str) -> bool:
    """
    Validate E.164 phone number format.
    
    E.164 format: +[country code][number] (max 15 digits total)
    Examples: +14155551234, +442071234567, +8613812345678
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        bool: True if valid E.164 format, False otherwise
    """
    if not isinstance(phone_number, str):
        return False
    
    # Basic E.164 pattern: + followed by 1-15 digits, country code 1-3 digits
    e164_pattern = re.compile(r'^\+[1-9]\d{1,14}$')
    if not e164_pattern.match(phone_number):
        return False
    
    # Additional validation for common country codes
    if phone_number.startswith('+1'):  # North America
        return len(phone_number) == 12  # +1 + 10 digits
    elif phone_number.startswith('+44'):  # UK
        return len(phone_number) >= 12 and len(phone_number) <= 13
    elif phone_number.startswith('+86'):  # China
        return len(phone_number) == 14  # +86 + 11 digits
    elif phone_number.startswith('+33'):  # France
        return len(phone_number) == 12  # +33 + 9 digits
    elif phone_number.startswith('+49'):  # Germany
        return len(phone_number) >= 12 and len(phone_number) <= 13
    elif phone_number.startswith('+81'):  # Japan
        return len(phone_number) >= 12 and len(phone_number) <= 13
    elif phone_number.startswith('+91'):  # India
        return len(phone_number) == 13  # +91 + 10 digits
    elif phone_number.startswith('+55'):  # Brazil
        return len(phone_number) == 14  # +55 + 11 digits
    elif phone_number.startswith('+61'):  # Australia
        return len(phone_number) == 12  # +61 + 9 digits
    elif phone_number.startswith('+7'):   # Russia/Kazakhstan
        return len(phone_number) == 12  # +7 + 10 digits
    
    # For other countries, just check basic length constraints
    return len(phone_number) >= 8 and len(phone_number) <= 16


def get_e164_validation_error(phone_number: str) -> Optional[str]:
    """
    Get detailed error message for invalid E.164 phone number.
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        str: Error message if invalid, None if valid
    """
    if not isinstance(phone_number, str):
        return "Phone number must be a string"
    
    if not phone_number:
        return "Phone number cannot be empty"
    
    if not phone_number.startswith('+'):
        return "Phone number must start with '+' (E.164 format required)"
    
    if len(phone_number) < 8:
        return "Phone number too short (minimum 8 characters including '+')"
    
    if len(phone_number) > 16:
        return "Phone number too long (maximum 15 digits after '+')"
    
    # Check that everything after + is digits
    digits_part = phone_number[1:]
    if not digits_part.isdigit():
        return "Phone number must contain only digits after '+'"
    
    # Check country code doesn't start with 0
    if digits_part.startswith('0'):
        return "Country code cannot start with 0"
    
    # Country-specific validation with detailed errors
    if phone_number.startswith('+1'):  # North America
        if len(phone_number) != 12:
            return f"US/Canada phone numbers must be 12 characters (+1 + 10 digits), got {len(phone_number)}"
    elif phone_number.startswith('+44'):  # UK
        if len(phone_number) < 12 or len(phone_number) > 13:
            return f"UK phone numbers must be 12-13 characters, got {len(phone_number)}"
    elif phone_number.startswith('+86'):  # China
        if len(phone_number) != 14:
            return f"China phone numbers must be 14 characters (+86 + 11 digits), got {len(phone_number)}"
    elif phone_number.startswith('+33'):  # France
        if len(phone_number) != 12:
            return f"France phone numbers must be 12 characters (+33 + 9 digits), got {len(phone_number)}"
    elif phone_number.startswith('+49'):  # Germany
        if len(phone_number) < 12 or len(phone_number) > 13:
            return f"Germany phone numbers must be 12-13 characters, got {len(phone_number)}"
    elif phone_number.startswith('+81'):  # Japan
        if len(phone_number) < 12 or len(phone_number) > 13:
            return f"Japan phone numbers must be 12-13 characters, got {len(phone_number)}"
    elif phone_number.startswith('+91'):  # India
        if len(phone_number) != 13:
            return f"India phone numbers must be 13 characters (+91 + 10 digits), got {len(phone_number)}"
    elif phone_number.startswith('+55'):  # Brazil
        if len(phone_number) != 14:
            return f"Brazil phone numbers must be 14 characters (+55 + 11 digits), got {len(phone_number)}"
    elif phone_number.startswith('+61'):  # Australia
        if len(phone_number) != 12:
            return f"Australia phone numbers must be 12 characters (+61 + 9 digits), got {len(phone_number)}"
    elif phone_number.startswith('+7'):   # Russia/Kazakhstan
        if len(phone_number) != 12:
            return f"Russia/Kazakhstan phone numbers must be 12 characters (+7 + 10 digits), got {len(phone_number)}"
    
    return None


def get_store_hours_validation_error(hours_data) -> Optional[str]:
    """
    Get detailed error message for invalid store hours.
    
    Args:
        hours_data: Hours data to validate
        
    Returns:
        str: Error message if invalid, None if valid
    """
    if not isinstance(hours_data, list):
        return "Store hours must be a list"
    
    if not hours_data:  # Empty list is valid
        return None
    
    seen_weekdays = set()
    time_pattern = re.compile(r'^([01]?\d|2[0-3]):([0-5]\d)$')
    
    for i, entry in enumerate(hours_data):
        # Must be a dictionary
        if not isinstance(entry, dict):
            return f"Entry {i} must be a dictionary"
        
        # Must have required fields
        required_fields = {'weekday', 'open', 'close'}
        missing_fields = required_fields - set(entry.keys())
        if missing_fields:
            return f"Entry {i} missing required fields: {', '.join(missing_fields)}"
        
        # Must have only the required fields (no extra fields)
        extra_fields = set(entry.keys()) - required_fields
        if extra_fields:
            return f"Entry {i} has unexpected fields: {', '.join(extra_fields)}"
        
        weekday = entry['weekday']
        open_time = entry['open']
        close_time = entry['close']
        
        # Weekday validation
        if not isinstance(weekday, int):
            return f"Entry {i}: weekday must be an integer"
        if weekday < 0 or weekday > 6:
            return f"Entry {i}: weekday must be 0-6 (Monday=0, Sunday=6), got {weekday}"
        
        # No duplicate weekdays
        if weekday in seen_weekdays:
            weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            return f"Entry {i}: duplicate weekday {weekday} ({weekday_names[weekday]})"
        seen_weekdays.add(weekday)
        
        # Time format validation
        if not isinstance(open_time, str):
            return f"Entry {i}: open time must be a string"
        if not isinstance(close_time, str):
            return f"Entry {i}: close time must be a string"
        
        if not time_pattern.match(open_time):
            return f"Entry {i}: open time '{open_time}' must be in HH:MM format (24-hour)"
        if not time_pattern.match(close_time):
            return f"Entry {i}: close time '{close_time}' must be in HH:MM format (24-hour)"
        
        # Logical validation: open < close (no overnight hours for now)
        open_minutes = time_to_minutes(open_time)
        close_minutes = time_to_minutes(close_time)
        
        if open_minutes >= close_minutes:
            return f"Entry {i}: open time '{open_time}' must be before close time '{close_time}'"
    
    return None


class ForevaAgent:
    """
    Foreva Voice AI Agent
    
    The phone_number is the key that uniquely identifies and wires up the AI agent.
    
    Simple Usage:
        agent = ForevaAgent(api_key, "+14155551234", "test")
        agent.set_store("Tony's Pizza", "123 Main St", "America/Los_Angeles")
        agent.set_menu(menu_data)
        agent.set_hours(hours_data)
        agent.activate()  # Shows forwarding instructions and enables AI
        
    Advanced Control:
        agent.set_order_mode(OrderMode.SMS, order_url="https://order.com")
        agent.set_forwarding_number("+14155559999")  
        agent.set_greeting("Welcome to Tony's Pizza!")
        agent.add_escalation_events(["delivery", "catering"])
        agent.enable_notifications({"sms": "+14155559999"})
        agent.set_webhook_url("https://webhook.com/orders")
    """
    
    def __init__(self, api_key: str, phone_number: str):
        """
        Initialize Foreva Voice AI Agent
        
        Args:
            api_key: Your Foreva API key
            phone_number: The phone number customers call (E.164 format)
            
        The phone_number uniquely identifies this agent.
        """
        # Validate phone number format
        phone_error = get_e164_validation_error(phone_number)
        if phone_error:
            raise ForevaValidationError(f"Invalid phone number: {phone_error}")
        
        self.api_key = api_key
        self.phone_number = phone_number
        self.agent_id = None
        self._server_config = None
        
        # Initialize API client
        self._client = ForevaAPIClient(api_key)
        
        # Get configuration from server
        self._fetch_server_config()
        
        # Show initialization info
        self._log_initialization()
        
        # Internal state
        self._context_data = {}
        self._store_data = {}
        self._hours_data = {}
        self._menu_data = {}
        self._order_mode = OrderMode.DEFAULT
        self._order_config = {}
        self._forwarding_number = None
        self._forwarding_enabled = True
        self._greeting = None
        self._escalation_events = []
        self._notifications = {}
        self._webhook_url = None
        self._is_activated = False
        
        # Auto-load existing agent if exists (phone_number is the key)
        self._load_if_exists()
    
    # ============ CONTEXT SETUP (Broken down from your draft) ============
    
    def set_store(self, name: str, address: str, timezone: str = "America/Los_Angeles", 
                  website: Optional[str] = None, category: str = "restaurant") -> 'ForevaAgent':
        """
        Set/update store information
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            name: Store name
            address: Full address
            timezone: Store timezone
            website: Store website (optional)
            category: Store category
            
        Returns:
            Self for method chaining
        """
        # Store locally
        self._store_data = {
            "name": name,
            "address": address,
            "timezone": timezone,
            "website": website,
            "category": category
        }
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print(f"🏪 Store updated: {name} (will sync on next activate/sync call)")
            else:
                print(f"🏪 Store configured: {name}")
            
        return self
    
    def set_hours(self, hours_data: List[Dict[str, Any]]) -> 'ForevaAgent':
        """
        Set/update business hours
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            hours_data: List of hour objects with weekday, open, and close times
                Format: [{"weekday": 0, "open": "11:30", "close": "21:00"}, ...]
                - weekday: 0-6 (Monday=0, Sunday=6)
                - open/close: HH:MM format in 24-hour time
                
        Returns:
            Self for method chaining
        """
        # Validate hours format
        hours_error = get_store_hours_validation_error(hours_data)
        if hours_error:
            raise ForevaValidationError(f"Invalid store hours: {hours_error}")
        
        # Store locally
        self._hours_data = hours_data
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                if hours_data:
                    print(f"🕐 Store hours updated: {len(hours_data)} day(s) (will sync on next activate/sync call)")
                else:
                    print("🕐 Store hours updated: closed all week (will sync on next activate/sync call)")
            else:
                if hours_data:
                    print(f"🕐 Store hours configured: {len(hours_data)} day(s)")
                else:
                    print("🕐 Store hours configured: closed all week")
                
        return self
    
    def set_menu(self, menu_data: Dict[str, Any]) -> 'ForevaAgent':
        """
        Set/update the restaurant menu
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            menu_data: Dictionary containing menu items and optional categories
            
        Expected menu structure:
        {
            "categories": [  # Optional: organize items into categories
                {"id": 1, "name": "Appetizers"},
                {"id": 2, "name": "Main Courses"}
            ],
            "items": [  # Required: list of menu items
                {
                    "id": 101,              # Required: unique item ID
                    "name": "Spring Rolls", # Required: item name
                    "price": 8.50,         # Required: item price
                    "category": 1,         # Optional: category ID reference
                    "desc": "Crispy vegetable spring rolls",  # Optional: description
                    "alt_name": "素春卷",   # Optional: alternative name (e.g., Chinese)
                    "customization": [     # Optional: item customizations/modifiers
                        {
                            "title": "Spice Level",    # Required: customization name
                            "required": False,          # Required: is selection required?
                            "multiple": False,          # Required: allow multiple selections?
                            "desc": "Choose your spice level",  # Optional: description
                            "options": [               # Required: available options
                                {"name": "Mild", "price": 0},
                                {"name": "Medium", "price": 0},
                                {"name": "Hot", "price": 0.50}
                            ]
                        }
                    ]
                }
            ]
        }
        
        Example - Simple menu:
            agent.set_menu({
                "items": [
                    {"id": 1, "name": "Burger", "price": 12.99, "desc": "Classic beef burger"},
                    {"id": 2, "name": "Pizza", "price": 15.99, "desc": "Margherita pizza"},
                    {"id": 3, "name": "Salad", "price": 8.99, "desc": "Fresh garden salad"}
                ]
            })
            
        Example - Menu with categories and customizations:
            agent.set_menu({
                "categories": [
                    {"id": 1, "name": "Burgers"},
                    {"id": 2, "name": "Drinks"}
                ],
                "items": [
                    {
                        "id": 101,
                        "name": "Cheeseburger",
                        "price": 13.99,
                        "category": 1,
                        "desc": "Beef patty with cheese",
                        "customization": [
                            {
                                "title": "Add-ons",
                                "required": False,
                                "multiple": True,
                                "desc": "Choose your add-ons",
                                "options": [
                                    {"name": "Bacon", "price": 2.00},
                                    {"name": "Extra Cheese", "price": 1.50},
                                    {"name": "Avocado", "price": 2.50}
                                ]
                            },
                            {
                                "title": "Cook Level",
                                "required": True,
                                "multiple": False,
                                "options": [
                                    {"name": "Rare", "price": 0},
                                    {"name": "Medium", "price": 0},
                                    {"name": "Well Done", "price": 0}
                                ]
                            }
                        ]
                    },
                    {
                        "id": 201,
                        "name": "Coke",
                        "price": 2.99,
                        "category": 2,
                        "desc": "Coca-Cola"
                    }
                ]
            })
                
        Returns:
            Self for method chaining
        """
        # Store locally
        self._menu_data = menu_data
        
        # Helpful user feedback
        if not is_debug_build():
            item_count = len(menu_data.get('items', [])) if isinstance(menu_data, dict) else 0
            if self._is_activated:
                print(f"📋 Menu updated: {item_count} items (will sync on next activate/sync call)")
            else:
                print(f"📋 Menu configured: {item_count} items")
            
        return self

    def set_context(self, context: Union[str, Dict[str, Any]], **kwargs) -> 'ForevaAgent':
        """
        Set/update business context information
        Works both before activation (initial setup) and after activation (live update)

        Args:
            context: Either a string (treated as extra_info) or a dictionary with keys:
                    - extra_info: General business information
                    - knowledge_base: Domain knowledge and FAQs
                    - special_instructions: Special handling instructions
                    - policies: Business policies (refund, delivery, etc.)
            **kwargs: Additional context fields can be passed as keyword arguments

        Returns:
            Self for method chaining
        """
        # Handle string input - treat as extra_info
        if isinstance(context, str):
            self._context_data['extra_info'] = context
        elif isinstance(context, dict):
            self._context_data.update(context)

        # Add any additional kwargs
        if kwargs:
            self._context_data.update(kwargs)

        # Helpful user feedback
        if not is_debug_build():
            if isinstance(self._context_data, dict):
                context_keys = list(self._context_data.keys())
                if self._is_activated:
                    print(f"📝 Context updated: {', '.join(context_keys)} (will sync on next activate/sync call)")
                else:
                    print(f"📝 Context configured: {', '.join(context_keys)}")
            else:
                if self._is_activated:
                    print("📝 Context updated (will sync on next activate/sync call)")
                else:
                    print("📝 Context configured")

        return self

    # ============ ORDER MODE CONTROL (From your draft) ============
    
    def set_order_mode(self, mode: OrderMode, **kwargs) -> 'ForevaAgent':
        """
        Set/update how AI handles orders
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            mode: OrderMode.DEFAULT, OrderMode.SMS, or OrderMode.STAFF
            **kwargs: Mode-specific parameters
                - For SMS mode: order_url (required)
                - For STAFF mode: forward_number (required)
                
        Examples:
            agent.set_order_mode(OrderMode.DEFAULT)  # AI processes orders
            agent.set_order_mode(OrderMode.SMS, order_url="https://order.com") # AI sends SMS with order link
            agent.set_order_mode(OrderMode.STAFF, forward_number="+14155559999") # AI forwards calls to staff
            
        Returns:
            Self for method chaining
        """
        if mode == OrderMode.SMS and not kwargs.get('order_url'):
            raise ForevaValidationError("SMS mode requires 'order_url' parameter")
        elif mode == OrderMode.STAFF and not kwargs.get('forward_number'):
            raise ForevaValidationError("STAFF mode requires 'forward_number' parameter")
            
        # Store locally
        self._order_mode = mode
        self._order_config = kwargs
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print(f"📦 Order mode updated: {mode.value} (will sync on next activate/sync call)")
            else:
                print(f"📦 Order mode configured: {mode.value}")
        
        return self
    
    # ============ CALL FORWARDING CONTROL (From your draft) ============
    
    def set_forwarding_number(self, forward_number: str) -> 'ForevaAgent':
        """
        Set/update call forwarding number for escalations
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            forward_number: Phone number to forward calls to (E.164 format)
            
        Returns:
            Self for method chaining
        """
        # Validate forwarding phone number
        phone_error = get_e164_validation_error(forward_number)
        if phone_error:
            raise ForevaValidationError(f"Invalid forwarding number: {phone_error}")
        
        # Store locally
        self._forwarding_number = forward_number
        self._forwarding_enabled = True
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print(f"☎️ Forwarding number updated: {forward_number} (will sync on next activate/sync call)")
            else:
                print(f"☎️ Forwarding number configured: {forward_number}")
        
        return self
    
    def disable_forwarding(self) -> 'ForevaAgent':
        """
        Disable call forwarding - AI will not escalate to staff
        Works both before activation (initial setup) and after activation (live update)
        
        Warning: Use carefully. Customers may get stuck if AI can't handle request.
        
        Returns:
            Self for method chaining
        """
        # Store locally
        self._forwarding_enabled = False
        self._forwarding_number = None
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print("☎️ Forwarding disabled (will sync on next activate/sync call)")
            else:
                print("☎️ Forwarding disabled")
        
        return self
    
    # ============ AI BEHAVIOR CONTROL (From your draft) ============
    
    def set_greeting(self, greeting: str) -> 'ForevaAgent':
        """
        Set/update custom greeting message
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            greeting: Custom greeting text
            
        Returns:
            Self for method chaining
        """
        # Store locally
        self._greeting = greeting
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print("💬 Greeting updated (will sync on next activate/sync call)")
            else:
                print("💬 Greeting configured")
        
        return self
    
    def set_escalation_events(self, events: Union[str, List[str]]) -> 'ForevaAgent':
        """
        Override default escalation behavior (optional)
        
        The AI handles most situations automatically including:
        - Taking orders and handling menu questions
        - Collecting info for reservations and catering
        - Escalating complaints and complex issues
        
        Only use this if you want to force specific events to always go to staff.
        
        Args:
            events: Event keywords or list of keywords to always escalate
                Examples: 
                  "delivery" - Always forward delivery questions
                  ["delivery", "catering"] - Multiple events
                  ["custom_event"] - Any custom string works
                
        Returns:
            Self for method chaining
        """
        # Handle single values
        if isinstance(events, str):
            events = [events]
        
        # Accept any strings - no validation needed
        # This allows custom events and learning what developers need
        self._escalation_events = events[:]
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print(f"🔴 Escalation events updated: {', '.join(events)} (will sync on next activate/sync call)")
            else:
                print(f"🔴 Escalation events configured: {', '.join(events)}")
        
        return self
    
    # ============ NOTIFICATIONS & WEBHOOKS ============
    
    def set_notifications(self, sms: str = None, email: str = None, **kwargs) -> 'ForevaAgent':
        """
        Set notification settings using keyword arguments
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            sms: SMS phone number for notifications (E.164 format)
            email: Email address for notifications
            **kwargs: Additional notification settings
                
        Returns:
            Self for method chaining
        """
        # Build notification config from kwargs
        notification_config = {}
        
        if sms:
            notification_config['sms'] = sms
        if email:
            notification_config['email'] = email
        
        # Add any additional kwargs
        notification_config.update(kwargs)
        
        # Validate SMS phone number if provided
        if 'sms' in notification_config:
            sms_number = notification_config['sms']
            phone_error = get_e164_validation_error(sms_number)
            if phone_error:
                raise ForevaValidationError(f"Invalid SMS notification number: {phone_error}")
        
        # Store locally
        self._notifications = notification_config
        
        # Helpful user feedback
        if not is_debug_build():
            notif_types = list(notification_config.keys())
            if self._is_activated:
                print(f"🔔 Notifications updated: {', '.join(notif_types)} (will sync on next activate/sync call)")
            else:
                print(f"🔔 Notifications configured: {', '.join(notif_types)}")
        
        return self
    
    def set_webhook_url(self, webhook_url: str) -> 'ForevaAgent':
        """
        Set/update webhook URL for order notifications
        Works both before activation (initial setup) and after activation (live update)
        
        Args:
            webhook_url: Your webhook endpoint URL
            
        The AI will POST order data to this URL when orders are placed.
        
        Returns:
            Self for method chaining
        """
        # Store locally
        self._webhook_url = webhook_url
        
        # Helpful user feedback
        if not is_debug_build():
            if self._is_activated:
                print(f"🔗 Webhook URL updated (will sync on next activate/sync call)")
            else:
                print(f"🔗 Webhook URL configured")
        
        return self
    
    # ============ ACTIVATION (Your acceptCall method) ============
    
    def activate(self) -> Dict[str, Any]:
        """
        Activate agent and get setup instructions
        
        This can only be called once per agent. After activation, use set_* methods to update.
        
        Returns:
            Server-provided setup instructions
        """
        # Check if already activated
        if self._is_activated:
            raise ForevaAPIError("Agent is already activated. Use set_* methods to update configuration.")
        
        # Validate minimum required configuration
        if not self._store_data or not self._store_data.get('name'):
            raise ForevaValidationError("Store information is required. Call set_store() first.")
        
        if not self._menu_data or not self._menu_data.get('items'):
            raise ForevaValidationError("Menu is required. Call set_menu() first.")
        
        # Hours are optional (store might be 24/7 or have special arrangements)
        # Context is optional
        
        try:
            # Send all configuration to server
            config_data = {
                "phone_number": self.phone_number,
                "store": self._store_data,
                "hours": self._hours_data,
                "menu": self._menu_data,
                "context": self._context_data,
                "order_mode": self._order_mode.value,
                "order_config": self._order_config,
                "forwarding_number": self._forwarding_number,
                "forwarding_enabled": self._forwarding_enabled,
                "greeting": self._greeting,
                "escalation_events": self._escalation_events,
                "notifications": self._notifications,
                "webhook_url": self._webhook_url
            }
            
            # Let server handle everything and return instructions
            response = self._client.setup_agent(config_data)
            
            # Extract server response
            result = response.get('data', {})
            self.agent_id = result.get('agent_id')
            
            # IMPORTANT: Only set activated flag if server confirms success
            if result.get('success', True):  # Default to True for backward compatibility
                self._is_activated = True
                
                # Log activation
                if not is_debug_build():
                    print(f"✅ Agent activated successfully for {self.phone_number}")
            else:
                raise ForevaAPIError(f"Activation failed: {result.get('error', 'Unknown error')}")
            
            # Show server-provided instructions
            self._print_server_instructions(result)
            
            return result
            
        except ForevaValidationError:
            raise  # Re-raise validation errors as-is
        except Exception as e:
            raise ForevaAPIError(f"Setup failed: {str(e)}")
    
    def sync(self) -> Dict[str, Any]:
        """
        Force immediate sync of agent with recent updates
        
        Normally changes are picked up by background processes automatically.
        Use this method when you need immediate synchronization after making updates.
        
        Can only be called on activated agents.
        
        Returns:
            Dict with sync status
            
        Raises:
            ForevaAPIError: If agent is not activated or sync fails
        """
        if not self._is_activated:
            raise ForevaAPIError("Agent must be activated before syncing. Call activate() first.")
        
        try:
            # Send all current local state to server for sync
            sync_data = {
                "phone_number": self.phone_number,
                "store": self._store_data,
                "hours": self._hours_data,
                "menu": self._menu_data,
                "context": self._context_data,
                "order_mode": self._order_mode.value,
                "order_config": self._order_config,
                "forwarding_number": self._forwarding_number,
                "forwarding_enabled": self._forwarding_enabled,
                "greeting": self._greeting,
                "escalation_events": self._escalation_events,
                "notifications": self._notifications,
                "webhook_url": self._webhook_url
            }
            
            result = self._client.sync_agent(sync_data)
            
            # Helpful user feedback
            if not is_debug_build():
                print(f"🔄 Agent sync initiated for {self.phone_number}")
                print(f"   Status: {result.get('status', 'unknown')}")
                print(f"   Message: {result.get('message', 'Sync requested')}")
            
            return result
            
        except Exception as e:
            raise ForevaAPIError(f"Sync failed: {str(e)}")
    
    # ============ GLOBAL QUERIES (New requirement) ============
    
    @classmethod
    def load(cls, api_key: str, phone_number: str) -> 'ForevaAgent':
        """
        Load an existing agent
        
        Use this when you know an agent already exists and want to update it.
        
        Args:
            api_key: Your Foreva API key
            phone_number: The phone number of the existing agent (E.164 format)
            
        Returns:
            ForevaAgent instance with loaded configuration
            
        Raises:
            ForevaNotFoundError: If no agent exists for this phone number
        """
        # Create instance (will auto-load via _load_if_exists)
        agent = cls(api_key, phone_number)
        
        # Verify it was actually loaded
        if not agent._is_activated and not agent.agent_id:
            raise ForevaNotFoundError(f"No agent found for phone number: {phone_number}")
        
        return agent
    
    @classmethod
    def list_agents(cls, api_key: str, mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all agents for this API key
        
        Args:
            api_key: Your Foreva API key
            mode: Optional filter by mode ("test" or "live")
            
        Returns:
            List of agent summaries
        """
        try:
            client = ForevaAPIClient(api_key)
            params = {"mode": mode} if mode else {}
            response = client.list_agents(params)
            
            # Server returns agents inside data object
            data = response.get('data', {})
            return data.get('agents', [])
            
        except Exception as e:
            raise ForevaAPIError(f"Failed to list agents: {str(e)}")
    
    @classmethod 
    def get_agents(cls, api_key: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all agents grouped by environment
        
        Args:
            api_key: Your Foreva API key
            
        Returns:
            Dict with 'test' and 'live' lists
        """
        return {
            'test': cls.list_agents(api_key, 'test'),
            'live': cls.list_agents(api_key, 'live')
        }
    
    # ============ STATUS & INFO ============
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and configuration with prominent mode display
        
        Returns:
            Current status information with mode details
        """
        status = {
            'phone_number': self.phone_number,
            'mode': self.mode.upper(),
            'mode_description': 'Test Mode (Free with limits)' if self.mode == 'test' else 'Live Mode (Production)',
            'agent_id': self.agent_id,
            'activated': self._is_activated,
            'store_name': self._store_data.get('name'),
            'order_mode': self._order_mode.value,
            'forwarding_enabled': self._forwarding_enabled,
            'has_greeting': bool(self._greeting),
            'has_webhook': bool(self._webhook_url),
            'escalation_events': len(self._escalation_events)
        }
        
        # Print status for user awareness
        mode_icon = "🟡" if self.mode.value == "test" else "🟢"
        print(f"\n{mode_icon} AGENT STATUS - {status['mode']} MODE")
        print(f"   📱 Phone: {self.phone_number}")
        print(f"   🏪 Store: {status['store_name'] or 'Not configured'}")
        print(f"   ✅ Active: {'Yes' if status['activated'] else 'No'}")
        print(f"   🎯 Mode: {status['mode_description']}\n")
        
        return status
    
    # ============ INTERNAL METHODS ============
    
    def _load_if_exists(self):
        """Load existing agent if it exists for this phone number"""
        try:
            params = {
                "phone_number": self.phone_number
            }
            response = self._client.load_agent(params)
            
            if response and response.get('exists'):
                # Load existing configuration
                self.agent_id = response.get('agent_id')
                # IMPORTANT: Check if agent has been activated before
                self._is_activated = response.get('is_activated', False)
                
                # Load stored configuration
                config = response.get('configuration', {})
                if config:
                    self._store_data = config.get('store', self._store_data)
                    self._hours_data = config.get('hours', self._hours_data)
                    self._menu_data = config.get('menu', self._menu_data)
                    self._order_mode = OrderMode(config.get('order_mode', 'default'))
                    self._order_config = config.get('order_config', {})
                    self._forwarding_number = config.get('forwarding_number')
                    self._forwarding_enabled = config.get('forwarding_enabled', True)
                    self._greeting = config.get('greeting')
                    self._escalation_events = config.get('escalation_events', [])
                    self._notifications = config.get('notifications', {})
                    self._webhook_url = config.get('callback_url')
                
                # Log if we loaded an activated agent
                if not is_debug_build() and self._is_activated:
                    print(f"✅ Loaded existing activated agent for {self.phone_number}")
                
        except Exception:
            # No existing agent, that's fine - will create new one
            pass
    
    def _fetch_server_config(self):
        """Fetch configuration from server"""
        try:
            self._server_config = self._client.get_config()
        except Exception as e:
            raise ForevaAPIError(f"Failed to connect to server: {str(e)}")

    @property
    def mode(self):
        """Get mode from server configuration"""
        return self._server_config.get('data', {}).get('mode') if self._server_config else None
    
    @property 
    def server_info(self):
        """Get server information for display"""
        return self._server_config.get('data', {}) if self._server_config else {}
    
    @property
    def routing_number(self):
        """Get the routing number for call forwarding setup"""
        return self._server_config.get('data', {}).get('routing_number') if self._server_config else None

    def _log_initialization(self):
        """Log initialization info based on build type"""

        if is_debug_build():
            # Debug build - show detailed internal info for development
            print(f'\n🔧 FOREVA SDK DEBUG INITIALIZED')
            print(f'   📱 Phone: {self.phone_number}')
            print(f'   🎯 Mode: {self.mode or "Loading..."}')
            print(f'   🔑 API Key: {self.api_key[:12]}...{self.api_key[-4:]}')
            if should_show_urls():
                print(f'   🌐 API URL: {self._client.base_url}')
            if should_show_internal_logs():
                print(f'   📊 Server Config: {bool(self._server_config)}')
                if self.server_info:
                    for key, value in self.server_info.items():
                        if key != 'mode':  # Already shown
                            print(f'   📋 {key}: {value}')
            print(f'   ⚠️  DEBUG BUILD - Internal development use only')
            print()
        else:
            # Production build - show helpful guidance for users
            print(f'\n🤖 Foreva AI Agent Initialized')
            print(f'   📞 Phone Number: {self.phone_number}')
            if self.mode:
                if self.mode == "test":
                    print(f'   🧪 Test Mode - Free for development')
                    print(f'   💡 Use .activate() to get setup instructions')
                else:
                    print(f'   🚀 Live Mode - Production ready')
                    print(f'   💡 Use .activate() to configure for customers')
            print(f'   📚 Next: Configure store with .set_store() then .activate()')
            print()

    def _print_server_instructions(self, result: Dict[str, Any]):
        """Print server-provided setup instructions with helpful user guidance"""

        if is_debug_build():
            # Debug build - show all server details
            print(f"\n📋 DEBUG: Server Response")
            print(f"   Raw data: {result}")
            if 'message' in result:
                print(f"   Message: {result['message']}")
        else:
            # Production build - clean, helpful guidance
            print(f"\n✅ Agent Configured Successfully!")
            
        # Show server-provided instructions (all builds)
        if 'instructions' in result:
            print(f"\n📋 Setup Instructions:")
            for instruction in result['instructions']:
                print(f"   {instruction}")
        
        # Show setup info with helpful context
        if 'setup_info' in result:
            setup = result['setup_info']
            print(f"\n📞 Your Phone Number: {setup.get('phone_number', self.phone_number)}")
            
            if 'routing_number' in setup:
                print(f"🔀 Forward calls to: {setup['routing_number']}")
                if not is_debug_build():
                    print(f"💡 Contact your phone provider to set up call forwarding")
                    
            if 'next_steps' in setup:
                print(f"\n🚀 Next Steps:")
                for step in setup['next_steps']:
                    print(f"   • {step}")
        
        if not is_debug_build():
            print(f"\n🧪 Test: Call {self.phone_number} to verify your AI agent answers!")
        
        print()  # Empty line


# ============ CONVENIENCE FUNCTIONS ============

def quick_setup(api_key: str, phone_number: str, store_name: str) -> ForevaAgent:
    """
    Quick setup for simple use cases
    
    Args:
        api_key: Your Foreva API key (mode auto-detected)
        phone_number: The key phone number
        store_name: Store name
        
    Returns:
        Configured agent ready for additional setup and activation
    """
    print(f"\n🚀 Quick Setup")
    agent = ForevaAgent(api_key, phone_number)
    agent.set_store(store_name, "Address TBD", "America/Los_Angeles")
    return agent


def quick_setup_both(test_api_key: str, live_api_key: str, phone_number: str, store_name: str) -> Dict[str, ForevaAgent]:
    """
    Quick setup for both test and live modes
    
    Args:
        test_api_key: Your test API key (foreva_test_*)
        live_api_key: Your live API key (foreva_live_*)
        phone_number: The key phone number
        store_name: Store name
        
    Returns:
        Dict with 'test' and 'live' agents
    """
    print("\n🔄 Setting up both modes")
    print("   🟡 Test mode: Development environment")
    print("   🟢 Live mode: Production environment\n")
    
    return {
        'test': quick_setup(test_api_key, phone_number, store_name),
        'live': quick_setup(live_api_key, phone_number, store_name)
    }


# ============ MENU BUILDER HELPERS (Optional) ============

class MenuBuilder:
    """
    Optional helper class for building menu structures programmatically
    
    Example:
        menu = (MenuBuilder()
            .add_category(1, "Appetizers")
            .add_category(2, "Main Courses")
            .add_item(
                id=101,
                name="Spring Rolls",
                price=8.50,
                category=1,
                desc="Crispy vegetable spring rolls"
            )
            .add_item_with_customization(
                id=201,
                name="Burger",
                price=12.99,
                category=2,
                desc="Classic beef burger",
                customizations=[
                    MenuCustomization("Toppings")
                        .add_option("Lettuce", 0)
                        .add_option("Tomato", 0)
                        .add_option("Bacon", 2.00)
                        .set_multiple(True)
                        .build()
                ]
            )
            .build()
        )
        
        agent.set_menu(menu)
    """
    
    def __init__(self):
        self.categories = []
        self.items = []
    
    def add_category(self, id: int, name: str) -> 'MenuBuilder':
        """Add a menu category"""
        self.categories.append({"id": id, "name": name})
        return self
    
    def add_item(self, id: int, name: str, price: float, 
                 category: int = None, desc: str = None, 
                 alt_name: str = None) -> 'MenuBuilder':
        """Add a simple menu item"""
        item = {
            "id": id,
            "name": name,
            "price": price
        }
        if category is not None:
            item["category"] = category
        if desc:
            item["desc"] = desc
        if alt_name:
            item["alt_name"] = alt_name
        
        self.items.append(item)
        return self
    
    def add_item_with_customization(self, id: int, name: str, price: float,
                                   customizations: list,
                                   category: int = None, desc: str = None,
                                   alt_name: str = None) -> 'MenuBuilder':
        """Add a menu item with customizations"""
        item = {
            "id": id,
            "name": name,
            "price": price,
            "customization": customizations
        }
        if category is not None:
            item["category"] = category
        if desc:
            item["desc"] = desc
        if alt_name:
            item["alt_name"] = alt_name
            
        self.items.append(item)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final menu structure"""
        menu = {"items": self.items}
        if self.categories:
            menu["categories"] = self.categories
        return menu


class MenuCustomization:
    """
    Helper for building menu item customizations
    
    Example:
        customization = (MenuCustomization("Size")
            .add_option("Small", -1.00)
            .add_option("Regular", 0)
            .add_option("Large", 2.00)
            .set_required(True)
            .build()
        )
    """
    
    def __init__(self, title: str, desc: str = None):
        self.customization = {
            "title": title,
            "required": False,
            "multiple": False,
            "options": []
        }
        if desc:
            self.customization["desc"] = desc
    
    def add_option(self, name: str, price: float) -> 'MenuCustomization':
        """Add an option to this customization"""
        self.customization["options"].append({
            "name": name,
            "price": price
        })
        return self
    
    def set_required(self, required: bool) -> 'MenuCustomization':
        """Set whether this customization is required"""
        self.customization["required"] = required
        return self
    
    def set_multiple(self, multiple: bool) -> 'MenuCustomization':
        """Set whether multiple selections are allowed"""
        self.customization["multiple"] = multiple
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the customization structure"""
        return self.customization