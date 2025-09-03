# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release planning

## [0.1.0] - 2025-09-03

### Added
- **Core Features**
  - `Colory` main class for colorful terminal output
  - `ColorText` class for text with color and style information
  - `Color` class for standard ANSI colors
  - `ColorRGB` class for 24-bit RGB colors
  - `Style` and `StyleCombination` classes for text styling

- **Text Functionality**
  - `colored()` function for creating colored text strings
  - `print_colored()` function for direct colored output
  - Support for foreground and background colors
  - Support for text styles: bold, italic, underline, strikethrough, etc.
  - Style combinations (e.g., bold+italic+underline)

- **Color Support**
  - Standard ANSI colors (black, red, green, yellow, blue, magenta, cyan, white)
  - Bright/intense colors (bright_red, bright_green, etc.)
  - RGB colors with full 24-bit support
  - Hex color support (#FF0000)
  - Color detection and auto-disable on non-supporting terminals

- **Convenience Features**
  - Color convenience functions (red(), green(), blue(), etc.)
  - Style convenience functions (bold(), italic(), underline(), etc.)
  - Quick access functions (quick_print(), quick_colored())
  - Demo functions to showcase capabilities

- **Command Line Interface**
  - `colory demo` - Show color and style demonstrations
  - `colory print` - Print colored text from command line
  - `colory list` - List available colors and styles
  - Color enable/disable options

- **Developer Experience**
  - Comprehensive type hints throughout
  - Extensive documentation and examples
  - Full test coverage with pytest
  - Cross-platform compatibility (Windows, macOS, Linux)
  - Minimal dependencies (zero runtime dependencies)

- **Performance & Quality**
  - Lightweight and fast execution
  - Automatic ANSI escape sequence detection
  - Windows console color support
  - ANSI sequence stripping utilities
  - Text length calculation ignoring ANSI codes

### Technical Details
- **Dependencies**: None (runtime), pytest, black, isort, mypy (development)
- **Python Support**: 3.8+
- **License**: MIT
- **Package Structure**: Modern src/ layout with pyproject.toml
- **Code Quality**: Black formatting, isort imports, mypy type checking

### Examples Added
- Basic color and style usage
- RGB and hex color examples
- Style combination examples
- CLI usage examples
- API reference documentation

[Unreleased]: https://github.com/KHADER/khx-colory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/KHADER/khx-colory/releases/tag/v0.1.0
