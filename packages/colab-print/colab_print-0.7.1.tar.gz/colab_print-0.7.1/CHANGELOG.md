# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-05-31

### Added
- New TextBox component for creating styled containers with titles, captions, and progress bars
  - Support for required title parameter with proper validation
  - Optional caption paragraphs displayed as separate text blocks
  - Optional progress bar with customizable value, max, and label
  - Style customization with predefined themes (default, info, success, warning, error, etc.)
  - Animation support via Animate.css integration
  - **Dynamic content updates** for real-time information display (like timers or continuous data)
- Added convenience `text_box()` function for quick access to TextBox display
- Added `update_text_box()` function for updating TextBox content dynamically
- Added TextBoxDisplayer class with dynamic ID tracking for updates
- Added TextBoxDisplayer methods to the Printer class API:
  - `display_text_box(title, captions=None, progress=None, style="default", animate=None, **inline_styles)`
- New TextBox-specific exception classes for robust error handling:
  - `TextBoxError` as the base class for TextBox-related exceptions
  - `MissingTitleError` for title validation
  - `InvalidProgressValueError` for progress bar validation
  - `UnsupportedComponentError` for unsupported component types

### Improved
- Enhanced style definitions with dedicated TextBox styles in both DEFAULT_THEMES and SPECIAL_STYLES
- Added specialized styles for TextBox components (title, captions, progress container)
- Better documentation with comprehensive examples for TextBox usage
- Extended example.py with TextBox demonstrations

## [0.6.1] - 2025-05-18

### Added
- Support for pandas Series objects in DataFrame display functions
- New `SeriesError` exception class for more specific error handling
- New utility function `series_like()` to detect Series-like objects

### Fixed
- Fixed crash when attempting to display pandas Series objects
- Improved type checking with better validation for Series objects
- Enhanced error messages for Series-specific exceptions

### Improved
- Better documentation for Series display capabilities in docstrings
- Expanded DataFrame displayer to properly handle Series conversion
- More robust validation of input types across display functions

## [0.6.0b0] - 2025-05-14

### Added
- New PDF display functionality with interactive viewer capabilities
  - Support for displaying PDF files from local paths with `pdf_("/path/to/file.pdf")`
  - Support for displaying PDF files from URLs with `pdf_("https://example.com/doc.pdf", is_url=True)`
  - Interactive page navigation with previous/next buttons
  - Keyboard navigation support (arrow keys for page turning)
  - Built-in file picker interface when no source is provided (`pdf_()`)
  - Responsive design for various screen sizes
  - Animation support via Animate.css integration
- Added convenience `pdf_()` function for quick access to PDF display
- Added PDFDisplayer methods to the Printer class API:
  - `display_pdf(source, is_url=False, style="default", animate=None, **options)`
- New PDF-specific exception class: `PDFError` for robust error handling

### Improved
- Enhanced error handling for PDF file loading and rendering
- Better documentation with comprehensive examples for PDF viewer usage
- Improved browser compatibility for PDF display

### Notes
- This is a beta release focused on PDF display functionality
- PDF rendering is handled directly in the browser using native capabilities
- Detailed examples available in the example.py file

## [0.5.0b0] - 2025-05-04

### Added
- New interactive button component with extensive event handling capabilities
  - Support for Python callbacks via `on_click` parameter
  - Comprehensive event tracking and logging via status display area
  - Visual feedback for hover, press, and focus states
  - Ability to update button text and enabled state programmatically
  - Return value convention to update button text from callbacks: `__UPDATE_BUTTON_TEXT__: New Text`
  - Keyboard navigation and accessibility features (Enter/Space key support)
- Added convenience `button()` function for quick access to interactive functionality
- Added support for button positioning with `position` parameter ('left', 'mid', 'right')
- Added animation support for buttons using Animate.css
- Added ButtonDisplayer methods to the Printer class API:
  - `update_button_text(button_id, new_text)` to update button text after creation
  - `enable_button(button_id, enabled)` to enable or disable buttons

### Improved
- Enhanced error handling for button interactions with specialized exceptions
- Better documentation with comprehensive examples for button usage
- Improved browser compatibility for interactive elements

