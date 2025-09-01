"""
Foreva AI SDK - Quick Start Examples
Updated examples for the current SDK implementation
"""

import os
from foreva_ai import ForevaAgent, MenuBuilder, MenuCustomization, OrderMode

def example_basic_setup():
    """
    Example 1: Basic restaurant setup
    Complete setup with menu, hours, and activation
    """
    print("🍕 Example 1: Basic Restaurant Setup")
    print("-" * 50)
    
    # Get API key from environment (never hardcode it!)
    api_key = os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE')
    phone_number = "+14155551234"  # Your phone number
    
    try:
        # Step 1: Create agent
        print("1️⃣ Creating agent...")
        agent = ForevaAgent(api_key, phone_number)
        print(f"✅ Agent created in {agent.mode} mode")
        
        # Step 2: Set store information
        print("2️⃣ Setting store information...")
        agent.set_store(
            name="Tony's Pizza",
            address="123 Main St, San Francisco, CA 94110",
            timezone="America/Los_Angeles",
            website="https://tonypizza.com",
            category="Pizza"
        )
        
        # Step 3: Set business hours
        print("3️⃣ Setting business hours...")
        hours = [
            {"weekday": 0, "open": "11:00", "close": "21:00"},  # Monday
            {"weekday": 1, "open": "11:00", "close": "22:00"},  # Tuesday
            {"weekday": 2, "open": "11:00", "close": "22:00"},  # Wednesday
            {"weekday": 3, "open": "11:00", "close": "22:00"},  # Thursday
            {"weekday": 4, "open": "11:00", "close": "23:00"},  # Friday
            {"weekday": 5, "open": "12:00", "close": "23:00"},  # Saturday
            {"weekday": 6, "open": "12:00", "close": "21:00"}   # Sunday
        ]
        agent.set_hours(hours)
        
        # Step 4: Build and set menu
        print("4️⃣ Building menu...")
        menu = (MenuBuilder()
            .add_category(1, "Pizza")
            .add_category(2, "Drinks")
            
            .add_item(
                id=101,
                name="Margherita",
                price=18.99,
                category=1,
                desc="Fresh mozzarella, tomato, basil"
            )
            .add_item(
                id=102,
                name="Pepperoni",
                price=20.99,
                category=1,
                desc="Classic pepperoni with mozzarella"
            )
            .add_item(
                id=201,
                name="Coke",
                price=2.99,
                category=2,
                desc="Coca-Cola"
            )
            .build()
        )
        agent.set_menu(menu)
        
        # Step 5: Configure additional settings
        print("5️⃣ Configuring additional settings...")
        agent.set_greeting("Hello! Welcome to Tony's Pizza. How can I help you today?")
        agent.set_forwarding_number("+14155559999")  # Your staff phone
        agent.set_webhook_url("https://your-pos-system.com/webhooks/orders")
        
        # Step 6: Activate the agent
        print("6️⃣ Activating agent...")
        result = agent.activate()
        
        print(f"\n✅ Success! Your voice AI is configured")
        print(f"📞 Customer phone: {phone_number}")
        print(f"🔀 Forward calls to: {result.get('routing_number', 'N/A')}")
        print(f"🎯 Agent ID: {result.get('agent_id', 'N/A')}")
        print(f"🎭 Mode: {result.get('mode', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")


def example_order_modes():
    """
    Example 2: Different order handling modes
    """
    print("\n🎯 Example 2: Order Handling Modes")
    print("-" * 50)
    
    api_key = os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE')
    phone_number = "+14155552345"
    
    try:
        agent = ForevaAgent(api_key, phone_number)
        
        # Basic setup
        agent.set_store("Demo Restaurant", "456 Demo St", "America/Los_Angeles")
        agent.set_menu({
            "items": [
                {"id": 1, "name": "Demo Item", "price": 10.99}
            ]
        })
        
        # Mode 1: AI handles everything (default)
        agent.set_order_mode(OrderMode.DEFAULT)
        print("🤖 Mode: AI processes orders automatically")
        
        # Mode 2: Send SMS with ordering link
        agent.set_order_mode(OrderMode.SMS, order_url="https://order.demo.com")
        print("📱 Mode: AI sends SMS with ordering link")
        
        # Mode 3: Forward to staff for orders
        agent.set_order_mode(OrderMode.STAFF, forward_number="+14155557777")
        print("👥 Mode: AI forwards order calls to staff")
        
        # Activate
        result = agent.activate()
        print(f"✅ Agent configured with order modes: {result.get('agent_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Order modes example failed: {e}")


