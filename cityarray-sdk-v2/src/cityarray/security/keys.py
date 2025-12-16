"""
Key Management

Manages cryptographic keys for message signing.

MVP: Software-based key storage (encrypted at rest)
Production: HSM integration (keys never extractable)

Key Hierarchy:
- Root CA Key: Offline, air-gapped
- Intermediate CA Key: HSM-protected
- Message Signing Key: HSM-protected
- Device Identity Key: Per-device, for mTLS
"""

import os
import json
import logging
import hashlib
import secrets
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import cryptography
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography library not available")


@dataclass
class KeyInfo:
    """Metadata about a key (without the actual key material)."""
    key_id: str
    key_type: str  # signing, identity, encryption
    algorithm: str  # ed25519, x25519, aes256
    created_at: str
    expires_at: Optional[str]
    public_key_hex: Optional[str]  # For asymmetric keys


class KeyStore(ABC):
    """Abstract base class for key storage backends."""
    
    @abstractmethod
    def generate_signing_key(self, key_id: str) -> KeyInfo:
        """Generate a new signing key pair."""
        pass
    
    @abstractmethod
    def get_public_key(self, key_id: str) -> bytes:
        """Get public key bytes for a key ID."""
        pass
    
    @abstractmethod
    def sign(self, key_id: str, data: bytes) -> bytes:
        """Sign data with the specified key."""
        pass
    
    @abstractmethod
    def list_keys(self) -> list[KeyInfo]:
        """List all keys in the store."""
        pass
    
    @abstractmethod
    def delete_key(self, key_id: str) -> bool:
        """Delete a key (if allowed by policy)."""
        pass


