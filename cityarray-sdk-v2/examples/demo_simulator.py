#!/usr/bin/env python3
"""
CITYARRAY Simulator Demo with Security Integration

Demonstrates:
- Signed messages display correctly
- Unsigned messages are REJECTED
- Different alert tiers have different colors
- WARNING/EMERGENCY require authorization

Controls:
  1 - Display INFORMATIONAL message (autonomous, displays)
  2 - Display ADVISORY message (autonomous, displays)
  3 - Display WARNING message (requires auth, will FAIL)
  4 - Display EMERGENCY message (requires auth, will FAIL)
  5 - Display WARNING with authorization (will display)
  C - Clear display
  ESC - Exit
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pygame
from cityarray.security.signing import MessageSigner, MessageVerifier, Authorization
from cityarray.security.audit import AuditLogger
from cityarray.security.tiers import AlertTier
from cityarray.display.secure_engine import SecureDisplayEngine
from cityarray.display.simulator_backend import SimulatorDisplayBackend
from cityarray.display.led_simulator import SimulatorConfig


class SecureSimulatorDemo:
    """Demo showing security integration with LED simulator."""
    
    def __init__(self):
        # Device ID for this demo
        self.device_id = "demo-simulator-001"
        
        # Create simulator with custom config
        config = SimulatorConfig(
            width=64,
            height=32,
            pixel_size=12,
            glow=True,
            title="CITYARRAY Secure LED Simulator"
        )
        self.backend = SimulatorDisplayBackend(config)
        
        # Create security components
        self.signer = MessageSigner()  # Generates ephemeral key for demo
        self.verifier = MessageVerifier(
            public_key=self.signer.public_key,
            device_id=self.device_id
        )
        self.audit = AuditLogger(
            device_id=self.device_id,
            log_path=Path("./demo_audit.log")
        )
        
        # Create secure display engine
        self.display = SecureDisplayEngine(
            device_id=self.device_id,
            backend=self.backend,
            verifier=self.verifier,
            audit_logger=self.audit
        )
        
        print("=" * 60)
        print("CITYARRAY Secure LED Simulator Demo")
        print("=" * 60)
        print()
        print("Controls:")
        print("  1 - INFORMATIONAL (autonomous, will display)")
        print("  2 - ADVISORY (autonomous, will display)")
        print("  3 - WARNING (no auth, will FAIL)")
        print("  4 - EMERGENCY (no auth, will FAIL)")
        print("  5 - WARNING with auth (will display)")
        print("  C - Clear display")
        print("  ESC - Exit")
        print()
        print("=" * 60)
    
    def display_message(
        self,
        text: str,
        tier: str,
        authorizations: list = None
    ) -> bool:
        """Create signed message and attempt to display."""
        content = {
            "template_id": f"{tier}-alert",
            "text": {"en": text},
            "_tier": tier,  # Pass tier for color selection
        }
        
        # Create and sign message
        message = self.signer.create_signed_message(
            device_id=self.device_id,
            tier=tier,
            content=content,
            ttl_seconds=300,
            authorizations=authorizations or []
        )
        
        # Attempt to display (SecureDisplayEngine will verify)
        result = self.display.display(message)
        
        if result.success:
            print(f"✓ {tier.upper()} message displayed")
        else:
            print(f"✗ {tier.upper()} message REJECTED: {result.error}")
        
        return result.success
    
    def run(self):
        """Main demo loop."""
        running = True
        
        # Show initial message
        self.display_message("CITYARRAY READY", "informational")
        
        while running:
            # Process pygame events
            if not self.backend.process_events():
                running = False
                continue
            
            # Check for key presses
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.display_message("CROWD: 1250", "informational")
                    
                    elif event.key == pygame.K_2:
                        self.display_message("USE SOUTH EXIT", "advisory")
                    
                    elif event.key == pygame.K_3:
                        # WARNING without authorization - should FAIL
                        self.display_message("SMOKE DETECTED", "warning")
                    
                    elif event.key == pygame.K_4:
                        # EMERGENCY without authorization - should FAIL
                        self.display_message("EVACUATE NOW", "emergency")
                    
                    elif event.key == pygame.K_5:
                        # WARNING with authorization - should succeed
                        auth = Authorization(
                            operator_id="operator-001",
                            timestamp="2024-12-15T00:00:00Z",
                            method="dashboard"
                        )
                        self.display_message("SMOKE DETECTED", "warning", [auth])
                    
                    elif event.key == pygame.K_c:
                        self.display.clear()
                        print("Display cleared")
                    
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Render and tick
            self.backend.simulator.render()
            self.backend.tick(30)
        
        # Cleanup
        self.backend.quit()
        print()
        print("Demo ended.")
        
        # Show audit summary
        print()
        print("Audit Log Summary:")
        entries = self.audit.get_entries(limit=10)
        for entry in entries:
            print(f"  [{entry.event_type}] {entry.data}")


def main():
    demo = SecureSimulatorDemo()
    demo.run()


if __name__ == "__main__":
    main()
