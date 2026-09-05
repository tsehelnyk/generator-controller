from machine import I2C, Pin
import ssd1306, utime
from math import sin, cos, radians

SIN_TABLE = [int(256 * sin(radians(i))) for i in range(360)]
COS_TABLE = [int(256 * cos(radians(i))) for i in range(360)]

def fast_sin(angle):
    """Fast sine using a lookup table."""
    return SIN_TABLE[angle % 360]

def fast_cos(angle):
    """Fast cosine using a lookup table."""
    return COS_TABLE[angle % 360]

# Cyrillic font (8x8 pixels)
font = {
    # Cyrillic (uppercase)
    'А': b'\x10\x28\x44\x82\xFE\x82\x82\x82',
    'Б': b'\xFE\x80\x80\xFC\x82\x82\x82\xFC',
    'В': b'\xFC\x82\x82\xFC\x82\x82\x82\xFC',
    'Г': b'\xFE\x80\x80\x80\x80\x80\x80\x80',
    'Ґ': b'\x04\xFC\x80\x80\x80\x80\x80\x80',
    'Д': b'\x0C\x12\x22\x42\x42\xFE\x82\x00',
    'Е': b'\xFC\x80\x80\xFC\x80\x80\xFC\x00',
    'Ё': b'\x48\x00\xFC\x80\xFC\x80\xFC\x00',
    'Є': b'\x7C\x80\x80\xFC\x80\x80\x7C\x00',
    'Ж': b'\x8A\x8A\x8A\x74\x8A\x8A\x8A\x8A',
    'З': b'\x7C\x82\x02\x1C\x02\x82\x82\x7C',
    'И': b'\x82\x82\x86\x8A\x92\xA2\xC2\x82',
    'І': b'\xFE\x10\x10\x10\x10\x10\x10\xFE',
    'Ї': b'\x6C\x00\xFE\x10\x10\x10\x10\xFE',
    'Й': b'\x38\x86\x8A\x92\xA2\xC2\x82\x82',
    'К': b'\x82\x84\x88\xF0\x88\x84\x82\x82',
    'Л': b'\x3E\x22\x22\x42\x42\x42\x82\x00',
    'М': b'\x82\xC6\xAA\x92\x82\x82\x82\x82',
    'Н': b'\x82\x82\x82\xFE\x82\x82\x82\x82',
    'О': b'\x7C\x82\x82\x82\x82\x82\x82\x7C',
    'П': b'\xFE\x82\x82\x82\x82\x82\x82\x82',
    'Р': b'\xFC\x82\x82\xFC\x80\x80\x80\x80',
    'С': b'\x7C\x82\x80\x80\x80\x80\x82\x7C',
    'Т': b'\xFE\x10\x10\x10\x10\x10\x10\x10',
    'У': b'\x82\x82\x82\x46\x3A\x02\x82\x7C',
    'Ф': b'\x38\x54\x92\x54\x38\x10\x10\x10',
    'Х': b'\x82\x44\x28\x10\x28\x44\x82\x00',
    'Ц': b'\x82\x82\x82\x82\x82\x82\xFE\x02',
    'Ч': b'\x82\x82\x82\x42\x3E\x02\x02\x02',
    'Ш': b'\x92\x92\x92\x92\x92\x92\xFE\x00',
    'Щ': b'\x92\x92\x92\x92\x92\xFE\x04\x08',
    'Ъ': b'\xE0\x20\x20\x3C\x22\x22\x22\x3C',
    'Ы': b'\x82\x82\x82\xF2\x8E\x82\x82\x82',
    'Ь': b'\x80\x80\x80\xFC\x82\x82\x82\xFC',
    'Э': b'\x7C\x82\x02\x3E\x02\x82\x82\x7C',
    'Ю': b'\x9C\xA2\xA2\xE2\xA2\xA2\xA2\x9C',
    'Я': b'\x3E\x42\x82\x42\x3E\x42\x82\x82',
    # Cyrillic (lowercase)
    'а': b'\x00\x3C\x04\x02\x7E\x82\x7C\x00',
    'б': b'\x00\x78\x80\xF8\x84\x84\x78\x00',
    'в': b'\x00\xF8\x84\xF8\x84\x84\xF8\x00',
    'г': b'\x00\xFC\x80\x80\x80\x80\x80\x00',
    'ґ': b'\x00\x04\xFC\x80\x80\x80\x80\x00',
    'д': b'\x00\x0C\x12\x22\x42\xFE\x82\x00',
    'е': b'\x00\x3C\x42\x81\xFF\x80\x7E\x00',
    'ё': b'\x48\x00\x78\x84\xFC\x80\x7C\x00',
    'є': b'\x00\x3C\x80\x80\xFC\x80\x7E\x00',
    'ж': b'\x8A\x8A\x54\x28\x54\x8A\x8A\x00',
    'з': b'\x00\x78\x84\x08\x04\x84\x78\x00',
    'и': b'\x00\x84\x8C\x94\xA4\xC4\x84\x00',
    'і': b'\x00\x10\x00\x30\x10\x10\x38\x00',
    'ї': b'\x00\x28\x00\x30\x10\x10\x38\x00',
    'й': b'\x38\x8C\x94\xA4\xC4\x84\x84\x00',
    'к': b'\x00\x84\x88\xF0\x88\x84\x84\x00',
    'л': b'\x00\x3E\x22\x42\x42\x42\x82\x00',
    'м': b'\x00\x82\xC6\xAA\x92\x82\x82\x00',
    'н': b'\x00\x84\x84\xFC\x84\x84\x84\x00',
    'о': b'\x00\x78\x84\x84\x84\x84\x78\x00',
    'п': b'\x00\xFC\x84\x84\x84\x84\x84\x00',
    'р': b'\x00\xF8\x84\x84\xF8\x80\x80\x00',
    'с': b'\x00\x78\x84\x80\x80\x84\x78\x00',
    'т': b'\x00\xFC\x10\x10\x10\x10\x10\x00',
    'у': b'\x00\x82\x44\x28\x10\x20\x40\x00',
    'ф': b'\x00\x7C\x92\x7C\x10\x10\x10\x00',
    'х': b'\x00\x84\x48\x30\x30\x48\x84\x00',
    'ц': b'\x00\x84\x84\x84\x84\x84\xFC\x04',
    'ч': b'\x00\x84\x84\x44\x3C\x04\x04\x00',
    'ш': b'\x00\x92\x92\x92\x92\x92\xFE\x00',
    'щ': b'\x00\x92\x92\x92\x92\xFE\x04\x00',
    'ъ': b'\x00\xE0\x20\x3C\x22\x22\x1C\x00',
    'ы': b'\x00\x84\x84\xE4\x9C\x84\x84\x00',
    'ь': b'\x00\x80\x80\xF8\x84\x84\xF8\x00',
    'э': b'\x00\x78\x84\x04\x3C\x04\x78\x00',
    'ю': b'\x00\x9C\xA2\xE2\xA2\xA2\x9C\x00',
    'я': b'\x00\x7C\x82\x42\x3C\x42\x82\x00',
    # Latin (uppercase)
    'A': b'\x10\x28\x44\x82\xFE\x82\x82\x82',
    'B': b'\xFC\x82\x82\xFC\x82\x82\x82\xFC',
    'C': b'\x7C\x82\x80\x80\x80\x80\x82\x7C',
    'D': b'\xFC\x82\x82\x82\x82\x82\x82\xFC',
    'E': b'\xFE\x80\x80\xFC\x80\x80\x80\xFE',
    'F': b'\xFE\x80\x80\xFC\x80\x80\x80\x80',
    'G': b'\x7C\x82\x80\x80\x8E\x82\x82\x7C',
    'H': b'\x82\x82\x82\xFE\x82\x82\x82\x82',
    'I': b'\xFE\x10\x10\x10\x10\x10\x10\xFE',
    'J': b'\x06\x02\x02\x02\x02\x82\x82\x7C',
    'K': b'\x82\x84\x88\xF0\x88\x84\x82\x82',
    'L': b'\x80\x80\x80\x80\x80\x80\x80\xFE',
    'M': b'\x82\xC6\xAA\x92\x82\x82\x82\x82',
    'N': b'\x82\xC2\xA2\x92\x8A\x86\x82\x82',
    'O': b'\x7C\x82\x82\x82\x82\x82\x82\x7C',
    'P': b'\xFC\x82\x82\xFC\x80\x80\x80\x80',
    'Q': b'\x7C\x82\x82\x82\x8A\x84\x82\x7E',
    'R': b'\xFC\x82\x82\xFC\x88\x84\x82\x82',
    'S': b'\x7C\x82\x80\x7C\x02\x02\x82\x7C',
    'T': b'\xFE\x10\x10\x10\x10\x10\x10\x10',
    'U': b'\x82\x82\x82\x82\x82\x82\x82\x7C',
    'V': b'\x82\x82\x82\x82\x82\x44\x28\x10',
    'W': b'\x82\x82\x82\x92\x92\xAA\xC6\x82',
    'X': b'\x82\x44\x28\x10\x28\x44\x82\x82',
    'Y': b'\x82\x44\x28\x10\x10\x10\x10\x10',
    'Z': b'\xFE\x02\x04\x08\x10\x20\x40\xFE',
    # Latin (lowercase)
    'a': b'\x00\x00\x78\x04\x7C\x84\x7C\x00',
    'b': b'\x00\x78\x80\xF8\x84\x84\x78\x00',
    'c': b'\x00\x00\x7C\x80\x80\x80\x7C\x00',
    'd': b'\x00\x04\x04\x7C\x84\x84\x7C\x00',
    'e': b'\x00\x00\x78\x84\xFC\x80\x7C\x00',
    'f': b'\x00\x38\x40\xF0\x40\x40\x40\x00',
    'g': b'\x00\x00\x7C\x84\x7C\x04\x78\x00',
    'h': b'\x00\x80\x80\xF8\x84\x84\x84\x00',
    'i': b'\x00\x10\x00\x30\x10\x10\x38\x00',
    'j': b'\x00\x04\x00\x04\x04\x84\x78\x00',
    'k': b'\x00\x80\x88\x90\xE0\x90\x88\x00',
    'l': b'\x00\x30\x10\x10\x10\x10\x38\x00',
    'm': b'\x00\x00\xD8\xA4\xA4\xA4\xA4\x00',
    'n': b'\x00\x00\xF8\x84\x84\x84\x84\x00',
    'o': b'\x00\x00\x78\x84\x84\x84\x78\x00',
    'p': b'\x00\x00\xF8\x84\xF8\x80\x80\x00',
    'q': b'\x00\x00\x7C\x84\x7C\x04\x04\x00',
    'r': b'\x00\x00\xB8\xC4\x80\x80\x80\x00',
    's': b'\x00\x00\x7C\x80\x78\x04\xF8\x00',
    't': b'\x00\x40\xF0\x40\x40\x40\x38\x00',
    'u': b'\x00\x00\x84\x84\x84\x84\x7C\x00',
    'v': b'\x00\x00\x84\x84\x84\x48\x30\x00',
    'w': b'\x00\x00\x84\x84\xA4\xA4\x58\x00',
    'x': b'\x00\x00\x84\x48\x30\x48\x84\x00',
    'y': b'\x00\x00\x84\x84\x7C\x04\x78\x00',
    'z': b'\x00\x00\xFC\x08\x10\x20\xFC\x00',
    # Digits
    '0': b'\x7C\x82\x82\x82\x82\x82\x82\x7C',
    '1': b'\x10\x30\x10\x10\x10\x10\x10\x38',
    '2': b'\x7C\x82\x02\x04\x18\x20\x40\xFE',
    '3': b'\x7C\x82\x02\x1C\x02\x02\x82\x7C',
    '4': b'\x04\x0C\x14\x24\x44\xFE\x04\x04',
    '5': b'\xFE\x80\x80\xFC\x02\x02\x82\x7C',
    '6': b'\x7C\x82\x80\xFC\x82\x82\x82\x7C',
    '7': b'\xFE\x02\x04\x08\x10\x20\x40\x80',
    '8': b'\x7C\x82\x82\x7C\x82\x82\x82\x7C',
    '9': b'\x7C\x82\x82\x7E\x02\x02\x82\x7C',
    # Symbols
    '!': b'\x10\x10\x10\x10\x10\x00\x10\x00',
    '?': b'\x7C\x82\x02\x04\x08\x00\x08\x00',
    '@': b'\x7C\x82\xBA\xAA\xBE\x80\x82\x7C',
    '#': b'\x24\x24\xFE\x24\x24\xFE\x24\x24',
    '$': b'\x10\x7C\x90\x7C\x12\x12\xFC\x10',
    '%': b'\xC2\xC4\x08\x10\x20\x46\x86\x00',
    '^': b'\x10\x28\x44\x00\x00\x00\x00\x00',
    '&': b'\x30\x48\x50\x20\x54\x88\x74\x00',
    '*': b'\x00\x10\xAA\x44\xAA\x10\x00\x00',
    '(': b'\x10\x20\x40\x40\x40\x20\x10\x00',
    ')': b'\x10\x08\x04\x04\x04\x08\x10\x00',
    '-': b'\x00\x00\x00\xFE\x00\x00\x00\x00',
    '_': b'\x00\x00\x00\x00\x00\x00\x00\xFE',
    '+': b'\x00\x10\x10\xFE\x10\x10\x00\x00',
    '=': b'\x00\x00\xFE\x00\xFE\x00\x00\x00',
    '[': b'\x78\x40\x40\x40\x40\x40\x78\x00',
    ']': b'\x78\x08\x08\x08\x08\x08\x78\x00',
    '{': b'\x0C\x10\x10\x60\x10\x10\x0C\x00',
    '}': b'\x60\x10\x10\x0C\x10\x10\x60\x00',
    '\\': b'\x80\x40\x20\x10\x08\x04\x02\x00',
    '|': b'\x10\x10\x10\x10\x10\x10\x10\x00',
    ';': b'\x00\x10\x00\x00\x00\x10\x10\x20',
    ':': b'\x00\x10\x00\x00\x00\x10\x00\x00',
    '"': b'\x28\x28\x00\x00\x00\x00\x00\x00',
    "'": b'\x10\x10\x00\x00\x00\x00\x00\x00',
    ',': b'\x00\x00\x00\x00\x00\x10\x10\x20',
    '.': b'\x00\x00\x00\x00\x00\x00\x10\x00',
    '/': b'\x02\x04\x08\x10\x20\x40\x80\x00',
    '<': b'\x04\x08\x10\x20\x10\x08\x04\x00',
    '>': b'\x20\x10\x08\x04\x08\x10\x20\x00',
    '`': b'\x10\x08\x00\x00\x00\x00\x00\x00',
    '~': b'\x00\x44\xA8\x10\x00\x00\x00\x00',
    # Space
    ' ': b'\x00\x00\x00\x00\x00\x00\x00\x00',
}

