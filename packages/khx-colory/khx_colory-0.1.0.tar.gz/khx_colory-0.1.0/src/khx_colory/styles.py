"""
Text styling definitions and utilities for terminal output.

This module provides style classes and utilities for managing terminal text styles
like bold, italic, underline, and strikethrough.
"""

from typing import Dict, List, Set
from enum import Enum


class StyleType(Enum):
    """Enumeration of style types."""

    FORMATTING = "formatting"
    RESET = "reset"


class Style:
    """
    Text style representation for terminal output.

    Provides predefined styles and methods to generate ANSI escape sequences
    for text formatting like bold, italic, underline, etc.
    """

    # Style codes mapping
    STYLES = {
        "normal": 0,  # Reset/normal
        "bold": 1,  # Bold or increased intensity
        "dim": 2,  # Dim or decreased intensity
        "italic": 3,  # Italic
        "underline": 4,  # Underline
        "blink": 5,  # Slow blink
        "reverse": 7,  # Reverse video
        "strikethrough": 9,  # Strikethrough
    }

    # Reset codes for specific styles
    RESET_CODES = {
        "bold": 22,  # Normal intensity
        "dim": 22,  # Normal intensity
        "italic": 23,  # Not italic
        "underline": 24,  # Not underlined
        "blink": 25,  # Not blinking
        "reverse": 27,  # Not reversed
        "strikethrough": 29,  # Not strikethrough
    }

    # General reset
    RESET_ALL = "\033[0m"

    def __init__(self, name: str):
        """
        Initialize a style with a predefined name.

        Args:
            name: Style name (e.g., 'bold', 'italic', 'underline')

        Raises:
            ValueError: If style name is not recognized
        """
        if name not in self.STYLES:
            raise ValueError(
                f"Unknown style: {name}. Available styles: {list(self.STYLES.keys())}"
            )
        self.name = name
        self.code = self.STYLES[name]

    def apply(self) -> str:
        """Get ANSI escape sequence to apply this style."""
        return f"\033[{self.code}m"

    def reset(self) -> str:
        """Get ANSI escape sequence to reset this style."""
        if self.name == "normal":
            return self.RESET_ALL
        elif self.name in self.RESET_CODES:
            return f"\033[{self.RESET_CODES[self.name]}m"
        else:
            return self.RESET_ALL

    def __str__(self) -> str:
        """String representation of the style."""
        return self.name

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Style('{self.name}')"

    @classmethod
    def available_styles(cls) -> List[str]:
        """Get list of available style names."""
        return list(cls.STYLES.keys())


class StyleCombination:
    """
    Combination of multiple styles that can be applied together.

    Allows combining multiple styles like bold + underline + italic.
    """

    def __init__(self, *styles: str):
        """
        Initialize with multiple style names.

        Args:
            *styles: Variable number of style names

        Raises:
            ValueError: If any style name is not recognized
        """
        self.styles: Set[str] = set()
        for style_name in styles:
            if style_name not in Style.STYLES:
                raise ValueError(f"Unknown style: {style_name}")
            self.styles.add(style_name)

    def add_style(self, style_name: str) -> "StyleCombination":
        """
        Add a style to the combination.

        Args:
            style_name: Name of style to add

        Returns:
            Self for method chaining
        """
        if style_name not in Style.STYLES:
            raise ValueError(f"Unknown style: {style_name}")
        self.styles.add(style_name)
        return self

    def remove_style(self, style_name: str) -> "StyleCombination":
        """
        Remove a style from the combination.

        Args:
            style_name: Name of style to remove

        Returns:
            Self for method chaining
        """
        self.styles.discard(style_name)
        return self

    def apply(self) -> str:
        """Get ANSI escape sequence to apply all styles in combination."""
        if not self.styles or "normal" in self.styles:
            return Style.RESET_ALL

        codes = [Style.STYLES[style] for style in self.styles if style != "normal"]
        if codes:
            return f"\033[{';'.join(map(str, codes))}m"
        return ""

    def reset(self) -> str:
        """Get ANSI escape sequence to reset all styles."""
        return Style.RESET_ALL

    def __str__(self) -> str:
        """String representation of style combination."""
        if not self.styles:
            return "normal"
        return " + ".join(sorted(self.styles))

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"StyleCombination({', '.join(repr(s) for s in sorted(self.styles))})"

    def __bool__(self) -> bool:
        """Check if combination has any styles."""
        return bool(self.styles and "normal" not in self.styles)


# Predefined style instances for convenience
class Styles:
    """Predefined style instances for easy access."""

    NORMAL = Style("normal")
    BOLD = Style("bold")
    DIM = Style("dim")
    ITALIC = Style("italic")
    UNDERLINE = Style("underline")
    BLINK = Style("blink")
    REVERSE = Style("reverse")
    STRIKETHROUGH = Style("strikethrough")


def get_available_styles() -> List[str]:
    """
    Get list of all available predefined styles.

    Returns:
        List of style names
    """
    return Style.available_styles()


def parse_style(style: str) -> StyleCombination:
    """
    Parse a style string into a StyleCombination.

    Supports both single styles and combinations separated by '+' or spaces.

    Args:
        style: Style string (e.g., 'bold', 'bold+italic', 'bold underline')

    Returns:
        StyleCombination instance

    Examples:
        >>> parse_style('bold')
        StyleCombination('bold')
        >>> parse_style('bold+italic+underline')
        StyleCombination('bold', 'italic', 'underline')
        >>> parse_style('bold italic underline')
        StyleCombination('bold', 'italic', 'underline')
    """
    if not style or style.strip() == "":
        return StyleCombination("normal")

    # Handle both '+' and space separators
    if "+" in style:
        style_names = [s.strip() for s in style.split("+")]
    else:
        style_names = style.split()

    # Filter out empty strings and normalize
    style_names = [s.strip().lower() for s in style_names if s.strip()]

    if not style_names:
        return StyleCombination("normal")

    return StyleCombination(*style_names)


def get_style(style_spec: str) -> StyleCombination:
    """
    Convert style specification to StyleCombination.

    Args:
        style_spec: Style specification string

    Returns:
        StyleCombination instance
    """
    return parse_style(style_spec)