### Notes
- This is a beta release focused on interactive button functionality
- Button callbacks require Google Colab environment to function properly
- Full API documentation available in docstrings and example notebooks

## [0.4.1] - 2025-05-01

### Added
- Introduced new `compact` parameter to TableDisplayer to control data condensing behavior
  - Set `compact=True` (default) to condense large data structures for better readability
  - Set `compact=False` to display all data without condensing
- Added support for a wider range of iterable data structures in table display
- Added automatic detection and conversion of data structures with `to_list()` or `tolist()` methods

### Fixed
- Fixed bug where TableDisplayer strictly required Python lists for the `rows` parameter
- Fixed inconsistency in condensing behavior where some data structures were condensed while others were not
- Fixed display issues with NumPy arrays and other array-like objects

### Improved
- Made TableDisplayer more robust with improved type handling and validation
- Enhanced support for dictionaries and dictionary-like data sources
- Better handling of large data structures with more consistent condensing behavior
- Code refactoring for cleaner, more maintainable data processing and validation

## [0.4.0] - 2025-05-01

### Added
- Introduced comprehensive animation support throughout the library using Animate.css under the hood
- Support for animation configuration on the run through the string parameter (`animate=None` by default), which processes the string value to follow Animate.css pattern
- Better example.py with enhanced demonstrations showcasing all features
- New markdown display functionality with `md()` function for rendering markdown content from files or URLs
  - Support for local files: `md("/content/SECURITY.md", is_url=False)`
  - Support for remote URLs: `md("https://raw.githubusercontent.com/alaamer12/c4f/main/README.md", is_url=True)`
  - Custom styling options with color parameter: `md("https://example.com/doc.md", is_url=True, color="white")`

### Improved
- More robust exception handling across all display components
- Better code refactoring resulting in cleaner, more maintainable codebase
- Enhanced function docstrings with more detailed parameter descriptions and usage examples

## [0.3.0] - 2025-04-30

### Added
- Progress bar functionality with full tqdm compatibility
- Support for both determined and undetermined progress states
- New `progress()` function [tqdm-like] for easy progress tracking
- Enhanced exception hierarchy with detailed error context and improved tracebacks
- Advanced ListDisplay capabilities for rendering nested structures, matrices, and array-like objects
- Automatic detection and optimized display for NumPy arrays and Pandas data structures

### Improved
- Comprehensive input validation across all display methods
- Better style override mechanisms with more intuitive syntax
- Consistent error handling throughout the codebase
- Enhanced style inheritance for nested content elements
- More robust color processing and validation

### Changed
- Standardized display behavior across different content types
- Redesigned progress visualization with animations
- Updated all display components to properly propagate and handle exceptions
- Enhanced style definitions with better visual consistency

### Fixed
- Inconsistent error handling in various displayer components
- Improved exception context preservation for better debugging
- Standardized HTML generation and rendering process

## [0.2.0] - 2025-04-25

### Added
- New display styles including `code_block`, `quote`, `card`, `notice`, `badge`, `footer`, `data_highlight`, and `section_divider`
- Added specialized styles for different content types: `df`, `table`, `list`, and `dict`
- Global shortcut functions for all styles (e.g., `header()`, `title()`, `success()`)
- Content-specific display shortcuts: `dfd()`, `table()`, `list_()`, and `dict_()`
- Style overloading capabilities through inline style parameters
- Helper dataclasses: `DFDisplayParams` and `TableDisplayParams`

### Changed
- Enhanced visualization with better borders, shadows, and spacing
- Improved color contrast for better accessibility and readability
- Extended style properties for all display formats
- Optimized display behavior with more consistent margins and padding
- Better handling of nested structures in lists and dictionaries

### Improved
- Enhanced example.py with comprehensive demonstrations
- Better documentation with more usage examples
- Graceful fallback behavior outside Jupyter/Colab environments
- More consistent styling between different display functions

## [0.1.0.post1] - 2025-04-22

### Fixed
- Minor fixes and improvements from the initial release

## [0.1.0] - 2023-04-22

### Added
- Initial release with basic display functionality
- Support for styled text display
- Support for table display
- Support for DataFrame display
- Support for list display
- Support for dictionary display
- Default style themes 