def example_menu_with_customizations():
    """
    Example 3: Menu with customizations/modifiers
    """
    print("\n🍔 Example 3: Menu with Customizations")
    print("-" * 50)
    
    api_key = os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE')
    phone_number = "+14155553456"
    
    try:
        agent = ForevaAgent(api_key, phone_number)
        agent.set_store("Bob's Burgers", "Ocean Avenue, SF", "America/Los_Angeles")
        
        # Build menu with customizations
        menu = (MenuBuilder()
            .add_category(1, "Burgers")
            
            .add_item_with_customization(
                id=101,
                name="Cheeseburger",
                price=13.99,
                category=1,
                desc="Beef patty with cheese",
                customizations=[
                    MenuCustomization("Add-ons")
                        .add_option("Bacon", 2.00)
                        .add_option("Extra Cheese", 1.50)
                        .add_option("Avocado", 2.50)
                        .set_multiple(True)  # Allow multiple selections
                        .build(),
                    
                    MenuCustomization("Cook Level")
                        .add_option("Rare", 0)
                        .add_option("Medium", 0)
                        .add_option("Well Done", 0)
                        .set_required(True)  # Must select one
                        .build()
                ]
            )
            .build()
        )
        
        agent.set_menu(menu)
        agent.activate()
        
        print("✅ Menu with customizations configured!")
        
    except Exception as e:
        print(f"❌ Menu customization example failed: {e}")


def example_live_updates():
    """
    Example 4: Update existing agent configuration
    """
    print("\n🔄 Example 4: Live Updates")
    print("-" * 50)
    
    api_key = os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE')
    phone_number = "+14155551234"
    
    try:
        # Load existing agent
        print("Loading existing agent...")
        agent = ForevaAgent.load(api_key, phone_number)
        print(f"✅ Loaded agent in {agent.mode} mode")
        
        # Update context
        print("Updating context...")
        agent.set_context("Now offering lunch specials from 11am-2pm!")
        
        # Update hours
        print("Updating hours...")
        new_hours = [
            {"weekday": 0, "open": "10:00", "close": "23:00"},  # Extended Monday hours
        ]
        agent.set_hours(new_hours)
        
        # Sync changes
        print("Syncing changes...")
        result = agent.sync()
        print(f"✅ Updates synced: {result.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Live update example failed: {e}")


def example_list_agents():
    """
    Example 5: List and manage multiple agents
    """
    print("\n📋 Example 5: List Agents")
    print("-" * 50)
    
    api_key = os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE')
    
    try:
        # List all agents for this API key
        print("Listing all agents...")
        agents = ForevaAgent.list_agents(api_key, mode='test')
        
        print(f"📋 Found {len(agents)} test mode agents:")
        for agent_info in agents:
            print(f"  • Phone: {agent_info.get('phone_number', 'N/A')}")
            print(f"    Store: {agent_info.get('store_name', 'Unknown')}")
            print(f"    Status: {agent_info.get('status', 'unknown')}")
            print(f"    Created: {agent_info.get('created_at', 'N/A')}")
        
        # Get both test and live agents
        all_agents = ForevaAgent.get_agents(api_key)
        print(f"\n📊 Total agents:")
        print(f"  Test mode: {len(all_agents.get('test', []))}")
        print(f"  Live mode: {len(all_agents.get('live', []))}")
        
    except Exception as e:
        print(f"❌ List agents example failed: {e}")


def example_escalation_events():
    """
    Example 6: Configure escalation events
    """
    print("\n🔴 Example 6: Escalation Events")
    print("-" * 50)
    
    api_key = os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE')
    phone_number = "+14155554567"
    
    try:
        agent = ForevaAgent(api_key, phone_number)
        agent.set_store("Test Restaurant", "789 Test St", "America/Los_Angeles")
        agent.set_menu({"items": [{"id": 1, "name": "Test Item", "price": 9.99}]})
        
        # Set forwarding number for escalations
        agent.set_forwarding_number("+14155559999")
        
        # Configure which events trigger escalation to staff
        agent.set_escalation_events([
            "delivery",     # Forward delivery questions
            "catering",     # Forward catering requests
            "complaint"     # Forward complaints
        ])
        
        # Set up notifications
        agent.set_notifications(
            sms="+14155559999",      # SMS notifications to this number
            email="manager@demo.com"  # Email notifications
        )
        
        agent.activate()
        print("✅ Escalation events configured!")
        
    except Exception as e:
        print(f"❌ Escalation example failed: {e}")


if __name__ == "__main__":
    print("🎉 Foreva AI SDK Quick Start Examples")
    print("=" * 50)
    print("Using the current SDK implementation\n")
    
    # Note about API key
    if 'YOUR_KEY_HERE' in os.getenv('FOREVA_API_KEY', 'foreva_test_YOUR_KEY_HERE'):
        print("⚠️  Using default test key. Set FOREVA_API_KEY environment variable:")
        print("   export FOREVA_API_KEY='foreva_test_YOUR_ACTUAL_KEY'")
        print()
    
    # Run examples (comment out ones you don't want to run)
    example_basic_setup()
    example_order_modes()
    example_menu_with_customizations()
    # example_live_updates()  # Only works if you have existing agents
    example_list_agents()
    example_escalation_events()
    
    print("\n✨ Examples completed!")
    print("📚 See test_local_server.py for more comprehensive testing")