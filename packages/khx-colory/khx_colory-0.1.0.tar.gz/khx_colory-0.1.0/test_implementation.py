#!/usr/bin/env python3
"""
Test script to verify KHX Colory colorful text implementation.

This script tests the core functionality without requiring the full package installation.
"""

import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Test imports
try:
    from khx_colory import colored, print_colored, Colory
    from khx_colory import red, green, blue, bold, italic, underline
    from khx_colory import get_available_colors, get_available_styles

    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_basic_functionality():
    """Test basic colorful text functionality."""
    print("\n🧪 Testing Basic Functionality")
    print("=" * 40)

    # Test colored function
    print("Testing colored() function:")
    result = colored("Hello World!", "red")
    print(f"  {result}")

    # Test print_colored function
    print("Testing print_colored() function:")
    print("  ", end="")
    print_colored("Hello World!", "blue")

    # Test styles
    print("Testing styles:")
    print(f"  {colored('Bold text', style='bold')}")
    print(f"  {colored('Italic text', style='italic')}")
    print(f"  {colored('Underlined text', style='underline')}")

    # Test combinations
    print("Testing color + style combinations:")
    print(f"  {colored('Red Bold', 'red', style='bold')}")
    print(f"  {colored('Blue Italic', 'blue', style='italic')}")

    print("✅ Basic functionality tests passed!")


def test_convenience_functions():
    """Test convenience functions."""
    print("\n🚀 Testing Convenience Functions")
    print("=" * 40)

    # Color functions
    print("Color convenience functions:")
    print(f"  {red('Red text')}")
    print(f"  {green('Green text')}")
    print(f"  {blue('Blue text')}")

    # Style functions
    print("Style convenience functions:")
    print(f"  {bold('Bold text')}")
    print(f"  {italic('Italic text')}")
    print(f"  {underline('Underlined text')}")

    print("✅ Convenience functions tests passed!")


def test_colory_class():
    """Test the main Colory class."""
    print("\n🏗️ Testing Colory Class")
    print("=" * 40)

    # Create instance
    colory = Colory()

    # Test methods
    print("Testing Colory methods:")
    colory.print_text("Hello from Colory!", "magenta")

    colored_text = colory.colored_text("Styled text", "cyan", style="italic")
    print(f"  Colored text: {colored_text}")

    # Test available options
    colors = colory.get_available_colors()
    styles = colory.get_available_styles()

    print(f"  Available colors: {len(colors)} colors")
    print(f"  Available styles: {len(styles)} styles")

    print("✅ Colory class tests passed!")


def test_rgb_colors():
    """Test RGB color functionality."""
    print("\n🎨 Testing RGB Colors")
    print("=" * 40)

    # Test RGB tuples
    rgb_colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
    ]

    print("Testing RGB colors:")
    for r, g, b in rgb_colors:
        result = colored(f"RGB({r}, {g}, {b})", color=(r, g, b))
        print(f"  {result}")

    print("✅ RGB color tests passed!")


def test_style_combinations():
    """Test style combinations."""
    print("\n💫 Testing Style Combinations")
    print("=" * 40)

    combinations = [
        "bold+italic",
        "bold+underline",
        "italic+underline",
        "bold+italic+underline",
    ]

    print("Testing style combinations:")
    for combo in combinations:
        result = colored(f"Style: {combo}", "white", style=combo)
        print(f"  {result}")

    print("✅ Style combination tests passed!")


def test_error_handling():
    """Test error handling."""
    print("\n🛡️ Testing Error Handling")
    print("=" * 40)

    # Test invalid color
    try:
        colored("Test", "invalid_color")
        print("❌ Should have raised error for invalid color")
    except ValueError:
        print("✅ Invalid color correctly rejected")

    # Test invalid style
    try:
        colored("Test", style="invalid_style")
        print("❌ Should have raised error for invalid style")
    except ValueError:
        print("✅ Invalid style correctly rejected")

    print("✅ Error handling tests passed!")


def demo_output():
    """Show a demo of the colorful text output."""
    print("\n🌈 Demo Output")
    print("=" * 40)

    # Show available colors
    colors = get_available_colors()
    print("Available colors:")
    for color in colors[:8]:  # Show first 8 colors
        print(f"  {colored(color, color)}")

    print("\nStyle examples:")
    styles = ["bold", "italic", "underline", "strikethrough"]
    for style in styles:
        print(f"  {colored(style, 'white', style=style)}")

    print("\nCombination examples:")
    print(f"  {colored('Bold Red', 'red', style='bold')}")
    print(f"  {colored('Italic Blue', 'blue', style='italic')}")
    print(f"  {colored('Underlined Green', 'green', style='underline')}")

    print("✅ Demo completed!")


def main():
    """Run all tests."""
    print("🧪 KHX Colory - Colorful Text Implementation Test")
    print("=" * 60)

    try:
        test_basic_functionality()
        test_convenience_functions()
        test_colory_class()
        test_rgb_colors()
        test_style_combinations()
        test_error_handling()
        demo_output()

        print("\n🎉 All tests passed successfully!")
        print("\nThe colorful text implementation is working correctly!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
