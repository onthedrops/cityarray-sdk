"""
Tamper-Evident Audit Logging

Every security-relevant event is logged with hash chaining
to detect any tampering with the log.

Log entries include:
- Hash of previous entry (chain integrity)
- Timestamp
- Event type and data
- Device state at time of event
"""

import json
import hashlib
import logging
import threading
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of auditable events."""
    # Display events (7 year retention)
    MESSAGE_DISPLAYED = "message_displayed"
    MESSAGE_CLEARED = "message_cleared"
    MESSAGE_REJECTED = "message_rejected"
    
    # Authorization events (7 year retention)
    AUTHORIZATION_REQUESTED = "auth_requested"
    AUTHORIZATION_GRANTED = "auth_granted"
    AUTHORIZATION_DENIED = "auth_denied"
    
    # Detection events (90 day retention)
    DETECTION_EVENT = "detection"
    DETECTION_SUPPRESSED = "detection_suppressed"
    
    # Security events (7 year retention)
    SIGNATURE_INVALID = "sig_invalid"
    SIGNATURE_VALID = "sig_valid"
    REPLAY_DETECTED = "replay_detected"
    TAMPER_DETECTED = "tamper_detected"
    KEY_ROTATED = "key_rotated"
    CERTIFICATE_UPDATED = "cert_updated"
    
    # System events (1 year retention)
    SYSTEM_BOOT = "boot"
    SYSTEM_SHUTDOWN = "shutdown"
    CONFIG_CHANGED = "config_changed"
    UPDATE_APPLIED = "update_applied"
    UPDATE_REJECTED = "update_rejected"
    NETWORK_CONNECTED = "net_connected"
    NETWORK_DISCONNECTED = "net_disconnected"


@dataclass
class AuditEvent:
    """A single audit log entry."""
    sequence: int
    timestamp: str
    event_type: str
    device_id: str
    data: Dict[str, Any]
    previous_hash: str
    entry_hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Compute hash of this entry (excluding entry_hash field)."""
        payload = {
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "device_id": self.device_id,
            "data": self.data,
            "previous_hash": self.previous_hash
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "AuditEvent":
        return cls.from_dict(json.loads(json_str))


class AuditLogger:
    """
    Tamper-evident audit logger with hash chaining.
    
    Security Properties:
    - Each entry includes hash of previous entry
    - Modification of any entry breaks the chain
    - Entries are flushed immediately (no buffering)
    - Remote sync capability for off-device backup
    """
    
    # Genesis hash for first entry in chain
    GENESIS_HASH = "0" * 64
    
    def __init__(
        self,
        device_id: str,
        log_path: Optional[Path] = None,
        remote_callback: Optional[Callable[[AuditEvent], None]] = None
    ):
        """
        Initialize audit logger.
        
        Args:
            device_id: This device's ID
            log_path: Path to local log file (default: ./audit.log)
            remote_callback: Optional callback for remote sync
        """
        self.device_id = device_id
        self.log_path = log_path or Path("./audit.log")
        self.remote_callback = remote_callback
        
        self._lock = threading.Lock()
        self._sequence = 0
        self._last_hash = self.GENESIS_HASH
        
        # Load existing log to continue chain
        self._load_existing()
    
    def _load_existing(self) -> None:
        """Load existing log file and verify chain integrity."""
        if not self.log_path.exists():
            logger.info(f"Starting new audit log at {self.log_path}")
            return
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    event = AuditEvent.from_json(line)
                    
                    # Verify chain
                    if event.previous_hash != self._last_hash:
                        logger.error(f"AUDIT CHAIN BROKEN at sequence {event.sequence}!")
                        logger.error(f"Expected previous_hash: {self._last_hash}")
                        logger.error(f"Got: {event.previous_hash}")
                        # Continue anyway but log the break
                        self.log(
                            AuditEventType.TAMPER_DETECTED,
                            {
                                "sequence": event.sequence,
                                "expected_hash": self._last_hash,
                                "actual_hash": event.previous_hash
                            }
                        )
                    
                    # Verify entry hash
                    computed_hash = event.compute_hash()
                    if event.entry_hash != computed_hash:
                        logger.error(f"AUDIT ENTRY TAMPERED at sequence {event.sequence}!")
                    
                    self._sequence = event.sequence
                    self._last_hash = event.entry_hash or computed_hash
            
            logger.info(f"Loaded audit log with {self._sequence} entries")
            
        except Exception as e:
            logger.error(f"Error loading audit log: {e}")
            # Start fresh but note the corruption
            self._sequence = 0
            self._last_hash = self.GENESIS_HASH
    
    def log(
        self,
        event_type: AuditEventType,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            data: Event-specific data
            timestamp: Optional timestamp (default: now)
            
        Returns:
            The logged event
        """
        with self._lock:
            self._sequence += 1
            
            ts = timestamp or datetime.now(timezone.utc)
            ts_str = ts.isoformat().replace('+00:00', 'Z')
            
            event = AuditEvent(
                sequence=self._sequence,
                timestamp=ts_str,
                event_type=event_type.value,
                device_id=self.device_id,
                data=data,
                previous_hash=self._last_hash
            )
            
            event.entry_hash = event.compute_hash()
            self._last_hash = event.entry_hash
            
            # Write immediately (no buffering for security)
            self._write_event(event)
            
            # Remote sync if configured
            if self.remote_callback:
                try:
                    self.remote_callback(event)
                except Exception as e:
                    logger.error(f"Remote audit sync failed: {e}")
            
            return event
    
    def _write_event(self, event: AuditEvent) -> None:
        """Write event to local log file."""
        try:
            with open(self.log_path, 'a') as f:
                f.write(event.to_json() + '\n')
                f.flush()  # Force write to disk
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def verify_chain(self) -> tuple[bool, List[int]]:
        """
        Verify entire audit chain integrity.
        
        Returns:
            Tuple of (is_valid, list_of_broken_sequences)
        """
        broken = []
        last_hash = self.GENESIS_HASH
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    event = AuditEvent.from_json(line)
                    
                    # Check chain link
                    if event.previous_hash != last_hash:
                        broken.append(event.sequence)
                    
                    # Check entry integrity
                    computed = event.compute_hash()
                    if event.entry_hash != computed:
                        broken.append(event.sequence)
                    
                    last_hash = event.entry_hash or computed
            
            return len(broken) == 0, broken
            
        except Exception as e:
            logger.error(f"Chain verification failed: {e}")
            return False, [-1]  # -1 indicates file-level error
    
    def get_entries(
        self,
        since_sequence: int = 0,
        event_types: Optional[List[AuditEventType]] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """
        Retrieve audit entries.
        
        Args:
            since_sequence: Start from this sequence number
            event_types: Filter by event types (None = all)
            limit: Maximum entries to return
            
        Returns:
            List of audit events
        """
        entries = []
        type_values = {t.value for t in event_types} if event_types else None
        
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if len(entries) >= limit:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    event = AuditEvent.from_json(line)
                    
                    if event.sequence <= since_sequence:
                        continue
                    
                    if type_values and event.event_type not in type_values:
                        continue
                    
                    entries.append(event)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
            return []
    
    # Convenience methods for common events
    
    def log_message_displayed(self, message_id: str, tier: str, content_hash: str) -> AuditEvent:
        """Log that a message was displayed."""
        return self.log(AuditEventType.MESSAGE_DISPLAYED, {
            "message_id": message_id,
            "tier": tier,
            "content_hash": content_hash
        })
    
    def log_message_rejected(self, message_id: str, reason: str) -> AuditEvent:
        """Log that a message was rejected."""
        return self.log(AuditEventType.MESSAGE_REJECTED, {
            "message_id": message_id,
            "reason": reason
        })
    
    def log_signature_invalid(self, message_id: str, error: str) -> AuditEvent:
        """Log an invalid signature attempt."""
        return self.log(AuditEventType.SIGNATURE_INVALID, {
            "message_id": message_id,
            "error": error
        })
    
    def log_detection(self, detection_type: str, confidence: float, details: Dict[str, Any]) -> AuditEvent:
        """Log a detection event."""
        return self.log(AuditEventType.DETECTION_EVENT, {
            "detection_type": detection_type,
            "confidence": confidence,
            "details": details
        })
    
    def log_boot(self, version: str, config_hash: str) -> AuditEvent:
        """Log system boot."""
        return self.log(AuditEventType.SYSTEM_BOOT, {
            "version": version,
            "config_hash": config_hash
        })
