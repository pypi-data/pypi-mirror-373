"""
Exception classes for the Colab Print library.

This module defines a comprehensive exception hierarchy for the Colab Print library,
providing specialized exceptions for different error categories and scenarios.
These exceptions enable precise error handling and clear error messages throughout
the library.

The exception hierarchy is designed with a base `ColabPrintError` class and multiple
specialized subclasses organized by error category:

Categories:
    - Display Environment: Errors related to the notebook environment
    - Style: Errors related to styling and CSS
    - Content Type: Errors related to specific content types (text, tables, etc.)
    - Formatting and Parameter: Errors related to invalid parameters
    - Conversion and Rendering: Errors related to data conversion and HTML rendering
    - Structure: Errors related to processing nested structures
    - Method: Errors related to display methods
    - Animation: Errors related to CSS animations
    - Button: Errors related to interactive buttons
    - PDF: Errors related to PDF display and processing
    - TextBox: Errors related to TextBox display and components

Example:
    ```python
    from colab_print._exception import StyleNotFoundError
    
    def apply_style(style_name):
        available_styles = {"default", "highlight", "error"}
        if style_name not in available_styles:
            raise StyleNotFoundError(
                style_name=style_name,
                message=f"Style '{style_name}' not found. Available styles: {', '.join(available_styles)}"
            )
        # Apply the style...
    ```

Note:
    The exception hierarchy follows this structure:
    - ColabPrintError (base)
        - DisplayEnvironmentError
            - IPythonNotAvailableError
            - HTMLRenderingError
        - StyleError
            - StyleNotFoundError
        - ContentTypeError
        - ParameterError
        - RenderingError
        - StructureError
        - MethodError
        - AnimationError
        - ButtonError
        - PDFError
            - PDFSourceError
            - PDFRenderingError
            - PDFDownloadError
        - TextBoxError
            - MissingTitleError
            - InvalidProgressValueError
            - UnsupportedComponentError
"""


# Custom Exception Hierarchy for colab-print library
class ColabPrintError(Exception):
    """Base exception class for all colab-print exceptions."""

    def __init__(self, message="An error occurred in the colab-print library"):
        self.message = message
        super().__init__(self.message)


# Display Environment Exceptions
class DisplayEnvironmentError(ColabPrintError):
    """Exception raised when there are issues with the display environment."""

    def __init__(self, message="Display environment error"):
        super().__init__(message)


class IPythonNotAvailableError(DisplayEnvironmentError):
    """Exception raised when IPython display is not available."""

    def __init__(self, message="IPython display is not available in the current environment"):
        super().__init__(message)


class HTMLRenderingError(DisplayEnvironmentError):
    """Exception raised when HTML cannot be rendered properly."""

    def __init__(self, message="Failed to render HTML content"):
        super().__init__(message)


# Style Exceptions
class StyleError(ColabPrintError):
    """Exception raised for issues with styles and styling."""

    def __init__(self, message="Style error"):
        super().__init__(message)


class StyleNotFoundError(StyleError):
    """Exception raised when a requested style is not found."""

    def __init__(self, style_name="Unknown", message=None):
        if message is None:
            message = f"Style '{style_name}' not found"
        super().__init__(message)
        self.style_name = style_name


class StyleParsingError(StyleError):
    """Exception raised when there's an error parsing style strings."""

    def __init__(self, style_value="Unknown", message=None):
        if message is None:
            message = f"Error parsing style value: {style_value}"
        super().__init__(message)
        self.style_value = style_value


class StyleConflictError(StyleError):
    """Exception raised when there are conflicting style properties."""

    def __init__(self, style1="", style2="", message=None):
        if message is None:
            message = f"Style conflict between '{style1}' and '{style2}'"
        super().__init__(message)
        self.style1 = style1
        self.style2 = style2


# Content Type Exceptions
class ContentTypeError(ColabPrintError):
    """Exception raised for content type issues."""

    def __init__(self, expected_type="Unknown", received_type="Unknown", message=None):
        if message is None:
            message = f"Expected content of type {expected_type}, received {received_type}"
        super().__init__(message)
        self.expected_type = expected_type
        self.received_type = received_type


class TextError(ContentTypeError):
    """Exception raised for text content issues."""

    def __init__(self, message="Text content error"):
        super().__init__(expected_type="str", message=message)


