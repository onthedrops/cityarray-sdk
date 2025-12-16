"""
Alert Tier Classification

Classifies alerts by severity and defines authorization requirements.

Tiers:
- INFORMATIONAL: Autonomous (pre-signed templates)
- ADVISORY: Autonomous (pre-signed templates)  
- WARNING: Single operator confirmation required
- EMERGENCY: Multi-party authorization (2 of 3) required
- IPAWS: Pass-through (already authorized by government)
"""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)


class AlertTier(Enum):
    """Alert severity tiers with increasing authorization requirements."""
    
    INFORMATIONAL = "informational"  # Crowd count, weather, time
    ADVISORY = "advisory"            # Congestion, rain expected
    WARNING = "warning"              # Smoke detected, investigating
    EMERGENCY = "emergency"          # Fire confirmed, evacuate
    IPAWS = "ipaws"                  # Government alerts (pass-through)
    
    @property
    def requires_human(self) -> bool:
        """Whether this tier requires human authorization."""
        return self in (AlertTier.WARNING, AlertTier.EMERGENCY)
    
    @property
    def requires_multiparty(self) -> bool:
        """Whether this tier requires multi-party authorization."""
        return self == AlertTier.EMERGENCY
    
    @property
    def min_authorizations(self) -> int:
        """Minimum number of authorizations required."""
        if self == AlertTier.EMERGENCY:
            return 2  # 2 of 3
        elif self == AlertTier.WARNING:
            return 1
        else:
            return 0  # Autonomous
    
    @property
    def max_latency_seconds(self) -> int:
        """Maximum acceptable latency for this tier."""
        latencies = {
            AlertTier.INFORMATIONAL: 1,
            AlertTier.ADVISORY: 2,
            AlertTier.WARNING: 60,
            AlertTier.EMERGENCY: 120,
            AlertTier.IPAWS: 5,
        }
        return latencies.get(self, 60)
    
    @property
    def ttl_seconds(self) -> int:
        """Default time-to-live for messages of this tier."""
        ttls = {
            AlertTier.INFORMATIONAL: 300,   # 5 minutes
            AlertTier.ADVISORY: 600,        # 10 minutes
            AlertTier.WARNING: 900,         # 15 minutes
            AlertTier.EMERGENCY: 1800,      # 30 minutes
            AlertTier.IPAWS: 3600,          # 1 hour (defer to IPAWS expiry)
        }
        return ttls.get(self, 300)


