"""
Colab Print - Enhanced display utilities for Jupyter/Colab notebooks.

This module provides a comprehensive set of display utilities for creating beautiful, 
customizable HTML outputs in Jupyter and Google Colab notebooks. It transforms plain
data into visually appealing, styled content to improve notebook readability and presentation.

Features:
- 🎨 Rich text styling with 20+ predefined styles (headers, titles, cards, quotes, etc.)
- 📊 Beautiful DataFrame display with extensive customization options
- 📑 Customizable tables with header/row styling and cell highlighting
- 📜 Formatted lists and nested structures with ordered/unordered options
- 📖 Structured dictionary display with customizable key/value styling
- 🎭 Extensible theming system for consistent visual styling
- 📏 Smart row/column limiting for large DataFrames
- 🔍 Targeted highlighting for specific rows, columns, or individual cells
- 🔄 Graceful fallbacks when used outside of notebook environments
- 🔘 Interactive buttons with customizable callbacks and event handling

Content Display Methods:
- text: printer.display(text, style="default", **inline_styles)
- tables: printer.display_table(headers, rows, style="default", **table_options)
- DataFrames: printer.display_df(df, style="default", highlight_cols=[], **options)
- lists: printer.display_list(items, ordered=False, style="default", **options)
- dictionaries: printer.display_dict(data, style="default", **options)
- progress: printer.display_progress(total, desc="", style="default", **options)
- mermaid: printer.display_mermaid(diagram_code, style="default", **options)
- buttons: printer.display_button(text, on_click=None, style="default", **options)


Convenience Functions:
- Text styling: header(), title(), subtitle(), highlight(), info(), success(), etc.
- Content display: dfd(), table(), list_(), dict_()
- Feedback display: progress(), data_highlight(), error(), warning(), success(), etc.
- Mermaid diagrams: mermaid(diagram_code)
- Code display: code(code_string)
- Interactive elements: button(text, on_click=None)

Basic Usage:
    from colab_print import Printer, header, success, dfd, button
    
    # Object-oriented style
    printer = Printer()
    printer.display("Hello World!", style="highlight")
    
    # Shortcut functions
    header("Main Section")
    success("Operation completed successfully")
    
    # Content-specific display
    df = pandas.DataFrame(...)
    dfd(df, highlight_cols=["important_column"], max_rows=20)
    
    # Interactive button with callback
    def on_click():
        print("Button clicked!")
        return "__UPDATE_BUTTON_TEXT__: Clicked!"
    
    button_id = button("Click Me", on_click=on_click)
See [example.py](https://github.com/alaamer12/colab-print/blob/main/example.py) for complete style list and customization options.
"""

from colab_print._core import Printer
from colab_print.functions import (code, dfd, card, info, badge, dict_, error,
                                   list_, muted, quote, table, title, header,
                                   footer, mermaid, primary, success, warning,
                                   progress, data_highlight, secondary, section_divider,
                                   highlight, subheader, subtitle, button, md, pdf_)

from colab_print.utilities import (DEFAULT_THEMES, SPECIAL_STYLES, VALID_ANIMATIONS,
                                   process_animation_class, is_in_notebook,
                                   DFDisplayParams, TableDisplayParams)

P = Printer()

__version__ = "0.7.0"
__author__ = "alaamer12"
__email__ = "ahmedmuhmmed239@gmail.com"
__license__ = "MIT"
__keywords__ = ["jupyter",
                "colab",
                "display",
                "dataframe",
                "html",
                "visualization",
                "notebook",
                "presentation",
                "rich-text",
                "tables",
                "pandas",
                "ipython",
                "progress-bar",
                "syntax-highlighting",
                "markdown",
                "mermaid",
                "code-display",
                "matrix",
                "nested-lists",
                "dictionary-display",
                "formatting",
                "styling",
                "output",
                "data-science",
                "interactive",
                "tqdm-compatible",
                "array-visualization",
                "numpy",
                "torch",
                "tensorflow",
                "jax",
                "theme-customization",
                "animation",
                "buttons",
                "callbacks",
                "event-handling",
                "graceful-fallbacks",
                "styling",
                "customization",
                "custom-styles",
                "pdf",
                "blob",
                "base64",
                "dataframe",
                "dataframe-display",
                "dataframe-styles",
                ]
__description__ = "Enhanced display utilities for Jupyter/Colab notebooks."
__url__ = "https://github.com/alaamer12/colab-print"
__author_email__ = "ahmedmuhmmed239@gmail.com"
__all__ = [
    # Classes
    "Printer",
    "DFDisplayParams",
    "TableDisplayParams",

    # Functions
    "code", "dfd", "card", "info", "badge", "dict_", "error",
    "list_", "muted", "quote", "table", "title", "header",
    "footer", "mermaid", "primary", "success", "warning",
    "progress", "data_highlight", "secondary", "section_divider",
    "highlight", "subheader", "subtitle", "button", "md", "pdf_",

    # Utilities
    "process_animation_class", "is_in_notebook",

    # Constants
    "DEFAULT_THEMES",
    "SPECIAL_STYLES",
    "VALID_ANIMATIONS",
]
