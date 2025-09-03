"""
Color definitions and utilities for terminal output.

This module provides color classes and utilities for managing terminal colors,
including both standard ANSI colors and RGB colors.
"""

from typing import Dict, List, Tuple, Union
from enum import Enum


class ColorType(Enum):
    """Enumeration of color types."""

    FOREGROUND = "fg"
    BACKGROUND = "bg"


class Color:
    """
    Standard ANSI color representation.

    Provides predefined colors and methods to generate ANSI escape sequences
    for both foreground and background colors.
    """

    # Standard ANSI colors (foreground codes)
    COLORS = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "bright_black": 90,
        "bright_red": 91,
        "bright_green": 92,
        "bright_yellow": 93,
        "bright_blue": 94,
        "bright_magenta": 95,
        "bright_cyan": 96,
        "bright_white": 97,
    }

    # Reset codes
    RESET = "\033[0m"
    RESET_FG = "\033[39m"
    RESET_BG = "\033[49m"

    def __init__(self, name: str):
        """
        Initialize a color with a predefined name.

        Args:
            name: Color name (e.g., 'red', 'blue', 'bright_green')

        Raises:
            ValueError: If color name is not recognized
        """
        if name not in self.COLORS:
            raise ValueError(
                f"Unknown color: {name}. Available colors: {list(self.COLORS.keys())}"
            )
        self.name = name
        self.code = self.COLORS[name]

    def fg(self) -> str:
        """Get ANSI escape sequence for foreground color."""
        return f"\033[{self.code}m"

    def bg(self) -> str:
        """Get ANSI escape sequence for background color."""
        return f"\033[{self.code + 10}m"

    def __str__(self) -> str:
        """String representation of the color."""
        return self.name

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Color('{self.name}')"

    @classmethod
    def available_colors(cls) -> List[str]:
        """Get list of available color names."""
        return list(cls.COLORS.keys())


class ColorRGB:
    """
    RGB color representation for 24-bit color terminals.

    Provides methods to create RGB colors and generate appropriate ANSI escape sequences.
    """

    def __init__(self, r: int, g: int, b: int):
        """
        Initialize RGB color.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)

        Raises:
            ValueError: If any component is outside 0-255 range
        """
        for component, name in [(r, "red"), (g, "green"), (b, "blue")]:
            if not 0 <= component <= 255:
                raise ValueError(
                    f"{name} component must be between 0 and 255, got {component}"
                )

        self.r = r
        self.g = g
        self.b = b

    def fg(self) -> str:
        """Get ANSI escape sequence for RGB foreground color."""
        return f"\033[38;2;{self.r};{self.g};{self.b}m"

    def bg(self) -> str:
        """Get ANSI escape sequence for RGB background color."""
        return f"\033[48;2;{self.r};{self.g};{self.b}m"

    def __str__(self) -> str:
        """String representation of RGB color."""
        return f"rgb({self.r}, {self.g}, {self.b})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ColorRGB({self.r}, {self.g}, {self.b})"

    def to_hex(self) -> str:
        """Convert RGB to hexadecimal representation."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @classmethod
    def from_hex(cls, hex_color: str) -> "ColorRGB":
        """
        Create RGB color from hexadecimal string.

        Args:
            hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')

        Returns:
            ColorRGB instance

        Raises:
            ValueError: If hex string is invalid
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}. Expected 6 characters.")

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return cls(r, g, b)
        except ValueError as e:
            raise ValueError(f"Invalid hex color: {hex_color}") from e


# Predefined color instances for convenience
class Colors:
    """Predefined color instances for easy access."""

    # Standard colors
    BLACK = Color("black")
    RED = Color("red")
    GREEN = Color("green")
    YELLOW = Color("yellow")
    BLUE = Color("blue")
    MAGENTA = Color("magenta")
    CYAN = Color("cyan")
    WHITE = Color("white")

    # Bright colors
    BRIGHT_BLACK = Color("bright_black")
    BRIGHT_RED = Color("bright_red")
    BRIGHT_GREEN = Color("bright_green")
    BRIGHT_YELLOW = Color("bright_yellow")
    BRIGHT_BLUE = Color("bright_blue")
    BRIGHT_MAGENTA = Color("bright_magenta")
    BRIGHT_CYAN = Color("bright_cyan")
    BRIGHT_WHITE = Color("bright_white")


def get_available_colors() -> List[str]:
    """
    Get list of all available predefined colors.

    Returns:
        List of color names
    """
    return Color.available_colors()


def get_color(
    color: Union[str, Color, ColorRGB, Tuple[int, int, int]],
) -> Union[Color, ColorRGB]:
    """
    Convert various color representations to Color or ColorRGB instance.

    Args:
        color: Color specification (name, Color instance, ColorRGB instance, or RGB tuple)

    Returns:
        Color or ColorRGB instance

    Raises:
        ValueError: If color specification is invalid
    """
    if isinstance(color, (Color, ColorRGB)):
        return color
    elif isinstance(color, str):
        if color.startswith("#") or (
            len(color) == 6 and all(c in "0123456789abcdefABCDEF" for c in color)
        ):
            return ColorRGB.from_hex(color)
        else:
            return Color(color)
    elif isinstance(color, tuple) and len(color) == 3:
        return ColorRGB(*color)
    else:
        raise ValueError(f"Invalid color specification: {color}")