@dataclass
class TierAuthorization:
    """
    Authorization state for a pending alert.
    
    Tracks who has authorized and whether requirements are met.
    """
    tier: AlertTier
    required_count: int
    authorizations: List[Dict[str, Any]]
    
    @classmethod
    def for_tier(cls, tier: AlertTier) -> "TierAuthorization":
        """Create authorization tracker for a tier."""
        return cls(
            tier=tier,
            required_count=tier.min_authorizations,
            authorizations=[]
        )
    
    def add_authorization(
        self,
        operator_id: str,
        method: str = "dashboard",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an authorization.
        
        Args:
            operator_id: ID of authorizing operator
            method: Authorization method (dashboard, api, hardware_key)
            metadata: Additional metadata
            
        Returns:
            True if this authorization was accepted (not duplicate)
        """
        # Check for duplicate
        for auth in self.authorizations:
            if auth["operator_id"] == operator_id:
                logger.warning(f"Duplicate authorization from {operator_id}")
                return False
        
        from datetime import datetime, timezone
        
        self.authorizations.append({
            "operator_id": operator_id,
            "method": method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        })
        
        logger.info(f"Authorization added from {operator_id} ({len(self.authorizations)}/{self.required_count})")
        return True
    
    @property
    def is_satisfied(self) -> bool:
        """Check if authorization requirements are met."""
        return len(self.authorizations) >= self.required_count
    
    @property
    def remaining(self) -> int:
        """Number of additional authorizations needed."""
        return max(0, self.required_count - len(self.authorizations))


# Pre-approved message templates for autonomous tiers
AUTONOMOUS_TEMPLATES = {
    AlertTier.INFORMATIONAL: [
        "crowd-count",
        "weather-current",
        "time-display",
        "event-info",
        "wayfinding",
    ],
    AlertTier.ADVISORY: [
        "area-congested",
        "weather-advisory",
        "event-starting",
        "event-ending",
        "alternate-route",
    ],
}


def get_tier_for_detection(detection_type: str, confidence: float) -> AlertTier:
    """
    Determine appropriate tier for a detection event.
    
    Args:
        detection_type: Type of detection (fire, smoke, crowd, etc.)
        confidence: Detection confidence (0.0 to 1.0)
        
    Returns:
        Appropriate alert tier
    """
    # High-severity detections
    if detection_type in ("fire", "active_shooter", "explosion"):
        if confidence >= 0.9:
            return AlertTier.EMERGENCY
        elif confidence >= 0.7:
            return AlertTier.WARNING
        else:
            return AlertTier.ADVISORY
    
    # Medium-severity detections
    if detection_type in ("smoke", "fight", "medical_emergency"):
        if confidence >= 0.85:
            return AlertTier.WARNING
        else:
            return AlertTier.ADVISORY
    
    # Low-severity detections
    if detection_type in ("crowd", "congestion", "weather"):
        return AlertTier.INFORMATIONAL
    
    # Default to advisory for unknown types
    return AlertTier.ADVISORY


def is_template_autonomous(tier: AlertTier, template_id: str) -> bool:
    """
    Check if a template can be displayed autonomously for this tier.
    
    Args:
        tier: Alert tier
        template_id: Template identifier
        
    Returns:
        True if template is pre-approved for autonomous display
    """
    if tier.requires_human:
        return False
    
    allowed = AUTONOMOUS_TEMPLATES.get(tier, [])
    return template_id in allowed


def requires_authorization(tier: AlertTier):
    """
    Decorator to enforce authorization requirements.
    
    Usage:
        @requires_authorization(AlertTier.WARNING)
        def display_warning(message, authorizations):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract authorizations from kwargs
            authorizations = kwargs.get('authorizations', [])
            
            if len(authorizations) < tier.min_authorizations:
                raise PermissionError(
                    f"Tier {tier.value} requires {tier.min_authorizations} authorizations, "
                    f"got {len(authorizations)}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class TierValidator:
    """
    Validates messages against tier requirements.
    """
    
    def __init__(self, allowed_operators: Optional[List[str]] = None):
        """
        Initialize validator.
        
        Args:
            allowed_operators: List of operator IDs allowed to authorize
                             (None = all operators allowed)
        """
        self.allowed_operators = set(allowed_operators) if allowed_operators else None
    
    def validate(
        self,
        tier: AlertTier,
        template_id: str,
        authorizations: List[Dict[str, Any]]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a message against tier requirements.
        
        Args:
            tier: Alert tier
            template_id: Message template ID
            authorizations: List of authorization records
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if autonomous is allowed
        if not tier.requires_human:
            if is_template_autonomous(tier, template_id):
                return True, None
            else:
                return False, f"Template '{template_id}' not approved for autonomous {tier.value}"
        
        # Check authorization count
        if len(authorizations) < tier.min_authorizations:
            return False, f"Need {tier.min_authorizations} authorizations, got {len(authorizations)}"
        
        # Check operator validity
        if self.allowed_operators:
            for auth in authorizations:
                op_id = auth.get("operator_id")
                if op_id not in self.allowed_operators:
                    return False, f"Operator '{op_id}' not authorized"
        
        # Check for duplicate operators in multi-party
        if tier.requires_multiparty:
            operator_ids = [a.get("operator_id") for a in authorizations]
            if len(operator_ids) != len(set(operator_ids)):
                return False, "Multi-party authorization requires different operators"
        
        return True, None
