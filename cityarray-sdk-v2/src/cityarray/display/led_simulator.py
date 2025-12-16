"""
CITYARRAY Virtual LED Simulator

A pygame-based LED matrix simulator for testing without hardware.
Simulates a 64x32 pixel LED display matching the P3 panel spec.
"""

import pygame
import numpy as np
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class LEDColor(Enum):
    """Standard LED colors for emergency signage."""
    OFF = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    AMBER = (255, 191, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 100, 255)


@dataclass
class SimulatorConfig:
    """Configuration for the LED simulator."""
    width: int = 64          # LED columns
    height: int = 32         # LED rows
    pixel_size: int = 12     # Size of each LED pixel on screen
    pixel_gap: int = 2       # Gap between LEDs
    background: Tuple[int, int, int] = (20, 20, 20)  # Dark background
    glow: bool = True        # Enable LED glow effect
    title: str = "CITYARRAY LED Simulator"


# Simple 5x7 bitmap font for LED display
FONT_5X7 = {
    'A': [0x7E, 0x11, 0x11, 0x11, 0x7E],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    'D': [0x7F, 0x41, 0x41, 0x41, 0x3E],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
    'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
    'G': [0x3E, 0x41, 0x49, 0x49, 0x7A],
    'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
    'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
    'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
    'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
    'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F],
    'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
    'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
    'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
    'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E],
    'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
    'S': [0x46, 0x49, 0x49, 0x49, 0x31],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
    'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
    'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
    'W': [0x3F, 0x40, 0x38, 0x40, 0x3F],
    'X': [0x63, 0x14, 0x08, 0x14, 0x63],
    'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
    'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
    '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
    '2': [0x42, 0x61, 0x51, 0x49, 0x46],
    '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
    '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
    '5': [0x27, 0x45, 0x45, 0x45, 0x39],
    '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
    '7': [0x01, 0x71, 0x09, 0x05, 0x03],
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],
    '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    ':': [0x00, 0x36, 0x36, 0x00, 0x00],
    '-': [0x08, 0x08, 0x08, 0x08, 0x08],
    '.': [0x00, 0x60, 0x60, 0x00, 0x00],
    '!': [0x00, 0x00, 0x5F, 0x00, 0x00],
    '?': [0x02, 0x01, 0x51, 0x09, 0x06],
}


