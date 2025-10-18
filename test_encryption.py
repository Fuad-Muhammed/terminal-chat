"""
Simple script to test encryption functionality
"""

from shared.crypto import get_or_create_encryption

# Initialize encryption
enc = get_or_create_encryption()

# Test messages
test_messages = [
    "Hello, world!",
    "This is a secret message 🔒",
    "Special chars: <>&\"'",
    "Long message: " + "a" * 100
]

print("=" * 60)
print("ENCRYPTION TEST")
print("=" * 60)
print()

for msg in test_messages:
    print(f"Original: {msg[:50]}...")

    # Encrypt
    encrypted = enc.encrypt(msg)
    print(f"Encrypted: {encrypted[:50]}...")

    # Decrypt
    decrypted = enc.decrypt(encrypted)
    print(f"Decrypted: {decrypted[:50]}...")

    # Verify
    if msg == decrypted:
        print("✓ PASS - Encryption/decryption successful")
    else:
        print("✗ FAIL - Decryption doesn't match original")

    print()

from pathlib import Path
key_path = Path.home() / ".terminal-chat" / "encryption.key"
print("=" * 60)
print(f"Encryption key location: {key_path}")
print("=" * 60)
