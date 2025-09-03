"""
KHX Colory - A rich terminal printing library for colorful text, lines, banners, and highlights.

This package provides an easy-to-use API for creating colorful and styled terminal output
with minimal dependencies and high performance.
"""

__version__ = "0.1.0"
__author__ = "KHADER"
__email__ = "khader@example.com"

# Import main classes and functions for easy access
from .colors import Color, ColorRGB, get_available_colors
from .styles import Style, get_available_styles
from .text import (
    ColorText,
    print_colored,
    colored,
    red,
    green,
    blue,
    yellow,
    magenta,
    cyan,
    white,
    black,
    bold,
    italic,
    underline,
    strikethrough,
)
from .core import Colory

# Main API exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Core classes
    "Colory",
    "ColorText",
    # Color classes
    "Color",
    "ColorRGB",
    # Style classes
    "Style",
    # Utility functions
    "print_colored",
    "colored",
    "get_available_colors",
    "get_available_styles",
    # Convenience functions - colors
    "red",
    "green",
    "blue",
    "yellow",
    "magenta",
    "cyan",
    "white",
    "black",
    # Convenience functions - styles
    "bold",
    "italic",
    "underline",
    "strikethrough",
]

# Create a default instance for convenience
colory = Colory()


# Convenience functions using the default instance
def quick_print(text: str, color: str = "white", style: str = "normal") -> None:
    """Quick print with color and style using default instance."""
    colory.print_text(text, color=color, style=style)


def quick_colored(text: str, color: str = "white", style: str = "normal") -> str:
    """Quick colored text formatting using default instance."""
    return colory.colored_text(text, color=color, style=style)
