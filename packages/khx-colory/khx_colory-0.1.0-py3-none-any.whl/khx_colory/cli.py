"""
Command-line interface for KHX Colory.

This module provides a simple CLI for demonstrating and testing the colorful
terminal output capabilities.
"""

import argparse
import sys
from typing import Optional
from . import __version__
from .core import Colory
from .text import colored, print_colored


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="colory",
        description="KHX Colory - Colorful Terminal Output",
        epilog="Examples:\n"
        "  colory demo                    # Show all available colors and styles\n"
        "  colory print 'Hello' red       # Print 'Hello' in red\n"
        "  colory print 'Bold' blue bold  # Print 'Bold' in blue with bold style\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument("--no-color", action="store_true", help="Disable color output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser(
        "demo", help="Show demonstration of colors and styles"
    )
    demo_parser.add_argument(
        "--colors", action="store_true", help="Show only colors demo"
    )
    demo_parser.add_argument(
        "--styles", action="store_true", help="Show only styles demo"
    )
    demo_parser.add_argument(
        "--combinations", action="store_true", help="Show only combinations demo"
    )

    # Print command
    print_parser = subparsers.add_parser("print", help="Print colored text")
    print_parser.add_argument("text", help="Text to print")
    print_parser.add_argument("color", nargs="?", help="Foreground color")
    print_parser.add_argument("style", nargs="?", help="Text style")
    print_parser.add_argument("--bg-color", help="Background color")

    # List command
    list_parser = subparsers.add_parser("list", help="List available colors or styles")
    list_parser.add_argument("type", choices=["colors", "styles"], help="What to list")

    return parser


def cmd_demo(args, colory: Colory) -> None:
    """Handle demo command."""
    if args.colors:
        colory.demo_colors()
    elif args.styles:
        colory.demo_styles()
    elif args.combinations:
        colory.demo_combinations()
    else:
        colory.demo_all()


def cmd_print(args, colory: Colory) -> None:
    """Handle print command."""
    colory.print_text(
        args.text, color=args.color, bg_color=args.bg_color, style=args.style
    )


def cmd_list(args, colory: Colory) -> None:
    """Handle list command."""
    if args.type == "colors":
        colors = colory.get_available_colors()
        print("Available colors:")
        for color in colors:
            colory.print_text(f"  {color}", color=color)
    elif args.type == "styles":
        styles = colory.get_available_styles()
        print("Available styles:")
        for style in styles:
            if style == "normal":
                print(f"  {style}")
            else:
                colory.print_text(f"  {style}", style=style)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Create Colory instance
    colory = Colory(force_color=not args.no_color)

    if args.no_color:
        colory.disable_color()

    # Handle commands
    if args.command == "demo":
        cmd_demo(args, colory)
    elif args.command == "print":
        cmd_print(args, colory)
    elif args.command == "list":
        cmd_list(args, colory)
    else:
        # No command specified, show help
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
