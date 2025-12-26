"""
Simulator Display Backend

Connects the LED simulator to the SDK security layer.
Only cryptographically signed messages can be displayed.
"""

from typing import Dict, Any, Optional
from .led_simulator import LEDSimulator, LEDColor, SimulatorConfig
from .secure_engine import SecureDisplayBackend


# Color mapping for alert tiers
TIER_COLORS = {
    "informational": LEDColor.BLUE.value,
    "advisory": LEDColor.GREEN.value,
    "warning": LEDColor.AMBER.value,
    "emergency": LEDColor.RED.value,
    "ipaws": LEDColor.RED.value,
}


class SimulatorDisplayBackend(SecureDisplayBackend):
    """
    Display backend that renders to the LED simulator.
    
    Implements SecureDisplayBackend interface so it can be
    used with SecureDisplayEngine (which enforces signatures).
    """
    
    def __init__(self, config: Optional[SimulatorConfig] = None):
        """
        Initialize simulator backend.
        
        Args:
            config: Optional simulator configuration
        """
        self.config = config or SimulatorConfig()
        self.simulator = LEDSimulator(self.config)
        self._current_tier: Optional[str] = None
        self._initialized = False
    
    def _ensure_init(self) -> None:
        """Initialize simulator if not already done."""
        if not self._initialized:
            self.simulator.init()
            self._initialized = True
    
    def render(self, content: Dict[str, Any]) -> bool:
        """
        Render signed message content to the simulator.
        
        Args:
            content: Message content dict with template_id, params, text
            
        Returns:
            True if render succeeded
        """
        self._ensure_init()
        
        # Clear display
        self.simulator.clear()
        
        # Get text to display
        text = self._extract_text(content)
        
        # Get color based on tier (stored by SecureDisplayEngine)
        tier = content.get("_tier", "informational")
        color = TIER_COLORS.get(tier, LEDColor.GREEN.value)
        
        # Render text centered
        self._render_multiline(text, color)
        
        # Update display
        self.simulator.render()
        
        return True
    
    def _extract_text(self, content: Dict[str, Any]) -> str:
        """Extract display text from content."""
        # Try text field first (localized)
        text_dict = content.get("text", {})
        if isinstance(text_dict, dict):
            # Prefer English, fall back to first available
            text = text_dict.get("en") or next(iter(text_dict.values()), "")
        elif isinstance(text_dict, str):
            text = text_dict
        else:
            text = ""
        
        # Fall back to template_id if no text
        if not text:
            template_id = content.get("template_id", "")
            params = content.get("params", {})
            text = f"{template_id}: {params}" if params else template_id
        
        return text.upper()  # LED displays typically uppercase
    
    def _render_multiline(self, text: str, color: tuple) -> None:
        """Render text, splitting into multiple lines if needed."""
        max_chars = self.config.width // 6  # 6 pixels per character
        
        # Split into lines
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Limit to 3 lines (what fits on 32-pixel height with 7-pixel font + spacing)
        lines = lines[:3]
        
        # Calculate vertical centering
        total_height = len(lines) * 9  # 7 pixels + 2 spacing
        start_y = (self.config.height - total_height) // 2
        
        # Render each line centered
        for i, line in enumerate(lines):
            y = start_y + i * 9
            self.simulator.draw_text_centered(line, color, y_offset=y - self.config.height // 2 + 3)
    
    def clear(self) -> bool:
        """Clear the display."""
        self._ensure_init()
        self.simulator.clear()
        self.simulator.render()
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get display capabilities."""
        return {
            "width": self.config.width,
            "height": self.config.height,
            "color": True,
            "backend": "simulator",
            "max_chars_per_line": self.config.width // 6,
            "max_lines": 3,
        }
    
    def process_events(self) -> bool:
        """
        Process pygame events.
        
        Returns: False if window should close
        """
        self._ensure_init()
        return self.simulator.process_events()
    
    def tick(self, fps: int = 30) -> None:
        """Limit frame rate."""
        self._ensure_init()
        self.simulator.tick(fps)
    
    def quit(self) -> None:
        """Clean up resources."""
        if self._initialized:
            self.simulator.quit()
            self._initialized = False
