"""
CITYARRAY SDK - Main Orchestration

Ties together all SDK components with integrated security.
"""

import logging
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass

from .security.signing import MessageSigner, MessageVerifier, SignedMessage
from .security.audit import AuditLogger, AuditEventType
from .security.tiers import AlertTier, TierAuthorization, get_tier_for_detection
from .security.keys import KeyManager, SoftwareKeyStore
from .display.secure_engine import SecureDisplayEngine, ConsoleDisplayBackend

logger = logging.getLogger(__name__)


@dataclass
class SDKConfig:
    """SDK configuration."""
    device_id: str
    data_dir: Path = Path("./cityarray_data")
    key_password: Optional[str] = None
    cloud_endpoint: Optional[str] = None
    offline_mode: bool = False
    log_level: str = "INFO"


class CityArraySDK:
    """
    Main CITYARRAY SDK class.
    
    Provides unified interface to all SDK components with
    integrated security enforcement.
    """
    
    def __init__(self, device_id: str, config: Optional[SDKConfig] = None):
        """
        Initialize CITYARRAY SDK.
        
        Args:
            device_id: Unique device identifier
            config: Optional SDK configuration
        """
        self.config = config or SDKConfig(device_id=device_id)
        self.device_id = self.config.device_id
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        # Create data directory
        self.config.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self._init_security()
        self._init_display()
        
        # State
        self._running = False
        self._detection_callbacks: List[Callable] = []
        
        logger.info(f"CITYARRAY SDK initialized for device {device_id}")
    
    def _init_security(self) -> None:
        """Initialize security components."""
        # Key management
        key_store = SoftwareKeyStore(
            storage_path=self.config.data_dir / "keys",
            password=self.config.key_password
        )
        self.key_manager = KeyManager(key_store)
        
        # Message signing (for cloud/testing)
        self.signer = MessageSigner(None)  # Generates ephemeral key for dev
        
        # Message verification (for edge)
        self.verifier = MessageVerifier(
            public_key=self.signer.public_key,
            device_id=self.device_id
        )
        
        # Audit logging
        self.audit = AuditLogger(
            device_id=self.device_id,
            log_path=self.config.data_dir / "audit.log"
        )
        
        # Log boot
        from . import __version__
        self.audit.log_boot(
            version=__version__,
            config_hash="development"
        )
        
        logger.info("Security components initialized")
    
    def _init_display(self) -> None:
        """Initialize display components."""
        # Default to console backend
        backend = ConsoleDisplayBackend()
        
        self.display = SecureDisplayEngine(
            device_id=self.device_id,
            backend=backend,
            verifier=self.verifier,
            audit_logger=self.audit
        )
        
        logger.info("Display engine initialized")
    
    def start(self) -> None:
        """Start the SDK."""
        if self._running:
            logger.warning("SDK already running")
            return
        
        self._running = True
        logger.info("CITYARRAY SDK started")
    
    def stop(self) -> None:
        """Stop the SDK."""
        if not self._running:
            return
        
        self._running = False
        self.display.clear()
        
        self.audit.log(AuditEventType.SYSTEM_SHUTDOWN, {
            "reason": "normal"
        })
        
        logger.info("CITYARRAY SDK stopped")
    
    # =========================================================================
    # DISPLAY OPERATIONS
    # =========================================================================
    
    def display_message(
        self,
        template_id: str,
        tier: str = "informational",
        params: Optional[Dict[str, Any]] = None,
        text: Optional[Dict[str, str]] = None,
        ttl_seconds: int = 300
    ) -> bool:
        """
        Display a message (signs and verifies internally for dev/testing).
        
        In production, messages come pre-signed from cloud.
        
        Args:
            template_id: Message template identifier
            tier: Alert tier (informational, advisory, warning, emergency)
            params: Template parameters
            text: Localized text {"en": "...", "es": "..."}
            ttl_seconds: Time-to-live
            
        Returns:
            True if message was displayed
        """
        content = {
            "template_id": template_id,
            "params": params or {},
            "text": text or {}
        }
        
        # Create and sign message
        signed = self.signer.create_signed_message(
            device_id=self.device_id,
            tier=tier,
            content=content,
            ttl_seconds=ttl_seconds
        )
        
        # Display (will verify signature)
        result = self.display.display(signed)
        return result.success
    
    def display_signed_message(self, message: SignedMessage) -> bool:
        """
        Display a pre-signed message (from cloud).
        
        Args:
            message: Signed message from cloud
            
        Returns:
            True if message was displayed
        """
        result = self.display.display(message)
        return result.success
    
    def clear_display(self) -> bool:
        """Clear the display."""
        return self.display.clear()
    
    # =========================================================================
    # DETECTION OPERATIONS
    # =========================================================================
    
    def register_detection_callback(
        self,
        callback: Callable[[str, float, Dict[str, Any]], None]
    ) -> None:
        """
        Register a callback for detection events.
        
        Args:
            callback: Function(detection_type, confidence, details)
        """
        self._detection_callbacks.append(callback)
    
    def process_detection(
        self,
        detection_type: str,
        confidence: float,
        details: Optional[Dict[str, Any]] = None
    ) -> AlertTier:
        """
        Process a detection event.
        
        Determines appropriate tier and logs the detection.
        Does NOT automatically display - that requires authorization
        for warning/emergency tiers.
        
        Args:
            detection_type: Type of detection
            confidence: Detection confidence (0.0 to 1.0)
            details: Additional detection details
            
        Returns:
            Determined alert tier
        """
        tier = get_tier_for_detection(detection_type, confidence)
        
        self.audit.log_detection(
            detection_type=detection_type,
            confidence=confidence,
            details=details or {}
        )
        
        # Notify callbacks
        for callback in self._detection_callbacks:
            try:
                callback(detection_type, confidence, details or {})
            except Exception as e:
                logger.error(f"Detection callback error: {e}")
        
        logger.info(f"Detection: {detection_type} (conf={confidence:.2f}) -> tier={tier.value}")
        
        return tier
    
    # =========================================================================
    # AUTHORIZATION WORKFLOW
    # =========================================================================
    
    def request_authorization(
        self,
        tier: AlertTier,
        detection_type: str,
        details: Dict[str, Any]
    ) -> TierAuthorization:
        """
        Create an authorization request for an alert.
        
        For warning/emergency tiers, this would be sent to
        the cloud for operator approval.
        
        Args:
            tier: Alert tier
            detection_type: What was detected
            details: Detection details
            
        Returns:
            Authorization tracker
        """
        auth = TierAuthorization.for_tier(tier)
        
        self.audit.log(AuditEventType.AUTHORIZATION_REQUESTED, {
            "tier": tier.value,
            "detection_type": detection_type,
            "required_count": auth.required_count
        })
        
        return auth
    
    # =========================================================================
    # SECURITY OPERATIONS  
    # =========================================================================
    
    def verify_audit_chain(self) -> tuple[bool, List[int]]:
        """
        Verify audit log integrity.
        
        Returns:
            Tuple of (is_valid, broken_sequences)
        """
        return self.audit.verify_chain()
    
    def get_audit_entries(
        self,
        since_sequence: int = 0,
        limit: int = 100
    ) -> List:
        """Get recent audit entries."""
        return self.audit.get_entries(since_sequence=since_sequence, limit=limit)
    
    @property
    def public_key(self) -> bytes:
        """Get this device's public key for verification."""
        return self.signer.public_key
