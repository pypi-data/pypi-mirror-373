#!/usr/bin/env python3
"""
Example usage of the Gymix Python SDK.

This script demonstrates how to use the main features of the Gymix API client.
"""

import os
from gymix import GymixClient
from gymix.exceptions import GymixAPIError, GymixAuthenticationError


def main():
    """Main example function."""
    
    # Initialize the client with your API token
    # You can get your API token from the Gymix dashboard
    api_token = os.getenv("GYMIX_API_TOKEN")
    if not api_token:
        print("Please set the GYMIX_API_TOKEN environment variable")
        return
    
    # Create the client
    client = GymixClient(api_token=api_token)
    
    try:
        # 1. Get user information
        print("=== User Information ===")
        user_info = client.users.get_info()
        print(f"User: {user_info['name']} {user_info['lastname']}")
        print(f"Phone: {user_info['phone']}")
        print(f"Balance: {user_info['balance']:,} تومان")
        print(f"Number of gyms: {len(user_info['gyms'])}")
        
        if not user_info['gyms']:
            print("No gyms found for this user.")
            return
        
        # Use the first gym for examples
        gym = user_info['gyms'][0]
        gym_public_key = gym['id']
        
        print(f"\nUsing gym: {gym['name']} ({gym['location']})")
        
        # 2. Get gym detailed information
        print("\n=== Gym Information ===")
        gym_info = client.gym.get_info(gym_public_key)
        
        gym_data = gym_info['gym_info']
        subscription = gym_info['subscription_info']
        plan = gym_info['plan_info']
        
        print(f"Gym: {gym_data['name']}")
        print(f"Location: {gym_data['location']}")
        print(f"Status: {gym_data['status']}")
        
        print(f"\nSubscription: {subscription['name']}")
        print(f"Price: {subscription['price']:,} تومان")
        print(f"Remaining days: {subscription['remaining_days']}")
        print(f"Usage: {subscription['usage_percentage']:.1f}%")
        
        print(f"\nPlan: {plan['name']}")
        print(f"Features: Backup={plan['features']['includes_backup']}, "
              f"Support={plan['features']['includes_support']}")
        
        # 3. Check backup plan
        print("\n=== Backup Plan ===")
        backup_plan = client.backup.get_plan(gym_public_key)
        
        plan_info = backup_plan['plan_info']
        usage = backup_plan['current_usage']
        
        print(f"Max backups: {plan_info['max_backups']}")
        print(f"Current backups: {usage['backup_count']}")
        print(f"Backups today: {usage['today_backup_count']}")
        print(f"Can create more today: {usage['can_create_more_today']}")
        
        # 4. List existing backups
        print("\n=== Existing Backups ===")
        backups = client.backup.list(gym_public_key)
        
        if backups['backups']:
            for backup in backups['backups']:
                print(f"- {backup['file_name']} (ID: {backup['id']})")
                print(f"  Created: {backup['created_at']}")
        else:
            print("No backups found.")
        
        # 5. Create a backup (example - you would provide a real file)
        print("\n=== Creating Backup (Example) ===")
        print("To create a backup, you would use:")
        print("with open('backup.zip', 'rb') as f:")
        print("    backup = client.backup.create(gym_public_key, f)")
        
        # 6. Health check
        print("\n=== API Health Check ===")
        health = client.health.check()
        print(f"API Status: {health['status']}")
        print(f"Version: {health['version']}")
        print(f"Database: {health['database']}")
        print(f"Storage: {health['storage']}")
        
    except GymixAuthenticationError:
        print("Authentication failed. Please check your API token.")
    except GymixAPIError as e:
        print(f"API Error: {e}")
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
