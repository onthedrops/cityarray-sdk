"""
Cryptographic Message Signing

All display commands must be cryptographically signed.
Uses Ed25519 (EdDSA) for fast verification and small signatures.

Security Properties:
- Messages include timestamp and nonce to prevent replay attacks
- Device ID binding prevents message redirection
- Expiration prevents stale message display
"""

import json
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import cryptography library, fall back to stub for development
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey, Ed25519PublicKey
    )
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography library not available - using development stubs")


class SignatureError(Exception):
    """Raised when signature verification fails."""
    pass


class MessageExpiredError(Exception):
    """Raised when a message has expired."""
    pass


class ReplayDetectedError(Exception):
    """Raised when a replay attack is detected."""
    pass


@dataclass
class Authorization:
    """Record of an authorization for a message."""
    operator_id: str
    timestamp: str
    method: str = "dashboard"  # dashboard, api, auto
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Authorization":
        return cls(**data)


@dataclass
class SignedMessage:
    """
    A cryptographically signed display message.
    
    All fields except 'signature' are included in the signed payload.
    The signature covers the canonical JSON representation.
    """
    message_id: str
    device_id: str
    timestamp: str
    expires: str
    nonce: str
    tier: str
    content: Dict[str, Any]
    authorizations: List[Authorization] = field(default_factory=list)
    signature: Optional[str] = None
    
    def payload_for_signing(self) -> bytes:
        """Generate canonical payload for signing (excludes signature field)."""
        payload = {
            "message_id": self.message_id,
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "expires": self.expires,
            "nonce": self.nonce,
            "tier": self.tier,
            "content": self.content,
            "authorizations": [a.to_dict() for a in self.authorizations]
        }
        # Canonical JSON: sorted keys, no whitespace
        return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "expires": self.expires,
            "nonce": self.nonce,
            "tier": self.tier,
            "content": self.content,
            "authorizations": [a.to_dict() for a in self.authorizations],
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignedMessage":
        authorizations = [
            Authorization.from_dict(a) for a in data.get("authorizations", [])
        ]
        return cls(
            message_id=data["message_id"],
            device_id=data["device_id"],
            timestamp=data["timestamp"],
            expires=data["expires"],
            nonce=data["nonce"],
            tier=data["tier"],
            content=data["content"],
            authorizations=authorizations,
            signature=data.get("signature")
        )
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        expires_dt = datetime.fromisoformat(self.expires.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires_dt
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "SignedMessage":
        return cls.from_dict(json.loads(json_str))


class MessageSigner:
    """
    Signs messages for display.
    
    In production, this runs in the cloud with HSM-protected keys.
    For MVP/development, software keys are acceptable.
    """
    
    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize signer with private key.
        
        Args:
            private_key: Ed25519 private key bytes (32 bytes seed or 64 bytes full)
                        If None, generates a new key (development only!)
        """
        if not CRYPTO_AVAILABLE:
            logger.warning("Crypto not available - signatures will be development stubs")
            self._private_key = None
            self._public_key_bytes = b"DEVELOPMENT_PUBLIC_KEY_STUB_32B"
            return
            
        if private_key is None:
            logger.warning("Generating ephemeral signing key - DEVELOPMENT ONLY")
            self._private_key = Ed25519PrivateKey.generate()
        else:
            self._private_key = Ed25519PrivateKey.from_private_bytes(private_key[:32])
        
        self._public_key_bytes = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    @property
    def public_key(self) -> bytes:
        """Get public key bytes for distribution to verifiers."""
        return self._public_key_bytes
    
    def sign(self, message: SignedMessage) -> SignedMessage:
        """
        Sign a message.
        
        Args:
            message: Message to sign (signature field will be set)
            
        Returns:
            Same message with signature field populated
        """
        payload = message.payload_for_signing()
        
        if not CRYPTO_AVAILABLE or self._private_key is None:
            # Development stub - NOT SECURE
            stub_sig = hashlib.sha256(payload).hexdigest()
            message.signature = f"DEV:{stub_sig}"
            logger.warning(f"Using development stub signature for message {message.message_id}")
        else:
            signature = self._private_key.sign(payload)
            message.signature = signature.hex()
        
        logger.info(f"Signed message {message.message_id} for device {message.device_id}")
        return message
    
    def create_signed_message(
        self,
        device_id: str,
        tier: str,
        content: Dict[str, Any],
        ttl_seconds: int = 300,
        authorizations: Optional[List[Authorization]] = None
    ) -> SignedMessage:
        """
        Create and sign a new message.
        
        Args:
            device_id: Target device ID
            tier: Alert tier (informational, advisory, warning, emergency)
            content: Message content (template_id, params, etc.)
            ttl_seconds: Time-to-live in seconds (default 5 minutes)
            authorizations: List of authorizations (required for warning/emergency)
            
        Returns:
            Signed message ready for transmission
        """
        now = datetime.now(timezone.utc)
        
        message = SignedMessage(
            message_id=secrets.token_hex(16),
            device_id=device_id,
            timestamp=now.isoformat().replace('+00:00', 'Z'),
            expires=(now + timedelta(seconds=ttl_seconds)).isoformat().replace('+00:00', 'Z'),
            nonce=secrets.token_hex(16),
            tier=tier,
            content=content,
            authorizations=authorizations or []
        )
        
        return self.sign(message)


class MessageVerifier:
    """
    Verifies message signatures on edge devices.
    
    CRITICAL: This is the last line of defense.
    If verification fails, the message MUST NOT be displayed.
    """
    
    def __init__(self, public_key: bytes, device_id: str):
        """
        Initialize verifier.
        
        Args:
            public_key: Ed25519 public key bytes (32 bytes)
            device_id: This device's ID (messages for other devices rejected)
        """
        self.device_id = device_id
        self._seen_nonces: set = set()  # For replay detection
        self._max_nonces = 10000  # Limit memory usage
        
        if not CRYPTO_AVAILABLE:
            logger.warning("Crypto not available - using development stub verification")
            self._public_key = None
            return
        
        self._public_key = Ed25519PublicKey.from_public_bytes(public_key)
    
    def verify(self, message: SignedMessage) -> bool:
        """
        Verify a signed message.
        
        Checks:
        1. Signature is valid
        2. Message is for this device
        3. Message has not expired
        4. Message has not been seen before (replay protection)
        
        Args:
            message: Message to verify
            
        Returns:
            True if all checks pass
            
        Raises:
            SignatureError: Invalid signature
            MessageExpiredError: Message has expired
            ReplayDetectedError: Nonce has been seen before
            ValueError: Message is for different device
        """
        # Check device ID
        if message.device_id != self.device_id and message.device_id != "*":
            raise ValueError(f"Message for device {message.device_id}, not {self.device_id}")
        
        # Check expiration
        if message.is_expired():
            raise MessageExpiredError(f"Message {message.message_id} expired at {message.expires}")
        
        # Check replay
        if message.nonce in self._seen_nonces:
            raise ReplayDetectedError(f"Nonce {message.nonce} already seen - replay attack?")
        
        # Verify signature
        if message.signature is None:
            raise SignatureError("Message has no signature")
        
        payload = message.payload_for_signing()
        
        if not CRYPTO_AVAILABLE or self._public_key is None:
            # Development stub verification
            if message.signature.startswith("DEV:"):
                expected = f"DEV:{hashlib.sha256(payload).hexdigest()}"
                if message.signature != expected:
                    raise SignatureError("Invalid development stub signature")
                logger.warning(f"Accepted development stub signature for {message.message_id}")
            else:
                raise SignatureError("Production signature but crypto not available")
        else:
            try:
                signature_bytes = bytes.fromhex(message.signature)
                self._public_key.verify(signature_bytes, payload)
            except InvalidSignature:
                raise SignatureError(f"Invalid signature for message {message.message_id}")
            except ValueError as e:
                raise SignatureError(f"Malformed signature: {e}")
        
        # Record nonce (after all checks pass)
        self._seen_nonces.add(message.nonce)
        if len(self._seen_nonces) > self._max_nonces:
            # Remove oldest half (simple LRU approximation)
            to_remove = list(self._seen_nonces)[:self._max_nonces // 2]
            for nonce in to_remove:
                self._seen_nonces.discard(nonce)
        
        logger.info(f"Verified message {message.message_id} (tier: {message.tier})")
        return True
    
    def verify_safe(self, message: SignedMessage) -> tuple[bool, Optional[str]]:
        """
        Verify without raising exceptions.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.verify(message)
            return True, None
        except (SignatureError, MessageExpiredError, ReplayDetectedError, ValueError) as e:
            return False, str(e)
