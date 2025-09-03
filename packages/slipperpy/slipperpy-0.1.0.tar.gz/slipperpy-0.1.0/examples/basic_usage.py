#!/usr/bin/env python3
"""Example script showing how to use SlipperPy."""

import asyncio
import os
from datetime import datetime, timedelta

from slipperpy import SlipperClient
from slipperpy.exceptions import AuthenticationError, GraphQLError, NetworkError


async def main():
    """Main example function."""
    # Get configuration from environment variables
    phone = os.getenv("SLIPPER_PHONE")
    sms_code = os.getenv("SLIPPER_SMS_CODE")  # Optional: if you already have a code
    
    if not phone:
        print("Please set SLIPPER_PHONE environment variable")
        print("Example: export SLIPPER_PHONE='+47123456789'")
        return

    # Create client
    client = SlipperClient()
    
    try:
        token = None
        # read token from file if exists
        if os.path.exists("slipper_token.txt"):
            with open("slipper_token.txt", "r") as f:
                token = f.read().strip()
        if token:
            client.token = token
            client.set_auth_token(token)
            print("✓ Loaded token from slipper_token.txt")
        else:
            print("⚠️  slipper_token.txt is empty, will request new SMS code")

            if not sms_code:
                # Step 1: Request SMS code
                print(f"Requesting SMS code for phone: {phone}")
                await client.request_sms_code(phone)
                print("✓ SMS code sent!")
                sms_code = input("Enter the SMS code you received: ")
                if not sms_code:
                    return
            
            # Step 2: Login with SMS code
            print("Verifying SMS code...")
            try:
                token = await client.login_with_sms_code(phone, int(sms_code))
                print(f"✓ Successfully logged in!")
            except ValueError:
                print("❌ Invalid SMS code format. Please enter numbers only.")
                return
            
            # save token to file
            with open("slipper_token.txt", "w") as f:
                f.write(token)
            print("✓ Token saved to slipper_token.txt")
        
        # Get current user
        user = await client.get_current_user()
        if user:
            print(f"Welcome, {user.first_name} {user.last_name}!")
        
        # Get homes
        print("\nFetching homes...")
        homes = await client.get_homes()
        print(f"Found {len(homes)} homes:")
        
        for home in homes:
            print(f"  - {home.name or 'Unnamed'} at {home.street} {home.street_number}, {home.city}")
            print(f"    Meter ID: {home.meter_id}")
            print(f"    Estimated yearly consumption: {home.estimated_yearly_consumption} kWh")
            if home.current_plan:
                print(f"    Current plan: {home.current_plan.id}")
        
        # Get consumption data for the first home
        if homes:
            home = homes[0]
            print(f"\nFetching consumption data for {home.name or 'first home'}...")
            
            # Get data for the last 7 days
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=7)
            
            consumptions = await client.get_consumptions(
                home_id=home.id,
                start=start_date,
                end=end_date,
                granularity="DAILY"
            )
            
            print(f"Found {len(consumptions)} consumption records:")
            total_kwh = 0
            total_cost = 0
            
            for consumption in consumptions[-5:]:  # Show last 5 days
                print(f"  {consumption.date.strftime('%Y-%m-%d')}: "
                      f"{consumption.kwh} kWh, {consumption.cost} NOK")
                total_kwh += float(consumption.kwh)
                total_cost += float(consumption.cost)
            
            if consumptions:
                print(f"  Total (last 5 days): {total_kwh:.1f} kWh, {total_cost:.2f} NOK")
        
        # Get electricity prices for today
        print("\nFetching electricity prices for today...")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        try:
            prices = await client.get_electricity_prices(
                start=today,
                end=tomorrow,
                granularity="HOURLY",
                area="NO1"
            )
            
            if prices:
                print(f"Found {len(prices)} hourly prices for today:")
                current_hour = datetime.now().hour
                
                # Show current hour and next few hours
                for price in prices[current_hour:current_hour+4]:
                    hour = price.date.strftime('%H:%M')
                    print(f"  {hour}: {price.priceKwh} øre/kWh")

                # Show daily average
                avg_price = sum(float(p.priceKwh) for p in prices) / len(prices)
                print(f"  Average today: {avg_price:.2f} øre/kWh")
            else:
                print("No price data available for today")
        except GraphQLError as e:
            print(f"Could not fetch electricity prices: {e.message}")
        
        # Get available plans
        print("\nFetching available electricity plans...")
        try:
            plans = await client.get_plans(active=True)
            print(f"Found {len(plans)} active plans:")
            
            for plan in plans[:5]:  # Show first 5 plans
                print(f"  - {plan.name}")
                print(f"    Provider: {plan.provider or 'Unknown'}")
                print(f"    Price: {plan.price_per_kwh} øre/kWh + {plan.fixed_fee} NOK/month")
        except GraphQLError as e:
            print(f"Could not fetch plans: {e.message}")

        # get devices
        print("\nFetching devices...")
        try:            
            devices = await client.get_devices()
            print(f"Found {len(devices)} devices:")
            for device in devices:
                print(f"  - {device.name} (ID: {device.id}, Type: {device.type}) fingerprint: {device.fingerprint} firebase_registration_token: {device.firebase_registration_token}")
        except GraphQLError as e:
            print(f"Could not fetch devices: {e.message}")

    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e.message}")
    except NetworkError as e:
        print(f"❌ Network error: {e.message}")
    except GraphQLError as e:
        print(f"❌ GraphQL error: {e.message}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