class TableError(ContentTypeError):
    """Exception raised for table content issues."""

    def __init__(self, message="Table content error"):
        super().__init__(expected_type="List[List]", message=message)


class DataFrameError(ContentTypeError):
    """Exception raised for DataFrame issues."""

    def __init__(self, message="DataFrame error"):
        super().__init__(expected_type="pandas.DataFrame", message=message)


class SeriesError(ContentTypeError):
    """Exception raised for pandas Series issues."""

    def __init__(self, message="Series error"):
        super().__init__(expected_type="pandas.Series", message=message)


class CodeError(ContentTypeError):
    """Exception raised for code display issues."""

    def __init__(self, message="Code content error"):
        super().__init__(expected_type="str", message=message)


class CodeParsingError(CodeError):
    """Exception raised when parsing code with prompts fails."""

    def __init__(self, line_number=None, message=None):
        if message is None:
            message = f"Error parsing code syntax" + (f" at line {line_number}" if line_number else "")
        super().__init__(message)
        self.line_number = line_number


class SyntaxHighlightingError(CodeError):
    """Exception raised when applying syntax highlighting fails."""

    def __init__(self, highlighting_mode=None, message=None):
        if message is None:
            mode_info = f" with mode '{highlighting_mode}'" if highlighting_mode else ""
            message = f"Failed to apply syntax highlighting{mode_info}"
        super().__init__(message)
        self.highlighting_mode = highlighting_mode


class ListError(ContentTypeError):
    """Exception raised for list content issues."""

    def __init__(self, message="List content error"):
        super().__init__(expected_type="List/Tuple", message=message)


class DictError(ContentTypeError):
    """Exception raised for dictionary content issues."""

    def __init__(self, message="Dictionary content error"):
        super().__init__(expected_type="Dict", message=message)


class ProgressError(ContentTypeError):
    """Exception raised for progress bar issues."""

    def __init__(self, message="Progress bar error"):
        super().__init__(message=message)


class MermaidError(ContentTypeError):
    """Exception raised for mermaid diagram issues."""

    def __init__(self, message="Mermaid diagram error"):
        super().__init__(expected_type="str", message=message)


class MarkdownError(ContentTypeError):
    """Exception raised for markdown content issues."""

    def __init__(self, message="Markdown content error"):
        super().__init__(expected_type="str", message=message)


class MarkdownSourceError(MarkdownError):
    """Exception raised when there's an issue with the markdown source (file or URL)."""

    def __init__(self, source="Unknown", is_url=False, message=None):
        source_type = "URL" if is_url else "file path"
        if message is None:
            message = f"Error accessing markdown content from {source_type}: {source}"
        super().__init__(message)
        self.source = source
        self.is_url = is_url


class MarkdownParsingError(MarkdownError):
    """Exception raised when parsing markdown content fails."""

    def __init__(self, message="Failed to parse markdown content"):
        super().__init__(message)


class MarkdownRenderingError(MarkdownError):
    """Exception raised when rendering markdown content fails."""

    def __init__(self, message="Failed to render markdown content"):
        super().__init__(message)


# Formatting and Parameter Exceptions
class FormattingError(ColabPrintError):
    """Exception raised for formatting issues."""

    def __init__(self, message="Formatting error"):
        super().__init__(message)


class InvalidParameterError(ColabPrintError):
    """Exception raised for invalid parameters."""

    def __init__(self, param_name="Unknown", expected="valid value", received=None, message=None):
        if message is None:
            message = f"Invalid parameter '{param_name}': expected {expected}, received {received}"
        super().__init__(message)
        self.param_name = param_name
        self.expected = expected
        self.received = received


class ColorError(StyleError):
    """Exception raised for invalid color values."""

    def __init__(self, color_value="Unknown", message=None):
        if message is None:
            message = f"Invalid color value: {color_value}"
        super().__init__(message)
        self.color_value = color_value


# Conversion and Rendering Exceptions
class ConversionError(ColabPrintError):
    """Exception raised when data conversion fails."""

    def __init__(self, from_type="Unknown", to_type="Unknown", message=None):
        if message is None:
            message = f"Failed to convert from {from_type} to {to_type}"
        super().__init__(message)
        self.from_type = from_type
        self.to_type = to_type