class LEDSimulator:
    """
    Virtual LED matrix display simulator.
    
    Creates a pygame window that simulates an LED sign.
    Integrates with the CITYARRAY SDK display backend.
    """
    
    def __init__(self, config: Optional[SimulatorConfig] = None):
        """Initialize the LED simulator."""
        self.config = config or SimulatorConfig()
        
        # Calculate window size
        self.window_width = (
            self.config.width * (self.config.pixel_size + self.config.pixel_gap) 
            + self.config.pixel_gap
        )
        self.window_height = (
            self.config.height * (self.config.pixel_size + self.config.pixel_gap)
            + self.config.pixel_gap
        )
        
        # Pixel buffer - stores RGB color for each LED
        self.pixels = np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
        
        # Pygame initialization
        self._initialized = False
        self.screen = None
        self.clock = None
    
    def init(self) -> bool:
        """Initialize pygame. Call before using the simulator."""
        if self._initialized:
            return True
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(self.config.title)
        self.clock = pygame.time.Clock()
        self._initialized = True
        return True
    
    def quit(self) -> None:
        """Clean up pygame resources."""
        if self._initialized:
            pygame.quit()
            self._initialized = False
    
    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear all pixels to specified color (default: off/black)."""
        self.pixels[:, :] = color
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Set a single pixel to specified RGB color."""
        if 0 <= x < self.config.width and 0 <= y < self.config.height:
            self.pixels[y, x] = color
    
    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get the color of a pixel."""
        if 0 <= x < self.config.width and 0 <= y < self.config.height:
            return tuple(self.pixels[y, x])
        return (0, 0, 0)
    
    def draw_char(
        self, 
        char: str, 
        x: int, 
        y: int, 
        color: Tuple[int, int, int]
    ) -> int:
        """
        Draw a single character at position.
        
        Returns: width of character drawn (for positioning next char)
        """
        char = char.upper()
        if char not in FONT_5X7:
            char = '?'
        
        bitmap = FONT_5X7[char]
        
        for col, byte in enumerate(bitmap):
            for row in range(7):
                if byte & (1 << row):
                    self.set_pixel(x + col, y + row, color)
        
        return 6  # Character width + 1 pixel spacing
    
    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int] = LEDColor.GREEN.value,
        center: bool = False
    ) -> None:
        """
        Draw text string at position.
        
        Args:
            text: String to display
            x: Starting X position (or center X if center=True)
            y: Starting Y position
            color: RGB color tuple
            center: If True, center text at x position
        """
        if center:
            text_width = len(text) * 6 - 1
            x = x - text_width // 2
        
        cursor_x = x
        for char in text:
            cursor_x += self.draw_char(char, cursor_x, y, color)
    
    def draw_text_centered(
        self,
        text: str,
        color: Tuple[int, int, int] = LEDColor.GREEN.value,
        y_offset: int = 0
    ) -> None:
        """Draw text centered on the display."""
        center_x = self.config.width // 2
        center_y = (self.config.height - 7) // 2 + y_offset
        self.draw_text(text, center_x, center_y, color, center=True)
    
    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int]
    ) -> None:
        """Fill a rectangular area with color."""
        for py in range(y, min(y + height, self.config.height)):
            for px in range(x, min(x + width, self.config.width)):
                self.set_pixel(px, py, color)
    
    def render(self) -> None:
        """Render the pixel buffer to the pygame window."""
        if not self._initialized:
            self.init()
        
        # Fill background
        self.screen.fill(self.config.background)
        
        # Draw each LED pixel
        for y in range(self.config.height):
            for x in range(self.config.width):
                color = tuple(self.pixels[y, x])
                
                # Calculate screen position
                screen_x = x * (self.config.pixel_size + self.config.pixel_gap) + self.config.pixel_gap
                screen_y = y * (self.config.pixel_size + self.config.pixel_gap) + self.config.pixel_gap
                
                # Draw glow effect (larger, dimmer circle behind)
                if self.config.glow and color != (0, 0, 0):
                    glow_color = tuple(c // 4 for c in color)
                    glow_size = self.config.pixel_size + 4
                    glow_rect = pygame.Rect(
                        screen_x - 2,
                        screen_y - 2,
                        glow_size,
                        glow_size
                    )
                    pygame.draw.ellipse(self.screen, glow_color, glow_rect)
                
                # Draw the LED pixel
                pixel_rect = pygame.Rect(
                    screen_x,
                    screen_y,
                    self.config.pixel_size,
                    self.config.pixel_size
                )
                pygame.draw.ellipse(self.screen, color, pixel_rect)
        
        # Update display
        pygame.display.flip()
    
    def process_events(self) -> bool:
        """
        Process pygame events.
        
        Returns: False if window should close, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def tick(self, fps: int = 30) -> None:
        """Limit frame rate."""
        self.clock.tick(fps)


def demo():
    """Simple demonstration of the LED simulator."""
    print("CITYARRAY LED Simulator Demo")
    print("Press ESC to exit")
    print()
    
    # Create simulator
    sim = LEDSimulator()
    sim.init()
    
    # Demo messages
    messages = [
        ("CITYARRAY", LEDColor.GREEN.value),
        ("ALERT", LEDColor.RED.value),
        ("CAUTION", LEDColor.AMBER.value),
        ("INFO", LEDColor.BLUE.value),
    ]
    
    current_msg = 0
    frame_count = 0
    
    running = True
    while running:
        # Process events
        running = sim.process_events()
        
        # Change message every 2 seconds (60 frames)
        if frame_count % 60 == 0:
            sim.clear()
            text, color = messages[current_msg % len(messages)]
            sim.draw_text_centered(text, color)
            current_msg += 1
        
        # Render
        sim.render()
        sim.tick(30)
        frame_count += 1
    
    sim.quit()
    print("Demo ended.")


if __name__ == "__main__":
    demo()
