# Terminal Chat Encryption Architecture

This document provides a comprehensive overview of the encryption implementation in Terminal Chat, including the algorithms used, key management, security considerations, and technical details.

---

## Table of Contents

1. [Overview](#overview)
2. [Encryption Algorithm](#encryption-algorithm)
3. [Key Management](#key-management)
4. [Message Flow](#message-flow)
5. [Implementation Details](#implementation-details)
6. [Security Considerations](#security-considerations)
7. [Threat Model](#threat-model)
8. [Limitations](#limitations)
9. [Future Improvements](#future-improvements)

---

## Overview

Terminal Chat implements **end-to-end encryption (E2EE)** to ensure message privacy. Messages are encrypted on the sender's device and can only be decrypted by the intended recipients.

### Key Features

- ✅ **End-to-End Encryption**: Server cannot read message contents
- ✅ **Symmetric Encryption**: Fast and efficient using Fernet
- ✅ **Client-Side Key Generation**: Keys never leave user's device
- ✅ **Encrypted Storage**: Messages stored encrypted in database
- ❌ **Perfect Forward Secrecy**: Not implemented (shared static key)
- ❌ **Key Exchange Protocol**: Not implemented (manual key sharing required)

### Security Level

**Current Implementation**: **Basic E2EE**
- Suitable for casual private conversations
- Not suitable for high-security applications
- Server operator could theoretically intercept if they wanted to

**Recommended Use Cases:**
- Personal chat
- Small team communication
- Learning/educational purposes

**NOT Recommended For:**
- Classified information
- Legal/financial communications
- Whistleblowing
- High-risk activism

---

## Encryption Algorithm

### Fernet (Symmetric Encryption)

Terminal Chat uses **Fernet** from the Python `cryptography` library.

#### Technical Specifications

- **Algorithm**: AES-128 in CBC mode
- **Authentication**: HMAC-SHA256
- **Encoding**: Base64 URL-safe
- **Library**: `cryptography.fernet.Fernet`

#### Why Fernet?

**Advantages:**
1. **Simple API**: Easy to implement correctly
2. **Authenticated Encryption**: Prevents tampering (HMAC)
3. **Built-in Timestamp**: Messages include creation time
4. **Battle-tested**: Used in production systems
5. **Python Standard**: Part of PyCA cryptography

**Disadvantages:**
1. **Symmetric Only**: Same key encrypts and decrypts
2. **No Perfect Forward Secrecy**: Key compromise = all messages compromised
3. **Limited to Python**: Cross-platform requires compatible implementation

#### Encryption Format

Encrypted message structure (Base64 encoded):
```
gAAAAABmE2jQ... (Fernet token)
```

Decoded Fernet token structure:
```
Version (1 byte) | Timestamp (8 bytes) | IV (16 bytes) | Ciphertext | HMAC (32 bytes)
```

---

## Key Management

### Key Generation

**Location**: `shared/crypto.py`

```python
def get_or_create_encryption():
    """Get existing or create new encryption instance"""
    key_path = Path.home() / ".terminal-chat" / "encryption.key"

    if key_path.exists():
        with open(key_path, "rb") as f:
            key = f.read()
    else:
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)

    return Fernet(key)
```

### Key Storage

**Client Side:**
- **Path**: `~/.terminal-chat/encryption.key`
- **Format**: Raw binary key (32 bytes, Base64 encoded)
- **Permissions**: Should be `600` (read/write for owner only)
- **Generated**: On first run if not present

**Example Key:**
```
b'1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR='
```

### Key Distribution

**Current Method**: **Manual Key Sharing**

For users to communicate:
1. All users must use the **same encryption key**
2. Key must be **manually copied** to each device
3. Key file: `~/.terminal-chat/encryption.key`

**Process:**
```bash
# On User A's device (generate key)
python -m client.main
# Key created at ~/.terminal-chat/encryption.key

# Copy key to User B
scp ~/.terminal-chat/encryption.key userB@remote:~/.terminal-chat/

# Or manually copy the key file
cat ~/.terminal-chat/encryption.key
# Then paste into ~/.terminal-chat/encryption.key on User B's device
```

**Security Warning:**
- Keys shared over insecure channels can be intercepted
- Use secure methods to share keys (in person, encrypted email, etc.)

### Key Rotation

**Status**: **Not Implemented**

Key rotation would require:
1. Re-encrypting all existing messages with new key
2. Distributing new key to all users
3. Maintaining backward compatibility

Currently, the key is **static** and never rotates.

---

## Message Flow

### Encryption Flow (Sending)

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ 1. User types message
     ▼
┌──────────────────┐
│ Original Message │
│ "Hello, World!"  │
└────┬─────────────┘
     │ 2. Encrypt with Fernet
     ▼
┌──────────────────────────────────────┐
│ Encrypted Message                    │
│ gAAAAABmE2jQ7Xk... (Base64)          │
└────┬─────────────────────────────────┘
     │ 3. Send via WebSocket
     ▼
┌──────────┐
│  Server  │
└────┬─────┘
     │ 4. Store encrypted in database
     ▼
┌──────────────────────┐
│ Database (encrypted) │
│ gAAAAABmE2jQ7Xk...   │
└────┬─────────────────┘
     │ 5. Broadcast encrypted to all clients
     ▼
┌──────────┐
│  Clients │
└──────────┘
```

### Decryption Flow (Receiving)

```
┌──────────┐
│  Server  │
└────┬─────┘
     │ 1. Broadcast encrypted message
     ▼
┌──────────┐
│  Client  │
└────┬─────┘
     │ 2. Receive encrypted message
     ▼
┌──────────────────────────────────────┐
│ Encrypted Message                    │
│ gAAAAABmE2jQ7Xk... (Base64)          │
└────┬─────────────────────────────────┘
     │ 3. Decrypt with Fernet
     ▼
┌──────────────────┐
│ Original Message │
│ "Hello, World!"  │
└────┬─────────────┘
     │ 4. Display to user
     ▼
┌──────────┐
│  Screen  │
└──────────┘
```

### What the Server Sees

**Server's View:**
```json
{
  "type": "message",
  "user_id": 1,
  "username": "alice",
  "content": "gAAAAABmE2jQ7XkPqR...",
  "timestamp": "2025-01-15T10:30:00"
}
```

The server sees:
- ✅ Who sent the message (`user_id`, `username`)
- ✅ When it was sent (`timestamp`)
- ✅ Encrypted content (meaningless without key)
- ❌ **CANNOT** see actual message text

---

## Implementation Details

### Encryption Code

**Location**: `shared/crypto.py`

```python
from cryptography.fernet import Fernet
from pathlib import Path
import os

class EncryptionManager:
    """Manages message encryption and decryption"""

    def __init__(self, key: bytes = None):
        if key:
            self.fernet = Fernet(key)
        else:
            self.fernet = Fernet(Fernet.generate_key())

    def encrypt(self, message: str) -> str:
        """Encrypt a message"""
        if not isinstance(message, str):
            raise TypeError("Message must be a string")

        encrypted = self.fernet.encrypt(message.encode('utf-8'))
        return encrypted.decode('utf-8')

    def decrypt(self, encrypted_message: str) -> str:
        """Decrypt a message"""
        if not isinstance(encrypted_message, str):
            raise TypeError("Encrypted message must be a string")

        decrypted = self.fernet.decrypt(encrypted_message.encode('utf-8'))
        return decrypted.decode('utf-8')
```

### Client Usage

**Location**: `client/main.py`

```python
from shared.crypto import get_or_create_encryption

# Initialize encryption
self.encryption = get_or_create_encryption()

# Encrypt before sending
encrypted_message = self.encryption.encrypt(message)
await self.connection.send_message(encrypted_message)

# Decrypt when receiving
content = self.encryption.decrypt(encrypted_content)
chat_screen.add_message(username, content, timestamp)
```

### Server Storage

**Location**: `server/main.py`

```python
# Server receives encrypted message
content = message_data.get("content", "")  # Encrypted!

# Store encrypted in database
new_message = Message(
    user_id=user_id,
    content=content,  # Still encrypted
    room_id=message_data.get("room_id", "general")
)
db.add(new_message)
db.commit()

# Broadcast encrypted to all clients
broadcast_data = json.dumps({
    "type": "message",
    "content": new_message.content,  # Still encrypted!
    "username": user.username,
    "timestamp": new_message.timestamp.isoformat()
})
await manager.broadcast(broadcast_data)
```

---

## Security Considerations

### Strengths

1. **Server Cannot Read Messages**
   - Server stores only encrypted blobs
   - Database compromise doesn't expose content
   - Server operator has no access to plaintext

2. **Authenticated Encryption**
   - HMAC prevents message tampering
   - Recipients know message hasn't been modified
   - Protects against man-in-the-middle attacks (on message content)

3. **Timestamp Validation**
   - Fernet includes timestamp in token
   - Can detect replay attacks
   - Can implement message expiration

### Weaknesses

1. **Shared Static Key**
   - All users use the same key
   - Key compromise = all messages compromised
   - No per-conversation keys

2. **No Key Exchange Protocol**
   - Keys must be shared manually
   - Insecure key distribution is possible
   - No automatic key verification

3. **No Perfect Forward Secrecy**
   - Old messages vulnerable if key is compromised
   - Key compromise affects past AND future messages
   - No session-specific keys

4. **Metadata Exposed**
   - Server sees: who, when, to whom
   - Traffic analysis possible
   - Doesn't hide communication patterns

5. **No User Authentication of Keys**
   - Users can't verify they have the correct key
   - Possible man-in-the-middle during key distribution
   - No key fingerprints or verification

6. **Single Point of Failure**
   - One key for all messages
   - Key loss = cannot decrypt any messages
   - No key recovery mechanism

---

## Threat Model

### What We Protect Against

✅ **Passive Server Operator**
- Server admin can't read messages
- Database breach doesn't expose content
- Server logs don't contain plaintext

✅ **Database Compromise**
- Stolen database only contains encrypted messages
- No value without encryption keys

✅ **Message Tampering**
- HMAC prevents modification of messages in transit
- Recipients can detect if messages were altered

### What We DON'T Protect Against

❌ **Active Attacker with Key**
- If attacker gets encryption key, all messages are readable
- Past and future messages compromised

❌ **Compromised Client**
- Malware on client can read messages before encryption
- Keylogger can capture typed messages
- Compromised client can steal encryption key

❌ **Man-in-the-Middle During Key Exchange**
- Attacker can intercept key during manual sharing
- No verification that received key is correct

❌ **Traffic Analysis**
- Server sees who talks to whom and when
- Message sizes visible (encrypted size ≈ plaintext size)
- Communication patterns exposed

❌ **Endpoint Compromise**
- If device is compromised, all bets are off
- Screen capture, keylogging, etc. bypass encryption

---

## Limitations

### Current Limitations

1. **No Per-User Encryption**
   - Everyone uses the same key
   - Can't have private conversations

2. **No Key Verification**
   - Can't verify key is correct
   - No key fingerprints

3. **No Key Rotation**
   - Key is static forever
   - Can't change keys without losing access to old messages

4. **No Perfect Forward Secrecy**
   - Key compromise affects all messages
   - No session keys

5. **Manual Key Distribution**
   - Users must manually share keys
   - Error-prone and potentially insecure

6. **No Multi-Device Support**
   - Each device generates its own key
   - Messages encrypted on one device can't be read on another

---

## Future Improvements

### Recommended Enhancements

#### 1. Implement Signal Protocol
**Benefits:**
- Perfect forward secrecy
- Per-session keys
- Proven security
- Used by WhatsApp, Signal

**Complexity:** High

#### 2. Add Public Key Infrastructure (PKI)
**Benefits:**
- Per-user key pairs
- No shared keys
- Secure key exchange

**Complexity:** Medium

#### 3. Implement Key Rotation
**Benefits:**
- Limit damage from key compromise
- Regularly refresh keys
- Backward compatibility for old messages

**Complexity:** Medium

#### 4. Add Key Verification
**Benefits:**
- Users can verify they have correct key
- Detect MITM attacks
- QR codes or fingerprints

**Complexity:** Low

#### 5. Implement Sealed Sender
**Benefits:**
- Hide sender metadata
- Server doesn't know who sent what
- Better privacy

**Complexity:** High

### Migration Path

**Phase 1**: Add key verification (fingerprints)
**Phase 2**: Implement per-user keys (PKI)
**Phase 3**: Add key rotation
**Phase 4**: Implement Signal Protocol
**Phase 5**: Add sealed sender

---

## Best Practices for Users

### Protecting Your Encryption Key

1. **Secure Storage**
   ```bash
   # Set restrictive permissions
   chmod 600 ~/.terminal-chat/encryption.key
   ```

2. **Backup Safely**
   ```bash
   # Encrypted backup
   gpg -c ~/.terminal-chat/encryption.key
   ```

3. **Never Share Publicly**
   - Don't commit to Git
   - Don't send via email (unencrypted)
   - Don't post in chat

4. **Secure Key Distribution**
   - Share in person if possible
   - Use encrypted channels (PGP, Signal, etc.)
   - Verify key fingerprint after exchange

### Verifying Key Integrity

```bash
# Generate SHA256 fingerprint
sha256sum ~/.terminal-chat/encryption.key

# Compare with other users
# Should match exactly if using same key
```

---

## Technical References

### Cryptography Libraries

- **Python cryptography**: https://cryptography.io/
- **Fernet Spec**: https://github.com/fernet/spec/
- **AES**: https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
- **HMAC**: https://en.wikipedia.org/wiki/HMAC

### Encryption Protocols

- **Signal Protocol**: https://signal.org/docs/
- **Double Ratchet**: https://signal.org/docs/specifications/doubleratchet/
- **X3DH**: https://signal.org/docs/specifications/x3dh/

### Security Resources

- **OWASP Cryptography**: https://owasp.org/www-community/Cryptography
- **Crypto101**: https://www.crypto101.io/
- **Serious Cryptography** (book by Jean-Philippe Aumasson)

---

## Conclusion

Terminal Chat provides **basic end-to-end encryption** suitable for casual private conversations. While the current implementation protects against passive server operators and database breaches, it has limitations that make it unsuitable for high-security applications.

For casual use and learning, the current encryption is adequate. For production use with sensitive data, consider implementing the recommended enhancements (Signal Protocol, PKI, key rotation).

---

**Version**: 1.0.0
**Last Updated**: 2025-01-18
**Security Audit**: Not performed

For security questions or to report vulnerabilities, contact: security@example.com