class ArrayConversionError(ConversionError):
    """Exception raised when array-like object conversion fails."""

    def __init__(self, array_type="Unknown", message=None):
        if message is None:
            message = f"Failed to convert array-like object of type {array_type}"
        super().__init__(from_type=array_type, to_type="List", message=message)


class MatrixDetectionError(ContentTypeError):
    """Exception raised when matrix detection or processing fails."""

    def __init__(self, message="Error in matrix detection or processing"):
        super().__init__(message=message)


class NestedStructureError(ContentTypeError):
    """Exception raised for errors in handling nested structures."""

    def __init__(self, message="Error processing nested structure"):
        super().__init__(message=message)


# Display Method Exceptions
class DisplayMethodError(ColabPrintError):
    """Exception raised for display method issues."""

    def __init__(self, method_name="Unknown", message=None):
        if message is None:
            message = f"Error in display method '{method_name}'"
        super().__init__(message)
        self.method_name = method_name


class HTMLGenerationError(DisplayMethodError):
    """Exception raised when HTML generation fails."""

    def __init__(self, component="Unknown", message=None):
        if message is None:
            message = f"Failed to generate HTML for {component}"
        super().__init__(method_name="generate_html", message=message)
        self.component = component


class DisplayUpdateError(DisplayMethodError):
    """Exception raised when updates to a displayed element fail."""

    def __init__(self, element_id="Unknown", message=None):
        if message is None:
            message = f"Failed to update displayed element with ID '{element_id}'"
        super().__init__(method_name="update", message=message)
        self.element_id = element_id


class AnimationError(ColabPrintError):
    """Error raised when there's an issue with animation parameters."""

    def __init__(self, animation_name: str, message: str):
        self.animation_name = animation_name
        super().__init__(message)


class ButtonError(ContentTypeError):
    """Exception raised for button issues."""

    def __init__(self, message="Button error"):
        super().__init__(expected_type="Button", message=message)


class ButtonCallbackError(ButtonError):
    """Exception raised when there's an issue with button callbacks."""

    def __init__(self, callback_name="Unknown", message=None):
        if message is None:
            message = f"Error registering or executing callback '{callback_name}'"
        super().__init__(message)
        self.callback_name = callback_name


# PDF Display Exceptions
class PDFError(ContentTypeError):
    """Base exception raised for PDF display issues."""

    def __init__(self, message="PDF display error"):
        super().__init__(expected_type="PDF", message=message)


class PDFSourceError(PDFError):
    """Exception raised when there's an issue with the PDF source (file or URL)."""

    def __init__(self, source="Unknown", is_url=False, message=None):
        source_type = "URL" if is_url else "file path"
        if message is None:
            message = f"Error accessing PDF content from {source_type}: {source}"
        super().__init__(message)
        self.source = source
        self.is_url = is_url


class PDFRenderingError(PDFError):
    """Exception raised when rendering PDF content fails."""

    def __init__(self, message="Failed to render PDF content"):
        super().__init__(message)


class PDFDownloadError(PDFError):
    """Exception raised when downloading a PDF from a URL fails."""

    def __init__(self, url="Unknown", message=None):
        if message is None:
            message = f"Failed to download PDF from URL: {url}"
        super().__init__(message)
        self.url = url


# TextBox Display Exceptions
class TextBoxError(ContentTypeError):
    """Base exception raised for TextBox display issues."""

    def __init__(self, message="TextBox display error"):
        super().__init__(expected_type="TextBox", message=message)


class MissingTitleError(TextBoxError):
    """Exception raised when a TextBox is created without a required title."""

    def __init__(self, message="TextBox requires a title"):
        super().__init__(message)


class InvalidProgressValueError(TextBoxError):
    """Exception raised when a progress value is invalid."""

    def __init__(self, value=None, max_value=None, message=None):
        if message is None:
            message = f"Invalid progress value: {value}"
            if max_value is not None:
                message += f" (max: {max_value})"
        super().__init__(message)
        self.value = value
        self.max_value = max_value


class UnsupportedComponentError(TextBoxError):
    """Exception raised when an unsupported component type is added to a TextBox."""

    def __init__(self, component_type="Unknown", message=None):
        if message is None:
            message = f"Unsupported component type: {component_type}"
        super().__init__(message)
        self.component_type = component_type
