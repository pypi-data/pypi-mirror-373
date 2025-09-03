# KHX Colory 🌈

A lightweight, user-friendly Python library for creating colorful and styled terminal output with minimal dependencies and high performance.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Package Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://pypi.org/project/khx-colory/)

## ✨ Features

- **🎨 Rich Color Support**: Standard ANSI colors, bright colors, and full RGB (24-bit) color support
- **💫 Text Styling**: Bold, italic, underline, strikethrough, and more
- **🔗 Style Combinations**: Mix multiple styles together (e.g., bold + italic + underline)
- **🚀 High Performance**: Lightweight with minimal dependencies
- **🌍 Cross-Platform**: Works on Windows, macOS, and Linux
- **🎯 User-Friendly API**: Intuitive and easy-to-use interface
- **📚 Well Documented**: Comprehensive documentation and examples
- **🧪 Fully Tested**: Extensive test coverage
- **🔧 Extensible**: Easy to customize and extend

## 🚀 Quick Start

### Installation

```bash
pip install khx-colory
```

### Basic Usage

```python
from khx_colory import colored, print_colored

# Simple colored text
print(colored("Hello World!", "red"))

# Styled text
print(colored("Bold text", style="bold"))

# Combine color and style
print(colored("Bold red text", "red", style="bold"))

# Background colors
print(colored("Text with background", "white", bg_color="blue"))

# Print directly
print_colored("This prints directly in green", "green")

# RGB colors
print(colored("RGB color text", color=(255, 100, 50)))

# Multiple styles
print(colored("Bold italic underlined", style="bold+italic+underline"))
```

### Using the Main Class

```python
from khx_colory import Colory

# Create a Colory instance
colory = Colory()

# Print colored text
colory.print_text("Hello!", "blue", style="bold")

# Get colored string
text = colory.colored_text("Styled text", "green", style="italic")
print(text)

# Create ColorText objects
color_text = colory.create_text("Custom text", "magenta", style="underline")
print(color_text)
```

## 🎨 Available Colors

### Standard Colors
- `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`

### Bright Colors  
- `bright_black`, `bright_red`, `bright_green`, `bright_yellow`
- `bright_blue`, `bright_magenta`, `bright_cyan`, `bright_white`

### RGB Colors
```python
# Using RGB tuples
colored("RGB text", color=(255, 0, 128))

# Using hex colors
from khx_colory import ColorRGB
rgb_color = ColorRGB.from_hex("#FF0080")
colored("Hex color text", color=rgb_color)
```

## 💫 Available Styles

- `normal` - Reset to normal text
- `bold` - Bold/bright text
- `dim` - Dimmed text
- `italic` - Italic text (not supported on all terminals)
- `underline` - Underlined text
- `blink` - Blinking text
- `reverse` - Reverse/invert colors
- `strikethrough` - Strikethrough text

### Style Combinations
```python
# Multiple styles can be combined with '+' or spaces
colored("Multi-styled text", style="bold+italic+underline")
colored("Multi-styled text", style="bold italic underline")
```

## 🔧 Advanced Usage

### ColorText Objects

```python
from khx_colory import ColorText

# Create ColorText objects for more control
text = ColorText("Hello", fg_color="red", bg_color="yellow", style="bold")
print(text.render())

# Concatenate ColorText objects
text1 = ColorText("Hello ", "red")
text2 = ColorText("World!", "blue")
combined = text1 + text2
print(combined)

# Copy and modify
modified = text.copy(text="Modified", fg_color="green")
print(modified)
```

### Convenience Functions

```python
from khx_colory import red, green, blue, bold, italic, underline

# Color convenience functions
print(red("Red text"))
print(green("Green text"))
print(blue("Blue text", style="bold"))

# Style convenience functions
print(bold("Bold text"))
print(italic("Italic text"))
print(underline("Underlined text", color="red"))
```

### Color Detection and Control

```python
from khx_colory import Colory, set_color_enabled, is_color_enabled

# Check if colors are supported
colory = Colory()
print(f"Color supported: {colory.is_color_enabled()}")

# Disable colors globally
set_color_enabled(False)

# Force enable colors
colory = Colory(force_color=True)
```

## 🖥️ Command Line Interface

KHX Colory includes a CLI for testing and demonstration:

```bash
# Show all available colors and styles
colory demo

# Show only colors
colory demo --colors

# Show only styles  
colory demo --styles

# Print colored text
colory print "Hello World" red
colory print "Bold text" blue bold
colory print "Background" white --bg-color red

# List available colors or styles
colory list colors
colory list styles

# Disable colors
colory --no-color demo
```

## 📖 API Reference

### Core Classes

#### `Colory`
Main class for colorful terminal output.

```python
Colory(auto_reset=True, force_color=None)
```

**Methods:**
- `colored_text(text, color=None, bg_color=None, style=None)` - Create colored text string
- `print_text(text, color=None, bg_color=None, style=None, **kwargs)` - Print colored text
- `create_text(text, color=None, bg_color=None, style=None)` - Create ColorText object
- `get_available_colors()` - Get list of available colors
- `get_available_styles()` - Get list of available styles
- `demo_all()` - Show comprehensive demo

#### `ColorText`
Represents colored and styled text.

```python
ColorText(text, fg_color=None, bg_color=None, style=None)
```

**Methods:**
- `render()` - Get text with ANSI escape sequences
- `copy(**kwargs)` - Create a copy with modifications
- `__str__()` - Returns rendered text
- `__len__()` - Returns length of text content

#### `Color`
Standard ANSI color representation.

```python
Color(name)  # e.g., Color("red")
```

**Methods:**
- `fg()` - Get foreground color escape sequence
- `bg()` - Get background color escape sequence
- `available_colors()` - Class method to get available colors

#### `ColorRGB`
RGB color representation for 24-bit color.

```python
ColorRGB(r, g, b)  # e.g., ColorRGB(255, 0, 128)
```

**Methods:**
- `fg()` - Get RGB foreground escape sequence
- `bg()` - Get RGB background escape sequence
- `to_hex()` - Convert to hex string
- `from_hex(hex_color)` - Class method to create from hex

### Utility Functions

- `colored(text, color=None, bg_color=None, style=None)` - Create colored text string
- `print_colored(text, color=None, bg_color=None, style=None, **kwargs)` - Print colored text
- `get_available_colors()` - Get list of available colors
- `get_available_styles()` - Get list of available styles
- `strip_ansi(text)` - Remove ANSI escape sequences from text
- `get_text_length(text)` - Get display length ignoring ANSI codes

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=khx_colory

# Run specific tests
pytest tests/test_text.py -v
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/KHADER/khx-colory.git
cd khx-colory

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for simple, lightweight terminal coloring
- Thanks to the Python community for excellent tools and libraries
- Special thanks to contributors and users who provide feedback

## 📞 Support

- 📧 **Email**: khader@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/KHADER/khx-colory/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/KHADER/khx-colory/discussions)

---

Made with ❤️ by KHADER