class SillyOled:
    def __init__(self, interface, width=128, height=64, **kwargs):
        """
        Initialize the display.
        :param interface: Interface (I2C or SPI).
        :param width: Display width (default 128).
        :param height: Display height (default 64).
        :param kwargs: Additional parameters for I2C or SPI.
        """
        self.interface = interface
        self.width = width
        self.height = height
        self.font = font
        self.current_scale = 1

        # Initialize the display depending on the interface
        if isinstance(interface, I2C):
            # I2C display
            self.display = ssd1306.SSD1306_I2C(width, height, interface, addr=kwargs.get('address', 0x3C))
        elif isinstance(interface, SPI):
            # SPI display
            dc = kwargs.get('dc')
            res = kwargs.get('res')
            cs = kwargs.get('cs')
            if not all([dc, res, cs]):
                raise ValueError("For SPI, you must specify the pins dc, res, and cs.")
            self.display = ssd1306.SSD1306_SPI(width, height, interface, dc, res, cs)
        else:
            raise ValueError("Unsupported interface. Use I2C or SPI.")

    def clear(self):
        """Clear the screen."""
        self.display.fill(0)

    def show(self):
        """Update the screen."""
        self.display.show()
    
    def set_font(self, font, width=8, height=8):
        """
        Set the font.
        :param font: Dictionary with font data.
        :param width: Width of the character.
        :param height: Height of the character.
        """
        self.font = font
        self.char_width = width
        self.char_height = height

    def scale(self, new_scale):
        """
        Set the text scale.
        :param new_scale: New scale (1, 2, 3, etc.).
        """
        if new_scale < 1:
            new_scale = 1  # Minimum scale — 1
        self.current_scale = new_scale
        
    def text(self, text, x, y, align="left"):
        """
        Display text on the screen.
        :param text: Text to display.
        :param x: X coordinate.
        :param y: Y coordinate.
        :param align: Alignment ("left", "center", "right").
        """
        original_x = x  # Save the initial x position for line wrapping
        char_width = 8 * self.current_scale  # Width of the character with scale
        char_height = 8 * self.current_scale  # Height of the character with scale

        # Calculate the offset for alignment
        if align == "center":
            x -= (len(text) * char_width) // 2  # Center the text
        elif align == "right":
            x -= len(text) * char_width  # Align the text to the right

        for char in text:
            # If the character goes beyond the screen width, wrap to the next line
            if x + char_width > self.width:
                x = original_x  # Return to the initial x position
                y += char_height  # Move to the next line

                # Recalculate the offset for alignment on the new line
                if align == "center":
                    x -= (len(text) * char_width) // 2
                elif align == "right":
                    x -= len(text) * char_width

                # If the text goes beyond the screen boundaries in height, stop displaying
                if y + char_height > self.height:
                    return  # Exit the function

            # Draw the character
            self._draw_char(char, x, y)
            x += char_width  # Shift the position for the next character

    def scroll_text(self, text, y, delay=50, direction="left"):
        """
        Scroll text across the screen.
        :param text: Text to scroll.
        :param y: Y coordinate (height of the text).
        :param delay: Delay between frames (in milliseconds).
        :param direction: Scroll direction ("left", "right").
        """
        text_width = len(text) * 8 * self.current_scale  # Width of the text
        x = self.width if direction == "left" else -text_width  # Initial position

        while True:
            self.clear()  # Clear the screen
            self.text(text, x, y)  # Draw the text
            self.show()  # Update the screen

            if direction == "left":
                x -= 1  # Move the text to the left
                if x + text_width < 0:  # If the text has completely moved off the screen
                    x = self.width  # Return it to the start
            else:
                x += 1  # Move the text to the right
                if x > self.width:  # If the text has completely moved off the screen
                    x = -text_width  # Return it to the start

            utime.sleep_ms(delay)  # Delay for smoothness

    def draw_buffer(self, buffer, x, y, width, height):
        """
        Draw a data buffer on the screen.
        :param buffer: Data buffer (list of bytes).
        :param x, y: Coordinates of the buffer's origin.
        :param width, height: Dimensions of the buffer.
        """
        for i in range(width):
            for j in range(height):
                if buffer[j * width + i]:
                    self.display.pixel(x + i, y + j, 1)

    def _draw_char(self, char, x, y):
        """Draw a single character with scaling."""
        """Optimized character drawing."""
        if char in self.font:
            char_data = self.font[char]
            for row in range(8):
                byte = char_data[row]
                for col in range(8):
                    if byte & (1 << (7 - col)):
                        self.display.pixel(x + col, y + row, 1)
    
    def fade_in(self, steps=10, delay=50):
        """
        Fade in the display.
        :param steps: Number of steps.
        :param delay: Delay between steps (in milliseconds).
        """
        for i in range(steps):
            self.contrast(int(255 * (i / steps)))
            self.show()
            time.sleep_ms(delay)

    def fade_out(self, steps=10, delay=50):
        """
        Fade out the display.
        :param steps: Number of steps.
        :param delay: Delay between steps (in milliseconds).
        """
        for i in range(steps, -1, -1):
            self.contrast(int(255 * (i / steps)))
            self.show()
            time.sleep_ms(delay)
            
    def rotate(self, degrees=0):
        """
        Rotate the display.
        :param degrees: Rotation angle (0, 90, 180, 270).
        """
        if degrees == 0:
            self.display.rotate(False)
        elif degrees == 90:
            self.display.rotate(True)
        elif degrees == 180:
            self.display.rotate(True)
            self.display.rotate(True)
        elif degrees == 270:
            self.display.rotate(True)
            self.display.rotate(True)
            self.display.rotate(True)

    def partial_update(self, x, y, width, height):
        """
        Perform a partial update of the screen.
        :param x: X coordinate.
        :param y: Y coordinate.
        :param width: Width of the area.
        :param height: Height of the area.
        """
        self.display.show_partial(x, y, width, height)

    def rect(self, x, y, width, height, fill=False):
        #Draw a rectangle.
        if fill:
            for i in range(width):
                for j in range(height):
                    self.display.pixel(x + i, y + j, 1)
        else:
            for i in range(width):
                self.display.pixel(x + i, y, 1)
                self.display.pixel(x + i, y + height - 1, 1)
            for i in range(height):
                self.display.pixel(x, y + i, 1)
                self.display.pixel(x + width - 1, y + i, 1)

    def line(self, x1, y1, x2, y2):
        """
        Draw a line.
        :param x1: Initial X coordinate.
        :param y1: Initial Y coordinate.
        :param x2: Final X coordinate.
        :param y2: Final Y coordinate.
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.display.pixel(x1, y1, 1)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def circle(self, x, y, radius, fill=False):
        """Draw a circle."""
        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x0 = 0
        y0 = radius

        while x0 < y0:
            if f >= 0:
                y0 -= 1
                ddf_y += 2
                f += ddf_y
            x0 += 1
            ddf_x += 2
            f += ddf_x

            if fill:
                self.line(x - x0, y + y0, x + x0, y + y0)
                self.line(x - x0, y - y0, x + x0, y - y0)
                self.line(x - y0, y + x0, x + y0, y + x0)
                self.line(x - y0, y - x0, x + y0, y - x0)
            else:
                self.display.pixel(x + x0, y + y0, 1)
                self.display.pixel(x - x0, y + y0, 1)
                self.display.pixel(x + x0, y - y0, 1)
                self.display.pixel(x - x0, y - y0, 1)
                self.display.pixel(x + y0, y + x0, 1)
                self.display.pixel(x - y0, y + x0, 1)
                self.display.pixel(x + y0, y - x0, 1)
                self.display.pixel(x - y0, y - x0, 1)
    
    def rounded_rect(self, x, y, width, height, radius, fill=False):
        """
        Draw a rounded rectangle.
        :param x: X coordinate.
        :param y: Y coordinate.
        :param width: Width.
        :param height: Height.
        :param radius: Corner radius.
        :param fill: Fill flag (True/False).
        """
        if fill:
            # Fill the main rectangle
            self.rect(x + radius, y, width - 2 * radius, height, fill=True)
            self.rect(x, y + radius, width, height - 2 * radius, fill=True)
            # Fill the rounded corners
            self.circle(x + radius, y + radius, radius, fill=True)
            self.circle(x + width - radius - 1, y + radius, radius, fill=True)
            self.circle(x + radius, y + height - radius - 1, radius, fill=True)
            self.circle(x + width - radius - 1, y + height - radius - 1, radius, fill=True)
        else:
            # Draw the outline
            self.line(x + radius, y, x + width - radius - 1, y)  # Top line
            self.line(x + radius, y + height - 1, x + width - radius - 1, y + height - 1)  # Bottom line
            self.line(x, y + radius, x, y + height - radius - 1)  # Left line
            self.line(x + width - 1, y + radius, x + width - 1, y + height - radius - 1)  # Right line
            # Draw the rounded corners
            self.circle(x + radius, y + radius, radius)
            self.circle(x + width - radius - 1, y + radius, radius)
            self.circle(x + radius, y + height - radius - 1, radius)
            self.circle(x + width - radius - 1, y + height - radius - 1, radius)
    
    def thick_line(self, x1, y1, x2, y2, thickness=1):
        """
        Draw a line with a specified thickness.
        :param x1, y1: Initial point.
        :param x2, y2: Final point.
        :param thickness: Line thickness.
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            for i in range(-thickness // 2, thickness // 2 + 1):
                for j in range(-thickness // 2, thickness // 2 + 1):
                    self.display.pixel(x1 + i, y1 + j, 1)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    
    def triangle(self, x1, y1, x2, y2, x3, y3, fill=False):
        """
        Draw a triangle.
        :param x1, y1: Coordinates of the first vertex.
        :param x2, y2: Coordinates of the second vertex.
        :param x3, y3: Coordinates of the third vertex.
        :param fill: Fill flag (True/False).
        """
        if fill:
            # Fill the triangle (scanline algorithm)
            def interpolate(y, x1, y1, x2, y2):
                if y1 == y2:
                    return x1
                return x1 + (y - y1) * (x2 - x1) // (y2 - y1)

            # Sort the vertices by Y
            vertices = sorted([(x1, y1), (x2, y2), (x3, y3)], key=lambda v: v[1])
            x1, y1 = vertices[0]
            x2, y2 = vertices[1]
            x3, y3 = vertices[2]

            for y in range(y1, y3 + 1):
                if y < y2:
                    x_start = interpolate(y, x1, y1, x2, y2)
                    x_end = interpolate(y, x1, y1, x3, y3)
                else:
                    x_start = interpolate(y, x2, y2, x3, y3)
                    x_end = interpolate(y, x1, y1, x3, y3)
                self.line(int(x_start), y, int(x_end), y)
        else:
            # Draw only the outline
            self.line(x1, y1, x2, y2)
            self.line(x2, y2, x3, y3)
            self.line(x3, y3, x1, y1)
    
    def gradient(self, x, y, width, height, color1, color2, direction="horizontal"):
        """
        Draw a gradient.
        :param x: X coordinate.
        :param y: Y coordinate.
        :param width: Width of the gradient.
        :param height: Height of the gradient.
        :param color1: Initial color (0-255).
        :param color2: Final color (0-255).
        :param direction: Gradient direction ("horizontal" or "vertical").
        """
        for i in range(width if direction == "horizontal" else height):
            t = i / (width if direction == "horizontal" else height)
            color = int(color1 + (color2 - color1) * t)
            if direction == "horizontal":
                self.line(x + i, y, x + i, y + height - 1, color)
            else:
                self.line(x, y + i, x + width - 1, y + i, color)
    
    def ellipse(self, x, y, width, height, fill=False):
        """
        Draw an ellipse.
        :param x: X coordinate of the center.
        :param y: Y coordinate of the center.
        :param width: Width of the ellipse.
        :param height: Height of the ellipse.
        :param fill: Fill flag (True/False).
        """
        a = width // 2
        b = height // 2
        for dy in range(-b, b + 1):
            for dx in range(-a, a + 1):
                if (dx * dx) / (a * a) + (dy * dy) / (b * b) <= 1:
                    self.display.pixel(x + dx, y + dy, 1 if fill else 1)

    def smooth_curve(self, x, y, length, angle, amplitude, phase=0, steps=20):
        """
        Draw a smooth curve, similar to a sine wave.
        :param x, y: Initial point.
        :param length: Length of the curve.
        :param angle: Angle of the curve (in degrees).
        :param amplitude: Amplitude of the curve (bending strength).
        :param phase: Phase of the curve (offset).
        :param steps: Number of steps for smoothing.
        """
        """
        Optimized version of smooth_curve.
        """
        angle_rad = angle % 360  # Normalize angle to [0, 360)
        prev_x, prev_y = x, y

        for i in range(steps + 1):
            t = (i << 8) // steps  # Parameter t in fixed-point format (8 bits for fractional part)
            # Compute the current point on the curve
            curve_x = x + (t * length * fast_cos(angle_rad)) >> 8
            curve_y = y + (t * length * fast_sin(angle_rad)) >> 8
            curve_y += (amplitude * fast_sin(phase + (t * 314) >> 8)) >> 8
            # Draw a line between the current and previous point
            self.line(prev_x, prev_y, curve_x, curve_y)
            prev_x, prev_y = curve_x, curve_y
    
    def bitmap(self, x, y, data, width, height):
        """
        Show bitmap-picture.
        :param x: Coordinate X.
        :param y: Coordinate Y.
        :param data: Picture data (byte list).
        :param width: Weight of picture.
        :param height: height of picture.
        """
        for j in range(height):  # Cycle through rows (height)
            for i in range(width):  # Cycle through columns (width)
                # Get the current byte (image row)
                byte = data[j]
                # Check if the bit is set in the current position
                if byte & (1 << (width - 1 - i)):
                    self.display.pixel(x + i, y + j, 1)

    # New functions from the original library ssd1306

    def contrast(self, value):
        """
        Sets the display contrast.
        :param value: Contrast value (0-255).
        """
        self.display.contrast(value)

    def power(self, on=True):
        """on/off display."""
        self.display.poweron() if on else self.display.poweroff()

    def invert(self, invert=True):
        """Invert colors."""
        self.display.invert(invert)
