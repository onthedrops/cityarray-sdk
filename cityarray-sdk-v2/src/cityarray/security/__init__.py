"""
CITYARRAY Security Module

Implements "Trust No Edge" security architecture:
- Cryptographic message signing (Ed25519)
- Signature verification
- Alert tier classification
- Tamper-evident audit logging
- Key management (software MVP / HSM production)
"""

from .signing import MessageSigner, MessageVerifier, SignedMessage
from .audit import AuditLogger, AuditEvent, AuditEventType
from .tiers import AlertTier, TierAuthorization, requires_authorization
from .keys import KeyManager, SoftwareKeyStore, HSMKeyStore

__all__ = [
    # Signing
    "MessageSigner",
    "MessageVerifier", 
    "SignedMessage",
    # Audit
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    # Tiers
    "AlertTier",
    "TierAuthorization",
    "requires_authorization",
    # Keys
    "KeyManager",
    "SoftwareKeyStore",
    "HSMKeyStore",
]
