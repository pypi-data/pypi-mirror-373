"""
Core functionality and main API for KHX Colory.

This module provides the main Colory class that serves as the primary interface
for the colorful terminal printing library.
"""

import sys
from typing import Optional, Union, TextIO, Tuple, List
from .colors import Color, ColorRGB, get_color, get_available_colors
from .styles import Style, StyleCombination, get_style, get_available_styles
from .text import ColorText, colored, print_colored


class Colory:
    """
    Main class for colorful terminal output.

    This class provides a high-level interface for creating colored and styled
    terminal output with various formatting options.
    """

    def __init__(self, auto_reset: bool = True, force_color: Optional[bool] = None):
        """
        Initialize Colory instance.

        Args:
            auto_reset: Whether to automatically reset formatting after each output
            force_color: Force color output even if terminal doesn't support it
                        (None = auto-detect, True = force, False = disable)
        """
        self.auto_reset = auto_reset
        self.force_color = force_color
        self._color_enabled = self._detect_color_support()

    def _detect_color_support(self) -> bool:
        """
        Detect if the current terminal supports color output.

        Returns:
            True if color is supported, False otherwise
        """
        if self.force_color is not None:
            return self.force_color

        # Check if output is a TTY
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        # Check environment variables
        import os

        term = os.environ.get("TERM", "").lower()
        colorterm = os.environ.get("COLORTERM", "").lower()

        # Common indicators of color support
        if colorterm in ("truecolor", "24bit"):
            return True

        if term in ("xterm-color", "xterm-256color", "screen-256color"):
            return True

        if "color" in term:
            return True

        # Windows Command Prompt and PowerShell support
        if sys.platform == "win32":
            # Try to enable ANSI support on Windows
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                kernel32.SetConsoleMode(
                    handle, mode.value | 4
                )  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                return True
            except:
                pass

        return True  # Default to supporting color

    def is_color_enabled(self) -> bool:
        """Check if color output is enabled."""
        return self._color_enabled

    def enable_color(self) -> None:
        """Enable color output."""
        self._color_enabled = True

    def disable_color(self) -> None:
        """Disable color output."""
        self._color_enabled = False

    def colored_text(
        self,
        text: str,
        color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        style: Optional[str] = None,
    ) -> str:
        """
        Create colored text string.

        Args:
            text: Text to colorize
            color: Foreground color specification
            bg_color: Background color specification
            style: Style specification

        Returns:
            Colored text string (or plain text if color is disabled)
        """
        if not self._color_enabled:
            return text

        return colored(text, color=color, bg_color=bg_color, style=style)

    def print_text(
        self,
        text: str,
        color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        style: Optional[str] = None,
        file: Optional[TextIO] = None,
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """
        Print colored text.

        Args:
            text: Text to print
            color: Foreground color specification
            bg_color: Background color specification
            style: Style specification
            file: File object to write to
            end: String appended after text
            flush: Whether to flush output
        """
        if not self._color_enabled:
            print(text, file=file, end=end, flush=flush)
            return

        print_colored(
            text,
            color=color,
            bg_color=bg_color,
            style=style,
            file=file,
            end=end,
            flush=flush,
        )

    def create_text(
        self,
        text: str,
        color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        bg_color: Optional[Union[str, Color, ColorRGB, Tuple[int, int, int]]] = None,
        style: Optional[str] = None,
    ) -> ColorText:
        """
        Create a ColorText object.

        Args:
            text: Text content
            color: Foreground color specification
            bg_color: Background color specification
            style: Style specification

        Returns:
            ColorText instance
        """
        return ColorText(text, fg_color=color, bg_color=bg_color, style=style)

    def get_available_colors(self) -> List[str]:
        """Get list of available colors."""
        return get_available_colors()

    def get_available_styles(self) -> List[str]:
        """Get list of available styles."""
        return get_available_styles()

    def demo_colors(self) -> None:
        """Print a demonstration of available colors."""
        print("Available Colors:")
        print("=" * 50)

        colors = self.get_available_colors()
        for color in colors:
            try:
                self.print_text(f"  {color:15}", color=color, end="")
                self.print_text(f" - Sample text in {color}", color=color)
            except:
                print(f"  {color:15} - (Error displaying color)")

    def demo_styles(self) -> None:
        """Print a demonstration of available styles."""
        print("Available Styles:")
        print("=" * 50)

        styles = self.get_available_styles()
        for style in styles:
            try:
                self.print_text(f"  {style:15}", style=style, end="")
                self.print_text(f" - Sample text with {style} style", style=style)
            except:
                print(f"  {style:15} - (Error displaying style)")

    def demo_combinations(self) -> None:
        """Print a demonstration of color and style combinations."""
        print("Color and Style Combinations:")
        print("=" * 50)

        combinations = [
            ("red", "bold"),
            ("blue", "italic"),
            ("green", "underline"),
            ("yellow", "strikethrough"),
            ("magenta", "bold+italic"),
            ("cyan", "bold+underline"),
        ]

        for color, style in combinations:
            try:
                self.print_text(f"  {color} + {style}", color=color, style=style)
            except:
                print(f"  {color} + {style} - (Error displaying combination)")

    def demo_all(self) -> None:
        """Print a comprehensive demonstration of all features."""
        print("KHX Colory - Colorful Terminal Output Demo")
        print("=" * 60)
        print()

        self.demo_colors()
        print()

        self.demo_styles()
        print()

        self.demo_combinations()
        print()

        # RGB color demo
        print("RGB Colors:")
        print("=" * 50)
        rgb_colors = [
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
        ]

        for r, g, b in rgb_colors:
            try:
                self.print_text(
                    f"  RGB({r:3}, {g:3}, {b:3}) - Sample text", color=(r, g, b)
                )
            except:
                print(f"  RGB({r:3}, {g:3}, {b:3}) - (Error displaying RGB color)")


# Create a default global instance
_default_colory = Colory()


# Convenience functions using the default instance
def set_color_enabled(enabled: bool) -> None:
    """Enable or disable color output globally."""
    if enabled:
        _default_colory.enable_color()
    else:
        _default_colory.disable_color()


def is_color_enabled() -> bool:
    """Check if color output is enabled globally."""
    return _default_colory.is_color_enabled()


def demo() -> None:
    """Run a comprehensive demo of all features."""
    _default_colory.demo_all()
