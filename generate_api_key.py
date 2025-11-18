#!/usr/bin/env python3
"""
Quick script to generate a new API key for testing
"""
from services.auth_service import AuthService

def main():
    auth_service = AuthService()

    # Generate new key for default user
    plaintext_key, api_key_record = auth_service.generate_api_key(
        user_id="default",
        name="Testing Key"
    )

    print("\n" + "="*60)
    print("NEW API KEY GENERATED")
    print("="*60)
    print(f"\nAPI Key: {plaintext_key}")
    print(f"\nKey ID: {api_key_record.id}")
    print(f"User ID: {api_key_record.user_id}")
    print(f"Name: {api_key_record.name}")
    print("\n⚠️  IMPORTANT: Save this key now! It won't be shown again.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
