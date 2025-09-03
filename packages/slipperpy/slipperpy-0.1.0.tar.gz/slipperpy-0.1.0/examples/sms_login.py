#!/usr/bin/env python3
"""Simple SMS login example for SlipperPy."""

import asyncio
import os

from slipperpy import SlipperClient
from slipperpy.exceptions import AuthenticationError, GraphQLError, NetworkError


async def sms_login_example():
    """Example of SMS-based login flow."""
    # Get phone number from environment or user input
    phone = os.getenv("SLIPPER_PHONE")
    if not phone:
        phone = input("Enter your phone number (e.g., +47123456789): ")
    
    # Initialize client
    client = SlipperClient("https://api.slipper.no/graphql")
    
    try:
        print(f"📱 Requesting SMS code for {phone}...")
        
        # Step 1: Request SMS code
        success = await client.request_sms_code(phone)
        
        if not success:
            print("❌ Failed to send SMS code. Please check your phone number.")
            return
        
        print("✅ SMS code sent!")
        
        # Step 2: Get SMS code from user
        while True:
            try:
                sms_code = input("📩 Enter the SMS code you received: ")
                sms_code_int = int(sms_code)
                break
            except ValueError:
                print("❌ Please enter a valid numeric code")
        
        # Step 3: Login with SMS code
        print("🔐 Verifying SMS code...")
        token = await client.login_with_sms_code(phone, sms_code_int)
        
        print("🎉 Successfully logged in!")
        
        # Test the authentication by getting user info
        user = await client.get_current_user()
        if user:
            print(f"👋 Welcome, {user.first_name} {user.last_name}!")
            print(f"📧 Email: {user.email}")
        else:
            print("⚠️  Could not retrieve user information")
        
        # Get homes to verify API access
        homes = await client.get_homes()
        print(f"🏠 You have {len(homes)} homes registered")
        
        for i, home in enumerate(homes, 1):
            print(f"  {i}. {home.name or 'Unnamed'} - {home.city}")
    
    except AuthenticationError as e:
        print(f"❌ Authentication error: {e.message}")
        print("💡 This could mean:")
        print("   - Invalid SMS code")
        print("   - Code expired (codes typically expire after a few minutes)")
        print("   - Phone number not registered")
    except NetworkError as e:
        print(f"❌ Network error: {e.message}")
        print("💡 Check your internet connection and endpoint URL")
    except GraphQLError as e:
        print(f"❌ API error: {e.message}")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    print("🔐 SlipperPy SMS Login Example")
    print("=" * 40)
    asyncio.run(sms_login_example())
