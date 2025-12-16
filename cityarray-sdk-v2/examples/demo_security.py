#!/usr/bin/env python3
"""
CITYARRAY SDK Demo

Demonstrates the secure message signing and display workflow.
"""

import sys
import time
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cityarray import CityArraySDK
from cityarray.security import AlertTier


def main():
    print("=" * 60)
    print("CITYARRAY SDK Demo - Trust No Edge Security")
    print("=" * 60)
    print()
    
    # Initialize SDK
    print("[1] Initializing SDK...")
    sdk = CityArraySDK(device_id="demo-device-001")
    sdk.start()
    print("    ✓ SDK initialized")
    print()
    
    # Display informational message (autonomous - no approval needed)
    print("[2] Displaying INFORMATIONAL message (autonomous)...")
    success = sdk.display_message(
        template_id="crowd-count",
        tier="informational",
        text={"en": "Current Attendance: 1,250"}
    )
    print(f"    ✓ Display result: {'SUCCESS' if success else 'FAILED'}")
    time.sleep(2)
    print()
    
    # Display advisory message (autonomous)
    print("[3] Displaying ADVISORY message (autonomous)...")
    success = sdk.display_message(
        template_id="area-congested",
        tier="advisory",
        text={"en": "North entrance congested - use South entrance"}
    )
    print(f"    ✓ Display result: {'SUCCESS' if success else 'FAILED'}")
    time.sleep(2)
    print()
    
    # Simulate a detection event
    print("[4] Simulating smoke detection...")
    tier = sdk.process_detection(
        detection_type="smoke",
        confidence=0.82,
        details={"location": "north_exit", "camera_id": "cam-03"}
    )
    print(f"    ✓ Detection classified as: {tier.value}")
    print(f"    ✓ Requires human approval: {tier.requires_human}")
    print(f"    ✓ Requires multi-party: {tier.requires_multiparty}")
    print()
    
    # In real system, WARNING tier would require operator approval
    # For demo, we show what WOULD be displayed after approval
    print("[5] Displaying WARNING message (would require operator approval)...")
    print("    [In production: Waiting for operator confirmation...]")
    success = sdk.display_message(
        template_id="smoke-detected",
        tier="warning",
        text={
            "en": "SMOKE DETECTED - North Exit - Please remain calm",
            "es": "HUMO DETECTADO - Salida Norte - Mantenga la calma"
        }
    )
    print(f"    ✓ Display result: {'SUCCESS' if success else 'FAILED'}")
    time.sleep(3)
    print()
    
    # Verify audit chain
    print("[6] Verifying audit chain integrity...")
    is_valid, broken = sdk.verify_audit_chain()
    print(f"    ✓ Chain valid: {is_valid}")
    if broken:
        print(f"    ⚠ Broken sequences: {broken}")
    print()
    
    # Show recent audit entries
    print("[7] Recent audit entries:")
    entries = sdk.get_audit_entries(limit=5)
    for entry in entries[-5:]:
        print(f"    [{entry.sequence}] {entry.event_type}: {entry.data}")
    print()
    
    # Clear and shutdown
    print("[8] Clearing display and shutting down...")
    sdk.clear_display()
    sdk.stop()
    print("    ✓ SDK stopped")
    print()
    
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