class SoftwareKeyStore(KeyStore):
    """
    Software-based key storage for MVP/development.
    
    Keys are encrypted at rest using a password-derived key.
    
    WARNING: This is NOT suitable for production deployment
    where keys must be protected by HSM.
    """
    
    def __init__(self, storage_path: Path, password: Optional[str] = None):
        """
        Initialize software key store.
        
        Args:
            storage_path: Directory to store encrypted keys
            password: Password for key encryption (prompts if None)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._keys: Dict[str, Any] = {}
        self._encryption_key: Optional[bytes] = None
        
        if CRYPTO_AVAILABLE:
            self._init_encryption(password)
            self._load_keys()
        else:
            logger.warning("Running without encryption - DEVELOPMENT ONLY")
    
    def _init_encryption(self, password: Optional[str]) -> None:
        """Initialize encryption key from password."""
        if password is None:
            # In production, this should prompt or use secure key injection
            password = os.environ.get("CITYARRAY_KEY_PASSWORD", "development-only")
            logger.warning("Using default/environment password - NOT FOR PRODUCTION")
        
        # Derive encryption key using scrypt
        salt_file = self.storage_path / ".salt"
        if salt_file.exists():
            salt = salt_file.read_bytes()
        else:
            salt = secrets.token_bytes(16)
            salt_file.write_bytes(salt)
        
        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
        self._encryption_key = kdf.derive(password.encode())
    
    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data with AES-GCM."""
        if not CRYPTO_AVAILABLE or self._encryption_key is None:
            return data
        
        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(self._encryption_key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext
    
    def _decrypt(self, data: bytes) -> bytes:
        """Decrypt data with AES-GCM."""
        if not CRYPTO_AVAILABLE or self._encryption_key is None:
            return data
        
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(self._encryption_key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    def _load_keys(self) -> None:
        """Load existing keys from disk."""
        for key_file in self.storage_path.glob("*.key"):
            try:
                encrypted = key_file.read_bytes()
                decrypted = self._decrypt(encrypted)
                key_data = json.loads(decrypted)
                key_id = key_file.stem
                self._keys[key_id] = key_data
                logger.debug(f"Loaded key {key_id}")
            except Exception as e:
                logger.error(f"Failed to load key {key_file}: {e}")
    
    def _save_key(self, key_id: str, key_data: Dict[str, Any]) -> None:
        """Save a key to disk."""
        key_file = self.storage_path / f"{key_id}.key"
        plaintext = json.dumps(key_data).encode()
        encrypted = self._encrypt(plaintext)
        key_file.write_bytes(encrypted)
        self._keys[key_id] = key_data
    
    def generate_signing_key(self, key_id: str) -> KeyInfo:
        """Generate a new Ed25519 signing key pair."""
        if key_id in self._keys:
            raise ValueError(f"Key {key_id} already exists")
        
        from datetime import datetime, timezone
        
        if CRYPTO_AVAILABLE:
            private_key = Ed25519PrivateKey.generate()
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        else:
            # Development stub
            private_bytes = secrets.token_bytes(32)
            public_bytes = hashlib.sha256(private_bytes).digest()
        
        now = datetime.now(timezone.utc).isoformat()
        
        key_data = {
            "key_type": "signing",
            "algorithm": "ed25519",
            "private_key": private_bytes.hex(),
            "public_key": public_bytes.hex(),
            "created_at": now,
            "expires_at": None
        }
        
        self._save_key(key_id, key_data)
        
        logger.info(f"Generated new signing key: {key_id}")
        
        return KeyInfo(
            key_id=key_id,
            key_type="signing",
            algorithm="ed25519",
            created_at=now,
            expires_at=None,
            public_key_hex=public_bytes.hex()
        )
    
    def get_public_key(self, key_id: str) -> bytes:
        """Get public key bytes."""
        if key_id not in self._keys:
            raise KeyError(f"Key {key_id} not found")
        
        return bytes.fromhex(self._keys[key_id]["public_key"])
    
    def sign(self, key_id: str, data: bytes) -> bytes:
        """Sign data with Ed25519."""
        if key_id not in self._keys:
            raise KeyError(f"Key {key_id} not found")
        
        private_bytes = bytes.fromhex(self._keys[key_id]["private_key"])
        
        if CRYPTO_AVAILABLE:
            private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
            return private_key.sign(data)
        else:
            # Development stub
            return hashlib.sha256(private_bytes + data).digest()
    
    def list_keys(self) -> list[KeyInfo]:
        """List all keys."""
        result = []
        for key_id, key_data in self._keys.items():
            result.append(KeyInfo(
                key_id=key_id,
                key_type=key_data["key_type"],
                algorithm=key_data["algorithm"],
                created_at=key_data["created_at"],
                expires_at=key_data.get("expires_at"),
                public_key_hex=key_data.get("public_key")
            ))
        return result
    
    def delete_key(self, key_id: str) -> bool:
        """Delete a key."""
        if key_id not in self._keys:
            return False
        
        key_file = self.storage_path / f"{key_id}.key"
        if key_file.exists():
            key_file.unlink()
        
        del self._keys[key_id]
        logger.info(f"Deleted key {key_id}")
        return True


class HSMKeyStore(KeyStore):
    """
    HSM-based key storage for production.
    
    Keys are stored in a Hardware Security Module and never
    leave the HSM boundary. Only the public key is accessible.
    
    Supports:
    - AWS CloudHSM
    - Azure Dedicated HSM
    - Google Cloud HSM
    - Thales Luna
    - Yubico HSM
    """
    
    def __init__(self, hsm_config: Dict[str, Any]):
        """
        Initialize HSM connection.
        
        Args:
            hsm_config: HSM-specific configuration
                - provider: aws, azure, gcp, thales, yubico
                - credentials: Provider-specific credentials
                - partition: HSM partition/slot
        """
        self.provider = hsm_config.get("provider", "stub")
        self.config = hsm_config
        
        logger.info(f"Initializing HSM connection: {self.provider}")
        
        # Provider-specific initialization would go here
        # For now, we stub it out
        if self.provider == "stub":
            logger.warning("Using HSM stub - NOT FOR PRODUCTION")
            self._stub_store = SoftwareKeyStore(
                Path("./hsm_stub"),
                password="hsm-stub-password"
            )
    
    def generate_signing_key(self, key_id: str) -> KeyInfo:
        """Generate key in HSM (key never leaves HSM)."""
        if self.provider == "stub":
            return self._stub_store.generate_signing_key(key_id)
        
        # Real HSM implementation would use PKCS#11 or provider SDK
        raise NotImplementedError(f"HSM provider {self.provider} not implemented")
    
    def get_public_key(self, key_id: str) -> bytes:
        """Get public key from HSM."""
        if self.provider == "stub":
            return self._stub_store.get_public_key(key_id)
        
        raise NotImplementedError(f"HSM provider {self.provider} not implemented")
    
    def sign(self, key_id: str, data: bytes) -> bytes:
        """Sign data using key in HSM (private key never exposed)."""
        if self.provider == "stub":
            return self._stub_store.sign(key_id, data)
        
        raise NotImplementedError(f"HSM provider {self.provider} not implemented")
    
    def list_keys(self) -> list[KeyInfo]:
        """List keys in HSM."""
        if self.provider == "stub":
            return self._stub_store.list_keys()
        
        raise NotImplementedError(f"HSM provider {self.provider} not implemented")
    
    def delete_key(self, key_id: str) -> bool:
        """Delete key from HSM (may require additional authorization)."""
        if self.provider == "stub":
            return self._stub_store.delete_key(key_id)
        
        raise NotImplementedError(f"HSM provider {self.provider} not implemented")


class KeyManager:
    """
    High-level key management interface.
    
    Manages key lifecycle and provides signing operations.
    """
    
    def __init__(self, key_store: KeyStore, default_key_id: str = "default"):
        """
        Initialize key manager.
        
        Args:
            key_store: Backend key storage
            default_key_id: Default key ID for signing operations
        """
        self.store = key_store
        self.default_key_id = default_key_id
        
        # Ensure default key exists
        try:
            self.store.get_public_key(default_key_id)
        except KeyError:
            logger.info(f"Generating default signing key: {default_key_id}")
            self.store.generate_signing_key(default_key_id)
    
    @property
    def public_key(self) -> bytes:
        """Get default public key."""
        return self.store.get_public_key(self.default_key_id)
    
    def sign(self, data: bytes, key_id: Optional[str] = None) -> bytes:
        """Sign data with the specified or default key."""
        kid = key_id or self.default_key_id
        return self.store.sign(kid, data)
    
    def rotate_key(self, new_key_id: Optional[str] = None) -> KeyInfo:
        """
        Rotate the signing key.
        
        Creates a new key and updates the default.
        Old key is retained for verification of existing signatures.
        """
        from datetime import datetime, timezone
        
        if new_key_id is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            new_key_id = f"signing-{ts}"
        
        key_info = self.store.generate_signing_key(new_key_id)
        
        old_default = self.default_key_id
        self.default_key_id = new_key_id
        
        logger.info(f"Rotated signing key: {old_default} -> {new_key_id}")
        return key_info
