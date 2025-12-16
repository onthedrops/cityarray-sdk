"""
CITYARRAY SDK

AI-powered emergency communication platform SDK.
Implements "Trust No Edge" security architecture.

Components:
- Detection: AI-powered object/event detection (YOLOv8)
- Decision: Alert classification and routing
- Display: Secure message rendering with signature verification
- TTS: Multilingual text-to-speech
- Security: Cryptographic signing, audit logging, tier authorization

Usage:
    from cityarray import CityArraySDK
    
    sdk = CityArraySDK(device_id="my-device")
    sdk.start()
"""

__version__ = "0.2.0"
__author__ = "CITYARRAY Team"

from .sdk import CityArraySDK
from .security import (
    MessageSigner,
    MessageVerifier,
    SignedMessage,
    AuditLogger,
    AlertTier,
    KeyManager,
    SoftwareKeyStore,
)

__all__ = [
    "CityArraySDK",
    "MessageSigner",
    "MessageVerifier",
    "SignedMessage",
    "AuditLogger",
    "AlertTier",
    "KeyManager",
    "SoftwareKeyStore",
]
