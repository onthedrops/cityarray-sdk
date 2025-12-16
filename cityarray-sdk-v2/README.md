# CITYARRAY SDK v0.2.0

**AI-Powered Emergency Communication Platform**

*"Trust No Edge" Security Architecture*

---

## Overview

CITYARRAY SDK enables autonomous AI-powered LED signage for crisis communication. The SDK provides detection, decision-making, and secure display capabilities with built-in cryptographic security.

### Key Features

- 🔐 **Cryptographic Message Signing** - Every displayed message is cryptographically signed (Ed25519)
- 📋 **Tamper-Evident Audit Logging** - Hash-chained logs detect any tampering
- 🎯 **Alert Tier System** - Automatic classification with authorization requirements
- 🤖 **AI Detection Integration** - YOLOv8-based object/event detection
- 🌍 **Multilingual TTS** - Text-to-speech in 15+ languages
- 🔒 **HSM Support** - Production-ready hardware security module integration

---

## Security Architecture

The SDK implements "Trust No Edge" security:

```
┌─────────────────────────────────────────────────────────────┐
│                    TRUSTED CLOUD                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Alert Queue │  │  Operator   │  │   HSM (Signing)     │  │
│  │ + Validate  │  │  Dashboard  │  │   Keys NEVER leave  │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         └────────────────┴─────────────────────┘            │
│                          │ Signed Commands Only             │
└──────────────────────────┬──────────────────────────────────┘
                           │ mTLS + Certificate Pinning
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                UNTRUSTED EDGE DEVICE                         │
│  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Camera │→ │Detection │→ │ Decision │→ │    Display    │  │
│  │Sensors │  │ (YOLOv8) │  │  Engine  │  │(Signed only!) │  │
│  └────────┘  └──────────┘  └────┬─────┘  └───────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Alert Tiers

| Tier | Examples | Authorization | Max Latency |
|------|----------|---------------|-------------|
| **Informational** | Crowd count, weather | Autonomous | < 1 sec |
| **Advisory** | Congestion, rain expected | Autonomous | < 2 sec |
| **Warning** | Smoke detected | Single operator | < 60 sec |
| **Emergency** | Fire confirmed, evacuate | Multi-party (2 of 3) | < 120 sec |
| **IPAWS** | Amber Alert, NWS warning | Pass-through | < 5 sec |

---

## Installation

```bash
# Core SDK
pip install cityarray-sdk

# With detection support
pip install cityarray-sdk[detection]

# With all features
pip install cityarray-sdk[all]

# Development
pip install cityarray-sdk[dev]
```

---

## Quick Start

```python
from cityarray import CityArraySDK

# Initialize SDK
sdk = CityArraySDK(device_id="demo-device-001")
sdk.start()

# Display an informational message (autonomous)
sdk.display_message(
    template_id="crowd-count",
    tier="informational",
    params={"count": 1250},
    text={"en": "Current attendance: 1,250"}
)

# Process a detection
tier = sdk.process_detection(
    detection_type="smoke",
    confidence=0.85,
    details={"location": "north_exit", "camera_id": "cam-03"}
)
# Returns: AlertTier.WARNING (requires operator confirmation)

# Verify audit chain integrity
is_valid, broken = sdk.verify_audit_chain()
print(f"Audit chain valid: {is_valid}")

# Clean shutdown
sdk.stop()
```

---

## Security Components

### Message Signing

```python
from cityarray.security import MessageSigner, MessageVerifier, SignedMessage

# Cloud side: Sign messages
signer = MessageSigner(private_key_bytes)
message = signer.create_signed_message(
    device_id="device-001",
    tier="warning",
    content={"template_id": "smoke-detected", "params": {"location": "Exit A"}},
    ttl_seconds=900
)

# Edge side: Verify before display
verifier = MessageVerifier(public_key_bytes, device_id="device-001")
try:
    verifier.verify(message)
    # Safe to display
except SignatureError:
    # REJECT - do not display
```

### Audit Logging

```python
from cityarray.security import AuditLogger, AuditEventType

audit = AuditLogger(device_id="device-001", log_path="./audit.log")

# Log events
audit.log_message_displayed("msg-123", "warning", "abc123")
audit.log_signature_invalid("msg-456", "Invalid signature")

# Verify chain integrity
is_valid, broken_sequences = audit.verify_chain()
```

### Key Management

```python
from cityarray.security import KeyManager, SoftwareKeyStore, HSMKeyStore

# Development: Software keys
store = SoftwareKeyStore("./keys", password="dev-password")
keys = KeyManager(store)

# Production: HSM keys
hsm_store = HSMKeyStore({"provider": "aws", "region": "us-east-1"})
keys = KeyManager(hsm_store)

# Sign data
signature = keys.sign(data_bytes)

# Rotate keys
new_key = keys.rotate_key()
```

---

## Project Structure

```
cityarray-sdk/
├── src/cityarray/
│   ├── __init__.py          # Package entry point
│   ├── sdk.py                # Main SDK orchestration
│   ├── security/
│   │   ├── __init__.py
│   │   ├── signing.py        # Ed25519 message signing
│   │   ├── audit.py          # Tamper-evident logging
│   │   ├── tiers.py          # Alert tier classification
│   │   └── keys.py           # Key management (Software/HSM)
│   ├── display/
│   │   ├── __init__.py
│   │   └── secure_engine.py  # Secure display with verification
│   ├── detection/            # AI detection (YOLOv8)
│   ├── decision/             # Alert routing logic
│   └── tts/                  # Multilingual text-to-speech
├── tests/
├── examples/
├── docs/
├── pyproject.toml
└── README.md
```

---

## Configuration

```python
from cityarray import CityArraySDK, SDKConfig
from pathlib import Path

config = SDKConfig(
    device_id="device-001",
    data_dir=Path("/var/cityarray"),
    key_password="secure-password",  # Or use env: CITYARRAY_KEY_PASSWORD
    cloud_endpoint="https://api.cityarray.ai",
    offline_mode=False,
    log_level="INFO"
)

sdk = CityArraySDK(device_id="device-001", config=config)
```

---

## Version History

### v0.2.0 (December 2024)
- ✅ "Trust No Edge" security architecture
- ✅ Ed25519 message signing
- ✅ Tamper-evident audit logging
- ✅ Alert tier system with authorization
- ✅ HSM key management interface
- ✅ Secure display engine

### v0.1.0 (December 2024)
- Initial SDK structure
- Basic detection/decision/display pipeline

---

## License

Proprietary - CITYARRAY Team

---

## Support

- GitHub Issues: https://github.com/onthedrops/cityarray-sdk/issues
- Email: dev@cityarray.ai
