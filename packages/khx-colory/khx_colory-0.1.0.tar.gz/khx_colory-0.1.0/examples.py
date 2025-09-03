"""
Example usage of KHX Colory - Colorful Terminal Text

This example demonstrates the basic usage of the KHX Colory library
for creating colorful and styled terminal output.
"""

# Import the main functions and classes
from khx_colory import (
    colored,
    print_colored,
    Colory,
    ColorText,
    red,
    green,
    blue,
    bold,
    italic,
    underline,
    get_available_colors,
    get_available_styles,
)


def basic_examples():
    """Basic usage examples."""
    print("🎨 KHX Colory - Basic Examples")
    print("=" * 40)

    # Simple colored text
    print(colored("Hello World!", "red"))
    print(colored("Green text", "green"))
    print(colored("Blue text", "blue"))

    # Text with styles
    print(colored("Bold text", style="bold"))
    print(colored("Italic text", style="italic"))
    print(colored("Underlined text", style="underline"))

    # Combine colors and styles
    print(colored("Bold red text", "red", style="bold"))
    print(colored("Italic blue text", "blue", style="italic"))
    print(colored("Underlined green text", "green", style="underline"))

    print()


def style_combinations():
    """Demonstrate style combinations."""
    print("💫 Style Combinations")
    print("=" * 40)

    # Multiple styles
    print(colored("Bold + Italic", style="bold+italic"))
    print(colored("Bold + Underline", style="bold+underline"))
    print(colored("Italic + Underline", style="italic+underline"))
    print(colored("Bold + Italic + Underline", style="bold+italic+underline"))

    # With colors
    print(colored("Red Bold Italic", "red", style="bold+italic"))
    print(colored("Blue Bold Underline", "blue", style="bold+underline"))

    print()


def background_colors():
    """Demonstrate background colors."""
    print("🌈 Background Colors")
    print("=" * 40)

    print(colored("White on Red", "white", bg_color="red"))
    print(colored("Black on Yellow", "black", bg_color="yellow"))
    print(colored("White on Blue", "white", bg_color="blue"))
    print(colored("Black on Green", "black", bg_color="green"))

    print()


def rgb_colors():
    """Demonstrate RGB colors."""
    print("🎨 RGB Colors")
    print("=" * 40)

    # RGB tuples
    print(colored("Pure Red", color=(255, 0, 0)))
    print(colored("Pure Green", color=(0, 255, 0)))
    print(colored("Pure Blue", color=(0, 0, 255)))
    print(colored("Purple", color=(128, 0, 128)))
    print(colored("Orange", color=(255, 165, 0)))

    # Gradient effect
    for i in range(5):
        r = 255 - (i * 50)
        g = i * 50
        b = 100
        print(colored(f"Gradient {i+1}", color=(r, g, b)))

    print()


def convenience_functions():
    """Demonstrate convenience functions."""
    print("🚀 Convenience Functions")
    print("=" * 40)

    # Color convenience functions
    print(red("Red text"))
    print(green("Green text"))
    print(blue("Blue text"))

    # Style convenience functions
    print(bold("Bold text"))
    print(italic("Italic text"))
    print(underline("Underlined text"))

    # Combine convenience functions
    print(bold(red("Bold red text")))
    print(italic(blue("Italic blue text")))
    print(underline(green("Underlined green text")))

    print()


def colortext_objects():
    """Demonstrate ColorText objects."""
    print("📝 ColorText Objects")
    print("=" * 40)

    # Create ColorText objects
    text1 = ColorText("Hello ", fg_color="red", style="bold")
    text2 = ColorText("World!", fg_color="blue", style="italic")

    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")

    # Concatenate ColorText objects
    combined = text1 + text2
    print(f"Combined: {combined}")

    # Copy and modify
    modified = text1.copy(text="Modified", fg_color="green")
    print(f"Modified: {modified}")

    print()


def colory_class():
    """Demonstrate the main Colory class."""
    print("🏗️ Colory Class")
    print("=" * 40)

    # Create a Colory instance
    colory = Colory()

    # Print colored text
    colory.print_text("Hello from Colory!", "magenta", style="bold")

    # Get colored string
    colored_str = colory.colored_text("Styled text", "cyan", style="italic")
    print(f"Colored string: {colored_str}")

    # Create ColorText object
    color_text = colory.create_text("Custom text", "yellow", style="underline")
    print(f"ColorText object: {color_text}")

    print()


def available_options():
    """Show available colors and styles."""
    print("📋 Available Options")
    print("=" * 40)

    print("Available Colors:")
    colors = get_available_colors()
    for i, color in enumerate(colors):
        if i % 4 == 0:
            print()
        print(f"  {colored(color, color):20}", end="")
    print("\n")

    print("Available Styles:")
    styles = get_available_styles()
    for style in styles:
        if style == "normal":
            print(f"  {style}")
        else:
            print(f"  {colored(style, style=style)}")

    print()


def interactive_demo():
    """Interactive demonstration."""
    print("🎮 Interactive Demo")
    print("=" * 40)

    try:
        # Get user input
        text = input("Enter text to colorize: ")
        if not text:
            text = "Sample Text"

        color = input("Enter color (or press Enter for red): ")
        if not color:
            color = "red"

        style = input("Enter style (or press Enter for bold): ")
        if not style:
            style = "bold"

        # Display the result
        print("\nResult:")
        print(colored(text, color, style=style))

    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Using default values...")
        print(colored("Default Example", "red", style="bold"))

    print()


def main():
    """Run all examples."""
    print("🌈 KHX Colory - Example Demonstrations")
    print("=" * 60)
    print()

    # Run all example functions
    basic_examples()
    style_combinations()
    background_colors()
    rgb_colors()
    convenience_functions()
    colortext_objects()
    colory_class()
    available_options()

    # Interactive demo (optional)
    try:
        response = input("Run interactive demo? (y/N): ")
        if response.lower() in ("y", "yes"):
            interactive_demo()
    except KeyboardInterrupt:
        print("\nSkipping interactive demo.")

    print("🎉 Examples completed!")
    print()
    print("To run the built-in demos, use:")
    print("  colory demo")
    print("  colory demo --colors")
    print("  colory demo --styles")


if __name__ == "__main__":
    main()
