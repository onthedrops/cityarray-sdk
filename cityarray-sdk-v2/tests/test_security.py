"""
Tests for CITYARRAY Security Module
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cityarray.security.signing import (
    MessageSigner, MessageVerifier, SignedMessage, Authorization,
    SignatureError, MessageExpiredError, ReplayDetectedError
)
from cityarray.security.audit import AuditLogger, AuditEventType
from cityarray.security.tiers import (
    AlertTier, TierAuthorization, get_tier_for_detection,
    is_template_autonomous, TierValidator
)


class TestMessageSigning:
    """Tests for message signing and verification."""
    
    def test_sign_and_verify(self):
        """Test basic sign/verify workflow."""
        signer = MessageSigner()
        verifier = MessageVerifier(signer.public_key, device_id="test-device")
        
        message = signer.create_signed_message(
            device_id="test-device",
            tier="informational",
            content={"template_id": "test", "text": {"en": "Hello"}},
            ttl_seconds=300
        )
        
        assert message.signature is not None
        assert verifier.verify(message) is True
    
    def test_reject_wrong_device(self):
        """Test that messages for other devices are rejected."""
        signer = MessageSigner()
        verifier = MessageVerifier(signer.public_key, device_id="device-A")
        
        message = signer.create_signed_message(
            device_id="device-B",
            tier="informational",
            content={"template_id": "test"},
        )
        
        with pytest.raises(ValueError, match="device-B"):
            verifier.verify(message)
    
    def test_reject_expired(self):
        """Test that expired messages are rejected."""
        signer = MessageSigner()
        verifier = MessageVerifier(signer.public_key, device_id="test")
        
        # Create message that's already expired
        message = signer.create_signed_message(
            device_id="test",
            tier="informational",
            content={"template_id": "test"},
            ttl_seconds=-10  # Already expired
        )
        
        with pytest.raises(MessageExpiredError):
            verifier.verify(message)
    
    def test_reject_replay(self):
        """Test that replayed messages are rejected."""
        signer = MessageSigner()
        verifier = MessageVerifier(signer.public_key, device_id="test")
        
        message = signer.create_signed_message(
            device_id="test",
            tier="informational",
            content={"template_id": "test"},
        )
        
        # First verification should succeed
        assert verifier.verify(message) is True
        
        # Second verification should fail (replay)
        with pytest.raises(ReplayDetectedError):
            verifier.verify(message)
    
    def test_reject_tampered(self):
        """Test that tampered messages are rejected."""
        signer = MessageSigner()
        verifier = MessageVerifier(signer.public_key, device_id="test")
        
        message = signer.create_signed_message(
            device_id="test",
            tier="informational",
            content={"template_id": "test"},
        )
        
        # Tamper with content
        message.content["template_id"] = "hacked"
        
        with pytest.raises(SignatureError):
            verifier.verify(message)


class TestAlertTiers:
    """Tests for alert tier classification."""
    
    def test_tier_properties(self):
        """Test tier property methods."""
        assert AlertTier.INFORMATIONAL.requires_human is False
        assert AlertTier.ADVISORY.requires_human is False
        assert AlertTier.WARNING.requires_human is True
        assert AlertTier.EMERGENCY.requires_human is True
        
        assert AlertTier.EMERGENCY.requires_multiparty is True
        assert AlertTier.WARNING.requires_multiparty is False
        
        assert AlertTier.INFORMATIONAL.min_authorizations == 0
        assert AlertTier.WARNING.min_authorizations == 1
        assert AlertTier.EMERGENCY.min_authorizations == 2
    
    def test_detection_classification(self):
        """Test detection to tier classification."""
        # High confidence fire -> emergency
        assert get_tier_for_detection("fire", 0.95) == AlertTier.EMERGENCY
        
        # Lower confidence fire -> warning
        assert get_tier_for_detection("fire", 0.75) == AlertTier.WARNING
        
        # Smoke -> warning
        assert get_tier_for_detection("smoke", 0.9) == AlertTier.WARNING
        
        # Crowd -> informational
        assert get_tier_for_detection("crowd", 0.99) == AlertTier.INFORMATIONAL
    
    def test_autonomous_templates(self):
        """Test autonomous template validation."""
        assert is_template_autonomous(AlertTier.INFORMATIONAL, "crowd-count") is True
        assert is_template_autonomous(AlertTier.INFORMATIONAL, "custom-alert") is False
        assert is_template_autonomous(AlertTier.WARNING, "crowd-count") is False
    
    def test_tier_authorization(self):
        """Test authorization workflow."""
        auth = TierAuthorization.for_tier(AlertTier.EMERGENCY)
        
        assert auth.is_satisfied is False
        assert auth.remaining == 2
        
        auth.add_authorization("operator-1", "dashboard")
        assert auth.is_satisfied is False
        assert auth.remaining == 1
        
        # Duplicate should be rejected
        result = auth.add_authorization("operator-1", "dashboard")
        assert result is False
        assert auth.remaining == 1
        
        auth.add_authorization("operator-2", "dashboard")
        assert auth.is_satisfied is True
        assert auth.remaining == 0


class TestAuditLogging:
    """Tests for audit logging."""
    
    def test_hash_chain(self, tmp_path):
        """Test that audit log maintains hash chain."""
        log_file = tmp_path / "test_audit.log"
        audit = AuditLogger(device_id="test", log_path=log_file)
        
        # Log some events
        audit.log(AuditEventType.SYSTEM_BOOT, {"version": "1.0"})
        audit.log(AuditEventType.MESSAGE_DISPLAYED, {"message_id": "msg-1"})
        audit.log(AuditEventType.MESSAGE_DISPLAYED, {"message_id": "msg-2"})
        
        # Verify chain
        is_valid, broken = audit.verify_chain()
        assert is_valid is True
        assert broken == []
    
    def test_chain_detection(self, tmp_path):
        """Test that chain tampering is detected."""
        log_file = tmp_path / "test_audit.log"
        audit = AuditLogger(device_id="test", log_path=log_file)
        
        audit.log(AuditEventType.SYSTEM_BOOT, {"version": "1.0"})
        audit.log(AuditEventType.MESSAGE_DISPLAYED, {"message_id": "msg-1"})
        
        # Tamper with log file
        lines = log_file.read_text().split('\n')
        if lines[0]:
            import json
            entry = json.loads(lines[0])
            entry["data"]["version"] = "HACKED"
            lines[0] = json.dumps(entry)
            log_file.write_text('\n'.join(lines))
        
        # Create new logger to reload
        audit2 = AuditLogger(device_id="test", log_path=log_file)
        is_valid, broken = audit2.verify_chain()
        
        # Should detect tampering
        assert is_valid is False or len(broken) > 0


class TestTierValidator:
    """Tests for tier validation."""
    
    def test_autonomous_allowed(self):
        """Test autonomous tier validation."""
        validator = TierValidator()
        
        is_valid, error = validator.validate(
            AlertTier.INFORMATIONAL, 
            "crowd-count",
            []
        )
        assert is_valid is True
    
    def test_autonomous_denied(self):
        """Test unauthorized template rejection."""
        validator = TierValidator()
        
        is_valid, error = validator.validate(
            AlertTier.INFORMATIONAL,
            "unauthorized-template",
            []
        )
        assert is_valid is False
        assert "not approved" in error
    
    def test_warning_needs_auth(self):
        """Test warning tier requires authorization."""
        validator = TierValidator()
        
        # Without authorization
        is_valid, error = validator.validate(
            AlertTier.WARNING,
            "smoke-detected",
            []
        )
        assert is_valid is False
        
        # With authorization
        is_valid, error = validator.validate(
            AlertTier.WARNING,
            "smoke-detected",
            [{"operator_id": "op-1", "method": "dashboard", "timestamp": "2024-01-01"}]
        )
        assert is_valid is True
    
    def test_emergency_needs_multiparty(self):
        """Test emergency tier requires multi-party."""
        validator = TierValidator()
        
        # Single authorization not enough
        is_valid, error = validator.validate(
            AlertTier.EMERGENCY,
            "fire-evacuation",
            [{"operator_id": "op-1", "method": "dashboard", "timestamp": "2024-01-01"}]
        )
        assert is_valid is False
        
        # Same operator twice not allowed
        is_valid, error = validator.validate(
            AlertTier.EMERGENCY,
            "fire-evacuation",
            [
                {"operator_id": "op-1", "method": "dashboard", "timestamp": "2024-01-01"},
                {"operator_id": "op-1", "method": "api", "timestamp": "2024-01-01"}
            ]
        )
        assert is_valid is False
        assert "different operators" in error
        
        # Two different operators OK
        is_valid, error = validator.validate(
            AlertTier.EMERGENCY,
            "fire-evacuation",
            [
                {"operator_id": "op-1", "method": "dashboard", "timestamp": "2024-01-01"},
                {"operator_id": "op-2", "method": "dashboard", "timestamp": "2024-01-01"}
            ]
        )
        assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
