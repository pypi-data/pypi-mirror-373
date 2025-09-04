# noinspection da
"""
Core implementation of the Colab Print display framework.

This module contains the primary implementation of all display components and the main
Printer class that orchestrates the different display methods. It provides a rich
set of displayer classes for rendering various types of content as styled HTML
in Jupyter/Colab notebook environments.

The module implements a hierarchical class structure with a base `Displayer` abstract
class and specialized displayers for different content types (text, code, tables,
DataFrames, lists, dictionaries, progress bars, interactive buttons, etc.).

Classes:
    Displayer: Abstract base class for all display components
    TextDisplayer: For displaying styled text content
    CodeDisplayer: For displaying code with syntax highlighting
    TableDisplayer: For displaying tabular data with customizable styling
    DFDisplayer: For displaying pandas DataFrames with advanced formatting
    ListDisplayer: For displaying lists, arrays, and nested structures
    DictDisplayer: For displaying dictionaries with key-value styling
    MermaidDisplayer: For rendering Mermaid.js diagrams
    MDDisplayer: For rendering Markdown content
    ProgressDisplayer: For creating and updating progress bars
    ButtonDisplayer: For creating interactive buttons with callbacks
    PDFDisplayer: For rendering PDF files
    Printer: Main class that orchestrates all displayers and exposes API

Example:
    ```python
    >>> from colab_print._core import Printer
    
    >>> # Create a printer instance
    >>> printer = Printer()
    
    >>> # Display styled text
    >>> printer.display("Hello World!", style="highlight")
    
    >>> # Display a data table
    >>> headers = ["Name", "Age", "City"]
    >>> rows = [["Alice", 28, "New York"], ["Bob", 34, "San Francisco"]]
    >>> printer.display_table(headers, rows, style="default")
    
    >>> # Create a progress bar
    >>> progress_id = printer.display_progress(total=100, desc="Processing...")
    
    >>> # Update the progress bar
    >>> for i in range(100):
    ...   # Do some work...
    ...   printer.update_progress(progress_id, i + 1)

    ```
"""

# noinspection PyUnresolvedReferences
import abc
import html
import os
import re
import uuid
import warnings
from collections.abc import Iterable, Mapping
from typing import Callable, Optional, Union, Dict, List, Any, Tuple, Literal
import base64
import mimetypes
import urllib.request
import tempfile
import hashlib

import pandas as pd
from IPython.display import display as ip_display, HTML, Javascript

from colab_print.exception import (ColabPrintError, TextError, ColorError,
                                   DisplayEnvironmentError, DisplayMethodError, DisplayUpdateError, ListError,
                                   StyleNotFoundError, StyleError,
                                   StyleConflictError, StyleParsingError, TableError, DictError,
                                   IPythonNotAvailableError, ProgressError, ConversionError, ArrayConversionError,
                                   FormattingError, HTMLGenerationError, HTMLRenderingError, DataFrameError, SeriesError,
                                   MatrixDetectionError, NestedStructureError, MermaidError, CodeError,
                                   CodeParsingError, SyntaxHighlightingError, InvalidParameterError, AnimationError,
                                   ButtonError, ButtonCallbackError,
                                   MarkdownSourceError, MarkdownParsingError, MarkdownRenderingError,
                                   PDFSourceError, PDFDownloadError, PDFRenderingError,
                                   MissingTitleError, InvalidProgressValueError, UnsupportedComponentError, TextBoxError)
from colab_print.utilities import DEFAULT_THEMES, SPECIAL_STYLES, process_animation_class, df_like, series_like

__all__ = [
    # Main classes
    "Printer"
]


class Displayer(abc.ABC):
    """
    Abstract base class for display components.
    
    All display components should extend this class and implement
    the display method according to their specific requirements.
    """

    def __init__(self, styles: Dict[str, str]):
        """
        Initialize a displayer with styles.
        
        Args:
            styles: Dictionary of named styles
        """
        self.styles = styles
        # Add flag to track if the Animate.css CDN has been loaded
        self._animate_css_loaded = False

    def _process_inline_styles(self, inline_styles: Dict[str, str]) -> str:
        """
        Convert Python-style keys to CSS style format and join them.
        
        Args:
            inline_styles: Dictionary of style attributes
            
        Returns:
            Formatted CSS string
            
        Raises:
            ConversionError: If there's an error converting Python-style keys to CSS format
        """
        try:
            corrected_styles = {k.replace('_', '-') if '_' in k else k: v for k, v in inline_styles.items()}
        except Exception as e:
            raise ConversionError(
                from_type="Dict[str, str]",
                to_type="CSS string",
                message=f"Failed to convert inline styles to CSS format: {str(e)}"
            )
        else:
            return "; ".join([f"{key}: {value}" for key, value in corrected_styles.items()])

    def _load_animate_css(self) -> str:
        """
        Return the HTML link to the Animate.css CDN.
        
        Returns:
            HTML link tag for Animate.css
        """
        self._animate_css_loaded = True
        return '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">'

    @abc.abstractmethod
    def display(self, *args, **kwargs):
        """Display content with the specified styling."""
        pass


class TextDisplayer(Displayer):
    """Displays styled text content."""

    def display(self, text: str, *, style: str = 'default', animate: Optional[str] = None, **inline_styles) -> None:
        """
        Display styled text.
        
        Args:
            text: The text to display
            style: Named style from the available styles
            animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
            **inline_styles: Additional CSS styles to apply
            
        Raises:
            TextError: If text is not a string
            StyleNotFoundError: If specified style is not found
            StyleParsingError: If there's an error parsing inline styles
            AnimationError: If the animation name is not valid
            HTMLRenderingError: If HTML content cannot be rendered
        """
        if not isinstance(text, str):
            received_type = type(text).__name__
            raise TextError(f"Text must be a string, received {received_type}")

        if style not in self.styles:
            raise StyleNotFoundError(style_name=style,
                                     message=f"Style '{style}' not found. Available styles: {', '.join(self.styles.keys())}")

        try:
            base_style = self.styles.get(style)
            inline_style_string = self._process_inline_styles(inline_styles)
            final_style = f"{base_style} {inline_style_string}" if inline_style_string else base_style

            # Process animation class if specified
            animation_class = process_animation_class(animate)
            class_attr = f'class="{animation_class}"' if animation_class else ''

            formatted_text = f'<span style="{final_style}" {class_attr}>{text}</span>'

            # Include Animate.css CDN if animation is specified - Always include it when animate is specified
            animate_css_link = self._load_animate_css() if animate else ''
            html_content = f"{animate_css_link}{formatted_text}" if animate else formatted_text

            self._display_html(html_content)
        except AnimationError:
            # Pass through animation validation errors
            raise
        except ValueError as e:
            raise StyleParsingError(style_value=str(inline_styles), message=f"Error parsing styles: {str(e)}")

    def _process_inline_styles(self, inline_styles: Dict[str, str]) -> str:
        """
        Convert Python-style keys to CSS style format and join them.
        
        Args:
            inline_styles: Dictionary of style attributes
            
        Returns:
            Formatted CSS string
            
        Raises:
            StyleParsingError: If there's an error parsing the styles
        """
        try:
            corrected_styles = {k.replace('_', '-') if '_' in k else k: v for k, v in inline_styles.items()}
            return "; ".join([f"{key}: {value}" for key, value in corrected_styles.items()])
        except Exception as e:
            raise StyleParsingError(style_value=str(inline_styles),
                                    message=f"Failed to process inline styles: {str(e)}")

    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content safely.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. HTML output will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render HTML content: {str(e)}")


class CodeDisplayer(Displayer):
    """Displays code with syntax highlighting and special formatting for Python prompts."""

    def __init__(self, styles: Dict[str, str]):
        """
        Initialize a code displayer with styles.
        
        Args:
            styles: Dictionary of named styles
        """
        super().__init__(styles)
        self.default_colors = [
            "#3498DB",  # Blue
            "#9B59B6",  # Purple
            "#2ECC71",  # Green
            "#F1C40F",  # Yellow
            "#E74C3C",  # Red
            "#1ABC9C",  # Turquoise
            "#FF5733",  # Coral
            "#C70039",  # Crimson
            "#900C3F",  # Maroon
            "#581845",  # Plum
            "#FFC300",  # Amber
            "#DAF7A6",  # Light Green
            "#FF5733",  # Orange
            "#16A085",  # Sea Green
            "#27AE60",  # Emerald
            "#2980B9",  # Steel Blue
            "#8E44AD",  # Violet
            "#34495E",  # Dark Slate
            "#D35400",  # Pumpkin
            "#7D3C98"   # Dark Purple
        ]

    @staticmethod
    def _parse_python_prompts(code: str) -> List[Dict[str, Any]]:
        """
        Parse Python code and identify prompt markers (>, >>>, ...).
        
        Args:
            code: Python code text
            
        Returns:
            List of dictionaries containing line info and prompt type
            
        Raises:
            CodeParsingError: If there's an error parsing the code
        """
        try:
            lines = code.split('\n')
            parsed_lines = []

            for i, line in enumerate(lines):
                line_info = {
                    'number': i + 1,
                    'text': line,
                    'prompt_type': None,
                    'indentation': 0
                }

                stripped = line.lstrip()
                line_info['indentation'] = len(line) - len(stripped)

                if stripped.startswith('>>> '):
                    line_info['prompt_type'] = 'primary'
                    line_info['text'] = stripped[4:]
                elif stripped.startswith('... '):
                    line_info['prompt_type'] = 'continuation'
                    line_info['text'] = stripped[4:]
                elif stripped.startswith('> '):
                    line_info['prompt_type'] = 'shell'
                    line_info['text'] = stripped[2:]

                parsed_lines.append(line_info)

            return parsed_lines
        except Exception as e:
            raise CodeParsingError(message=f"Failed to parse code: {str(e)}")

    @staticmethod
    def _calculate_gradient_color(line_number: int, total_lines: int,
                                  start_color: str = "#3498DB", end_color: str = "#9B59B6") -> str:
        """
        Calculate a gradient color based on the line position.
        
        Args:
            line_number: Current line number (1-based)
            total_lines: Total number of lines
            start_color: Starting color in the gradient
            end_color: Ending color in the gradient
            
        Returns:
            Hex color string
            
        Raises:
            ColorError: If there's an error parsing or calculating colors
        """
        try:
            # Parse start and end colors
            if not start_color.startswith('#') or not end_color.startswith('#'):
                raise ColorError(color_value=f"{start_color} or {end_color}",
                                 message="Colors must be hex values starting with #")

            start_r = int(start_color[1:3], 16)
            start_g = int(start_color[3:5], 16)
            start_b = int(start_color[5:7], 16)

            end_r = int(end_color[1:3], 16)
            end_g = int(end_color[3:5], 16)
            end_b = int(end_color[5:7], 16)

            # Calculate position in gradient (0 to 1)
            if total_lines <= 1:
                position = 0
            else:
                position = (line_number - 1) / (total_lines - 1)

            # Calculate new color
            r = int(start_r + position * (end_r - start_r))
            g = int(start_g + position * (end_g - start_g))
            b = int(start_b + position * (end_b - start_b))

            return f"#{r:02x}{g:02x}{b:02x}"
        except ColorError:
            raise  # Re-raise existing ColorError
        except Exception as e:
            raise ColorError(color_value=f"{start_color} to {end_color}",
                             message=f"Failed to calculate gradient color: {str(e)}")

    def _get_block_level_color(self, indentation: int) -> str:
        """
        Get a color based on the indentation level.
        
        Args:
            indentation: Number of spaces at the beginning of the line
            
        Returns:
            Hex color string
        """
        # Normalize indentation to a block level
        block_level = indentation // 4  # Assuming 4 spaces per indentation level
        color_index = block_level % len(self.default_colors)
        return self.default_colors[color_index]

    def _apply_syntax_highlighting(self, parsed_lines: List[Dict[str, Any]],
                                   highlighting_mode: str = 'block',
                                   base_style: str = "") -> str:
        """
        Apply syntax highlighting to parsed code lines.
        
        Args:
            parsed_lines: List of dictionaries containing line info
            highlighting_mode: 'block' for indentation-based coloring, 'gradient' for gradient coloring
            base_style: Base CSS style string
            
        Returns:
            HTML string with highlighted code
            
        Raises:
            SyntaxHighlightingError: If there's an error applying syntax highlighting
            InvalidParameterError: If an invalid highlighting mode is provided
        """
        try:
            if highlighting_mode not in ['block', 'gradient']:
                raise InvalidParameterError(param_name="highlighting_mode",
                                            expected="'block' or 'gradient'",
                                            received=highlighting_mode)

            total_lines = len(parsed_lines)
            html_lines = []

            # Start with a pre tag for proper code formatting
            pre_style = f"font-family: monospace; padding: 15px; border-radius: 5px; {base_style}"
            html_lines.append(f'<pre style="{pre_style}">')

            for _, line_info in enumerate(parsed_lines):
                line_number = line_info['number']
                text = html.escape(line_info['text'])
                indentation = line_info['indentation']
                prompt_type = line_info['prompt_type']

                # Determine line color based on the highlighting mode
                if highlighting_mode == 'gradient':
                    line_color = self._calculate_gradient_color(line_number, total_lines)
                else:  # block level
                    line_color = self._get_block_level_color(indentation)

                # Format based on prompt type
                if prompt_type == 'primary':
                    prompt_style = "color: #E67E22; font-weight: bold;"
                    line_html = f'<span style="{prompt_style}">>>></span> <span style="color: {line_color};">{text}</span>'
                elif prompt_type == 'continuation':
                    prompt_style = "color: #E67E22; font-weight: bold;"
                    line_html = f'<span style="{prompt_style}>...</span> <span style="color: {line_color};">{text}</span>'
                elif prompt_type == 'shell':
                    prompt_style = "color: #16A085; font-weight: bold;"
                    line_html = f'<span style="{prompt_style}">></span> <span style="color: {line_color};">{text}</span>'
                else:
                    line_html = f'<span style="color: {line_color};">{text}</span>'

                html_lines.append(line_html)

            html_lines.append('</pre>')
            return '\n'.join(html_lines)
        except (InvalidParameterError, ColorError):
            raise  # Re-raise specific exceptions
        except Exception as e:
            raise SyntaxHighlightingError(highlighting_mode=highlighting_mode,
                                          message=f"Failed to apply syntax highlighting: {str(e)}")

    def display(self, code: str, *,
                style: str = 'code_block',
                highlighting_mode: str = 'block',
                background_color: Optional[str] = None,
                animate: Optional[str] = None,) -> None:
        """
        Display code with syntax highlighting.
        
        Args:
            code: Code text to display
            style: Named style from available styles
            highlighting_mode: 'block' for indentation-based, 'line' for line-by-line highlighting
            background_color: Custom background color for code block
            animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
            
        Raises:
            CodeError: If code is not a string or there's an issue with code parsing
            StyleNotFoundError: If specified style is not found
            StyleParsingError: If there's an error parsing inline styles
            AnimationError: If the animation name is not valid
            HTMLRenderingError: If HTML content cannot be rendered
        """
        if not isinstance(code, str):
            raise CodeError(f"Code must be a string, received {type(code).__name__}")

        if style not in self.styles:
            raise StyleNotFoundError(style_name=style,
                                     message=f"Style '{style}' not found. Available styles: {', '.join(self.styles.keys())}")

        try:
            base_style = self.styles.get(style)

            # Parse the code and apply syntax highlighting
            parsed_lines = self._parse_python_prompts(code)

            # Apply background color if specified
            if background_color:
                if 'background-color' not in base_style:
                    base_style += f"; background-color: {background_color}"
                else:
                    base_style = re.sub(r'background-color:[^;]+', f'background-color: {background_color}', base_style)

            # Highlight the code
            highlighted_code = self._apply_syntax_highlighting(parsed_lines, highlighting_mode, base_style)

            # Process animation class if specified
            animation_class = process_animation_class(animate)
            if animation_class:
                highlighted_code = highlighted_code.replace('<pre ', f'<pre class="{animation_class}" ')

            # Include Animate.css CDN if animation is specified
            animate_css_link = self._load_animate_css() if animate else ''
            html_content = f"{animate_css_link}{highlighted_code}" if animate else highlighted_code

            self._display_html(html_content)
        except AnimationError:
            # Pass through animation validation errors
            raise
        except Exception as e:
            raise CodeError(f"Error displaying code: {str(e)}")

    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content safely.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. HTML output will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render HTML content: {str(e)}")


