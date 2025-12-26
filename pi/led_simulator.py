"""
CITYARRAY LED Simulator
64x32 LED matrix display simulation
"""

import pygame
from enum import Enum

class LEDColor(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    AMBER = (255, 191, 0)
    BLUE = (0, 100, 255)
    WHITE = (255, 255, 255)
    OFF = (20, 20, 20)

# 5x7 bitmap font
FONT = {
    'A': [0x7C,0x12,0x11,0x12,0x7C],
    'B': [0x7F,0x49,0x49,0x49,0x36],
    'C': [0x3E,0x41,0x41,0x41,0x22],
    'D': [0x7F,0x41,0x41,0x22,0x1C],
    'E': [0x7F,0x49,0x49,0x49,0x41],
    'F': [0x7F,0x09,0x09,0x09,0x01],
    'G': [0x3E,0x41,0x49,0x49,0x7A],
    'H': [0x7F,0x08,0x08,0x08,0x7F],
    'I': [0x00,0x41,0x7F,0x41,0x00],
    'J': [0x20,0x40,0x41,0x3F,0x01],
    'K': [0x7F,0x08,0x14,0x22,0x41],
    'L': [0x7F,0x40,0x40,0x40,0x40],
    'M': [0x7F,0x02,0x0C,0x02,0x7F],
    'N': [0x7F,0x04,0x08,0x10,0x7F],
    'O': [0x3E,0x41,0x41,0x41,0x3E],
    'P': [0x7F,0x09,0x09,0x09,0x06],
    'Q': [0x3E,0x41,0x51,0x21,0x5E],
    'R': [0x7F,0x09,0x19,0x29,0x46],
    'S': [0x46,0x49,0x49,0x49,0x31],
    'T': [0x01,0x01,0x7F,0x01,0x01],
    'U': [0x3F,0x40,0x40,0x40,0x3F],
    'V': [0x1F,0x20,0x40,0x20,0x1F],
    'W': [0x3F,0x40,0x38,0x40,0x3F],
    'X': [0x63,0x14,0x08,0x14,0x63],
    'Y': [0x07,0x08,0x70,0x08,0x07],
    'Z': [0x61,0x51,0x49,0x45,0x43],
    '0': [0x3E,0x51,0x49,0x45,0x3E],
    '1': [0x00,0x42,0x7F,0x40,0x00],
    '2': [0x42,0x61,0x51,0x49,0x46],
    '3': [0x21,0x41,0x45,0x4B,0x31],
    '4': [0x18,0x14,0x12,0x7F,0x10],
    '5': [0x27,0x45,0x45,0x45,0x39],
    '6': [0x3C,0x4A,0x49,0x49,0x30],
    '7': [0x01,0x71,0x09,0x05,0x03],
    '8': [0x36,0x49,0x49,0x49,0x36],
    '9': [0x06,0x49,0x49,0x29,0x1E],
    ' ': [0x00,0x00,0x00,0x00,0x00],
    ':': [0x00,0x36,0x36,0x00,0x00],
    '!': [0x00,0x00,0x5F,0x00,0x00],
    '-': [0x08,0x08,0x08,0x08,0x08],
    '.': [0x00,0x60,0x60,0x00,0x00],
}

class LEDSimulator:
    def __init__(self, width=64, height=32, pixel_size=10, gap=2):
        self.width = width
        self.height = height
        self.pixel_size = pixel_size
        self.gap = gap
        
        pygame.init()
        window_width = width * (pixel_size + gap) + gap
        window_height = height * (pixel_size + gap) + gap
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("CITYARRAY LED Simulator")
        
        self.pixels = [[(20, 20, 20) for _ in range(width)] for _ in range(height)]
        self.clock = pygame.time.Clock()
    
    def clear(self, color=(20, 20, 20)):
        """Clear display."""
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = color
    
    def set_pixel(self, x, y, color):
        """Set single pixel."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
    
    def draw_char(self, char, x, y, color):
        """Draw character at position."""
        char = char.upper()
        if char not in FONT:
            char = ' '
        
        bitmap = FONT[char]
        for col, bits in enumerate(bitmap):
            for row in range(7):
                if bits & (1 << row):
                    self.set_pixel(x + col, y + row, color)
    
    def draw_text(self, text, x, y, color):
        """Draw text string."""
        cursor = x
        for char in text:
            self.draw_char(char, cursor, y, color)
            cursor += 6
    
    def draw_text_centered(self, text, color, y=None):
        """Draw text centered on display."""
        text_width = len(text) * 6 - 1
        x = (self.width - text_width) // 2
        if y is None:
            y = (self.height - 7) // 2
        self.draw_text(text, x, y, color)
    
    def render(self):
        """Render to screen."""
        self.screen.fill((0, 0, 0))
        
        for y in range(self.height):
            for x in range(self.width):
                color = self.pixels[y][x]
                px = self.gap + x * (self.pixel_size + self.gap)
                py = self.gap + y * (self.pixel_size + self.gap)
                
                # Glow effect
                if color != (20, 20, 20):
                    glow = tuple(c // 4 for c in color)
                    pygame.draw.circle(self.screen, glow,
                        (px + self.pixel_size // 2, py + self.pixel_size // 2),
                        self.pixel_size)
                
                # Pixel
                pygame.draw.rect(self.screen, color,
                    (px, py, self.pixel_size, self.pixel_size),
                    border_radius=2)
        
        pygame.display.flip()
    
    def process_events(self):
        """Handle pygame events. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def tick(self, fps=30):
        """Limit frame rate."""
        self.clock.tick(fps)
    
    def quit(self):
        """Clean up."""
        pygame.quit()


def demo():
    """Demo the simulator."""
    sim = LEDSimulator()
    
    messages = [
        ("CITYARRAY", LEDColor.BLUE.value),
        ("READY", LEDColor.GREEN.value),
        ("PERSON DETECTED", LEDColor.AMBER.value),
        ("EXIT NOW", LEDColor.RED.value),
    ]
    
    msg_index = 0
    frame_count = 0
    
    running = True
    while running:
        running = sim.process_events()
        
        # Change message every 60 frames (2 seconds)
        if frame_count % 60 == 0:
            sim.clear()
            text, color = messages[msg_index]
            sim.draw_text_centered(text, color)
            msg_index = (msg_index + 1) % len(messages)
        
        sim.render()
        sim.tick(30)
        frame_count += 1
    
    sim.quit()


if __name__ == "__main__":
    demo()
