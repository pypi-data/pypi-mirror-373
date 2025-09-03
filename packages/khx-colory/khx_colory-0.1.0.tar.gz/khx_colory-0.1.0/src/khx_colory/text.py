"""
Colorful text functionality for terminal output.

This module provides the core text coloring and styling functionality,
including classes and functions for creating and printing colored text.
"""

import sys
from typing import Optional, Union, TextIO, Tuple
from .colors import Color, ColorRGB, get_color
from .styles import Style, StyleCombination, get_style


class ColorText:
    """
    A colored and styled text object.

    This class represents text with associated color and style information,
    providing methods to render the text with ANSI escape sequences.
    """

    def __init__(
        self,
        text: str,
        fg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        style: Optional[str] = None,
    ):
        """
        Initialize colored text.

        Args:
            text: The text content
            fg_color: Foreground color specification
            bg_color: Background color specification
            style: Style specification (e.g., 'bold', 'bold+italic')
        """
        self.text = text
        self.fg_color = get_color(fg_color) if fg_color else None
        self.bg_color = get_color(bg_color) if bg_color else None
        self.style = get_style(style) if style else StyleCombination("normal")

    def render(self) -> str:
        """
        Render the text with ANSI escape sequences.

        Returns:
            Text with ANSI codes for color and styling
        """
        if not self.text:
            return ""

        # Build the opening escape sequence
        sequences = []

        # Add style codes
        if self.style:
            style_seq = self.style.apply()
            if style_seq:
                sequences.append(style_seq)

        # Add foreground color
        if self.fg_color:
            sequences.append(self.fg_color.fg())

        # Add background color
        if self.bg_color:
            sequences.append(self.bg_color.bg())

        # If no formatting, return plain text
        if not sequences:
            return self.text

        # Combine sequences and add reset at the end
        opening = "".join(sequences)
        closing = Style.RESET_ALL

        return f"{opening}{self.text}{closing}"

    def __str__(self) -> str:
        """String representation returns rendered text."""
        return self.render()

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"ColorText(text={self.text!r}, fg_color={self.fg_color!r}, "
            f"bg_color={self.bg_color!r}, style={self.style!r})"
        )

    def __len__(self) -> int:
        """Return length of the text content (without ANSI codes)."""
        return len(self.text)

    def __add__(self, other: "ColorText") -> "ColorText":
        """Concatenate two ColorText objects."""
        if not isinstance(other, ColorText):
            return NotImplemented

        # Create a new ColorText with concatenated rendered output
        combined_text = self.render() + other.render()
        return ColorText(combined_text)

    def copy(
        self,
        text: Optional[str] = None,
        fg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        style: Optional[str] = None,
    ) -> "ColorText":
        """
        Create a copy with optional modifications.

        Args:
            text: New text content (if None, keeps current)
            fg_color: New foreground color (if None, keeps current)
            bg_color: New background color (if None, keeps current)
            style: New style (if None, keeps current)

        Returns:
            New ColorText instance
        """
        return ColorText(
            text=text if text is not None else self.text,
            fg_color=fg_color if fg_color is not None else self.fg_color,
            bg_color=bg_color if bg_color is not None else self.bg_color,
            style=style if style is not None else str(self.style),
        )


def colored(
    text: str,
    color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
    bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
    style: Optional[str] = None,
) -> str:
    """
    Create colored text string with ANSI escape sequences.

    This is a convenience function that creates a ColorText object and returns
    its rendered representation.

    Args:
        text: Text to colorize
        color: Foreground color specification
        bg_color: Background color specification
        style: Style specification

    Returns:
        Text with ANSI escape sequences

    Examples:
        >>> colored("Hello", "red")
        '\033[31mHello\033[0m'
        >>> colored("World", "blue", style="bold")
        '\033[1m\033[34mWorld\033[0m'
        >>> colored("Test", color=(255, 0, 0), style="bold+underline")
        '\033[1;4m\033[38;2;255;0;0mTest\033[0m'
    """
    color_text = ColorText(text, fg_color=color, bg_color=bg_color, style=style)
    return color_text.render()


def print_colored(
    text: str,
    color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
    bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
    style: Optional[str] = None,
    file: Optional[TextIO] = None,
    end: str = "\n",
    flush: bool = False,
) -> None:
    """
    Print colored text to terminal.

    This is a convenience function that creates colored text and prints it
    using the standard print function.

    Args:
        text: Text to print
        color: Foreground color specification
        bg_color: Background color specification
        style: Style specification
        file: File object to write to (default: sys.stdout)
        end: String appended after the text (default: newline)
        flush: Whether to forcibly flush the stream

    Examples:
        >>> print_colored("Hello World!", "red")
        Hello World!  # (in red)
        >>> print_colored("Bold Blue", "blue", style="bold")
        Bold Blue  # (in bold blue)
        >>> print_colored("Background", bg_color="yellow")
        Background  # (with yellow background)
    """
    colored_text = colored(text, color=color, bg_color=bg_color, style=style)
    print(colored_text, file=file, end=end, flush=flush)


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from text.

    Args:
        text: Text that may contain ANSI escape sequences

    Returns:
        Text with ANSI sequences removed
    """
    import re

    # ANSI escape sequence pattern
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def get_text_length(text: str) -> int:
    """
    Get the actual display length of text (ignoring ANSI codes).

    Args:
        text: Text that may contain ANSI escape sequences

    Returns:
        Display length of the text
    """
    return len(strip_ansi(text))


# Convenience functions for common colors
def red(text: str, style: Optional[str] = None) -> str:
    """Create red colored text."""
    return colored(text, "red", style=style)


def green(text: str, style: Optional[str] = None) -> str:
    """Create green colored text."""
    return colored(text, "green", style=style)


def blue(text: str, style: Optional[str] = None) -> str:
    """Create blue colored text."""
    return colored(text, "blue", style=style)


def yellow(text: str, style: Optional[str] = None) -> str:
    """Create yellow colored text."""
    return colored(text, "yellow", style=style)


def magenta(text: str, style: Optional[str] = None) -> str:
    """Create magenta colored text."""
    return colored(text, "magenta", style=style)


def cyan(text: str, style: Optional[str] = None) -> str:
    """Create cyan colored text."""
    return colored(text, "cyan", style=style)


def white(text: str, style: Optional[str] = None) -> str:
    """Create white colored text."""
    return colored(text, "white", style=style)


def black(text: str, style: Optional[str] = None) -> str:
    """Create black colored text."""
    return colored(text, "black", style=style)


# Convenience functions for common styles
def bold(text: str, color: Optional[str] = None) -> str:
    """Create bold text."""
    return colored(text, color, style="bold")


def italic(text: str, color: Optional[str] = None) -> str:
    """Create italic text."""
    return colored(text, color, style="italic")


def underline(text: str, color: Optional[str] = None) -> str:
    """Create underlined text."""
    return colored(text, color, style="underline")


def strikethrough(text: str, color: Optional[str] = None) -> str:
    """Create strikethrough text."""
    return colored(text, color, style="strikethrough")