class TableDisplayer(Displayer):
    """Displays HTML tables with customizable styling."""

    def _get_table_styles(self, style: str = 'default', width: str = '100%') -> tuple:
        """
        Generate the CSS styles for the table, headers, and cells.
        
        Args:
            style: Named style from the available styles
            width: Width of the table (CSS value)
            
        Returns:
            Tuple of (table_style, th_style, td_style)
        """
        base_style = self.styles.get(style, self.styles['default'])

        # Ensure width is explicitly included to take full notebook width
        table_style = f"{base_style} border-collapse: collapse; width: {width} !important;"
        th_style = "background-color: #f2f2f2; padding: 8px; border: 1px solid #ddd; text-align: left;"
        td_style = "padding: 8px; border: 1px solid #ddd;"

        return table_style, th_style, td_style

    def _condense(self, item, max_items: int = 5, recursive: bool = True) -> Any:
        """
        Condenses large iterables into a compact string representation.
        
        Args:
            item: The item to potentially condense
            max_items: Maximum number of items to display before condensing
            recursive: Whether to recursively condense nested iterables
            
        Returns:
            Condensed representation (maintaining structure where possible)
        """
        # Handle non-iterable types or special cases
        if self._is_non_condensable_type(item):
            return item

        # Handle sequences like lists and tuples
        if isinstance(item, (list, tuple)):
            return self._condense_sequence(item, max_items, recursive)

        # Handle other iterable types
        return self._condense_generic_iterable(item, max_items)

    @staticmethod
    def _is_non_condensable_type(item) -> bool:
        """
        Determines if an item should not be condensed.
        
        Args:
            item: The item to check
            
        Returns:
            True if the item should not be condensed
        """
        # Strings are iterable but shouldn't be condensed
        if isinstance(item, str):
            return True

        # Non-iterable types or mappings shouldn't be condensed
        if not hasattr(item, '__iter__') or isinstance(item, Mapping):
            return True

        return False

    def _condense_sequence(self, sequence, max_items: int, recursive: bool) -> Any:
        """
        Condenses a sequence (list, tuple) into a compact representation.
        
        Args:
            sequence: The sequence to condense
            max_items: Maximum number of items to display before condensing
            recursive: Whether to recursively condense nested iterables
            
        Returns:
            Condensed sequence or string representation
        """
        # Original type constructor
        constructor = type(sequence)

        # First check if the sequence itself is large and should be condensed
        if hasattr(sequence, '__len__') and len(sequence) > max_items:
            return self._format_condensed_representation(sequence)

        # If not too large and recursive, process each element
        if recursive:
            processed_items = self._process_sequence_recursively(sequence, max_items)
            return constructor(processed_items)

        # For small collections, return as is
        return sequence

    def _process_sequence_recursively(self, sequence, max_items: int) -> list:
        """
        Processes each element in a sequence recursively.
        
        Args:
            sequence: The sequence to process
            max_items: Maximum number of items before condensing
            
        Returns:
            List of processed items
        """
        processed_items = []
        for element in sequence:
            if hasattr(element, '__iter__') and not isinstance(element, (str, Mapping)):
                if hasattr(element, '__len__') and len(element) > max_items:
                    processed_items.append(self._format_condensed_representation(element))
                else:
                    processed_items.append(TableDisplayer._condense(self, element, max_items, True))
            else:
                processed_items.append(element)

        return processed_items

    @staticmethod
    def _format_condensed_representation(items) -> str:
        """
        Creates a condensed string representation of an iterable.
        
        Args:
            items: The iterable to condense
            
        Returns:
            String representation showing first and last elements
        """
        try:
            items_list = list(items)
            first_items = ', '.join(str(items_list[i]) for i in range(min(2, len(items_list))))
            last_items = ', '.join(str(items_list[i]) for i in range(max(0, len(items_list) - 2), len(items_list)))
            return f"[{first_items}, ..., {last_items}]"
        except (TypeError, ValueError):
            # If we can't process it, return the original
            return items

    def _condense_generic_iterable(self, item, max_items: int) -> Any:
        """
        Condenses a generic iterable that's not a list or tuple.
        
        Args:
            item: The iterable to condense
            max_items: Maximum number of items before condensing
            
        Returns:
            Original item or condensed string representation
        """
        try:
            if hasattr(item, '__len__') and len(item) > max_items:
                return self._format_condensed_representation(item)
            return item
        except (TypeError, ValueError):
            # Fall back to original item
            return item

    @staticmethod
    def _generate_table_caption(caption: Optional[str], style_base: str) -> List[str]:
        """
        Generate HTML for the table caption if provided.
        
        Args:
            caption: Caption text
            style_base: Base CSS style string
            
        Returns:
            List of HTML caption elements or empty list
        """
        if not caption:
            return []

        caption_style = f"caption-side: top; text-align: left; font-weight: bold; margin-bottom: 10px; {style_base}"
        return [f'<caption style="{caption_style}">{caption}</caption>']

    @staticmethod
    def _generate_table_header(headers: List[str], th_style: str) -> List[str]:
        """
        Generate HTML for the table header row.
        
        Args:
            headers: List of header texts
            th_style: CSS style for header cells
            
        Returns:
            List of HTML elements for the header row
        """
        html = ['<tr>']
        for header in headers:
            html.append(f'<th style="{th_style}">{header}</th>')
        html.append('</tr>')
        return html

    def _generate_table_rows(self, rows: List[Any], td_style: str, compact: bool = True) -> List[str]:
        """
        Generate HTML for the table data rows.
        
        Args:
            rows: List of rows, each row being a list of cell values
            td_style: CSS style for data cells
            compact: Whether to condense large data structures
            
        Returns:
            List of HTML elements for data rows
        """
        html = []
        for row in rows:
            html.append('<tr>')
            for cell in row:
                # Process cell content, condensing large nested iterables if compact=True
                cell_value = self._condense(cell) if compact else cell

                # Convert the processed cell to string for display
                if not isinstance(cell_value, str):
                    cell_value = str(cell_value)

                html.append(f'<td style="{td_style}">{cell_value}</td>')
            html.append('</tr>')
        return html

    def _process_styles(self, style: str, width: str, custom_header_style: Optional[str],
                        custom_row_style: Optional[str], inline_styles_dict: Dict[str, str]) -> Tuple[
                        str, str, str, str]:
        """
        Process and prepare all styles for the table.
        
        Args:
            style: Named style from the available styles
            width: Width of the table (CSS value)
            custom_header_style: Optional custom CSS for header cells
            custom_row_style: Optional custom CSS for data cells
            inline_styles_dict: Dictionary of additional CSS styles
            
        Returns:
            Tuple of (table_style, th_style, td_style, inline_style_string)
            
        Raises:
            StyleNotFoundError: If specified style is not found
            StyleConflictError: If there are conflicts between styles
            ConversionError: If there's an error converting styles
        """
        try:
            # Process inline styles
            inline_style_string = self._process_inline_styles(inline_styles_dict)

            # Validate and get base styles
            self._validate_style_exists(style)
            table_style, th_style, td_style = self._get_table_styles(style, width)

            # Check for style conflicts and apply custom styles
            th_style = self._apply_custom_header_style(th_style, custom_header_style)
            td_style = self._apply_custom_row_style(td_style, custom_row_style)

            # Combine table style with inline styles
            table_style = self._combine_table_and_inline_styles(table_style, inline_style_string)

            return table_style, th_style, td_style, inline_style_string

        except (StyleNotFoundError, StyleConflictError, ConversionError):
            raise
        except Exception as e:
            raise StyleError(f"Error processing table styles: {str(e)}")

    def _validate_style_exists(self, style: str) -> None:
        """
        Validate that the specified style exists in available styles.
        
        Args:
            style: Named style to validate
            
        Raises:
            StyleNotFoundError: If the style is not found
        """
        if style not in self.styles:
            raise StyleNotFoundError(style_name=style)

    @staticmethod
    def _apply_custom_header_style(base_th_style: str, custom_header_style: Optional[str]) -> str:
        """
        Apply custom header style, checking for conflicts.
        
        Args:
            base_th_style: Base header style
            custom_header_style: Custom header style to apply
            
        Returns:
            Final header style
            
        Raises:
            StyleConflictError: If there are conflicting styles
        """
        if not custom_header_style:
            return base_th_style

        if 'text-align:' in custom_header_style and 'text-align:' in base_th_style:
            raise StyleConflictError(
                style1="default header style",
                style2="custom header style",
                message="Conflicting text-align properties in header styles"
            )

        return custom_header_style

    @staticmethod
    def _apply_custom_row_style(base_td_style: str, custom_row_style: Optional[str]) -> str:
        """
        Apply custom row style, checking for conflicts.
        
        Args:
            base_td_style: Base row style
            custom_row_style: Custom row style to apply
            
        Returns:
            Final row style
            
        Raises:
            StyleConflictError: If there are conflicting styles
        """
        if not custom_row_style:
            return base_td_style

        if 'text-align:' in custom_row_style and 'text-align:' in base_td_style:
            raise StyleConflictError(
                style1="default row style",
                style2="custom row style",
                message="Conflicting text-align properties in row styles"
            )

        return custom_row_style

    @staticmethod
    def _combine_table_and_inline_styles(table_style: str, inline_style_string: str) -> str:
        """
        Combine table style with inline styles.
        
        Args:
            table_style: Base table style
            inline_style_string: Inline styles to add
            
        Returns:
            Combined table style
        """
        if inline_style_string:
            return f"{table_style} {inline_style_string}"
        return table_style

    def _build_table_html(self, headers: List[str], rows: List[List[Any]],
                          table_style: str, th_style: str, td_style: str,
                          caption: Optional[str], inline_style_string: str,
                          compact: bool = True) -> List[str]:
        """
        Build the HTML components for the table.
        
        Args:
            headers: List of column headers
            rows: List of rows, each row being a list of cell values
            table_style: CSS style for the table
            th_style: CSS style for header cells
            td_style: CSS style for data cells
            caption: Optional table caption
            inline_style_string: Additional CSS styles
            compact: Whether to condense large data structures
            
        Returns:
            List of HTML elements for the complete table
            
        Raises:
            HTMLGenerationError: If HTML generation fails
        """
        try:
            html = [f'<table style="{table_style}">']

            # Add caption if provided
            html.extend(self._generate_table_caption(caption, inline_style_string))

            # Add header row
            html.extend(self._generate_table_header(headers, th_style))

            # Add data rows
            html.extend(self._generate_table_rows(rows, td_style, compact))

            # Close the table
            html.append('</table>')

            return html
        except Exception as e:
            raise HTMLGenerationError(
                component="table",
                message=f"Failed to generate table HTML: {str(e)}"
            )

    @staticmethod
    def _display_html(html: List[str], headers: List[str], rows: List[List[Any]]) -> None:
        """
        Display the HTML table or fallback to text representation.
        
        Args:
            html: List of HTML elements for the table
            headers: List of column headers (for fallback display)
            rows: List of rows (for fallback display)
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(''.join(html)))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Table will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render HTML table: {str(e)}") from e

    def _process_dict_source(self, source_dict: Dict[Any, Any]) -> Tuple[List[str], List[List[Any]]]:
        """
        Process a dictionary data source into headers and rows.
        
        Args:
            source_dict: Dictionary to use as the data source
            
        Returns:
            Tuple of (headers, rows)
            
        Raises:
            TableError: If source_dict is not a dictionary
        """
        if not isinstance(source_dict, Mapping):
            raise TableError(f"source_dict must be a dictionary, got {type(source_dict).__name__}")

        # Convert dict to headers and rows
        headers = list(source_dict.keys())

        # If the values are scalars, make a single row with those values
        if all(not hasattr(v, '__iter__') or isinstance(v, (str, bytes)) for v in source_dict.values()):
            rows = [list(source_dict.values())]
        else:
            rows = self._transpose_dict_values(source_dict)

        return headers, rows

    @staticmethod
    def _transpose_dict_values(source_dict: Dict[Any, Any]) -> List[List[Any]]:
        """
        Transpose dictionary values into rows.
        
        For dict values that are iterables, each key-value pair becomes a column 
        where the key is the header and the values become entries in multiple rows.
        
        Args:
            source_dict: Dictionary with iterable values
            
        Returns:
            List of rows
        """
        # First, ensure all values are iterables with same length
        values = []
        for v in source_dict.values():
            if not hasattr(v, '__iter__') or isinstance(v, (str, bytes)):
                # Convert scalar to a single-item list
                values.append([v])
            else:
                # Convert to list if it's not already
                values.append(list(v))

        # Get the maximum length of all value lists
        max_len = max(len(v) for v in values)

        # Pad shorter lists with None
        for i, v in enumerate(values):
            if len(v) < max_len:
                values[i] = v + [None] * (max_len - len(v))

        # Transpose to get rows
        rows = [[] for _ in range(max_len)]
        for v in values:
            for i, item in enumerate(v):
                rows[i].append(item)

        return rows

    @staticmethod
    def _prepare_inline_styles(inline_styles: Dict[str, str], width: str) -> Dict[str, str]:
        """
        Prepare inline styles, ensuring width parameter takes precedence.
        
        Args:
            inline_styles: Dictionary of inline styles
            width: Width parameter that should take precedence
            
        Returns:
            Processed inline styles dictionary
        """
        inline_styles_dict = dict(inline_styles)
        if 'width' in inline_styles_dict:
            del inline_styles_dict['width']  # Ensure our width parameter takes precedence
        return inline_styles_dict

    def display(self, headers: Optional[List[str]] = None, rows: Optional[Iterable[Any]] = None, *,
                source_dict: Optional[Dict[Any, Any]] = None,
                style: str = 'default', width: str = '100%',
                caption: Optional[str] = None,
                custom_header_style: Optional[str] = None,
                custom_row_style: Optional[str] = None,
                compact: bool = True,
                **inline_styles) -> None:
        """
        Display a table with the given headers and rows.
        
        Args:
            headers: List of column headers (optional if source_dict is provided)
            rows: List of rows, each row being any iterable (list, tuple, array, etc.) of cell values (optional if source_dict is provided)
            source_dict: Dictionary to use as the data source (keys become headers, values become rows)
            style: Named style from available styles
            width: Width of the table (CSS value)
            caption: Optional table caption
            custom_header_style: Optional custom CSS for header cells
            custom_row_style: Optional custom CSS for data cells
            compact: Whether to condense large data structures (default: True)
            **inline_styles: Additional CSS styles to apply to the table
            
        Raises:
            TableError: If there's an issue with the table data
            StyleNotFoundError: If specified style is not found
            DisplayEnvironmentError: If display environment is not available
        """
        try:
            # Handle dictionary input
            if source_dict is not None:
                headers, rows = self._process_dict_source(source_dict)

            # Validate required inputs
            if headers is None or rows is None:
                raise TableError("Either provide both headers and rows, or a source_dict")

            # Process inline styles
            inline_styles_dict = self._prepare_inline_styles(inline_styles, width)

            # Process all styles
            table_style, th_style, td_style, inline_style_string = self._process_styles(
                style, width, custom_header_style, custom_row_style, inline_styles_dict
            )

            # Build HTML components
            html = self._build_table_html(
                headers, rows, table_style, th_style, td_style, caption, inline_style_string, compact
            )

            # Display the final HTML
            self._display_html(html, headers, rows)

        except Exception as e:
            if isinstance(e, (TableError, StyleNotFoundError, DisplayEnvironmentError)):
                # Pass through known exceptions
                raise
            else:
                # Wrap unknown exceptions
                raise TableError(f"Error displaying table: {str(e)}")


class DFDisplayer(Displayer):
    """Displays pandas DataFrames and Series with extensive styling options."""

    def __init__(self, styles: Dict[str, str], df: Union[pd.DataFrame, pd.Series]):
        """
        Initialize a DataFrame or Series displayer.
        
        Args:
            styles: Dictionary of named styles
            df: The DataFrame or Series to display
        """
        super().__init__(styles)
        self.df = df
        self.is_series = isinstance(df, pd.Series)

    @staticmethod
    def _extract_base_color(base_style: str) -> str:
        """
        Extract the text color from a base style string.
        
        Args:
            base_style: CSS style string
            
        Returns:
            CSS color property or empty string
        """
        base_color = ""
        for part in base_style.split(';'):
            if 'color:' in part and 'background-color:' not in part:
                base_color = part.strip()
                break
        return base_color

    def _prepare_table_styles(self, style: str, width: str, inline_style_string: str,
                              base_color: str, header_style: Optional[str],
                              odd_row_style: Optional[str], even_row_style: Optional[str]) -> tuple:
        """
        Prepare all the styles needed for the table.
        
        Args:
            style: Named style from the available styles
            width: Table width (CSS value)
            inline_style_string: Processed inline CSS styles
            base_color: Extracted text color
            header_style: Custom CSS for header cells
            odd_row_style: Custom CSS for odd rows
            even_row_style: Custom CSS for even rows
            
        Returns:
            Tuple of (table_style, th_style, odd_td_style, even_td_style)
        """
        # Base styles
        base_style = self.styles.get(style, self.styles['default'])

        # Table element styles - ensure width is important to override any other styles
        table_only_styles = f"border-collapse: collapse; width: {width} !important;"
        table_style = f"{base_style} {table_only_styles}"

        # Cell styles base
        cell_style_base = inline_style_string if inline_style_string else ""

        # Default styles with inline styles
        default_header = f"background-color: #f2f2f2; padding: 8px; border: 1px solid #ddd; text-align: left; font-weight: bold; {base_color}; {cell_style_base}"
        default_odd_row = f"background-color: #ffffff; padding: 8px; border: 1px solid #ddd; {base_color}; {cell_style_base}"
        default_even_row = f"background-color: #f9f9f9; padding: 8px; border: 1px solid #ddd; {base_color}; {cell_style_base}"

        # Apply custom styles if provided
        th_style = f"{header_style} {cell_style_base}" if header_style else default_header
        odd_td_style = f"{odd_row_style} {cell_style_base}" if odd_row_style else default_odd_row
        even_td_style = f"{even_row_style} {cell_style_base}" if even_row_style else default_even_row

        return table_style, th_style, odd_td_style, even_td_style

    def _convert_series_to_dataframe(self) -> pd.DataFrame:
        """
        Convert a pandas Series to a DataFrame for display.
        
        The Series is converted to a single-column DataFrame where:
        - The column name is taken from the Series name (or "Value" if unnamed)
        - The index of the Series is preserved
        
        Returns:
            DataFrame representation of the Series
            
        Raises:
            ConversionError: If Series conversion fails
        """
        try:
            if not self.is_series:
                return self.df
                
            # Convert Series to DataFrame with meaningful column name
            series_name = self.df.name or "Value"
            return pd.DataFrame({series_name: self.df})
        except Exception as e:
            raise ConversionError(
                from_type="pandas.Series",
                to_type="pandas.DataFrame",
                message=f"Failed to convert Series to DataFrame: {str(e)}"
            )

    def _prepare_dataframe(self, df: Union[pd.DataFrame, pd.Series], max_rows: Optional[int],
                           max_cols: Optional[int], precision: int) -> pd.DataFrame:
        """
        Prepare the DataFrame or Series for display with limits and formatting.
        
        Args:
            df: DataFrame or Series to prepare
            max_rows: Maximum number of rows to display
            max_cols: Maximum number of columns to display
            precision: Decimal precision for float values
            
        Returns:
            Prepared DataFrame copy
            
        Raises:
            FormattingError: If there's an error formatting the DataFrame
            DataFrameError: If there's an issue with the DataFrame structure
            ConversionError: If Series conversion fails
        """
        try:
            # Convert Series to DataFrame if needed
            if isinstance(df, pd.Series):
                df = pd.DataFrame({df.name or "Value": df})
                
            self._validate_dataframe_params(df, max_rows, max_cols, precision)
            df_copy = df.copy()
            df_copy = self._apply_row_limits(df_copy, max_rows)
            df_copy = self._apply_column_limits(df_copy, max_cols)
            df_copy = self._format_float_columns(df_copy, precision)
            return df_copy
        except (FormattingError, DataFrameError):
            raise
        except Exception as e:
            raise FormattingError(f"Error preparing DataFrame: {str(e)}")

    @staticmethod
    def _validate_dataframe_params(df: pd.DataFrame, max_rows: Optional[int],
                                   max_cols: Optional[int], precision: int) -> None:
        """
        Validate DataFrame and formatting parameters.
        
        Args:
            df: DataFrame to validate
            max_rows: Maximum number of rows to display
            max_cols: Maximum number of columns to display
            precision: Decimal precision for float values
            
        Raises:
            FormattingError: If any parameter is invalid
            DataFrameError: If the input is not a DataFrame
        """
        if max_rows is not None and max_rows <= 0:
            raise FormattingError("max_rows must be a positive integer")

        if max_cols is not None and max_cols <= 0:
            raise FormattingError("max_cols must be a positive integer")

        if precision < 0:
            raise FormattingError("precision must be a non-negative integer")

        if not isinstance(df, pd.DataFrame):
            raise DataFrameError(f"Expected pandas DataFrame, got {type(df).__name__}")

    @staticmethod
    def _apply_row_limits(df: pd.DataFrame, max_rows: Optional[int]) -> pd.DataFrame:
        """
        Apply row limits to the DataFrame if specified.
        
        Args:
            df: DataFrame to limit
            max_rows: Maximum number of rows to display
            
        Returns:
            DataFrame with row limits applied
        """
        if max_rows is not None and len(df) > max_rows:
            half_rows = max_rows // 2
            return pd.concat([df.head(half_rows), df.tail(half_rows)])
        return df

    @staticmethod
    def _apply_column_limits(df: pd.DataFrame, max_cols: Optional[int]) -> pd.DataFrame:
        """
        Apply column limits to the DataFrame if specified.
        
        Args:
            df: DataFrame to limit
            max_cols: Maximum number of columns to display
            
        Returns:
            DataFrame with column limits applied
        """
        if max_cols is not None and len(df.columns) > max_cols:
            half_cols = max_cols // 2
            first_cols = df.columns[:half_cols].tolist()
            last_cols = df.columns[-half_cols:].tolist()
            return df[first_cols + last_cols]
        return df

    @staticmethod
    def _format_float_columns(df: pd.DataFrame, precision: int) -> pd.DataFrame:
        """
        Format float columns with specified precision.
        
        Args:
            df: DataFrame to format
            precision: Decimal precision for float values
            
        Returns:
            DataFrame with formatted float columns
            
        Raises:
            FormattingError: If there's an error formatting any column
        """
        for col in df.select_dtypes(include=['float']).columns:
            try:
                df[col] = df[col].apply(lambda x: f"{x:.{precision}f}" if pd.notnull(x) else "")
            except Exception as e:
                raise FormattingError(f"Error formatting column '{col}': {str(e)}")
        return df

    @staticmethod
    def _generate_table_caption(caption: Optional[str], cell_style_base: str) -> List[str]:
        """
        Generate HTML for the table caption if provided.
        
        Args:
            caption: Caption text
            cell_style_base: Base CSS style string
            
        Returns:
            List of HTML caption elements or empty list
        """
        if not caption:
            return []

        caption_style = f"caption-side: top; text-align: left; font-weight: bold; margin-bottom: 10px; {cell_style_base}"
        return [f'<caption style="{caption_style}">{caption}</caption>']

    @staticmethod
    def _generate_header_row(df_copy: pd.DataFrame, th_style: str,
                             highlight_cols: Optional[Union[List, Dict]],
                             index: bool) -> List[str]:
        """
        Generate HTML for the table header row.
        
        Args:
            df_copy: Prepared DataFrame
            th_style: CSS style for header cells
            highlight_cols: Columns to highlight
            index: Whether to show DataFrame index
            
        Returns:
            List of HTML elements for the header row
        """
        html = ['<tr>']

        # Add index header if showing index
        if index:
            html.append(f'<th style="{th_style}"></th>')

        # Add column headers
        for col in df_copy.columns:
            col_style = th_style

            # Apply highlighting to columns if specified
            if highlight_cols:
                if isinstance(highlight_cols, dict) and col in highlight_cols:
                    col_style = f"{th_style} {highlight_cols[col]}"
                elif isinstance(highlight_cols, list) and col in highlight_cols:
                    col_style = f"{th_style} background-color: #FFEB3B !important;"

            html.append(f'<th style="{col_style}">{col}</th>')

        html.append('</tr>')
        return html

    def _generate_data_rows(self, df_copy: pd.DataFrame, even_td_style: str,
                            odd_td_style: str, highlight_rows: Optional[Union[List, Dict]],
                            highlight_cells: Optional[Dict], index: bool) -> List[str]:
        """
        Generate HTML for the table data rows.
        
        Args:
            df_copy: Prepared DataFrame
            even_td_style: CSS style for even rows
            odd_td_style: CSS style for odd rows
            highlight_rows: Rows to highlight
            highlight_cells: Cells to highlight
            index: Whether to show DataFrame index
            
        Returns:
            List of HTML elements for data rows
        """
        html = []

        for i, (idx, row) in enumerate(df_copy.iterrows()):
            row_style = self._get_row_style(i, idx, even_td_style, odd_td_style, highlight_rows)
            html.extend(self._generate_single_row(i, idx, row, row_style, df_copy.columns, highlight_cells, index))

        return html

    @staticmethod
    def _get_row_style(row_index: int, idx, even_td_style: str, odd_td_style: str,
                       highlight_rows: Optional[Union[List, Dict]]) -> str:
        """
        Determine the style for a table row.
        
        Args:
            row_index: Zero-based index of the row
            idx: DataFrame index value for the row
            even_td_style: CSS style for even rows
            odd_td_style: CSS style for odd rows
            highlight_rows: Rows to highlight
            
        Returns:
            CSS style string for the row
        """
        # Base style alternates between even and odd
        row_style = even_td_style if row_index % 2 == 0 else odd_td_style

        # Apply row highlighting if specified
        if highlight_rows:
            if isinstance(highlight_rows, dict) and idx in highlight_rows:
                row_style = f"{row_style} {highlight_rows[idx]}"
            elif isinstance(highlight_rows, list) and idx in highlight_rows:
                row_style = f"{row_style} background-color: #FFEB3B !important;"

        return row_style

    def _generate_single_row(self, row_index: int, idx, row, row_style: str, columns,
                             highlight_cells: Optional[Dict], index: bool) -> List[str]:
        """
        Generate HTML for a single table row.
        
        Args:
            row_index: Zero-based index of the row
            idx: DataFrame index value for the row
            row: Row data
            row_style: Base CSS style for the row
            columns: DataFrame columns
            highlight_cells: Cells to highlight
            index: Whether to show DataFrame index
            
        Returns:
            List of HTML elements for the row
        """
        html_row = ['<tr>']

        # Add index cell if showing index
        if index:
            html_row.append(f'<td style="{row_style} font-weight: bold;">{idx}</td>')

        # Add data cells
        for col in columns:
            cell_style = self._get_cell_style(row_index, idx, col, row_style, highlight_cells)
            cell_value = row[col]
            html_row.append(f'<td style="{cell_style}">{cell_value}</td>')

        html_row.append('</tr>')
        return html_row

    @staticmethod
    def _get_cell_style(row_index: int, idx, col, row_style: str,
                        highlight_cells: Optional[Dict]) -> str:
        """
        Determine the style for a table cell.
        
        Args:
            row_index: Zero-based index of the row
            idx: DataFrame index value for the row
            col: Column name
            row_style: Base CSS style for the row
            highlight_cells: Cells to highlight
            
        Returns:
            CSS style string for the cell
        """
        cell_style = row_style

        # Apply cell highlighting if specified
        if highlight_cells:
            # Try different ways to match the cell coordinates
            if (idx, col) in highlight_cells:
                cell_style = f"{cell_style} {highlight_cells[(idx, col)]}"
            elif (row_index, col) in highlight_cells:
                cell_style = f"{cell_style} {highlight_cells[(row_index, col)]}"
            elif (str(row_index), col) in highlight_cells:
                cell_style = f"{cell_style} {highlight_cells[(str(row_index), col)]}"

        return cell_style

    def display(self, *,
                style: str = 'default',
                max_rows: Optional[int] = None,
                max_cols: Optional[int] = None,
                precision: int = 2,
                header_style: Optional[str] = None,
                odd_row_style: Optional[str] = None,
                even_row_style: Optional[str] = None,
                index: bool = True,
                width: str = '100%',
                caption: Optional[str] = None,
                highlight_cols: Optional[Union[List, Dict]] = None,
                highlight_rows: Optional[Union[List, Dict]] = None,
                highlight_cells: Optional[Dict] = None,
                **inline_styles) -> None:
        """
        Display a pandas DataFrame or Series with customizable styling.

        Args:
            style: Named style from the available styles
            max_rows: Maximum number of rows to display
            max_cols: Maximum number of columns to display
            precision: Decimal precision for float values
            header_style: Custom CSS for header cells
            odd_row_style: Custom CSS for odd rows
            even_row_style: Custom CSS for even rows
            index: Whether to show DataFrame/Series index
            width: Table width (CSS value)
            caption: Table caption
            highlight_cols: Columns to highlight (list) or {col: style} mapping
            highlight_rows: Rows to highlight (list) or {row: style} mapping
            highlight_cells: Cell coordinates to highlight {(row, col): style}
            **inline_styles: Additional CSS styles for all cells
            
        Notes:
            For Series, the Series name (or "Value" if unnamed) will be used as the column name
            in the resulting table. The Series index is preserved and displayed when index=True.
        """
        # Process styles (but don't let them override the width)
        inline_styles_dict = dict(inline_styles)
        if 'width' in inline_styles_dict:
            del inline_styles_dict['width']  # Ensure our width parameter takes precedence

        inline_style_string = self._process_inline_styles(inline_styles_dict)
        base_style = self.styles.get(style, self.styles['default'])
        base_color = self._extract_base_color(base_style)

        # Prepare all styles
        table_style, th_style, odd_td_style, even_td_style = self._prepare_table_styles(
            style, width, inline_style_string, base_color,
            header_style, odd_row_style, even_row_style
        )

        # Convert Series to DataFrame if necessary and prepare the data
        df_to_display = self.df
        if self.is_series:
            df_to_display = self._convert_series_to_dataframe()
            
        # Prepare the DataFrame (handles both original DataFrames and converted Series)
        df_copy = self._prepare_dataframe(df_to_display, max_rows, max_cols, precision)

        # Build HTML components
        html = [f'<table style="{table_style}">']

        # Add caption if provided
        html.extend(self._generate_table_caption(caption, inline_style_string))

        # Add header row
        html.extend(self._generate_header_row(df_copy, th_style, highlight_cols, index))

        # Add data rows
        html.extend(self._generate_data_rows(df_copy, even_td_style, odd_td_style,
                                             highlight_rows, highlight_cells, index))

        html.append('</table>')

        # Display the final HTML
        try:
            ip_display(HTML(''.join(html)))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. DataFrame will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render DataFrame HTML: {str(e)}") from e


class ListDisplayer(Displayer):
    """Displays Python lists or tuples as HTML lists with enhanced styling for nested structures and matrices."""

    def __init__(self, styles: Dict[str, str]):
        """
        Initialize a list displayer with styles.
        
        Args:
            styles: Dictionary of named styles
        """
        super().__init__(styles)
        # Default color scheme for nested lists - can be customized
        self.nesting_colors = [
            "#3498DB",  # Level 0 - Blue
            "#9B59B6",  # Level 1 - Purple
            "#16A085",  # Level 2 - Teal
            "#F39C12",  # Level 3 - Orange
            "#E74C3C",  # Level 4 - Red
        ]

    def _generate_list_html(self, items: Any, ordered: bool, style: str,
                            item_style: Optional[str], nesting_level: int = 0,
                            is_matrix: bool = False, **inline_styles) -> str:
        """
        Recursively generate HTML for a list or tuple with enhanced styling.
        
        Args:
            items: The list or tuple to display
            ordered: True for ordered list (<ol>), False for unordered (<ul>)
            style: Base style name for the list container
            item_style: Optional custom CSS for list items
            nesting_level: Current nesting level for applying different styles
            is_matrix: Whether to render as a matrix (2D array)
            **inline_styles: Additional inline styles for list items
            
        Returns:
            HTML string for the list
            
        Raises:
            StyleNotFoundError: If the specified style is not found
            NestedStructureError: If there's an error processing nested structures
            HTMLGenerationError: If HTML generation fails
        """
        try:
            # Handle NumPy arrays or other array-like objects
            items = self._convert_to_list(items)

            # Check if this is a matrix (2D array) and wasn't already flagged
            if not is_matrix and self._is_matrix(items):
                return self._generate_matrix_html(items, style, **inline_styles)

            # Validate style and prepare list styling
            self._validate_style(style)
            list_style = self._prepare_list_style(style, nesting_level)

            # Process item styling
            final_item_style = self._prepare_item_style(item_style, inline_styles, nesting_level)

            # Generate the HTML
            return self._build_list_html(items, ordered, list_style, final_item_style, nesting_level, inline_styles)

        except StyleNotFoundError:
            raise
        except Exception as e:
            raise NestedStructureError(f"Error generating HTML for list at nesting level {nesting_level}: {str(e)}")

    def _validate_style(self, style: str) -> None:
        """
        Validate that the requested style exists.
        
        Args:
            style: Style name to validate
            
        Raises:
            StyleNotFoundError: If the style is not found
        """
        if style not in self.styles:
            raise StyleNotFoundError(style_name=style)

    def _prepare_list_style(self, style: str, nesting_level: int) -> str:
        """
        Prepare the CSS style for the list container based on nesting level.
        
        Args:
            style: Base style name
            nesting_level: Current nesting level
            
        Returns:
            CSS style string for the list container
        """
        style_base = self.styles.get(style)

        # Determine nesting color
        color_idx = min(nesting_level, len(self.nesting_colors) - 1)
        nesting_color = self.nesting_colors[color_idx]

        # Apply nesting-specific style enhancements
        if nesting_level > 0:
            # Add some visual differentiation based on nesting level
            indent = nesting_level * 5  # Slightly increase indent for deeper nesting
            return f"{style_base}; border-left: 2px solid {nesting_color}; padding-left: {indent}px; margin-left: {indent}px;"
        else:
            return style_base

    def _prepare_item_style(self, item_style: Optional[str], inline_styles: Dict[str, str], nesting_level: int) -> str:
        """
        Prepare the CSS style for list items.
        
        Args:
            item_style: Optional custom CSS for list items
            inline_styles: Additional inline styles
            nesting_level: Current nesting level
            
        Returns:
            CSS style string for list items
        """
        list_item_inline_style = self._process_inline_styles(inline_styles)
        final_item_style = item_style if item_style else ""

        if list_item_inline_style:
            final_item_style = f"{final_item_style}; {list_item_inline_style}".strip('; ')

        # Add color to items based on nesting level
        if not final_item_style or "color:" not in final_item_style:
            color_idx = min(nesting_level, len(self.nesting_colors) - 1)
            nesting_color = self.nesting_colors[color_idx]
            final_item_style = f"{final_item_style}; color: {nesting_color}".strip('; ')

        return final_item_style

    def _build_list_html(self, items: List, ordered: bool, list_style: str,
                         item_style: str, nesting_level: int, inline_styles: Dict[str, str]) -> str:
        """
        Build the HTML for the list.
        
        Args:
            items: List items to render
            ordered: Whether to use ordered or unordered list
            list_style: CSS style for the list container
            item_style: CSS style for list items
            nesting_level: Current nesting level
            inline_styles: Additional inline styles
            
        Returns:
            HTML string for the list
        """
        tag = 'ol' if ordered else 'ul'
        html = [f'<{tag} style="{list_style}">']

        for item in items:
            item_content = self._process_list_item(item, ordered, item_style, nesting_level, inline_styles)
            html.append(f'<li style="{item_style}">{item_content}</li>')

        html.append(f'</{tag}>')
        return ''.join(html)

    def _process_list_item(self, item: Any, ordered: bool, item_style: str,
                           nesting_level: int, inline_styles: Dict[str, str]) -> str:
        """
        Process a single list item, handling nested structures.
        
        Args:
            item: The item to process
            ordered: Whether to use ordered or unordered list for nested lists
            item_style: CSS style for the item
            nesting_level: Current nesting level
            inline_styles: Additional inline styles
            
        Returns:
            HTML string for the item content
        """
        if isinstance(item, (list, tuple)) or self._is_array_like(item):
            # Recursively handle nested lists/tuples with increased nesting level
            return self._generate_list_html(
                item, ordered, "list", item_style, nesting_level=nesting_level + 1, **inline_styles
            )
        elif isinstance(item, dict):
            # Handle dictionaries more elegantly
            return self._generate_dict_html(item, nesting_level)
        else:
            return str(item)


    def _is_array_like(self, obj: Any) -> bool:
        """
        Check if an object is array-like.
        
        Args:
            obj: Object to check
            
        Returns:
            True if the object is array-like, False otherwise
        """
        # Check common Python types first
        if self._is_known_sequence_type(obj):
            return True
            
        if self._is_known_non_sequence_type(obj):
            return False
            
        # Check for array library types
        if self._is_array_library_type(obj):
            return True
            
        # Check for sequence-like interfaces
        if self._has_sequence_interface(obj):
            return True
            
        # Check for array or buffer protocol
        if self._has_array_protocol(obj):
            return True
            
        return False
        
    def _is_known_sequence_type(self, obj: Any) -> bool:
        """Check if object is a known Python sequence type."""
        return isinstance(obj, (list, tuple))
        
    def _is_known_non_sequence_type(self, obj: Any) -> bool:
        """Check if object is a known non-sequence Python type."""
        return isinstance(obj, (str, dict, bytes, bool, int, float))
        
    def _is_array_library_type(self, obj: Any) -> bool:
        """Check if object is from a common array library."""
        return any(lib in str(type(obj)) for lib in ['numpy', 'pandas', 'torch', 'tensorflow', 'tf.', 'jax'])

    def _has_sequence_interface(self, obj: Any) -> bool:
        """Check if object implements sequence-like interfaces."""
        if not hasattr(obj, '__iter__'):
            return False
            
        # Check for indexing support
        if hasattr(obj, '__getitem__'):
            return True
            
        # Check for length support
        try:
            len(obj)
            return True
        except (TypeError, AttributeError):
            pass
            
        # Check if it's an iterator
        try:
            iter(obj)
            return True
        except TypeError:
            pass
            
        return False
        
    def _has_array_protocol(self, obj: Any) -> bool:
        """Check if object implements array or buffer protocols."""
        return hasattr(obj, '__array__') or hasattr(obj, 'buffer_info')

    def _convert_to_list(self, obj: Any) -> List:
        """
        Convert array-like objects to lists for display.
        
        Args:
            obj: Object to convert
            
        Returns:
            List representation of the object
            
        Raises:
            ArrayConversionError: If array-like object conversion fails
        """
        try:
            # Handle basic Python types first
            if self._is_basic_sequence(obj):
                return list(obj)

            # Get the object type as string for module detection
            obj_type = str(type(obj))

            # Try to convert using specialized handlers for known array types
            result = self._try_specialized_conversion(obj, obj_type)
            if result is not None:
                return result

            # Handle generic array-like objects
            if self._is_array_like(obj):
                return self._convert_generic_array(obj)

            # Single item, not an array-like - wrap in a list
            return [obj]

        except Exception as e:
            obj_type = type(obj).__name__
            raise ArrayConversionError(
                array_type=obj_type,
                message=f"Failed to convert object of type {obj_type}: {str(e)}"
            )

    @staticmethod
    def _is_basic_sequence(obj: Any) -> bool:
        """Check if object is a basic Python sequence type that can be directly converted."""
        return isinstance(obj, (list, tuple))

    def _try_specialized_conversion(self, obj: Any, obj_type: str) -> Optional[List]:
        """
        Try to convert object using specialized handlers for known array libraries.
        
        Args:
            obj: Object to convert
            obj_type: String representation of object type
            
        Returns:
            List representation if conversion succeeded, None otherwise
        """
        array_handlers = self._get_array_handlers()

        for module_name, handler in array_handlers.items():
            if module_name in obj_type:
                try:
                    return handler(obj)
                except (AttributeError, TypeError):
                    return list(obj)

        return None

    @staticmethod
    def _get_array_handlers() -> Dict[str, Callable]:
        """Get handlers for converting specific array library types."""
        return {
            'numpy': lambda x: x.tolist() if hasattr(x, 'tolist') else list(x),
            'pandas': lambda x: x.values.tolist() if hasattr(x, 'values') else list(x),
            'torch': lambda x: x.cpu().numpy().tolist() if hasattr(x, 'numpy') else list(x),
            'tensorflow': lambda x: x.numpy().tolist() if hasattr(x, 'numpy') else list(x),
            'tf.': lambda x: x.numpy().tolist() if hasattr(x, 'numpy') else list(x),
            'jax': lambda x: x.tolist() if hasattr(x, 'tolist') else list(x)
        }

    @staticmethod
    def _convert_generic_array(obj: Any) -> List:
        """
        Convert a generic array-like object to a list.
        
        Args:
            obj: Array-like object to convert
            
        Returns:
            List representation of the object
        """
        try:
            return list(obj)
        except (TypeError, ValueError):
            # Convert items one by one if direct conversion fails
            return [item for item in obj]

    @staticmethod
    def _is_matrix(items: List) -> bool:
        """
        Check if a list represents a matrix (2D array with consistent row lengths).
        
        Args:
            items: List to check
            
        Returns:
            True if the list is a matrix, False otherwise
            
        Raises:
            MatrixDetectionError: If matrix detection fails
        """
        try:
            if not items or not isinstance(items, (list, tuple)):
                return False

            # Check if all items are lists/tuples of the same length
            if all(isinstance(row, (list, tuple)) for row in items):
                try:
                    row_lengths = [len(row) for row in items]
                    return len(row_lengths) > 1 and all(length == row_lengths[0] for length in row_lengths)
                except (TypeError, AttributeError):
                    return False

            return False

        except Exception as e:
            raise MatrixDetectionError(f"Failed to detect if structure is a matrix: {str(e)}")

    def _generate_matrix_html(self, matrix: List[List], style: str, **inline_styles) -> str:
        """
        Generate HTML for a matrix-like structure.
        
        Args:
            matrix: 2D list/array to display as a matrix
            style: Base style name
            **inline_styles: Additional inline styles
            
        Returns:
            HTML string for the matrix
            
        Raises:
            StyleNotFoundError: If the specified style is not found
            MatrixDetectionError: If matrix processing fails
        """
        if style not in self.styles:
            raise StyleNotFoundError(style_name=style)
            
        try:
            return self._build_matrix_html(matrix, style, **inline_styles)
        except StyleNotFoundError:
            raise
        except Exception as e:
            raise MatrixDetectionError(f"Failed to generate HTML for matrix: {str(e)}")
    
    def _build_matrix_html(self, matrix: List[List], style: str, **inline_styles) -> str:
        """
        Build the HTML table structure for a matrix.
        
        Args:
            matrix: 2D list/array to display as a matrix
            style: Base style name
            **inline_styles: Additional inline styles
            
        Returns:
            HTML string for the matrix
        """
        style_base = self.styles.get(style)
        matrix_style = f"{style_base}; border-collapse: collapse; margin: 10px 0;"
        cell_style = "border: 1px solid #ddd; padding: 6px 10px; text-align: center;"
        
        html = [f'<table style="{matrix_style}">']
        
        for row in matrix:
            html.append('<tr>')
            html.extend(self._generate_matrix_row_cells(row, cell_style, style, **inline_styles))
            html.append('</tr>')
            
        html.append('</table>')
        return ''.join(html)
    
    def _generate_matrix_row_cells(self, row: List, cell_style: str, style: str, **inline_styles) -> List[str]:
        """
        Generate HTML for cells in a matrix row.
        
        Args:
            row: List of cell values in a matrix row
            cell_style: CSS style for the cell
            style: Base style name
            **inline_styles: Additional inline styles
            
        Returns:
            List of HTML strings for each cell
        """
        cells = []
        for cell in row:
            cell_content = self._format_cell_content(cell, style, **inline_styles)
            cells.append(f'<td style="{cell_style}">{cell_content}</td>')
        return cells
    
    def _format_cell_content(self, cell: Any, style: str, **inline_styles) -> str:
        """
        Format the content of a matrix cell based on its type.
        
        Args:
            cell: Cell value to format
            style: Base style name
            **inline_styles: Additional inline styles
            
        Returns:
            Formatted HTML string for the cell content
        """
        if isinstance(cell, (list, tuple)) or self._is_array_like(cell):
            return self._generate_list_html(
                cell, False, style, None, nesting_level=1, **inline_styles
            )
        elif isinstance(cell, dict):
            return self._generate_dict_html(cell, 1)
        else:
            return str(cell)

    def _generate_dict_html(self, data: Dict, nesting_level: int) -> str:
        """
        Generate HTML for dictionary inside a list.
        
        Args:
            data: Dictionary to display
            nesting_level: Current nesting level
            
        Returns:
            HTML string for the dictionary
            
        Raises:
            DictError: If dictionary processing fails
            ColorError: If color processing fails
        """
        if not isinstance(data, dict):
            raise DictError(f"Expected dictionary, received {type(data).__name__}")
            
        try:
            return self._render_dict_as_html(data, nesting_level)
        except ColorError:
            # Pass through color errors directly
            raise
        except Exception as e:
            raise DictError(f"Failed to generate HTML for dictionary: {str(e)}")
    
    def _render_dict_as_html(self, data: Dict, nesting_level: int) -> str:
        """
        Render a dictionary as styled HTML.
        
        Args:
            data: Dictionary to render
            nesting_level: Current nesting level for styling
            
        Returns:
            HTML string representation of the dictionary
        """
        # Get appropriate nesting color based on level
        color_idx = min(nesting_level, len(self.nesting_colors) - 1)
        nesting_color = self.nesting_colors[color_idx]
        bg_color = self._lighten_color(nesting_color, 0.9)
        
        # Create container with styling
        container_style = f"background-color: {bg_color}; padding: 6px; border-radius: 4px; " \
                          f"border-left: 2px solid {nesting_color}; margin: 4px 0;"
        html = [f'<div style="{container_style}">']
        
        # Process each key-value pair
        for key, value in data.items():
            key_style = f"font-weight: bold; color: {nesting_color};"
            html.append(f'<div><span style="{key_style}">{key}</span>: {self._format_dict_value(value, nesting_level)}</div>')
        
        html.append('</div>')
        return ''.join(html)
    
    def _format_dict_value(self, value: Any, nesting_level: int) -> str:
        """
        Format a dictionary value based on its type.
        
        Args:
            value: The value to format
            nesting_level: Current nesting level
            
        Returns:
            HTML string for the formatted value
        """
        if isinstance(value, (list, tuple)) or self._is_array_like(value):
            return self._generate_list_html(
                value, False, "default", None, nesting_level=nesting_level + 1
            )
        elif isinstance(value, dict):
            return self._generate_dict_html(value, nesting_level + 1)
        else:
            return str(value)

    @staticmethod
    def _lighten_color(color: str, factor: float = 0.5) -> str:
        """
        Lighten a hex color by the given factor.
        
        Args:
            color: Hex color string (#RRGGBB)
            factor: Factor to lighten (0-1, where 1 is white)
            
        Returns:
            Lightened hex color
            
        Raises:
            ColorError: If color processing fails
        """
        try:
            # Handle colors with or without #
            if color.startswith('#'):
                color = color[1:]

            # Handle both 3 and 6 digit hex
            if len(color) == 3:
                r = int(color[0] + color[0], 16)
                g = int(color[1] + color[1], 16)
                b = int(color[2] + color[2], 16)
            elif len(color) == 6:
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
            else:
                raise ColorError(color_value=color, message=f"Invalid hex color format: {color}")

            # Lighten
            r = int(r + (255 - r) * factor)
            g = int(g + (255 - g) * factor)
            b = int(b + (255 - b) * factor)

            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"

        except ValueError as e:
            raise ColorError(color_value=color, message=f"Invalid color value: {color}") from e
        except Exception as e:
            raise ColorError(color_value=color, message=f"Error processing color: {str(e)}") from e

    def display(self, items: Any, *,
                ordered: bool = False, style: str = 'default',
                item_style: Optional[str] = None,
                matrix_mode: Optional[bool] = None,
                nesting_colors: Optional[List[str]] = None,
                **inline_styles) -> None:
        """
        Display a list, tuple, or array-like object as an HTML list or matrix.
        
        Args:
            items: The list, tuple, or array-like object to display
            ordered: If True, use an ordered list (<ol>), otherwise unordered (<ul>)
            style: Named style for the list container
            item_style: Optional custom CSS style for list items
            matrix_mode: Force matrix display mode for 2D arrays (default: auto-detect)
            nesting_colors: Optional list of colors to use for different nesting levels
            **inline_styles: Additional CSS styles to apply to list items
            
        Raises:
            ListError: If the input cannot be displayed as a list
            StyleNotFoundError: If the specified style is not found
            ColorError: If color validation fails
            DisplayEnvironmentError: If display environment is not available
            InvalidParameterError: If invalid parameters are provided
        """
        try:
            self._validate_and_set_nesting_colors(nesting_colors)
            display_items = self._prepare_items_for_display(items)
            is_matrix = self._determine_matrix_mode(display_items, matrix_mode)
            html_content = self._generate_appropriate_html(display_items, is_matrix, ordered, style, item_style,
                                                           **inline_styles)
            self._display_html(html_content, display_items)
        except (ListError, StyleNotFoundError, ColorError, DisplayEnvironmentError, InvalidParameterError):
            raise
        except Exception as e:
            raise ListError(f"Error displaying list: {str(e)}")

    def _validate_and_set_nesting_colors(self, nesting_colors: Optional[List[str]]) -> None:
        """
        Validate and set nesting colors if provided.
        
        Args:
            nesting_colors: Optional list of colors to use for different nesting levels
            
        Raises:
            InvalidParameterError: If nesting_colors is not a list
            ColorError: If any color in the list is invalid
        """
        if not nesting_colors:
            return

        if not isinstance(nesting_colors, list):
            raise InvalidParameterError("nesting_colors", "a list of color strings",
                                        received=type(nesting_colors).__name__)

        for color in nesting_colors:
            if not isinstance(color, str):
                raise ColorError(color_value=str(color),
                                 message=f"Invalid color in nesting_colors: {color}")

        self.nesting_colors = nesting_colors

    def _prepare_items_for_display(self, items: Any) -> Union[List, Tuple]:
        """
        Convert input to a displayable list format.
        
        Args:
            items: The list, tuple, or array-like object to display
            
        Returns:
            Converted list or tuple ready for display
            
        Raises:
            ListError: If the input cannot be converted or is invalid
            ContentTypeError: If the input is of an incompatible type
        """
        try:
            display_items = self._convert_to_list(items)
            return display_items
        except ArrayConversionError as e:
            # Provide more helpful error message
            raise ListError(f"Failed to convert array-like object to displayable format: {str(e)}. "
                            f"The object type '{type(items).__name__}' is supported but an error occurred during conversion.")
        except Exception as e:
            raise ListError(f"Unable to display object of type '{type(items).__name__}': {str(e)}")

    def _determine_matrix_mode(self, items: Any, matrix_mode: Optional[bool]) -> bool:
        """
        Determine if the items should be displayed as a matrix.
        
        Args:
            items: The list or tuple to display
            matrix_mode: Force matrix display mode if provided
            
        Returns:
            Boolean indicating whether to use matrix display mode
        """
        return matrix_mode if matrix_mode is not None else self._is_matrix(items)

    def _generate_appropriate_html(self, items: Any, is_matrix: bool,
                                   ordered: bool, style: str, item_style: Optional[str],
                                   **inline_styles) -> str:
        """
        Generate the appropriate HTML based on whether the display is a matrix or list.
        
        Args:
            items: The list or tuple to display
            is_matrix: Whether to display as a matrix
            ordered: If True, use an ordered list (<ol>), otherwise unordered (<ul>)
            style: Named style for the list container
            item_style: Optional custom CSS style for list items
            **inline_styles: Additional CSS styles to apply to list items
            
        Returns:
            Generated HTML content
        """
        if is_matrix:
            return self._generate_matrix_html(items, style, **inline_styles)
        else:
            return self._generate_list_html(items, ordered, style, item_style, **inline_styles)

    @staticmethod
    def _display_html(html_content: str, items: Any) -> None:
        """
        Display HTML content safely, with fallback.
        
        Args:
            html_content: HTML content to display
            items: Original list/tuple (for fallback)
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. List will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render HTML content: {str(e)}")


class DictDisplayer(Displayer):
    """Displays Python dictionaries as HTML definition lists or tables."""

    def _generate_dict_html_dl(self, data: Dict, style: str,
                               key_style: Optional[str], value_style: Optional[str],
                               **inline_styles) -> str:
        """
        Recursively generate HTML definition list for a dictionary.
        
        Args:
            data: The dictionary to display
            style: Base style name for the list container
            key_style: Optional custom CSS for keys (<dt>)
            value_style: Optional custom CSS for values (<dd>)
            **inline_styles: Additional inline styles for list items
        
        Returns:
            HTML string for the definition list
        """
        # Get base container style
        dl_style = self.styles.get(style, self.styles['default'])
        
        # Process inline styles
        inline_style_string = self._process_inline_styles(inline_styles)
        
        # Set default styles for keys and values if not provided
        final_key_style = self._build_final_style(key_style or "font-weight: bold;", inline_style_string)
        final_value_style = self._build_final_style(value_style or "margin-left: 20px;", inline_style_string)
        
        # Start building HTML
        html_parts = [f'<dl style="{dl_style}">']
        
        # Process each key-value pair
        for key, value in data.items():
            key_content = str(key)
            value_content = self._format_value_content(value, style, key_style, value_style, **inline_styles)
            
            # Add the key-value pair to HTML
            html_parts.append(f'<dt style="{final_key_style}">{key_content}</dt>')
            html_parts.append(f'<dd style="{final_value_style}">{value_content}</dd>')
        
        # Close the definition list
        html_parts.append('</dl>')
        
        return ''.join(html_parts)
    
    def _build_final_style(self, base_style: str, inline_style: str) -> str:
        """
        Combine base style with inline styles.
        
        Args:
            base_style: The base style string
            inline_style: Additional inline styles to apply
            
        Returns:
            Combined style string
        """
        if not inline_style:
            return base_style
        return f"{base_style}; {inline_style}".strip('; ')
    
    def _format_value_content(self, value: Any, style: str, 
                              key_style: Optional[str], value_style: Optional[str],
                              **inline_styles) -> str:
        """
        Format the content of a value based on its type.
        
        Args:
            value: The value to format
            style: Base style name
            key_style: Style for keys in nested dictionaries
            value_style: Style for values in nested dictionaries
            **inline_styles: Additional inline styles
            
        Returns:
            Formatted HTML string for the value
        """
        if isinstance(value, dict):
            # Recursively handle nested dictionaries
            return self._generate_dict_html_dl(value, style, key_style, value_style, **inline_styles)
        elif isinstance(value, (list, tuple)):
            # For lists and tuples, convert to string for now
            # TODO: Implement proper ListDisplayer integration
            return str(value)
        else:
            # For simple values, convert to string
            return str(value)

    def display(self, data: Dict, *, style: str = 'default',
                key_style: Optional[str] = None,
                value_style: Optional[str] = None,
                **inline_styles) -> None:
        """
        Display a dictionary as an HTML definition list.
        
        Args:
            data: The dictionary to display
            style: Named style for the definition list container
            key_style: Optional custom CSS style for keys (<dt>)
            value_style: Optional custom CSS style for values (<dd>)
            **inline_styles: Additional CSS styles to apply to list items
        """
        if not isinstance(data, dict):
            raise TypeError("Input must be a dictionary")

        html_content = self._generate_dict_html_dl(data, style, key_style, value_style, **inline_styles)
        self._display_html(html_content, data)

    @staticmethod
    def _display_html(html_content: str, data: Dict) -> None:
        """
        Display HTML content safely, with fallback.
        
        Args:
            html_content: HTML content to display
            data: Original dictionary (for fallback)
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Dictionary will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render dictionary HTML: {str(e)}") from e


class MermaidDisplayer(Displayer):
    """Displays Mermaid diagrams using the Mermaid JavaScript library."""

    def display(self, diagram: str, *,
                style: str = 'default',
                theme: str = 'default',
                custom_css: Optional[Dict[str, str]] = None,
                **inline_styles) -> None:
        """
        Display a Mermaid diagram.
        
        Args:
            diagram: The Mermaid diagram definition/code or a file path
            style: Named style from the available styles
            theme: Mermaid theme ('default', 'forest', 'dark', 'neutral')
            custom_css: Optional dictionary mapping Mermaid CSS selectors to style properties
            **inline_styles: Additional CSS styles to apply to the container
            
        Raises:
            MermaidError: If there's an issue with the diagram
            StyleNotFoundError: If specified style is not found
            InvalidParameterError: If invalid parameters are provided
            DisplayEnvironmentError: If display environment is not available
            DisplayMethodError: If there's an issue with the display method
        """
        try:
            # Check if diagram is a file path and attempt to read from file
            diagram_content = self._read_diagram_from_path_or_use_directly(diagram)

            if not isinstance(diagram_content, str):
                received_type = type(diagram_content).__name__
                raise MermaidError(f"Diagram must be a string, received {received_type}")

            if style not in self.styles:
                raise StyleNotFoundError(style_name=style)

            if theme not in ['default', 'forest', 'dark', 'neutral']:
                raise InvalidParameterError("theme",
                                            "one of: 'default', 'forest', 'dark', 'neutral'",
                                            received=theme)

            base_style = self.styles.get(style)
            inline_style_string = self._process_inline_styles(inline_styles)
            container_style = f"{base_style} {inline_style_string}" if inline_style_string else base_style

            # Create HTML with Mermaid diagram
            html_content = self._generate_mermaid_html(diagram_content, container_style, theme, custom_css)

            # Display the diagram
            self._display_html(html_content)
        except (MermaidError, StyleNotFoundError, InvalidParameterError,
                DisplayEnvironmentError, HTMLGenerationError, ConversionError):
            # Pass through specific exceptions
            raise
        except Exception as e:
            # Wrap other exceptions with DisplayMethodError
            raise DisplayMethodError(
                method_name="display_mermaid",
                message=f"Error displaying Mermaid diagram: {str(e)}"
            )

    @staticmethod
    def _read_diagram_from_path_or_use_directly(diagram_input: str) -> str:
        """
        Check if input is a file path and read content if it is.
        
        Args:
            diagram_input: Either a Mermaid diagram string or a file path
            
        Returns:
            The Mermaid diagram content
            
        Raises:
            MermaidError: If there's an issue reading the file
        """
        # Skip empty strings
        if not diagram_input or not diagram_input.strip():
            return diagram_input

        # Check if diagram looks like a file path
        if (diagram_input.endswith('.md') or
                diagram_input.endswith('.mmd') or
                diagram_input.endswith('.mermaid') or
                ('/' in diagram_input or '\\' in diagram_input)):
            try:
                with open(diagram_input, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                # If it looks like a file path but reading fails, assume it's either
                # a diagram with slashes, or raise an error if it clearly ends with a file extension
                if (diagram_input.endswith('.md') or
                        diagram_input.endswith('.mmd') or
                        diagram_input.endswith('.mermaid')):
                    raise MermaidError(f"Failed to read Mermaid diagram from file: {diagram_input}. Error: {str(e)}")
                # Otherwise, treat it as a diagram string
                return diagram_input

        # If not a file path, return the original string
        return diagram_input

    def _generate_mermaid_html(self, diagram: str, container_style: str, theme: str,
                               custom_css: Optional[Dict[str, str]] = None) -> str:
        """
        Generate HTML for displaying a Mermaid diagram.
        
        Args:
            diagram: The Mermaid diagram definition/code
            container_style: CSS style for the container
            theme: Mermaid theme
            custom_css: Optional dictionary mapping Mermaid CSS selectors to style properties
            
        Returns:
            HTML content string
        """
        diagram_id = f"mermaid_{str(uuid.uuid4()).replace('-', '')}"

        # Prepare custom CSS if provided
        custom_css_string = ""
        if custom_css and isinstance(custom_css, dict):
            css_rules = []
            for selector, properties in custom_css.items():
                # Add a proper prefix for the current diagram if it doesn't already target .mermaid
                if not selector.startswith('.mermaid'):
                    prefixed_selector = f"#{diagram_id} {selector}"
                else:
                    prefixed_selector = f"#{diagram_id}{selector[8:]}"

                css_rules.append(f"{prefixed_selector} {{ {properties} }}")

            custom_css_string = f"<style>{' '.join(css_rules)}</style>"

        html = self._generate_html(diagram_id, container_style, custom_css_string, diagram, theme)
        return html

    def _generate_html(self, diagram_id: str, container_style: str, custom_css_string: str, diagram: str, theme: str) -> str:
        """
        Generate HTML for displaying a Mermaid diagram.
        
        Args:
            diagram_id: ID for the diagram container
            container_style: CSS style for the container
            custom_css_string: Custom CSS for the diagram
            diagram: The Mermaid diagram definition/code
            
        Returns:
            HTML content string
        """
        html = f"""
        <div style="{container_style}">
            {custom_css_string}
            <div class="mermaid" id="{diagram_id}">
            {diagram}
            </div>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <script>
                // Initialize Mermaid with specified theme
                mermaid.initialize({{ startOnLoad: true, theme: '{theme}' }});
                mermaid.run();
            </script>
        </div>
        """
        return html

    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content safely.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Mermaid diagram will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render Mermaid diagram: {str(e)}")


class MDDisplayer(Displayer):
    """Displays markdown content from URL or file path with read more/less functionality."""

    def display(self, source: str, *,
                is_url: bool = False,
                style: str = 'default',
                animate: Optional[str] = None,
                **inline_styles) -> None:
        """
        Display markdown content from a URL or file with syntax highlighting and read more/less functionality.
        
        Args:
            source: The URL or file path of the markdown file to display
            is_url: If True, treat source as a URL; if False, treat as a file path
            style: Named style from the available styles
            animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
            **inline_styles: Additional CSS styles to apply to the container
            
        Raises:
            StyleNotFoundError: If specified style is not found
            InvalidParameterError: If source is invalid
            MarkdownSourceError: If the markdown source (file or URL) cannot be accessed
            MarkdownParsingError: If the markdown content cannot be parsed
            MarkdownRenderingError: If the markdown content cannot be rendered
            AnimationError: If the specified animation is invalid
            IPythonNotAvailableError: If display environment is not available
        """
        try:
            if not isinstance(source, str) or not source:
                received_type = type(source).__name__
                raise InvalidParameterError("source", "non-empty string", received=received_type)

            if style not in self.styles:
                raise StyleNotFoundError(style_name=style)

            base_style = self.styles.get(style)
            inline_style_string = self._process_inline_styles(inline_styles)
            container_style = f"{base_style} {inline_style_string}" if inline_style_string else base_style

            # Process animation class if specified
            animation_class = process_animation_class(animate)
            class_attr = f'class="{animation_class}"' if animation_class else ''

            # Generate HTML for markdown display
            html_content = self._generate_markdown_html(source, is_url, container_style, class_attr)

            # Include Animate.css CDN if animation is specified
            animate_css_link = self._load_animate_css() if animate else ''
            html_content = f"{animate_css_link}{html_content}" if animate else html_content

            # Display the markdown content
            self._display_html(html_content)
        except (StyleNotFoundError, InvalidParameterError, AnimationError,
                MarkdownSourceError, MarkdownParsingError, MarkdownRenderingError):
            # Pass through specific exceptions
            raise
        except Exception as e:
            # Wrap other exceptions with DisplayMethodError
            raise DisplayMethodError(
                method_name="display_md",
                message=f"Error displaying markdown content: {str(e)}"
            )

    def _generate_markdown_html(self, source: str, is_url: bool, container_style: str, class_attr: str) -> str:
        """
        Generate HTML for displaying markdown content with read more/less functionality.
        
        Args:
            source: URL or file path to markdown content
            is_url: Whether source is a URL or file path
            container_style: CSS style for the container
            class_attr: Optional class attribute for animations
            
        Returns:
            HTML content string
            
        Raises:
            MarkdownSourceError: If the markdown source cannot be accessed
            MarkdownParsingError: If the markdown content cannot be parsed
        """
        markdown_id = self._generate_markdown_id()
        container_id = f"container_{markdown_id}"
        toggle_id = f"toggle_{markdown_id}"
        content_id = f"content_{markdown_id}"

        # JavaScript logic for fetching content based on whether source is URL or file content
        if is_url:
            # For URL, fetch the content
            js_logic = self._generate_js_logic_for_url(source)
        else:
            # For file, try to read the content
            try:
                if not os.path.exists(source):
                    raise MarkdownSourceError(source=source, is_url=False,
                                              message=f"File not found at {source}")

                # Read file content
                try:
                    with open(source, 'r', encoding='utf-8') as file:
                        markdown_content = file.read()
                except Exception as e:
                    raise MarkdownSourceError(source=source, is_url=False,
                                              message=f"Error reading file: {str(e)}")

                # Escape quotes and newlines for JavaScript string
                try:
                    markdown_content = markdown_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                except Exception as e:
                    raise MarkdownParsingError(f"Error processing markdown content: {str(e)}")

                js_logic = self._generate_js_logic_for_file(markdown_content)
            except (MarkdownSourceError, MarkdownParsingError):
                raise
            except Exception as e:
                raise MarkdownParsingError(f"Error processing markdown file: {str(e)}")

        html = self._generate_html(container_id, container_style, class_attr, content_id, toggle_id, js_logic)
        return html

    @staticmethod
    def _generate_markdown_id() -> str:
        """
        Generate a unique ID for the markdown container.
        
        Returns:
            Unique ID for the markdown container
        """
        return f"markdown_{str(uuid.uuid4()).replace('-', '')}"

    @staticmethod
    def _generate_js_logic_for_url(source: str) -> str:
        """
        Generate JavaScript logic for fetching markdown content from a URL.
        
        Args:
            source: URL of the markdown content
            
        Returns:
            JavaScript logic string
        """
        logic = f"""
            fetch("{source}")
              .then(response => {{
                if (!response.ok) {{
                  throw new Error('Network response was not ok: ' + response.status);
                }}
                return response.text();
              }})
              .then(text => {{
                contentDiv.innerHTML = marked.parse(text);
                const preElements = contentDiv.querySelectorAll('pre');
                preElements.forEach(pre => {{
                  pre.classList.add('line-numbers');
                  const code = pre.querySelector('code');
                  if (code) {{
                    if (!Array.from(code.classList).some(cls => cls.startsWith('language-'))) {{
                      code.classList.add('language-markdown');
                    }}
                  }}
                }});
                Prism.highlightAll();
                toggleBtn.style.display = 'inline-block';
              }})
              .catch(error => {{
                contentDiv.innerHTML = '<div class="error-message" style="color: #e53e3e; padding: 10px; background-color: #fff5f5; border-left: 4px solid #e53e3e; margin: 10px 0;">Error loading content: ' + error.message + '</div>';
              }});
            """
        return logic

    @staticmethod
    def _generate_js_logic_for_file(markdown_content: str) -> str:
        """
        Generate JavaScript logic for displaying markdown content with read more/less functionality.
        
        Args:
            markdown_content: Content of the markdown file
            
        Returns:
            JavaScript logic string
        """
        logic = f"""
                // Content is passed directly as a variable for file-based input
                const markdownText = "{markdown_content}";
                try {{
                    contentDiv.innerHTML = marked.parse(markdownText);
                    const preElements = contentDiv.querySelectorAll('pre');
                    preElements.forEach(pre => {{
                      pre.classList.add('line-numbers');
                      const code = pre.querySelector('code');
                      if (code) {{
                        if (!Array.from(code.classList).some(cls => cls.startsWith('language-'))) {{
                          code.classList.add('language-markdown');
                        }}
                      }}
                    }});
                    Prism.highlightAll();
                    toggleBtn.style.display = 'inline-block';
                }} catch (error) {{
                    contentDiv.innerHTML = '<div class="error-message" style="color: #e53e3e; padding: 10px; background-color: #fff5f5; border-left: 4px solid #e53e3e; margin: 10px 0;">Error parsing markdown: ' + error.message + '</div>';
                }}
                """
        return logic

    @staticmethod
    def _generate_html(container_id: str, container_style: str, class_attr: str, content_id: str, toggle_id: str,
                       js_logic: str) -> str:
        """
        Generate HTML for displaying markdown content with read more/less functionality.
        
        Args:
            container_id: ID for the container element
            container_style: CSS style for the container
            class_attr: Optional class attribute for animations
            content_id: ID for the content element
            toggle_id: ID for the toggle button
            js_logic: JavaScript logic for the toggle button
            
        Returns:
            HTML content string
        """
        html = f"""
        <div id="{container_id}" {class_attr} style="{container_style}">
          <div style="max-width: 800px; margin-left: 0;">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
            <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet" />
            <style>
              .markdown-body {{
                overflow: hidden;
                display: -webkit-box;
                -webkit-line-clamp: 4;
                -webkit-box-orient: vertical;
                text-overflow: ellipsis;
                transition: all 0.3s ease;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
              }}
              .markdown-body.expanded {{
                -webkit-line-clamp: unset;
                overflow: visible;
              }}
              .read-more-btn {{
                color: #0366d6;
                cursor: pointer;
                margin-top: 10px;
                display: inline-block;
                font-weight: 500;
              }}
              .error-message {{
                border-radius: 4px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
              }}
              table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
                overflow-x: auto;
                display: block;
                color: #333333;
              }}
              table th, table td {{
                border: 1px solid rgba(100, 116, 139, 0.2);
                padding: 12px 16px;
                text-align: left;
                transition: background-color 0.3s, color 0.3s;
              }}
              table th {{
                background-color: var(--th-bg, #f1f5f9);
                color: var(--th-text, #0f172a);
                font-weight: 600;
                font-size: 14px;
              }}
              table tr:nth-child(even) {{
                background-color: var(--even-bg, #f8f9fa);
              }}
              @media (prefers-color-scheme: dark) {{
                table th {{
                  background-color: var(--th-bg-dark, #1e293b);
                  color: var(--th-text-dark, #f8fafc);
                }}
                table td {{
                  color: #e2e8f0;
                  background-color: #0f172a;
                  border-color: rgba(255, 255, 255, 0.1);
                }}
                table tr:nth-child(even) {{
                  background-color: #1e293b;
                }}
              }}
              pre {{
                margin: 1em 0;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
              }}
              :not(pre) > code {{
                font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace;
                background-color: rgba(175, 184, 193, 0.2);
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-size: 85%;
                color: #24292f;
              }}
              .line-numbers .line-numbers-rows {{
                border-right: 1px solid #ddd;
              }}
            </style>
            <div id="{content_id}" class="markdown-body">Loading...</div>
            <span id="{toggle_id}" class="read-more-btn" style="display: none;">Read more</span>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/components/prism-core.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/plugins/autoloader/prism-autoloader.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
            <script>
              const contentDiv = document.getElementById('{content_id}');
              const toggleBtn = document.getElementById('{toggle_id}');
              let expanded = false;
              
              marked.setOptions({{
                highlight: function(code, lang) {{
                  return code;
                }},
                langPrefix: 'language-'
              }});
              
              {js_logic}
              
              toggleBtn.addEventListener('click', () => {{
                expanded = !expanded;
                contentDiv.classList.toggle('expanded');
                toggleBtn.textContent = expanded ? 'Read less' : 'Read more';
              }});
            </script>
          </div>
        </div>
        """
        return html

    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content safely.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            MarkdownRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Markdown content will not be rendered properly."
            )
        except Exception as e:
            raise MarkdownRenderingError(f"Failed to render markdown content: {str(e)}")


class ProgressDisplayer(Displayer):
    """Displays customizable progress bars using JavaScript or SVG."""

    def __init__(self, styles: Dict[str, str]):
        """Initialize a progress displayer with styles."""
        super().__init__(styles)

    def display(self, total: Optional[int] = None, *,
                desc: str = "",
                style: str = "default",
                color: str = "#3498DB",
                height: str = "20px",
                animated: bool = True,
                **inline_styles) -> str:
        """
        Display a progress bar with either determined or undetermined progress.
        
        Args:
            total: Total number of steps (None for undetermined progress)
            desc: Description text to display with the progress bar
            style: Named style from available styles
            color: Color of the progress bar
            height: Height of the progress bar
            animated: Whether to animate the progress bar
            **inline_styles: Additional CSS styles to apply
            
        Returns:
            Progress bar ID that can be used to update the progress
        """
        # Generate a unique ID for this progress bar
        progress_id = f"progress_{str(uuid.uuid4()).replace('-', '')}"
        container_id = f"container_{progress_id}"

        # Process styles
        base_style = self.styles.get(style, self.styles['default'])
        inline_style_string = self._process_inline_styles(inline_styles)

        # Create the progress bar HTML
        if total is None:
            # Undetermined progress (loading animation)
            html_content = self._create_undetermined_progress(
                progress_id, container_id, desc, base_style,
                inline_style_string, color, height, animated
            )
        else:
            # Determined progress (with total)
            html_content = self._create_determined_progress(
                progress_id, container_id, desc, base_style,
                inline_style_string, color, height, animated, total
            )

        # Display the progress bar
        self._display_html(html_content)

        return progress_id

    def update(self, progress_id: str, value: int, total: Optional[int] = None) -> None:
        """
        Update the progress of a displayed progress bar.
        
        Args:
            progress_id: ID of the progress bar to update
            value: Current progress value
            total: Optional new total (if changed)
            
        Raises:
            DisplayUpdateError: If update fails
            IPythonNotAvailableError: If IPython environment is not detected
            InvalidParameterError: If input parameters are invalid
        """
        # Validate inputs
        self._validate_update_parameters(progress_id, value, total)
        
        # Generate JavaScript code for the update
        js_code = self._generate_progress_update_js(progress_id, value, total)
        
        # Execute the JavaScript
        try:
            ip_display(Javascript(js_code))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Progress update will not be applied."
            )
        except Exception as e:
            raise DisplayUpdateError(
                element_id=progress_id,
                message=f"Failed to update progress bar: {str(e)}"
            ) from e
    
    def _validate_update_parameters(self, progress_id: str, value: int, total: Optional[int]) -> None:
        """
        Validate parameters for progress bar update.
        
        Args:
            progress_id: ID of the progress bar
            value: Current progress value
            total: Optional new total
            
        Raises:
            InvalidParameterError: If any parameter is invalid
        """
        if not isinstance(progress_id, str):
            raise InvalidParameterError("progress_id", "string", received=type(progress_id).__name__)

        if not isinstance(value, int):
            raise InvalidParameterError("value", "integer", received=type(value).__name__)

        if total is not None and not isinstance(total, int):
            raise InvalidParameterError("total", "integer or None", received=type(total).__name__)
    
    def _generate_progress_update_js(self, progress_id: str, value: int, total: Optional[int]) -> str:
        """
        Generate JavaScript code to update a progress bar.
        
        Args:
            progress_id: ID of the progress bar
            value: Current progress value
            total: Optional new total
            
        Returns:
            JavaScript code as string
        """
        container_id = f"container_{progress_id}"
        label_id = f"label_{progress_id}"
        
        if total is not None and value >= total:
            # For completed progress, stop animation and show 100%
            return self._generate_completion_js(progress_id, label_id, total, value)
        elif total is not None:
            # Regular update with new total
            return self._generate_update_with_new_total_js(progress_id, label_id, total, value)
        else:
            # Regular update without changing total
            return self._generate_update_js(progress_id, label_id, value)
    
    @staticmethod
    def _generate_completion_js(progress_id: str, label_id: str, total: int, value: int) -> str:
        """Generate JavaScript for completed progress bar."""
        return f"""
        (function() {{
            var progressBar = document.getElementById('{progress_id}');
            var container = document.getElementById('container_{progress_id}');
            if (progressBar) {{
                // Handle both determined and undetermined progress bars
                if (progressBar.tagName === 'PROGRESS') {{
                    progressBar.max = {total};
                    progressBar.value = {value};
                    var label = document.getElementById('{label_id}');
                    if (label) {{
                        label.textContent = '100%';
                    }}
                }} else {{
                    // This is an undetermined progress bar, replace with completed state
                    progressBar.style.animation = 'none';
                    progressBar.style.background = '#27AE60';  // Success green color
                    var label = document.createElement('span');
                    label.textContent = 'Complete';
                    label.style.position = 'absolute';
                    label.style.top = '50%';
                    label.style.left = '50%';
                    label.style.transform = 'translate(-50%, -50%)';
                    label.style.color = 'white';
                    label.style.fontWeight = 'bold';
                    label.style.fontSize = '12px';
                    progressBar.appendChild(label);
                }}
            }}
        }})();
        """
    
    @staticmethod
    def _generate_update_with_new_total_js(progress_id: str, label_id: str, total: int, value: int) -> str:
        """Generate JavaScript for updating progress with a new total."""
        return f"""
        (function() {{
            var progressBar = document.getElementById('{progress_id}');
            if (progressBar) {{
                progressBar.max = {total};
                progressBar.value = {value};
                var percent = Math.round(({value} / {total}) * 100);
                var label = document.getElementById('{label_id}');
                if (label) {{
                    label.textContent = percent + '%';
                }}
            }}
        }})();
        """
    
    @staticmethod
    def _generate_update_js(progress_id: str, label_id: str, value: int) -> str:
        """Generate JavaScript for updating progress without changing total."""
        return f"""
        (function() {{
            var progressBar = document.getElementById('{progress_id}');
            if (progressBar) {{
                progressBar.value = {value};
                var percent = Math.round(({value} / progressBar.max) * 100);
                var label = document.getElementById('{label_id}');
                if (label) {{
                    label.textContent = percent + '%';
                }}
            }}
        }})();
        """

    @staticmethod
    def _create_determined_progress(progress_id: str, container_id: str,
                                    desc: str, base_style: str, inline_style_string: str,
                                    color: str, height: str, animated: bool, total: int) -> str:
        """
        Create HTML for a determined progress bar.
        
        Args:
            progress_id: Unique ID for the progress element
            container_id: Unique ID for the container element
            desc: Description text
            base_style: Base CSS style
            inline_style_string: Additional inline CSS
            color: Progress bar color
            height: Progress bar height
            animated: Whether to animate
            total: Total number of steps
            
        Returns:
            HTML string for the progress bar
        """
        # Define CSS styles
        container_style = f"display: flex; align-items: center; margin: 10px 0; {base_style}"
        if inline_style_string:
            container_style = f"{container_style}; {inline_style_string}"

        desc_style = "margin-right: 10px; min-width: 120px; color: #3498DB;"
        progress_container_style = "flex-grow: 1; position: relative; height: 100%;"
        progress_style = f"""
            -webkit-appearance: none;
            appearance: none;
            width: 100%;
            height: {height};
            border: none;
            border-radius: 4px;
            background-color: #f0f0f0;
        """

        progress_value_style = f"""
            ::-webkit-progress-value {{
                background-color: {color};
                border-radius: 4px;
                transition: width 0.3s ease;
            }}
            ::-moz-progress-bar {{
                background-color: {color};
                border-radius: 4px;
                transition: width 0.3s ease;
            }}
        """

        label_style = """
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: bold;
            color: #333;
            text-shadow: 0 0 2px white, 0 0 2px white, 0 0 2px white, 0 0 2px white;
        """

        # Build HTML
        html = f"""
        <div id="{container_id}" style="{container_style}">
            <span style="{desc_style}">{desc}</span>
            <div style="{progress_container_style}">
                <progress id="{progress_id}" value="0" max="{total}" style="{progress_style}"></progress>
                <style>{progress_value_style}</style>
                <span id="label_{progress_id}" style="{label_style}">0%</span>
            </div>
        </div>
        """

        return html

    def _create_undetermined_progress(self, progress_id: str, container_id: str,
                                      desc: str, base_style: str, inline_style_string: str,
                                      color: str, height: str, animated: bool) -> str:
        """
        Create HTML for an undetermined progress bar (loading animation).
        
        Args:
            progress_id: Unique ID for the progress element
            container_id: Unique ID for the container element
            desc: Description text
            base_style: Base CSS style
            inline_style_string: Additional inline CSS
            color: Progress bar color
            height: Progress bar height
            animated: Whether to animate
            
        Returns:
            HTML string for the progress bar
        """
        # Define CSS styles
        container_style = f"display: flex; align-items: center; margin: 10px 0; {base_style}"
        if inline_style_string:
            container_style = f"{container_style}; {inline_style_string}"

        desc_style = "margin-right: 10px; min-width: 120px; color: #3498DB;"
        progress_container_style = "flex-grow: 1; position: relative; height: 100%;"

        # More elegant gradient with lighter colors for better visual effect
        lighter_color = self._lighten_color(color, 0.7)
        mid_color = self._lighten_color(color, 0.4)

        loading_style = f"""
            width: 100%;
            height: {height};
            position: relative;
            background: linear-gradient(90deg, 
                {lighter_color} 0%, 
                {color} 25%, 
                {mid_color} 50%, 
                {color} 75%, 
                {lighter_color} 100%);
            background-size: 400% 100%;
            border-radius: 4px;
            animation: loading_{progress_id} 2s ease infinite;
            overflow: hidden;
        """

        animation_style = f"""
            @keyframes loading_{progress_id} {{
                0% {{
                    background-position: 100% 50%;
                }}
                100% {{
                    background-position: 0% 50%;
                }}
            }}
        """

        shine_effect = f"""
            position: absolute;
            content: '';
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,255,255,0.3), 
                transparent);
            animation: shine_{progress_id} 1.5s infinite;
        """

        shine_animation = f"""
            @keyframes shine_{progress_id} {{
                0% {{
                    transform: translateX(-100%);
                }}
                100% {{
                    transform: translateX(100%);
                }}
            }}
        """

        # Build HTML with a more structured approach that's easier to modify via JS
        html = f"""
        <div id="{container_id}" style="{container_style}">
            <span style="{desc_style}">{desc}</span>
            <div style="{progress_container_style}">
                <div id="{progress_id}" style="{loading_style}">
                    <div style="{shine_effect}"></div>
                </div>
                <style>
                    {animation_style}
                    {shine_animation}
                </style>
            </div>
        </div>
        """

        return html

    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content safely.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            ip_display(HTML(html_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Progress bar will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render progress bar HTML: {str(e)}") from e

    @staticmethod
    def _lighten_color(color: str, factor: float = 0.5) -> str:
        """
        Lighten a hex color by the given factor.
        
        Args:
            color: Hex color string (#RRGGBB)
            factor: Factor to lighten (0-1, where 1 is white)
            
        Returns:
            Lightened hex color
        """
        # Handle colors with or without #
        if color.startswith('#'):
            color = color[1:]

        # Handle both 3 and 6 digit hex
        if len(color) == 3:
            r = int(color[0] + color[0], 16)
            g = int(color[1] + color[1], 16)
            b = int(color[2] + color[2], 16)
        else:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

        # Lighten
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"


class ButtonDisplayer(Displayer):
    """
    Displays interactive buttons with customizable callbacks and event handling.
    """

    def __init__(self, styles: Dict[str, str]):
        """
        Initialize a button displayer with styles.
        
        Args:
            styles: Dictionary of named styles
        """
        super().__init__(styles)
        # Store registered callbacks to keep references
        self._callback_registry = {}

    # noinspection PyUnresolvedReferences
    def display(self, text: str, *,
                style: str = 'default',
                on_click: Optional[Callable] = None,
                status_display: bool = True,
                hover_effect: bool = True,
                width: str = 'auto',
                height: str = 'auto',
                enabled: bool = True,
                animate: Optional[str] = None,
                position: Literal['left', 'mid', 'right'] = 'left',
                **inline_styles) -> str:
        """
        Display an interactive button with various events and callbacks.
        
        Args:
            text: Button text
            style: Named style from available styles
            on_click: Python function to call when button is clicked
            status_display: Whether to show a status display area below button
            hover_effect: Whether to enable hover effects
            width: Button width (CSS value)
            height: Button height (CSS value)
            enabled: Whether the button is initially enabled
            animate: Animation effect from Animate.css
            position: Button alignment ('left', 'mid', 'right')
            **inline_styles: Additional CSS styles to apply
            
        Returns:
            Button ID for reference
            
        Raises:
            ButtonError: If there's an issue with the button setup
            StyleNotFoundError: If specified style is not found
            ButtonCallbackError: If there's an issue with the callback
        """
        try:
            # Generate unique IDs
            button_id = f"colab_print_button_{uuid.uuid4().hex[:8]}"
            container_id = f"button_container_{uuid.uuid4().hex[:8]}"
            status_id = f"status_display_{uuid.uuid4().hex[:8]}"

            # Validate and get style
            self._validate_style(style)
            final_style = self._prepare_button_style(style, inline_styles)
            
            # Process animation
            class_attr = self._prepare_animation(animate)
            
            # Register callback if provided
            callback_id = self._register_callback(button_id, on_click)

            # Create HTML and JavaScript
            html_content = self._generate_button_html(
                button_id=button_id,
                container_id=container_id,
                status_id=status_id,
                text=text,
                style=final_style,
                status_display=status_display,
                width=width,
                height=height,
                enabled=enabled,
                class_attr=class_attr,
                position=position
            )

            js_content = self._generate_button_js(
                button_id=button_id,
                status_id=status_id,
                on_click=bool(on_click),
                callback_id=callback_id,
                hover_effect=hover_effect,
                status_display=status_display,
                enabled=enabled
            )

            # Display content
            self._display_html_and_js(html_content, js_content)
            return button_id

        except (StyleNotFoundError, ButtonCallbackError):
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise ButtonError(f"Error creating button: {str(e)}")
    
    def _validate_style(self, style: str) -> None:
        """
        Validate that the requested style exists.
        
        Args:
            style: Style name to validate
            
        Raises:
            StyleNotFoundError: If style doesn't exist
        """
        if style not in self.styles:
            raise StyleNotFoundError(style_name=style)
    
    def _prepare_button_style(self, style: str, inline_styles: Dict[str, str]) -> str:
        """
        Prepare the final button style by combining base style with inline styles.
        
        Args:
            style: Named style from available styles
            inline_styles: Additional CSS styles to apply
            
        Returns:
            Final CSS style string
        """
        base_style = self.styles.get(style)
        inline_style_string = self._process_inline_styles(inline_styles)
        return f"{base_style} {inline_style_string}" if inline_style_string else base_style
    
    def _prepare_animation(self, animate: Optional[str]) -> str:
        """
        Process animation class if specified.
        
        Args:
            animate: Animation effect name
            
        Returns:
            Class attribute string for HTML
        """
        animation_class = process_animation_class(animate)
        return f'class="{animation_class}"' if animation_class else ''
    
    def _register_callback(self, button_id: str, on_click: Optional[Callable]) -> Optional[str]:
        """
        Register callback function for the button if provided.
        
        Args:
            button_id: Unique ID for the button
            on_click: Callback function to register
            
        Returns:
            Callback ID or None if no callback
            
        Raises:
            ButtonCallbackError: If callback registration fails
        """
        if not on_click:
            return None
            
        try:
            # Try importing and using Google Colab's output module
            from google.colab import output
            callback_name = f"{button_id}_callback"
            callback_id = output.register_callback(callback_name, on_click)
            # Store reference to prevent garbage collection
            self._callback_registry[callback_id] = on_click
            return callback_id
        except (ImportError, AttributeError) as e:
            raise ButtonCallbackError(
                callback_name="on_click",
                message="Google Colab environment required for callbacks. "
                        f"Failed to register callback: {str(e)}"
            )

    # noinspection RegExpAnonymousGroup
    @staticmethod
    def _generate_button_html(button_id: str, container_id: str, status_id: str,
                              text: str, style: str, status_display: bool,
                              width: str, height: str, enabled: bool, class_attr: str,
                              position: Literal['left', 'mid', 'right'] = 'left') -> str:
        """
        Generate HTML for button and container.
        
        Args:
            button_id: Unique ID for button
            container_id: Unique ID for container
            status_id: Unique ID for status display
            text: Button text
            style: Button style
            status_display: Whether to include status display
            width: Button width
            height: Button height
            enabled: Whether button is enabled
            class_attr: Class attribute for animation
            position: Button alignment ('left', 'mid', 'right')
            
        Returns:
            HTML string for button
        """
        # Extract basic color from style for status display
        base_color = "#3498db"  # Default blue color
        color_match = re.search(r'background-color:\s*([^;]+)', style)
        if color_match:
            base_color = color_match.group(1).strip()

        # Button opacity based on enabled state
        opacity = "1.0" if enabled else "0.6"
        cursor = "pointer" if enabled else "not-allowed"

        # Base button style
        button_style = f"{style}; width: {width}; height: {height}; opacity: {opacity}; cursor: {cursor};"

        # Map position to text-align value
        text_align = {
            'left': 'left',
            'mid': 'center',
            'right': 'right'
        }[position]

        # Prepare HTML parts
        html_parts = [
            f'<div id="{container_id}" style="margin: 20px 0; text-align: {text_align};">',
            f'  <button id="{button_id}" style="{button_style}" {class_attr} {"disabled" if not enabled else ""}>',
            f'    {html.escape(text)}',
            f'  </button>'
        ]

        # Add status display if requested
        if status_display:
            html_parts.extend([
                f'  <div id="{status_id}" style="',
                f'    margin-top: 15px;',
                f'    padding: 10px;',
                f'    border: 1px solid #ddd;',
                f'    border-radius: 4px;',
                f'    min-height: 100px;',
                f'    max-height: 150px;',
                f'    overflow-y: auto;',
                f'    background-color: #f9f9f9;',
                f'    text-align: left;',  # Status display always left-aligned for readability
                f'  ">',
                f'    <p>Event log will appear here...</p>',
                f'  </div>'
            ])

        # Close container
        html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _generate_button_js(self, button_id: str, status_id: str,
                            on_click: bool, callback_id: Optional[str],
                            hover_effect: bool, status_display: bool,
                            enabled: bool) -> str:
        """
        Generate JavaScript for button behavior.
        """
        js_parts = [
            self._get_js_button_creation(button_id),
        ]

        if status_display:
            js_parts.append(self._get_js_status(status_id))

        if enabled:
            if hover_effect:
                js_parts.append(self._get_js_hover_effect(status_display))

            js_parts.append(self._get_press_effect(status_display))

            if on_click and callback_id:
                js_parts.append(self._get_js_click_effect(callback_id, status_display))
            else:
                js_parts.append(self._get_js_basic_click_effect(status_display))

            js_parts.append(self._get_js_focuse_effect(status_display))

        if status_display:
            js_parts.append('logEvent("Initialization", "Button is ready");')

        return "\n".join(js_parts)

    @staticmethod
    def _get_js_button_creation(button_id: str) -> str:
        """Generate JavaScript for button creation."""
        button = """// Get references to elements
    const button = document.getElementById("{button_id}");""".format(button_id=button_id)
        return button

    @staticmethod
    def _get_js_focuse_effect(status_display: bool) -> str:
        effect = """// OnFocus (focus event)
    button.addEventListener("focus", function(e) {{
        {log_focus}
        button.style.boxShadow = "0 0 0 3px rgba(52, 152, 219, 0.5)";
    }});

    // OnBlur (blur event)
    button.addEventListener("blur", function(e) {{
        {log_blur}
        button.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
    }});

    // OnKeyDown (keydown event when button is focused)
    button.addEventListener("keydown", function(e) {{
        {log_key_down}
        if (e.key === "Enter" || e.key === " ") {{
            button.style.boxShadow = "0 2px 3px rgba(0,0,0,0.1)";
            button.style.transform = "translateY(2px)";
        }}
    }});

    // OnKeyUp (keyup event when button is focused)
    button.addEventListener("keyup", function(e) {{
        {log_key_up}
        if (e.key === "Enter" || e.key === " ") {{
            button.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
            button.style.transform = "scale(1.0)";
            button.click();
        }}
    }});""".format(
            log_focus='logEvent("OnFocus", "Button received focus");' if status_display else "",
            log_blur='logEvent("OnBlur", "Button lost focus");' if status_display else "",
            log_key_down='logEvent("OnKeyDown", `Key pressed: ${e.key}`);' if status_display else "",
            log_key_up='logEvent("OnKeyUp", `Key released: ${e.key}`);' if status_display else ""
        )
        return effect

    @staticmethod
    def _get_js_basic_click_effect(status_display: bool) -> str:
        """Generate JavaScript for basic click effect."""
        base = """// OnClick (basic)
    button.addEventListener("click", function(e) {{
        {log_click}
    }});""".format(
            log_click='logEvent("OnClick", "Button was clicked!");' if status_display else ""
        )
        return base

    @staticmethod
    def _get_js_click_effect(callback_id: Optional[str], status_display: bool) -> str:
        """"Generate JavaScript for click effect."""

        effect = """// OnClick with Python callback
    button.addEventListener("click", function(e) {{
        {log_click}
        
        // Call the Python function
        google.colab.kernel.invokeFunction("{callback_id}", [], {{}})
        .then(function(result) {{
            {log_result}
            if (result.data["text/plain"] && result.data["text/plain"].includes("__UPDATE_BUTTON_TEXT__:")) {{
                const newText = result.data["text/plain"]
                                    .split("__UPDATE_BUTTON_TEXT__:")[1]
                                    .trim().replace(/^[\\'"](.+)[\\'"]$/, "$1");
                button.textContent = newText;
            }}
        }})
        .catch(function(error) {{
            {log_error}
        }});
    }});""".format(
            log_click='logEvent("OnClick", "Button was clicked!");' if status_display else "",
            callback_id=callback_id,
            log_result='logEvent("PythonCallback", `Returned: ${result.data["text/plain"]}`);' if status_display else "",
            log_error='logEvent("Error", `Python callback error: ${error}`);' if status_display else ""
        )

        return effect

    @staticmethod
    def _get_press_effect(status_display: bool) -> str:
        """"Generate JavaScript for press effect."""

        effect = """// OnPressDown (mousedown event)
    button.addEventListener("mousedown", function(e) {{
        {log_press_down}
        button.style.boxShadow = "0 2px 3px rgba(0,0,0,0.1)";
        button.style.transform = "translateY(2px)";
    }});

    // OnPressUp (mouseup event)
    button.addEventListener("mouseup", function(e) {{
        {log_press_up}
        button.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
        button.style.transform = "scale(1.0)";
    }});""".format(
            log_press_down='logEvent("OnPressDown", `at position (${e.offsetX}, ${e.offsetY})`);' if status_display else "",
            log_press_up='logEvent("OnPressUp");' if status_display else ""
        )

        return effect

    @staticmethod
    def _get_js_hover_effect(status_display: bool) -> str:
        """"Generate JavaScript for hover effect."""
        
        effect = """// OnHoverEntering (mouseenter event)
    button.addEventListener("mouseenter", function(e) {{
        {log_hover_enter}
        button.style.transform = "scale(1.05)";
        button.style.boxShadow = "0 6px 8px rgba(0,0,0,0.15)";
    }});

    // OnHoverExit (mouseleave event)
    button.addEventListener("mouseleave", function(e) {{
        {log_hover_exit}
        button.style.transform = "scale(1.0)";
        button.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
    }});""".format(
            log_hover_enter='logEvent("OnHoverEntering");' if status_display else "",
            log_hover_exit='logEvent("OnHoverExit");' if status_display else ""
        )

        return effect

    @staticmethod
    def _get_js_status(status_id: str) -> str:
        """"Generate JavaScript for status display."""
        status = """const status = document.getElementById("{status_id}");

    // Function to log events to status display
    function logEvent(eventName, details = "") {{
        const logEntry = document.createElement("p");
        logEntry.style.margin = "5px 0";
        logEntry.innerHTML = `<strong>${{eventName}}</strong>: ${{new Date().toLocaleTimeString()}} ${{details}}`;

        // Prepend to show newest events at the top
        status.insertBefore(logEntry, status.firstChild);

        // Limit number of entries
        if (status.children.length > 10) {{
            status.removeChild(status.lastChild);
        }}
    }}

    // Clear initial message
    status.innerHTML = "";""".format(status_id=status_id)
        return status

    @staticmethod
    def _display_html_and_js(html_content: str, js_content: str) -> None:
        """
        Display both HTML and JavaScript.
        
        Args:
            html_content: HTML content to display
            js_content: JavaScript content to execute
            
        Raises:
            IPythonNotAvailableError: If IPython environment is not detected
            HTMLRenderingError: If content cannot be rendered
        """
        try:
            # Display HTML first
            ip_display(HTML(html_content))

            # Then execute JavaScript
            ip_display(Javascript(js_content))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Button will not be rendered properly."
            )
        except Exception as e:
            raise HTMLRenderingError(f"Failed to render button: {str(e)}")

    @staticmethod
    def update_button_text(button_id: str, new_text: str) -> None:
        """
        Update the text of a button using JavaScript.
        
        Args:
            button_id: ID of the button to update
            new_text: New text for the button
            
        Raises:
            ButtonError: If the button cannot be updated
            IPythonNotAvailableError: If IPython environment is not detected
        """
        try:
            # JavaScript to update button text
            js_code = f"""
            const button = document.getElementById("{button_id}");
            if (button) {{
                button.textContent = "{html.escape(new_text)}";
            }} else {{
                console.error("Button with ID {button_id} not found");
            }}
            """

            # Execute JavaScript
            ip_display(Javascript(js_code))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Button text cannot be updated."
            )
        except Exception as e:
            raise ButtonError(f"Failed to update button text: {str(e)}")

    @staticmethod
    def enable_button(button_id: str, enabled: bool = True) -> None:
        """
        Enable or disable a button using JavaScript.
        
        Args:
            button_id: ID of the button to update
            enabled: Whether to enable (True) or disable (False) the button
            
        Raises:
            ButtonError: If the button cannot be updated
            IPythonNotAvailableError: If IPython environment is not detected
        """
        try:
            # JavaScript to update button state
            js_code = f"""
            const button = document.getElementById("{button_id}");
            if (button) {{
                button.disabled = {str(not enabled).lower()};
                button.style.opacity = {1.0 if enabled else 0.6};
                button.style.cursor = "{("pointer" if enabled else "not-allowed")}";
            }} else {{
                console.error("Button with ID {button_id} not found");
            }}
            """

            # Execute JavaScript
            ip_display(Javascript(js_code))
        except NameError:
            raise IPythonNotAvailableError(
                "IPython environment not detected. Button state cannot be updated."
            )
        except Exception as e:
            raise ButtonError(f"Failed to update button state: {str(e)}")


class PDFDisplayer(Displayer):
    """
    Component for displaying PDF files in Jupyter notebooks.
    
    This displayer enables interactive display of PDF documents from file paths,
    URLs, or through a file picker interface. It provides a viewer with page
    navigation controls and responsive design.
    """

    def __init__(self, styles: Dict[str, str]):
        """
        Initialize PDF displayer with styles.
        
        Args:
            styles: Dictionary of available named styles
        """
        super().__init__(styles)

    def display(self, source: Optional[str] = None, *,
                style: str = "default",
                is_url: bool = False,
                animate: Optional[str] = None,
                **inline_styles) -> None:
        """
        Display a PDF with interactive viewer.
        
        Args:
            source: Path to PDF file, URL to PDF, or None for file picker
            style: Style name from available styles
            is_url: Whether the source is a URL
            animate: Optional animation effect
            **inline_styles: Additional CSS styles to apply
            
        Raises:
            IPythonNotAvailableError: If IPython display capabilities are not available
            PDFSourceError: If there's an error accessing the PDF file
            PDFDownloadError: If downloading a PDF from URL fails
            PDFRenderingError: If rendering the PDF fails
        """
        try:
            # Get style attributes
            style_attributes = self._get_style_attributes(style)

            # Process inline styles to CSS format
            inline_css = self._process_inline_styles(inline_styles)

            # Generate HTML content with PDF viewer
            html_content = self._generate_pdf_viewer_html(
                source=source,
                is_url=is_url,
                animate=animate,
                style_attributes=style_attributes,
                inline_css=inline_css
            )

            # Display the content
            self._display_html(html_content)
        except Exception as e:
            # Handle specific exceptions
            if isinstance(e, (FileNotFoundError, PermissionError)):
                raise PDFSourceError(source=source, is_url=is_url) from e
            elif "Error downloading PDF from URL" in str(e):
                raise PDFDownloadError(url=source, message=str(e)) from e
            elif isinstance(e, IPythonNotAvailableError):
                raise
            else:
                raise PDFRenderingError(f"Failed to render PDF: {str(e)}") from e

    def _get_style_attributes(self, style_name: str) -> str:
        """
        Get style string for the requested style.
        
        Args:
            style_name: Name of the style to retrieve
            
        Returns:
            Style string
            
        Raises:
            StyleNotFoundError: If the requested style is not found
        """
        if style_name not in self.styles:
            raise StyleNotFoundError(style_name=style_name)
        return self.styles[style_name]

    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content using IPython's display capabilities.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython display is not available
        """
        try:
            from IPython.display import HTML, display
            display(HTML(html_content))
        except ImportError:
            raise IPythonNotAvailableError(
                "IPython.display is required to display PDFs. "
                "Please ensure you're in a Jupyter or Google Colab environment."
            )

    def _generate_pdf_viewer_html(self, source: Optional[str], is_url: bool,
                                  animate: Optional[str],
                                  style_attributes: str,
                                  inline_css: str) -> str:
        """
        Generate HTML content for the PDF viewer.
        
        Args:
            source: Path to PDF file, URL, or None for file picker
            is_url: Whether the source is a URL
            animate: Optional animation effect
            style_attributes: Style string
            inline_css: Additional CSS styles
            
        Returns:
            Complete HTML content for displaying PDF viewer
            
        Raises:
            FileNotFoundError: If the local file does not exist
            PDFDownloadError: If there's an error downloading the PDF from URL
            HTMLGenerationError: If there's an error generating the HTML content
        """
        try:

            # Set up animation
            animation_html, animation_class = self._prepare_animation(animate)

            # Process the source and prepare auto-loading
            file_input_visible, auto_load_script = self._process_pdf_source(source, is_url)

            # Combine styles
            container_style = self._combine_styles(style_attributes, inline_css)

            # Generate the final HTML content
            return self._generate_html_content(
                animation_html,
                animation_class,
                file_input_visible,
                auto_load_script,
                container_style
            )
        except Exception as e:
            raise HTMLGenerationError(component="PDF viewer", message=str(e))

    def _prepare_animation(self, animate: Optional[str]) -> tuple[str, str]:
        """
        Prepare animation HTML and class if animation is requested.
        
        Args:
            animate: Animation effect name or None
            
        Returns:
            Tuple of (animation_html, animation_class)
        """
        if animate:
            animation_html = self._load_animate_css()
            animation_class = f"animate__animated animate__{animate}"
        else:
            animation_html = ""
            animation_class = ""
        return animation_html, animation_class

    def _process_pdf_source(self, source: Optional[str], is_url: bool) -> tuple[bool, str]:
        """
        Process the PDF source and prepare auto-loading script.
        
        Args:
            source: Path to PDF file, URL, or None for file picker
            is_url: Whether the source is a URL
            
        Returns:
            Tuple of (file_input_visible, auto_load_script)
            
        Raises:
            FileNotFoundError: If the local file does not exist
            PDFDownloadError: If there's an error downloading the PDF from URL
        """

        # Just show file picker if no source
        if source is None:
            return True, ""

        # Handle URL source
        if is_url and source.startswith(('http://', 'https://')):
            return self._process_url_source(source)

        # Handle local file source
        return self._process_local_file(source)

    def _process_url_source(self, url: str) -> tuple[bool, str]:
        """
        Download PDF from URL and prepare for display.
        
        Args:
            url: URL to the PDF file
            
        Returns:
            Tuple of (file_input_visible, auto_load_script)
            
        Raises:
            PDFDownloadError: If there's an error downloading the PDF
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            temp_path = self._download_pdf_from_url(url, logger)
            self._validate_pdf_file(temp_path, url)
            auto_load_script = self._prepare_pdf_for_display(temp_path)
            return True, auto_load_script
        except urllib.error.URLError as e:
            raise PDFDownloadError(
                url=url,
                message=f"URL error when downloading PDF: {str(e)}"
            )
        except urllib.error.HTTPError as e:
            raise PDFDownloadError(
                url=url,
                message=f"HTTP error {e.code} when downloading PDF: {str(e)}"
            )
        except Exception as e:
            raise PDFDownloadError(
                url=url,
                message=f"Error downloading PDF from URL: {str(e)}"
            )

    def _download_pdf_from_url(self, url: str, logger) -> str:
        """
        Download PDF from URL to a temporary file.
        
        Args:
            url: URL to the PDF file
            logger: Logger instance
            
        Returns:
            Path to the downloaded temporary file
        """

        # Create a temporary file
        temp_dir = tempfile.gettempdir()

        # Extract filename from URL or create a default name
        filename = os.path.basename(url) or "downloaded.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        # Create a unique filename based on URL hash to avoid duplicates
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        hashed_filename = f"{url_hash}_{filename}"
        temp_path = os.path.join(temp_dir, hashed_filename)

        # Check if file already exists and is valid
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            return temp_path

        # Download the file
        logger.info(f"Downloading PDF from {url} to {temp_path}")

        # Create a request with browser-like headers
        headers = self._get_browser_headers(url)
        req = urllib.request.Request(url, headers=headers)

        # Download with proper error handling
        response: Optional[urllib.request.urlopen] = None
        try:
            response = urllib.request.urlopen(req, timeout=30)
            with open(temp_path, 'wb') as f:
                f.write(response.read())
        finally:
            if response:
                response.close()

        return temp_path

    @staticmethod
    def _validate_pdf_file(file_path: str, url: str) -> None:
        """
        Validate that the downloaded file is a valid PDF.
        
        Args:
            file_path: Path to the downloaded file
            url: Original URL (for error reporting)
            
        Raises:
            PDFDownloadError: If the file is not a valid PDF
        """

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise PDFDownloadError(
                url=url,
                message="Failed to download PDF file"
            )

        # Verify the downloaded file is actually a PDF
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                raise PDFDownloadError(
                    url=url,
                    message="Downloaded file is not a valid PDF"
                )

    def _prepare_pdf_for_display(self, file_path: str) -> str:
        """
        Prepare the PDF file for display by creating an auto-load script.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            JavaScript code to auto-load the PDF
        """

        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()

        file_type = mimetypes.guess_type(file_path)[0] or 'application/pdf'
        filename = os.path.basename(file_path)

        # Encode file data as base64
        file_b64 = base64.b64encode(file_data).decode('utf-8')

        # Script to create a file object and trigger the file input
        return self._create_auto_load_script(file_b64, filename, file_type)

    @staticmethod
    def _get_browser_headers(url) -> dict:
        """
        Get browser-like headers for downloading PDFs.
        
        Returns:
            Dictionary of headers
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': url,
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'DNT': '1'
        }

    def _process_local_file(self, file_path: str) -> tuple[bool, str]:
        """
        Process local PDF file and prepare for display.
        
        Args:
            file_path: Path to the local PDF file
            
        Returns:
            Tuple of (file_input_visible, auto_load_script)
            
        Raises:
            FileNotFoundError: If the file does not exist
        """

        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Get filename from path
        filename = os.path.basename(file_path)
        file_type = mimetypes.guess_type(file_path)[0] or 'application/pdf'

        # Encode file data as base64
        file_b64 = base64.b64encode(file_data).decode('utf-8')

        # Script to create a file object and trigger the file input
        auto_load_script = self._create_blob_auto_load_script(file_b64, filename, file_type)
        return True, auto_load_script

    @staticmethod
    def _combine_styles(style_attributes: str, inline_css: str) -> str:
        """
        Combine style attributes with inline CSS.
        
        Args:
            style_attributes: Style string
            inline_css: Additional CSS styles
            
        Returns:
            Combined style string
        """
        if inline_css:
            return f"{style_attributes}; {inline_css}"
        return style_attributes

    @staticmethod
    def _create_blob_auto_load_script(file_b64: str, filename: str, file_type: str) -> str:
        """
        Create a JavaScript script to automatically load a PDF file into the PDF viewer.
        
        Args:
            file_b64: Base64-encoded PDF data
            filename: Name of the PDF file
            file_type: MIME type of the PDF file
            
        Returns:
            str: JavaScript script to automatically load the PDF file
        """
        blob_script = f"""
                // Create file from local path data
                try {{
                    // Convert base64 to Blob
                    const binaryString = atob("{file_b64}");
                    const bytes = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {{
                        bytes[i] = binaryString.charCodeAt(i);
                    }}
                    
                    // Create a File object
                    const fileData = new Blob([bytes], {{type: "{file_type}"}});
                    const file = new File([fileData], "{filename}", {{type: "{file_type}"}});
                    
                    // Create a DataTransfer to set up the file input
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    
                    // Set the file to the input element
                    const fileInput = document.getElementById('file-selector');
                    fileInput.files = dataTransfer.files;
                    
                    // Update file name display - using the Python variable directly
                    document.getElementById('fileNameDisplay').innerHTML = '<span class="font-medium">{filename}</span>';
                    
                    // Trigger the change event
                    const event = new Event('change', {{ bubbles: true }});
                    fileInput.dispatchEvent(event);
                }} catch (error) {{
                    console.error('Error processing file:', error);
                    document.getElementById('error-message').textContent = 'Error processing file: ' + error.message;
                    document.getElementById('error-container').style.display = 'block';
                }}
                """

        return blob_script

    def _generate_html_content(self, animation_html: str, animation_class: str, file_input_visible: bool,
                               auto_load_script: str, container_style: str) -> str:
        """
        Generate HTML content for the PDF viewer.
        
        Args:
            animation_html: HTML content for the animation
            animation_class: CSS class for the animation
            file_input_visible: Whether the file input is visible
            auto_load_script: JavaScript script to automatically load the PDF file
            container_style: CSS style for the container
            
        Returns:
            str: HTML content for the PDF viewer
        """
        js_html_content = self._generate_js_html_content(auto_load_script)

        page_content = self._generate_page_content(animation_html, animation_class, js_html_content, file_input_visible,
                                                   container_style)

        return page_content

    @staticmethod
    def _generate_page_content(animation_html: str, animation_class: str, js_html_content: str,
                               file_input_visible: bool, container_style: str) -> str:
        """
        Generate HTML content for the PDF viewer.
        
        Args:
            animation_html: HTML content for the animation
            animation_class: CSS class for the animation
            js_html_content: JavaScript HTML content for the PDF viewer
            file_input_visible: Whether the file input is visible
            container_style: CSS style for the container
            
        Returns:
            str: HTML content for the PDF viewer
        """
        page_content = f"""{animation_html}
            <div class="{animation_class}" style="{container_style}">
            <div style="font-family: 'Inter', sans-serif; width: 100%; max-width: 800px; margin: 0 auto;">
                <div class="file-picker-container" style="display: {'block' if file_input_visible else 'none'}; background-color: #ffffff; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); width: 100%; max-width: 28rem; box-sizing: border-box; margin-bottom: 20px;">
                    <h2 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #374151; text-align: center;">Upload Your PDF</h2>
                    
                    <input type="file" id="file-selector" style="width: 0.1px; height: 0.1px; opacity: 0; overflow: hidden; position: absolute; z-index: -1;" accept=".pdf">
                    
                    <label for="file-selector" style="cursor: pointer; background-color: #2563eb; color: #ffffff; font-weight: 500; padding: 0.75rem 1.25rem; border-radius: 0.5rem; display: inline-flex; align-items: center; justify-content: center; width: 100%; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); transition: background-color 0.3s ease, box-shadow 0.3s ease; box-sizing: border-box;">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="height: 1.25rem; width: 1.25rem; margin-right: 0.5rem;">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                        <span>Choose a file</span>
                    </label>
                    
                    <div id="fileNameDisplay" style="margin-top: 1rem; font-size: 0.875rem; color: #4b5563; background-color: #f9fafb; padding: 0.75rem; border-radius: 0.375rem; border: 1px solid #e5e7eb; min-height: 40px; display: flex; align-items: center; justify-content: center; box-sizing: border-box;">
                        <span style="font-style: italic;">No file chosen</span>
                    </div>
                </div>
                
                <div id="error-container" style="display: none; color: #ef4444; margin-bottom: 15px;">
                    <p id="error-message"></p>
                </div>
                
                <div id="loading" style="display: none; text-align: center; margin: 20px 0;">
                    <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 30px; height: 30px; animation: spin 2s linear infinite; margin: 0 auto;"></div>
                    <p>Loading PDF...</p>
                </div>
                
                <div style="width: 100%; max-width: 800px; height: 70vh; margin: 20px auto; position: relative; background-color: white; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    <div id="page-container" style="width: 100%; height: 100%; overflow: auto; display: flex; justify-content: center;"></div>
                </div>

                <div style="display: flex; justify-content: center; margin-top: 10px; gap: 20px;">
                    <button id="prev-page" style="padding: 10px 20px; background-color: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;" disabled>Previous</button>
                    <div style="margin: 0 10px; font-size: 16px; display: flex; align-items: center;">
                        Page <span id="current-page">0</span> of <span id="total-pages">0</span>
                    </div>
                    <button id="next-page" style="padding: 10px 20px; background-color: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;" disabled>Next</button>
                </div>
            </div>

            {js_html_content}
            </div>
            """

        return page_content

    @staticmethod
    def _generate_js_html_content(auto_load_script: str) -> str:
        """
        Generate JavaScript HTML content for the PDF viewer.
        
        Args:
            auto_load_script: JavaScript script to automatically load the PDF file
            
        Returns:
            str: JavaScript HTML content for the PDF viewer
        """

        js_content = f"""<script>
                // Add PDF.js library
                if (!window.pdfjsLib) {{
                    const scriptTag = document.createElement('script');
                    scriptTag.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js';
                    document.head.appendChild(scriptTag);
                    
                    // Wait for script to load
                    scriptTag.onload = function() {{
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
                        initPdfViewer();
                    }};
                }} else {{
                    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
                    initPdfViewer();
                }}
                
                function initPdfViewer() {{
                    let pdfDoc = null;
                    let currentPage = 1;
                    let pageRendering = false;
                    let pageNumPending = null;
                    let scale = 1.5;

                    const pageContainer = document.getElementById('page-container');
                    const prevButton = document.getElementById('prev-page');
                    const nextButton = document.getElementById('next-page');
                    const currentPageEl = document.getElementById('current-page');
                    const totalPagesEl = document.getElementById('total-pages');
                    const loadingEl = document.getElementById('loading');
                    const fileNameDisplay = document.getElementById('fileNameDisplay');

                    function renderPage(pageNum) {{
                        pageRendering = true;

                        while (pageContainer.firstChild) {{
                            pageContainer.removeChild(pageContainer.firstChild);
                        }}

                        pdfDoc.getPage(pageNum).then(function(page) {{
                            const canvas = document.createElement('canvas');
                            const ctx = canvas.getContext('2d');
                            pageContainer.appendChild(canvas);

                            const viewport = page.getViewport({{ scale }});
                            canvas.height = viewport.height;
                            canvas.width = viewport.width;

                            const renderContext = {{
                                canvasContext: ctx,
                                viewport: viewport
                            }};

                            const renderTask = page.render(renderContext);
                            renderTask.promise.then(function() {{
                                pageRendering = false;
                                if (pageNumPending !== null) {{
                                    renderPage(pageNumPending);
                                    pageNumPending = null;
                                }}
                            }});
                        }});

                        currentPageEl.textContent = pageNum;
                        prevButton.disabled = pageNum <= 1;
                        nextButton.disabled = pageNum >= pdfDoc.numPages;
                    }}

                    function queueRenderPage(pageNum) {{
                        if (pageRendering) {{
                            pageNumPending = pageNum;
                        }} else {{
                            renderPage(pageNum);
                        }}
                    }}

                    function onPrevPage() {{
                        if (currentPage <= 1) return;
                        currentPage--;
                        queueRenderPage(currentPage);
                    }}

                    function onNextPage() {{
                        if (currentPage >= pdfDoc.numPages) return;
                        currentPage++;
                        queueRenderPage(currentPage);
                    }}

                    function loadPdf(typedArray) {{
                        loadingEl.style.display = 'block';
                        pdfjsLib.getDocument(typedArray).promise.then(function(pdf) {{
                            loadingEl.style.display = 'none';
                            pdfDoc = pdf;
                            totalPagesEl.textContent = pdfDoc.numPages;
                            currentPage = 1;
                            renderPage(currentPage);
                            prevButton.disabled = currentPage <= 1;
                            nextButton.disabled = currentPage >= pdfDoc.numPages;
                        }}).catch(function(error) {{
                            loadingEl.style.display = 'none';
                            console.error('Error loading PDF:', error);
                            document.getElementById('error-message').textContent = 'Error loading PDF: ' + error.message;
                            document.getElementById('error-container').style.display = 'block';
                        }});
                    }}

                    // Event listener for file selector
                    const fileSelector = document.getElementById('file-selector');
                    fileSelector.addEventListener('change', function(event) {{
                        document.getElementById('error-container').style.display = 'none';
                        const file = event.target.files[0];
                        if (!file || file.type !== 'application/pdf') {{
                            document.getElementById('error-message').textContent = 'Please select a PDF file.';
                            document.getElementById('error-container').style.display = 'block';
                            fileNameDisplay.innerHTML = '<span style="font-style: italic;">No file chosen</span>';
                            return;
                        }}

                        // Update file name display
                        fileNameDisplay.innerHTML = '<span style="font-weight: 500; color: #1f2937;">' + file.name + '</span>';

                        const fileReader = new FileReader();
                        loadingEl.style.display = 'block';
                        fileReader.onload = function() {{
                            const typedArray = new Uint8Array(this.result);
                            loadPdf(typedArray);
                        }};
                        fileReader.onerror = function() {{
                            loadingEl.style.display = 'none';
                            document.getElementById('error-message').textContent = 'Error reading file.';
                            document.getElementById('error-container').style.display = 'block';
                        }};
                        fileReader.readAsArrayBuffer(file);
                    }});

                    // Automatically load file if source is provided
                    {auto_load_script}

                    prevButton.addEventListener('click', onPrevPage);
                    nextButton.addEventListener('click', onNextPage);

                    document.addEventListener('keydown', function(event) {{
                        if (event.key === 'ArrowLeft') {{
                            onPrevPage();
                        }} else if (event.key === 'ArrowRight') {{
                            onNextPage();
                        }}
                    }});
                    
                    // Add keydown navigation
                    document.addEventListener('keydown', function(event) {{
                        if (event.key === 'ArrowLeft') {{
                            onPrevPage();
                        }} else if (event.key === 'ArrowRight') {{
                            onNextPage();
                        }}
                    }});
                    
                    // Add spin animation for loading
                    const style = document.createElement('style');
                    style.textContent = `
                        @keyframes spin {{
                            0% {{ transform: rotate(0deg); }}
                            100% {{ transform: rotate(360deg); }}
                        }}
                    `;
                    document.head.appendChild(style);
                }}
            </script>"""

        return js_content

    @staticmethod
    def _create_auto_load_script(file_b64: str, filename: str, file_type: str) -> str:
        """
        Create a JavaScript script to automatically load a PDF file into the PDF viewer.
        
        Args:
            file_b64: Base64-encoded PDF data
            filename: Name of the PDF file
            file_type: MIME type of the PDF file
            
        Returns:
            str: JavaScript script to automatically load the PDF file
        """
        script = f"""
                        // Create file from downloaded data
                        try {{
                            // Convert base64 to Blob
                            const binaryString = atob("{file_b64}");
                            const bytes = new Uint8Array(binaryString.length);
                            for (let i = 0; i < binaryString.length; i++) {{
                                bytes[i] = binaryString.charCodeAt(i);
                            }}
                            
                            // Create a File object
                            const fileData = new Blob([bytes], {{type: "{file_type}"}});
                            const file = new File([fileData], "{filename}", {{type: "{file_type}"}});
                            
                            // Create a DataTransfer to set up the file input
                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(file);
                            
                            // Set the file to the input element
                            const fileInput = document.getElementById('file-selector');
                            fileInput.files = dataTransfer.files;
                            
                            // Update file name display - using the Python variable directly
                            document.getElementById('fileNameDisplay').innerHTML = '<span class="font-medium">{filename}</span>';
                            
                            // Trigger the change event
                            const event = new Event('change', {{ bubbles: true }});
                            fileInput.dispatchEvent(event);
                        }} catch (error) {{
                            console.error('Error processing file:', error);
                            document.getElementById('error-message').textContent = 'Error processing downloaded file: ' + error.message;
                            document.getElementById('error-container').style.display = 'block';
                        }}
                        """
        return script


class TextBoxDisplayer(Displayer):
    """
    Component for displaying versatile container boxes with title, captions, and progress bars.
    
    This displayer enables the creation of styled container boxes that can embed
    various elements including titles, captions, progress bars, and potentially other
    components in the future. It provides a clean, structured way to present
    information in a notebook environment.
    """

    def __init__(self, styles: Dict[str, str]):
        """
        Initialize TextBox displayer with styles.
        
        Args:
            styles: Dictionary of available named styles
        """
        super().__init__(styles)

    def display(self, title: str, *,
                captions: Optional[List[str]] = None,
                progress: Optional[Dict[str, Any]] = None,
                style: str = "default",
                animate: Optional[str] = None,
                **inline_styles) -> str:
        """
        Display a styled text box with optional components.
        
        Args:
            title: The main title/heading of the text box
            captions: List of caption paragraphs to display in order
            progress: Optional progress bar parameters:
                      {'value': int, 'max': int, 'label': str}
            style: Named style from available styles
            animate: Animation effect from Animate.css
            **inline_styles: Additional CSS styles to apply
            
        Returns:
            str: The unique ID of the text box for dynamic updates
            
        Raises:
            MissingTitleError: If no title is provided
            InvalidProgressValueError: If progress values are invalid
            StyleNotFoundError: If specified style is not found
            UnsupportedComponentError: If an unsupported component is specified
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            # Validate title
            if not title or not isinstance(title, str):
                raise MissingTitleError("TextBox requires a non-empty title string")
                
            # Validate style
            if style not in self.styles:
                raise StyleNotFoundError(
                    style_name=style,
                    message=f"Style '{style}' not found. Available styles: {', '.join(self.styles.keys())}"
                )
            
            # Process the captions
            processed_captions = self._process_captions(captions)
            
            # Process the progress bar if provided
            progress_html = self._process_progress(progress) if progress else ""
            
            # Generate a unique ID for this text box
            text_box_id = self._generate_text_box_id()
            
            # Generate the HTML content
            html_content = self._generate_html(
                text_box_id,
                title, 
                processed_captions, 
                progress_html, 
                style, 
                animate, 
                **inline_styles
            )
            
            # Display the HTML
            self._display_html(html_content)
            
            # Return the ID for future updates
            return text_box_id
            
        except (MissingTitleError, StyleNotFoundError, InvalidProgressValueError, 
                UnsupportedComponentError, HTMLRenderingError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise TextBoxError(f"Error displaying text box: {str(e)}")
    
    def update(self, text_box_id: str, *,
               title: Optional[str] = None,
               captions: Optional[List[str]] = None,
               progress: Optional[Dict[str, Any]] = None) -> None:
        """
        Update an existing text box with new content.
        
        Args:
            text_box_id: The ID of the text box to update
            title: New title for the text box (if None, keeps existing title)
            captions: New captions for the text box (if None, keeps existing captions)
            progress: New progress bar parameters (if None, keeps existing progress)
            
        Raises:
            DisplayUpdateError: If the text box cannot be updated
            InvalidParameterError: If any parameters are invalid
            IPythonNotAvailableError: If IPython environment is not detected
        """
        try:
            # Validate text_box_id
            if not text_box_id or not isinstance(text_box_id, str):
                raise InvalidParameterError(
                    param_name="text_box_id",
                    expected="non-empty string",
                    received=type(text_box_id).__name__
                )
            
            # Process captions if provided
            captions_js = "null"
            if captions is not None:
                processed_captions = self._process_captions(captions)
                captions_html = ""
                for caption in processed_captions:
                    captions_html += f"<p>{html.escape(caption)}</p>"
                captions_js = f'`{captions_html}`'
            
            # Process progress if provided
            progress_js = "null"
            if progress is not None:
                progress_html = self._process_progress(progress)
                progress_js = f'`{progress_html}`'
            
            # Process title if provided
            title_js = "null"
            if title is not None:
                if not isinstance(title, str):
                    raise InvalidParameterError(
                        param_name="title",
                        expected="string",
                        received=type(title).__name__
                    )
                title_js = f'"{html.escape(title)}"'
            
            # Generate JavaScript to update the text box
            js_code = self._generate_update_js(text_box_id, title_js, captions_js, progress_js)
            
            # Execute the JavaScript
            from IPython.display import display, Javascript
            display(Javascript(js_code))
            
        except (InvalidParameterError, IPythonNotAvailableError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise DisplayUpdateError(
                element_id=text_box_id,
                message=f"Failed to update text box: {str(e)}"
            )
    
    def _process_captions(self, captions: Optional[List[str]]) -> List[str]:
        """
        Process and validate captions.
        
        Args:
            captions: List of caption strings
            
        Returns:
            Processed list of caption strings
            
        Raises:
            InvalidParameterError: If captions parameter is invalid
        """
        if captions is None:
            return []
            
        if not isinstance(captions, (list, tuple)):
            raise InvalidParameterError(
                param_name="captions",
                expected="list or tuple of strings",
                received=type(captions).__name__
            )
            
        # Ensure all captions are strings
        processed_captions = []
        for i, caption in enumerate(captions):
            if not isinstance(caption, str):
                raise InvalidParameterError(
                    param_name=f"captions[{i}]",
                    expected="string",
                    received=type(caption).__name__
                )
            processed_captions.append(caption)
            
        return processed_captions
    
    def _process_progress(self, progress: Dict[str, Any]) -> str:
        """
        Process progress bar parameters and generate HTML.
        
        Args:
            progress: Dictionary with progress parameters:
                      {'value': int, 'max': int, 'label': str}
                      
        Returns:
            HTML string for the progress bar
            
        Raises:
            InvalidProgressValueError: If progress values are invalid
            InvalidParameterError: If progress parameter is missing required keys
        """
        if not isinstance(progress, dict):
            raise InvalidParameterError(
                param_name="progress",
                expected="dictionary with 'value', 'max', and 'label' keys",
                received=type(progress).__name__
            )
            
        # Get progress values with defaults
        value = progress.get('value', 0)
        max_value = progress.get('max', 100)
        label = progress.get('label', 'Progress')
        
        # Validate values
        if not isinstance(value, (int, float)):
            raise InvalidParameterError(
                param_name="progress['value']",
                expected="number",
                received=type(value).__name__
            )
            
        if not isinstance(max_value, (int, float)):
            raise InvalidParameterError(
                param_name="progress['max']",
                expected="number",
                received=type(max_value).__name__
            )
            
        if value < 0 or max_value <= 0 or value > max_value:
            raise InvalidProgressValueError(
                value=value,
                max_value=max_value,
                message=f"Invalid progress values: value={value}, max={max_value}"
            )
            
        # Calculate percentage for the progress bar width
        percentage = int((value / max_value) * 100)
        percentage_text = f"{percentage}%"
        
        # Generate HTML for the progress bar
        return f"""
        <div class="progress-label">{html.escape(str(label))}</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage_text};"></div>
        </div>
        <div class="progress-text">{percentage_text}</div>
        """
    
    def _generate_html(self, text_box_id: str, title: str, captions: List[str], progress_html: str,
                       style: str, animate: Optional[str], **inline_styles) -> str:
        """
        Generate HTML for the text box.
        
        Args:
            text_box_id: Unique ID for the text box
            title: Box title
            captions: List of caption paragraphs
            progress_html: HTML for progress bar (if any)
            style: Style name
            animate: Animation name
            **inline_styles: Additional inline styles
            
        Returns:
            Complete HTML for the text box
        """
        # Process animation class if specified
        animation_class = process_animation_class(animate)
        class_attr = f'class="text-box {animation_class}"' if animation_class else 'class="text-box"'
        
        # Process base style and inline styles
        base_style = self.styles.get(style, '')
        inline_style_string = self._process_inline_styles(inline_styles)
        final_style = f"{base_style} {inline_style_string}" if inline_style_string else base_style
        
        # Construct captions HTML
        captions_html = ""
        for caption in captions:
            captions_html += f"<p>{html.escape(caption)}</p>"
        
        # Construct the complete HTML
        html_content = f"""
        <div id="{text_box_id}" style="{final_style}" {class_attr}>
            <div id="{text_box_id}-title" class="box-title">{html.escape(title)}</div>
            <div id="{text_box_id}-content" class="box-content">
                <div id="{text_box_id}-captions">{captions_html}</div>
                <div id="{text_box_id}-progress">{progress_html}</div>
            </div>
        </div>
        """
        
        # Include Animate.css CDN if animation is specified
        animate_css_link = self._load_animate_css() if animate else ''
        
        # Add JavaScript for initialization
        js_init = self._generate_init_js(text_box_id)
        
        return f"{animate_css_link}{html_content}{js_init}" if animate else f"{html_content}{js_init}"
    
    @staticmethod
    def _generate_text_box_id() -> str:
        """Generate a unique ID for a text box."""
        import uuid
        return f"text-box-{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def _generate_init_js(text_box_id: str) -> str:
        """Generate JavaScript to initialize the text box for updates."""
        return f"""
        <script>
        (function() {{
            // Initialize text box components for updates
            console.log("TextBox initialized with ID: {text_box_id}");
        }})();
        </script>
        """
    
    def _generate_update_js(self, text_box_id: str, title_js: str, captions_js: str, progress_js: str) -> str:
        """
        Generate JavaScript to update a text box.
        
        Args:
            text_box_id: ID of the text box to update
            title_js: JavaScript representation of the new title (or "null")
            captions_js: JavaScript representation of the new captions HTML (or "null")
            progress_js: JavaScript representation of the new progress HTML (or "null")
            
        Returns:
            JavaScript code to update the text box
        """
        return f"""
        (function() {{
            // Get the text box elements
            const textBox = document.getElementById("{text_box_id}");
            const titleEl = document.getElementById("{text_box_id}-title");
            const captionsEl = document.getElementById("{text_box_id}-captions");
            const progressEl = document.getElementById("{text_box_id}-progress");
            
            if (!textBox) {{
                console.error("TextBox with ID {text_box_id} not found");
                return;
            }}
            
            // Update title if provided
            if ({title_js} !== null && titleEl) {{
                titleEl.innerHTML = {title_js};
            }}
            
            // Update captions if provided
            if ({captions_js} !== null && captionsEl) {{
                captionsEl.innerHTML = {captions_js};
            }}
            
            // Update progress if provided
            if ({progress_js} !== null && progressEl) {{
                progressEl.innerHTML = {progress_js};
            }}
            
            console.log("TextBox {text_box_id} updated successfully");
        }})();
        """
    
    @staticmethod
    def _display_html(html_content: str) -> None:
        """
        Display HTML content in the notebook.
        
        Args:
            html_content: HTML content to display
            
        Raises:
            IPythonNotAvailableError: If IPython display is not available
        """
        try:
            from IPython.display import display, HTML
            display(HTML(html_content))
        except ImportError:
            raise IPythonNotAvailableError("IPython display capabilities are required to display text boxes")


class Printer:
    """
    Main class for displaying text, tables, and DataFrames with stylized HTML.
    
    This class provides a unified interface for all display operations,
    delegating to specialized displayers for each type of content.
    """

    def __init__(self, additional_styles: Optional[Dict[str, str]] = None):
        """
        Initialize the printer with default and optional additional styles.
        
        Args:
            additional_styles: Optional dictionary of additional styles to add
            
        Raises:
            StyleError: If there's an issue with the provided styles
        """
        try:
            # Set up styles with defaults and any additional styles
            self.styles = DEFAULT_THEMES.copy()
            # Add special styles
            self.styles.update(SPECIAL_STYLES)
            if additional_styles:
                if not isinstance(additional_styles, dict):
                    raise StyleError(f"additional_styles must be a dictionary, got {type(additional_styles).__name__}")
                self.styles.update(additional_styles)

            # Create displayers for different content types
            self.text_displayer = TextDisplayer(self.styles)
            self.code_displayer = CodeDisplayer(self.styles)
            self.table_displayer = TableDisplayer(self.styles)
            self.list_displayer = ListDisplayer(self.styles)
            self.dict_displayer = DictDisplayer(self.styles)
            self.progress_displayer = ProgressDisplayer(self.styles)
            self.mermaid_displayer = MermaidDisplayer(self.styles)
            self.button_displayer = ButtonDisplayer(self.styles)
            self.md_displayer = MDDisplayer(self.styles)
            self.pdf_displayer = PDFDisplayer(self.styles)
            self.text_box_displayer = TextBoxDisplayer(self.styles)
        except Exception as e:
            raise ColabPrintError(f"Error initializing Printer: {str(e)}")

    def display(self, text: str, *, style: str = 'default', animate: Optional[str] = None, **inline_styles) -> None:
        """
        Display text with the specified styling.
        
        Args:
            text: Text to display
            style: Named style from available styles
            animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
            **inline_styles: Additional CSS styles to apply
            
        Raises:
            TextError: If text is not a string
            StyleNotFoundError: If specified style is not found
            StyleParsingError: If there's an error parsing inline styles
            AnimationError: If the animation name is not valid
            DisplayEnvironmentError: If display environment is not available
        """
        try:
            # Validate inputs
            if not isinstance(text, str):
                raise TextError(f"Text must be a string, received {type(text).__name__}")

            if style not in self.styles:
                available_styles = ', '.join(list(self.styles.keys())[:10]) + "..." if len(
                    self.styles) > 10 else ', '.join(self.styles.keys())
                raise StyleNotFoundError(style_name=style,
                                         message=f"Style '{style}' not found. Available styles: {available_styles}")

            self.text_displayer.display(text, style=style, animate=animate, **inline_styles)
        except (TextError, StyleNotFoundError, StyleParsingError, AnimationError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise TextError(f"Error displaying text: {str(e)}") from e

    # noinspection da,PyUnresolvedReferences
    def display_table(self, headers: Optional[List[str]] = None, rows: Optional[List[Any]] = None, *,
                      source_dict: Optional[Dict[Any, Any]] = None,
                      style: str = 'default', width: str = '100%',
                      caption: Optional[str] = None,
                      custom_header_style: Optional[str] = None,
                      custom_row_style: Optional[str] = None,
                      compact: bool = True,
                      **table_options) -> None:
        """
        Display a table with the given headers and rows.
        
        Args:
            headers: List of column headers (optional if source_dict is provided)
            rows: List of rows, each row being any iterable (list, tuple, array, etc.) of cell values (optional if source_dict is provided)
            source_dict: Dictionary to use as the data source (keys become headers, values become rows)
            style: Named style from available styles
            width: Width of the table (CSS value)
            caption: Optional table caption
            custom_header_style: Optional custom CSS for header cells
            custom_row_style: Optional custom CSS for data cells
            compact: Whether to condense large data structures (default: True)
            **table_options: Additional table styling options
            
        Raises:
            TableError: If there's an issue with the table data
            StyleNotFoundError: If specified style is not found
            DisplayEnvironmentError: If display environment is not available
        
        Examples:
            >>> # Basic table with headers and rows
            >>> printer.display_table(['Name', 'Age'], [['Alice', 30], ['Bob', 25]])
            >>>
            >>> # Table from a dictionary (keys become headers, values become rows)
            >>> printer.display_table(source_dict={'Name': ['Alice', 'Bob'], 'Age': [30, 25]})
            >>>
            >>> # Dictionary with scalar values (creates a single-row table)
            >>> printer.display_table(source_dict={'Product': 'Widget', 'Price': 19.99, 'Stock': 42})
            >>>
            >>> # Display a table with large data structures without condensing
            >>> printer.display_table(['Data'], [[list(range(100))]], compact=False)
        """
        # Check if rows is a dataframe-like object
        if df_like(rows):
            raise ValueError("rows is a dataframe-like object. Use display_df instead.")

        try:
            self._validate_table_inputs(headers, rows, source_dict)
            params = self._prepare_table_params(
                headers, rows, source_dict, style, width,
                caption, custom_header_style, custom_row_style,
                compact, table_options
            )
            self.table_displayer.display(**params)
        except (TableError, StyleNotFoundError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise TableError(f"Error displaying table: {str(e)}")

    def _validate_table_inputs(self, headers: Optional[List[str]],
                               rows: Optional[List[Any]],
                               source_dict: Optional[Dict[Any, Any]]) -> None:
        """
        Validate the input parameters for table display.
        
        Args:
            headers: List of column headers
            rows: List of rows (or any iterable of iterables)
            source_dict: Dictionary to use as the data source
            
        Raises:
            TableError: If there's an issue with the table data
        """
        # If source_dict is provided, we'll handle dictionary validation at the displayer level
        if source_dict is not None:
            if not isinstance(source_dict, Mapping):
                raise TableError(f"source_dict must be a dictionary, got {type(source_dict).__name__}")
        # If using traditional approach, validate headers and rows
        elif headers is not None and rows is not None:
            if not isinstance(headers, list):
                raise TableError(f"Headers must be a list, got {type(headers).__name__}")

            # Check if rows is any iterable instead of strictly a list
            try:
                iter(rows)
            except TypeError:
                raise TableError(f"Rows must be iterable, got {type(rows).__name__}")

            # Convert rows to list if it has a to_list() or tolist() method
            rows = self._try_convert_to_list(rows)

            self._validate_row_iterability(rows)
        else:
            raise TableError("Either provide both headers and rows, or a source_dict")

    @staticmethod
    def _try_convert_to_list(rows: Iterable[Any]) -> List[Any]:
        """
        Try to convert an iterable to a list.
        
        Args:
            rows: Iterable to convert
            
        Returns:
            List of rows
        """
        try:
            list_rows = list(rows)
        except Exception:
            pass
        else:
            return list_rows

        if hasattr(rows, 'to_list') and callable(rows.to_list):
            rows = rows.to_list()
        elif hasattr(rows, 'tolist') and callable(rows.tolist):
            rows = rows.tolist()
        elif hasattr(rows, 'to_list'):
            rows = rows.to_list
        elif hasattr(rows, 'tolist'):
            rows = rows.tolist
        else:
            rows = rows
        return rows

    @staticmethod
    def _validate_row_iterability(rows: List[Any]) -> None:
        """
        Validate that each row is an iterable but not a mapping.
        
        Args:
            rows: List of rows to validate
            
        Raises:
            TableError: If any row is not iterable or is a mapping
        """
        for i, row in enumerate(rows):
            # Accept any non-mapping iterable
            if isinstance(row, Mapping):
                raise TableError(f"Row {i} cannot be a mapping type (e.g., dict), got {type(row).__name__}")

            try:
                # Just verify it's iterable
                iter(row)
            except TypeError:
                raise TableError(f"Row {i} must be iterable, got {type(row).__name__}")

    @staticmethod
    def _prepare_table_params(headers: Optional[List[str]],
                              rows: Optional[List[Any]],
                              source_dict: Optional[Dict[Any, Any]],
                              style: str, width: str,
                              caption: Optional[str],
                              custom_header_style: Optional[str],
                              custom_row_style: Optional[str],
                              compact: bool,
                              table_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare parameters for the table displayer.
        
        Args:
            headers: List of column headers
            rows: List of rows
            source_dict: Dictionary to use as the data source
            style: Named style from available styles
            width: Width of the table
            caption: Optional table caption
            custom_header_style: Optional custom CSS for header cells
            custom_row_style: Optional custom CSS for data cells
            compact: Whether to condense large data structures
            table_options: Additional table styling options
            
        Returns:
            Dictionary of parameters for the table displayer
        """
        # Extract explicitly defined parameters
        explicit_params = {
            'headers': headers,
            'rows': rows,
            'source_dict': source_dict,
            'style': style,
            'width': width,
            'caption': caption,
            'custom_header_style': custom_header_style,
            'custom_row_style': custom_row_style,
            'compact': compact
        }

        # Remove None values to use defaults from the display method
        params = {k: v for k, v in explicit_params.items() if v is not None}

        # Merge with any additional table_options
        params.update(table_options)

        return params

    def display_df(self, df: Union[pd.DataFrame, pd.Series], *,
                   style: str = 'default',
                   max_rows: Optional[int] = None,
                   max_cols: Optional[int] = None,
                   precision: int = 2,
                   header_style: Optional[str] = None,
                   odd_row_style: Optional[str] = None,
                   even_row_style: Optional[str] = None,
                   index: bool = True,
                   width: str = '100%',
                   caption: Optional[str] = None,
                   highlight_cols: Optional[Union[List, Dict]] = None,
                   highlight_rows: Optional[Union[List, Dict]] = None,
                   highlight_cells: Optional[Dict] = None,
                   **inline_styles) -> None:
        """
        Display a pandas DataFrame or Series with customizable styling.
        
        Args:
            df: DataFrame or Series to display
            style: Named style from available styles
            max_rows: Maximum number of rows to display
            max_cols: Maximum number of columns to display (applies only to DataFrames)
            precision: Decimal precision for float values
            header_style: Custom CSS for header cells
            odd_row_style: Custom CSS for odd rows
            even_row_style: Custom CSS for even rows
            index: Whether to show DataFrame/Series index
            width: Table width (CSS value)
            caption: Table caption
            highlight_cols: Columns to highlight (list) or {col: style} mapping
            highlight_rows: Rows to highlight (list) or {row: style} mapping
            highlight_cells: Cell coordinates to highlight {(row, col): style}
            **inline_styles: Additional CSS styles for all cells
            
        Raises:
            DataFrameError: If df is not a pandas DataFrame and not a pandas Series
            SeriesError: If there's an issue with the Series structure
            StyleNotFoundError: If specified style is not found
            InvalidParameterError: If invalid parameters are provided
            DisplayEnvironmentError: If display environment is not available
            
        Notes:
            For Series, the Series name (or "Value" if unnamed) will be used as the column name
            in the resulting table. The Series index is preserved and displayed when index=True.
        """

        # Check if df is a dataframe-like or series-like object
        dfe = "The 'df' parameter must be a pandas DataFrame or Series"
        
        if not df_like(df):
            raise DataFrameError(dfe)
        elif not series_like(df):
            raise SeriesError(dfe)

        try:
            # Validate numeric parameters
            if max_rows is not None and not isinstance(max_rows, int):
                raise InvalidParameterError("max_rows", "integer", received=type(max_rows).__name__)

            if max_cols is not None and not isinstance(max_cols, int):
                raise InvalidParameterError("max_cols", "integer", received=type(max_cols).__name__)

            if not isinstance(precision, int):
                raise InvalidParameterError("precision", "integer", received=type(precision).__name__)

            # Create the displayer and use it
            displayer = DFDisplayer(self.styles, df)
            displayer.display(
                style=style,
                max_rows=max_rows,
                max_cols=max_cols,
                precision=precision,
                header_style=header_style,
                odd_row_style=odd_row_style,
                even_row_style=even_row_style,
                index=index,
                width=width,
                caption=caption,
                highlight_cols=highlight_cols,
                highlight_rows=highlight_rows,
                highlight_cells=highlight_cells,
                **inline_styles
            )
        except (DataFrameError, SeriesError, StyleNotFoundError, InvalidParameterError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions with appropriate error type
            if isinstance(df, pd.Series):
                raise SeriesError(f"Error displaying Series: {str(e)}")
            else:
                raise DataFrameError(f"Error displaying DataFrame: {str(e)}")

    # noinspection PyUnresolvedReferences,da
    def display_list(self, items: Any, *,
                     ordered: bool = False, style: str = 'default',
                     item_style: Optional[str] = None,
                     matrix_mode: Optional[bool] = None,
                     nesting_colors: Optional[List[str]] = None,
                     **inline_styles) -> None:
        """
        Display a list or tuple as an HTML list.

        Args:
            items: The list, tuple, or array-like object to display
            ordered: If True, use an ordered list (<ol>), otherwise unordered (<ul>)
            style: Named style for the list container
            item_style: Optional custom CSS style for list items
            matrix_mode: Force matrix display mode for 2D arrays (default: auto-detect)
            nesting_colors: Optional list of colors to use for different nesting levels
            **inline_styles: Additional CSS styles to apply to list items
            
        Raises:
            ListError: If there's an issue with the list data
            StyleNotFoundError: If specified style is not found
            InvalidParameterError: If invalid parameters are provided
            ColorError: If color validation fails
            DisplayEnvironmentError: If display environment is not available
            
        Examples:
            >>> printer.display_list([1, 2, 3, 4])
            >>> printer.display_list([['a', 'b'], ['c', 'd']], matrix_mode=True)
            >>> printer.display_list(np.array([[1, 2], [3, 4]]))  # Auto-detects matrix mode
            
        Note:
            Supports automatic conversion from various array-like objects:
            - NumPy arrays: `np.array([1, 2, 3])`
            - Pandas Series/DataFrames: `pd.Series([1, 2, 3])`
            - PyTorch tensors: `torch.tensor([1, 2, 3])`
            - TensorFlow tensors: `tf.constant([1, 2, 3])`
            - JAX arrays: `jax.numpy.array([1, 2, 3])`
        """
        try:
            self.list_displayer.display(
                items,
                ordered=ordered,
                style=style,
                item_style=item_style,
                matrix_mode=matrix_mode,
                nesting_colors=nesting_colors,
                **inline_styles
            )
        except (ListError, StyleNotFoundError, InvalidParameterError, ColorError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise ListError(f"Error displaying list: {str(e)}")

    def display_dict(self, data: Dict, *, style: str = 'default',
                     key_style: Optional[str] = None,
                     value_style: Optional[str] = None,
                     **inline_styles) -> None:
        """
        Display a dictionary as an HTML definition list.
        
        Args:
            data: The dictionary to display
            style: Named style for the definition list container
            key_style: Optional custom CSS style for keys (<dt>)
            value_style: Optional custom CSS style for values (<dd>)
            **inline_styles: Additional CSS styles to apply to list items
            
        Raises:
            DictError: If data is not a dictionary or there's an issue with the dictionary
            StyleNotFoundError: If specified style is not found
            DisplayEnvironmentError: If display environment is not available
        """
        try:
            if not isinstance(data, dict):
                raise DictError(f"Input must be a dictionary, got {type(data).__name__}")

            self.dict_displayer.display(
                data,
                style=style,
                key_style=key_style,
                value_style=value_style,
                **inline_styles
            )
        except (DictError, StyleNotFoundError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise DictError(f"Error displaying dictionary: {str(e)}")

    # noinspection PyUnresolvedReferences
    def display_mermaid(self, diagram: str, *,
                        style: str = 'default',
                        theme: str = 'default',
                        custom_css: Optional[Dict[str, str]] = None,
                        **inline_styles) -> None:
        """
        Display a Mermaid diagram.
        
        Args:
            diagram: Mermaid diagram definition or file path to a Mermaid diagram file
            style: Named style from available styles for the container
            theme: Mermaid theme ('default', 'forest', 'dark', 'neutral')
            custom_css: Optional dictionary mapping Mermaid CSS selectors to style properties
            **inline_styles: Additional CSS styles to apply to the container
            
        Raises:
            MermaidError: If there's an issue with the diagram or diagram file
            StyleNotFoundError: If specified style is not found
            DisplayEnvironmentError: If display environment is not available
            InvalidParameterError: If theme is not valid
            
        Examples:
                >>> # Display a simple diagram
                >>> printer.display_mermaid('''
                ...    graph TD;
                ...    A-->B;
                ...    A-->C;
                ...    B-->D;
                ...    C-->D;
                ... '''
                ... )

                >>> # Read from a file
                >>> printer.display_mermaid('diagrams/flow.mmd', theme='dark')

                >>> # Apply custom CSS
                >>> printer.display_mermaid(diagram, custom_css={
                ... '.node rect': 'fill: #f9f9f9; stroke: #333; stroke-width: 2px;',
                ... '.edgeLabel': 'background-color: white; padding: 2px;'
                ... })
        """
        self.mermaid_displayer.display(
            diagram,
            style=style,
            theme=theme,
            custom_css=custom_css,
            **inline_styles
        )

    def display_md(self, source: str, *,
                   is_url: bool = False,
                   style: str = 'default',
                   animate: Optional[str] = None,
                   **inline_styles) -> None:
        """
        Display markdown content from a URL or file with read more/less functionality.
        
        Args:
            source: The URL or file path of the markdown file to display
            is_url: If True, treat source as a URL; if False, treat as a file path
            style: Named style from the available styles
            animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
            **inline_styles: Additional CSS styles to apply to the container
            
        Raises:
            DisplayMethodError: If there's an issue with the display method
            StyleNotFoundError: If specified style is not found
            InvalidParameterError: If source is invalid
            DisplayEnvironmentError: If display environment is not available
            
        Examples:
            # Display markdown from a file
            printer.display_md('docs/README.md')
            
            # Display markdown from a URL
            printer.display_md('https://raw.githubusercontent.com/user/repo/main/README.md', is_url=True)
            
            # Apply animation
            printer.display_md('docs/README.md', animate='fadeIn')
            
            # Apply custom styling
            printer.display_md('docs/README.md', max_width='800px', border='1px solid #ccc')
        """
        try:
            self.md_displayer.display(
                source,
                is_url=is_url,
                style=style,
                animate=animate,
                **inline_styles
            )
        except (StyleNotFoundError, InvalidParameterError, AnimationError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise DisplayMethodError(
                method_name="display_md",
                message=f"Error displaying markdown content: {str(e)}"
            ) from e

    def add_style(self, name: str, style_definition: str) -> None:
        """
        Add a new style to the available styles.
        
        Args:
            name: Name of the style
            style_definition: CSS style string
            
        Raises:
            InvalidParameterError: If parameters are invalid
            StyleError: If there's an issue with the style definition
        """
        try:
            if not isinstance(name, str):
                raise InvalidParameterError("name", "string", received=type(name).__name__)

            if not isinstance(style_definition, str):
                raise InvalidParameterError("style_definition", "string", received=type(style_definition).__name__)

            if name in self.styles:
                warnings.warn(f"Overwriting existing style: {name}")

            self.styles[name] = style_definition
        except InvalidParameterError:
            raise
        except Exception as e:
            raise StyleError(f"Error adding style: {str(e)}") from e

    def get_available_styles(self) -> List[str]:
        """
        Get a list of available style names.
        
        Returns:
            List of style names
        """
        return list(self.styles.keys())

    def create_styled_display(self, style: str, **default_styles) -> Callable[[str], None]:
        """
        Create a reusable display function with predefined style settings.
        
        This method returns a callable function that applies the specified 
        style and default inline styles to any text passed to it.
        
        Args:
            style: Named style from available styles
            **default_styles: Default inline CSS styles to apply
            
        Returns:
            A callable function that displays text with predefined styling
            
        Raises:
            StyleNotFoundError: If specified style is not found
            StyleError: If there's an issue with the style settings
            
        Example:
            # Create a header display function
            header = printer.create_styled_display('header')
            
            # Use it multiple times
            header("First Section")
            header("Second Section")
            
            # Create with overrides
            alert = printer.create_styled_display('error', font_weight='bold')
            
            # Override inline styles at call time
            header("Custom Header", color="#FF5722")
        """
        if style not in self.styles:
            raise StyleNotFoundError(style_name=style)

        def styled_display(text: str, **override_styles) -> None:
            # Merge default_styles with any override_styles
            combined_styles = default_styles.copy()
            combined_styles.update(override_styles)

            # Call the regular display method with the combined styles
            self.display(text, style=style, **combined_styles)

        return styled_display

    def display_progress(self, total: Optional[int] = None, *,
                         desc: str = "",
                         style: str = "default",
                         color: str = "#3498DB",
                         height: str = "20px",
                         animated: bool = True,
                         **inline_styles) -> str:
        """
        Display a progress bar with either determined or undetermined progress.
        
        Args:
            total: Total number of steps (None for undetermined progress)
            desc: Description text to display with the progress bar
            style: Named style from available styles
            color: Color of the progress bar
            height: Height of the progress bar
            animated: Whether to animate the progress bar
            **inline_styles: Additional CSS styles to apply
            
        Returns:
            Progress bar ID that can be used to update the progress
            
        Raises:
            ProgressError: If there's an issue with the progress bar
            StyleNotFoundError: If specified style is not found
            ColorError: If color validation fails
            DisplayEnvironmentError: If display environment is not available
            InvalidParameterError: If any parameter is invalid
        """
        try:
            # Validate parameters
            if total is not None and not isinstance(total, int):
                raise InvalidParameterError("total", "integer or None", received=type(total).__name__)

            if not isinstance(desc, str):
                raise InvalidParameterError("desc", "string", received=type(desc).__name__)

            if not isinstance(color, str):
                raise InvalidParameterError("color", "string", received=type(color).__name__)

            if not isinstance(height, str):
                raise InvalidParameterError("height", "string", received=type(height).__name__)

            if not isinstance(animated, bool):
                raise InvalidParameterError("animated", "boolean", received=type(animated).__name__)

            # Validate style exists
            if style not in self.styles:
                available_styles = ', '.join(list(self.styles.keys())[:10]) + "..." if len(
                    self.styles) > 10 else ', '.join(self.styles.keys())
                raise StyleNotFoundError(style_name=style,
                                         message=f"Style '{style}' not found. Available styles: {available_styles}")

            # Validate color format (basic check)
            if color.startswith('#') and not (len(color) == 7 or len(color) == 4):
                raise ColorError(color_value=color, message=f"Invalid hex color format: {color}")

            return self.progress_displayer.display(
                total=total,
                desc=desc,
                style=style,
                color=color,
                height=height,
                animated=animated,
                **inline_styles
            )
        except (InvalidParameterError, StyleNotFoundError, ColorError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise ProgressError(f"Error displaying progress bar: {str(e)}") from e

    def update_progress(self, progress_id: str, value: int, total: Optional[int] = None) -> None:
        """
        Update the progress of a displayed progress bar.
        
        Args:
            progress_id: ID of the progress bar to update
            value: Current progress value
            total: Optional new total (if changed)
            
        Raises:
            DisplayUpdateError: If update fails
            InvalidParameterError: If parameters are invalid
            IPythonNotAvailableError: If IPython environment is not detected
        """
        try:
            if not isinstance(progress_id, str):
                raise InvalidParameterError("progress_id", "string", received=type(progress_id).__name__)

            if not isinstance(value, int):
                raise InvalidParameterError("value", "integer", received=type(value).__name__)

            if total is not None and not isinstance(total, int):
                raise InvalidParameterError("total", "integer or None", received=type(total).__name__)

            if value < 0:
                raise InvalidParameterError("value", "positive integer", received=str(value))

            if total is not None and total <= 0:
                raise InvalidParameterError("total", "positive integer", received=str(total))

            self.progress_displayer.update(progress_id, value, total)
        except (InvalidParameterError, DisplayUpdateError, IPythonNotAvailableError):
            raise
        except Exception as e:
            raise DisplayUpdateError(element_id=progress_id, message=f"Failed to update progress bar: {str(e)}") from e

    def display_code(self, code: str, *,
                     style: str = 'code_block',
                     highlighting_mode: str = 'block',
                     background_color: Optional[str] = None,
                     prompt_style: Optional[str] = None,
                     animate: Optional[str] = None,
                     **inline_styles) -> None:
        """
        Display code with syntax highlighting.
        
        Args:
            code: Code text to display
            style: Named style from available styles
            highlighting_mode: 'block' for indentation-based, 'line' for line-by-line
            background_color: Custom background color override
            prompt_style: Style for code prompts (>>>, ...) if present
            animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
            **inline_styles: Additional CSS styles to apply
            
        Raises:
            CodeError: If code is not a string
            StyleNotFoundError: If specified style not found
            AnimationError: If the animation name is not valid
            DisplayEnvironmentError: If display environment is not available
        """
        try:
            self.code_displayer.display(
                code,
                style=style,
                highlighting_mode=highlighting_mode,
                background_color=background_color,
                prompt_style=prompt_style,
                animate=animate,
                **inline_styles
            )
        except (CodeError, StyleNotFoundError, AnimationError, DisplayEnvironmentError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise CodeError(f"Error displaying code: {str(e)}")

    def display_button(self, text: str, *,
                       style: str = 'default',
                       on_click: Optional[Callable] = None,
                       status_display: bool = True,
                       hover_effect: bool = True,
                       width: str = 'auto',
                       height: str = 'auto',
                       enabled: bool = True,
                       animate: Optional[str] = None,
                       position: Literal['left', 'mid', 'right'] = 'left',
                       **inline_styles) -> str:
        """
        Display an interactive button with various events and callbacks.
        
        Args:
            text: Button text
            style: Named style from available styles
            on_click: Python function to call when button is clicked
            status_display: Whether to show a status display area below button
            hover_effect: Whether to enable hover effects
            width: Button width (CSS value)
            height: Button height (CSS value)
            enabled: Whether the button is initially enabled
            animate: Animation effect from Animate.css
            position: Button alignment ('left', 'mid', 'right')
            **inline_styles: Additional CSS styles to apply
            
        Returns:
            Button ID for reference
            
        Raises:
            ButtonError: If there's an issue with the button setup
            StyleNotFoundError: If specified style is not found
            ButtonCallbackError: If there's an issue with the callback
        """
        return self.button_displayer.display(
            text,
            style=style,
            on_click=on_click,
            status_display=status_display,
            hover_effect=hover_effect,
            width=width,
            height=height,
            enabled=enabled,
            animate=animate,
            position=position,
            **inline_styles
        )

    def update_button_text(self, button_id: str, new_text: str) -> None:
        """
        Update the text of a button using JavaScript.
        
        Args:
            button_id: ID of the button to update
            new_text: New text for the button
            
        Raises:
            ButtonError: If the button cannot be updated
            IPythonNotAvailableError: If IPython environment is not detected
        """
        self.button_displayer.update_button_text(button_id, new_text)

    def enable_button(self, button_id: str, enabled: bool = True) -> None:
        """
        Enable or disable a button using JavaScript.
        
        Args:
            button_id: ID of the button to update
            enabled: Whether to enable (True) or disable (False) the button
            
        Raises:
            ButtonError: If the button cannot be updated
            IPythonNotAvailableError: If IPython environment is not detected
        """
        self.button_displayer.enable_button(button_id, enabled)

    def display_pdf(self, source: Optional[str] = None, *,
                    style: str = "default",
                    is_url: bool = False,
                    animate: Optional[str] = None,
                    **inline_styles) -> None:
        """
        Display a PDF with interactive viewer.
        
        Args:
            source: Path to PDF file, URL to PDF, or None for file picker
            style: Style name from available styles
            is_url: Whether the source is a URL
            animate: Optional animation effect
            **inline_styles: Additional CSS styles to apply
            
        Raises:
            IPythonNotAvailableError: If IPython display capabilities are not available
            PDFSourceError: If there's an error accessing the PDF file
            PDFDownloadError: If downloading a PDF from URL fails
            PDFRenderingError: If rendering the PDF fails
        """
        self.pdf_displayer.display(
            source=source,
            style=style,
            is_url=is_url,
            animate=animate,
            **inline_styles
        )

    def display_text_box(self, title: str, *,
                         captions: Optional[List[str]] = None,
                         progress: Optional[Dict[str, Any]] = None,
                         style: str = "default",
                         animate: Optional[str] = None,
                         **inline_styles) -> str:
        """
        Display a styled text box with optional components.
        
        Args:
            title: The main title/heading of the text box
            captions: List of caption paragraphs to display in order
            progress: Optional progress bar parameters:
                      {'value': int, 'max': int, 'label': str}
            style: Named style from available styles
            animate: Animation effect from Animate.css
            **inline_styles: Additional CSS styles to apply
            
        Returns:
            str: The unique ID of the text box for dynamic updates
            
        Raises:
            MissingTitleError: If no title is provided
            InvalidProgressValueError: If progress values are invalid
            StyleNotFoundError: If specified style is not found
            UnsupportedComponentError: If an unsupported component is specified
            HTMLRenderingError: If HTML content cannot be rendered
        """
        try:
            return self.text_box_displayer.display(
                title,
                captions=captions,
                progress=progress,
                style=style,
                animate=animate,
                **inline_styles
            )
        except (MissingTitleError, StyleNotFoundError, InvalidProgressValueError, 
                UnsupportedComponentError, HTMLRenderingError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise TextBoxError(f"Error displaying text box: {str(e)}")

    def update_text_box(self, text_box_id: str, *,
                        title: Optional[str] = None,
                        captions: Optional[List[str]] = None,
                        progress: Optional[Dict[str, Any]] = None) -> None:
        """
        Update an existing text box with new content.
        
        Args:
            text_box_id: The ID of the text box to update
            title: New title for the text box (if None, keeps existing title)
            captions: New captions for the text box (if None, keeps existing captions)
            progress: New progress bar parameters (if None, keeps existing progress)
            
        Raises:
            DisplayUpdateError: If the text box cannot be updated
            InvalidParameterError: If any parameters are invalid
            IPythonNotAvailableError: If IPython environment is not detected
        """
        try:
            self.text_box_displayer.update(
                text_box_id,
                title=title,
                captions=captions,
                progress=progress
            )
        except (DisplayUpdateError, InvalidParameterError, IPythonNotAvailableError) as e:
            # Pass through known exceptions
            raise
        except Exception as e:
            # Wrap unknown exceptions
            raise DisplayUpdateError(
                element_id=text_box_id,
                message=f"Failed to update text box: {str(e)}"
            )
