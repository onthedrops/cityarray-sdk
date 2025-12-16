"""
Secure Display Engine

Display engine with integrated security:
- Verifies message signatures before display
- Rejects unsigned or invalid messages
- Logs all display events to audit trail
- Enforces tier-based authorization requirements
"""

import logging
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from ..security.signing import (
    SignedMessage, MessageVerifier, 
    SignatureError, MessageExpiredError, ReplayDetectedError
)
from ..security.audit import AuditLogger, AuditEventType
from ..security.tiers import AlertTier, TierValidator, is_template_autonomous

logger = logging.getLogger(__name__)


@dataclass
class DisplayResult:
    """Result of a display operation."""
    success: bool
    message_id: Optional[str]
    error: Optional[str] = None
    displayed_at: Optional[str] = None


class SecureDisplayBackend(ABC):
    """
    Abstract base class for secure display backends.
    
    All display backends must implement signature verification
    before displaying any content.
    """
    
    @abstractmethod
    def render(self, content: Dict[str, Any]) -> bool:
        """
        Render content to the display.
        
        Args:
            content: Validated, signed content to display
            
        Returns:
            True if render succeeded
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear the display."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get display capabilities (resolution, colors, etc.)."""
        pass


class SecureDisplayEngine:
    """
    Main display engine with security enforcement.
    
    CRITICAL: This is the last line of defense.
    No unsigned message should ever reach the display.
    """
    
    def __init__(
        self,
        device_id: str,
        backend: SecureDisplayBackend,
        verifier: MessageVerifier,
        audit_logger: AuditLogger,
        tier_validator: Optional[TierValidator] = None
    ):
        """
        Initialize secure display engine.
        
        Args:
            device_id: This device's ID
            backend: Display backend implementation
            verifier: Message signature verifier
            audit_logger: Audit logging instance
            tier_validator: Optional tier validation (uses default if None)
        """
        self.device_id = device_id
        self.backend = backend
        self.verifier = verifier
        self.audit = audit_logger
        self.tier_validator = tier_validator or TierValidator()
        
        self._current_message: Optional[SignedMessage] = None
        self._on_display_callback: Optional[Callable[[SignedMessage], None]] = None
        self._on_reject_callback: Optional[Callable[[SignedMessage, str], None]] = None
    
    def set_callbacks(
        self,
        on_display: Optional[Callable[[SignedMessage], None]] = None,
        on_reject: Optional[Callable[[SignedMessage, str], None]] = None
    ) -> None:
        """Set callbacks for display events."""
        self._on_display_callback = on_display
        self._on_reject_callback = on_reject
    
    def display(self, message: SignedMessage) -> DisplayResult:
        """
        Display a signed message.
        
        Security checks performed:
        1. Signature verification
        2. Expiration check
        3. Replay detection
        4. Device ID binding
        5. Tier authorization validation
        
        Args:
            message: Signed message to display
            
        Returns:
            DisplayResult indicating success or failure
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Step 1: Verify signature
        try:
            self.verifier.verify(message)
        except SignatureError as e:
            error = f"Signature verification failed: {e}"
            logger.error(f"SECURITY: {error}")
            self.audit.log_signature_invalid(message.message_id, str(e))
            self._reject(message, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        except MessageExpiredError as e:
            error = f"Message expired: {e}"
            logger.warning(error)
            self.audit.log_message_rejected(message.message_id, "expired")
            self._reject(message, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        except ReplayDetectedError as e:
            error = f"Replay attack detected: {e}"
            logger.error(f"SECURITY: {error}")
            self.audit.log(AuditEventType.REPLAY_DETECTED, {
                "message_id": message.message_id,
                "nonce": message.nonce
            })
            self._reject(message, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        except ValueError as e:
            error = f"Invalid message: {e}"
            logger.error(error)
            self.audit.log_message_rejected(message.message_id, str(e))
            self._reject(message, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        
        # Step 2: Validate tier authorization
        try:
            tier = AlertTier(message.tier)
        except ValueError:
            error = f"Unknown tier: {message.tier}"
            logger.error(error)
            self.audit.log_message_rejected(message.message_id, error)
            self._reject(message, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        
        template_id = message.content.get("template_id", "unknown")
        authorizations = [a.to_dict() for a in message.authorizations]
        
        is_valid, tier_error = self.tier_validator.validate(tier, template_id, authorizations)
        if not is_valid:
            error = f"Tier validation failed: {tier_error}"
            logger.error(f"SECURITY: {error}")
            self.audit.log_message_rejected(message.message_id, tier_error)
            self._reject(message, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        
        # Step 3: Render to display
        try:
            success = self.backend.render(message.content)
        except Exception as e:
            error = f"Render failed: {e}"
            logger.error(error)
            self.audit.log_message_rejected(message.message_id, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        
        if not success:
            error = "Backend render returned false"
            self.audit.log_message_rejected(message.message_id, error)
            return DisplayResult(success=False, message_id=message.message_id, error=error)
        
        # Step 4: Log success and update state
        content_hash = hashlib.sha256(
            str(message.content).encode()
        ).hexdigest()[:16]
        
        self.audit.log_message_displayed(
            message_id=message.message_id,
            tier=message.tier,
            content_hash=content_hash
        )
        
        self._current_message = message
        
        if self._on_display_callback:
            try:
                self._on_display_callback(message)
            except Exception as e:
                logger.error(f"Display callback error: {e}")
        
        logger.info(f"Displayed message {message.message_id} (tier: {message.tier})")
        
        return DisplayResult(
            success=True,
            message_id=message.message_id,
            displayed_at=now
        )
    
    def _reject(self, message: SignedMessage, reason: str) -> None:
        """Handle message rejection."""
        if self._on_reject_callback:
            try:
                self._on_reject_callback(message, reason)
            except Exception as e:
                logger.error(f"Reject callback error: {e}")
    
    def clear(self) -> bool:
        """
        Clear the display.
        
        Returns:
            True if clear succeeded
        """
        if self._current_message:
            self.audit.log(AuditEventType.MESSAGE_CLEARED, {
                "message_id": self._current_message.message_id
            })
        
        self._current_message = None
        return self.backend.clear()
    
    @property
    def current_message(self) -> Optional[SignedMessage]:
        """Get currently displayed message."""
        return self._current_message


class ConsoleDisplayBackend(SecureDisplayBackend):
    """
    Console-based display backend for development/testing.
    """
    
    def __init__(self, width: int = 64, height: int = 16):
        self.width = width
        self.height = height
    
    def render(self, content: Dict[str, Any]) -> bool:
        """Render to console."""
        template_id = content.get("template_id", "unknown")
        params = content.get("params", {})
        text = content.get("text", {})
        
        # Build display text
        if "en" in text:
            display_text = text["en"]
        elif params:
            display_text = f"[{template_id}] {params}"
        else:
            display_text = f"[{template_id}]"
        
        # Print bordered display
        border = "+" + "-" * (self.width + 2) + "+"
        print("\n" + border)
        
        # Word wrap and center
        words = display_text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= self.width:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines[:self.height]:
            padded = line.center(self.width)
            print(f"| {padded} |")
        
        print(border + "\n")
        return True
    
    def clear(self) -> bool:
        """Clear console display."""
        border = "+" + "-" * (self.width + 2) + "+"
        print("\n" + border)
        for _ in range(3):
            print(f"|{' ' * (self.width + 2)}|")
        print(border + "\n")
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "color": False,
            "backend": "console"
        }
