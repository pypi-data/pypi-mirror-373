"""
Convenience functions for Colab Print library.

This module provides a collection of shortcut functions for displaying styled content
in Jupyter/Colab notebooks. These functions offer an easy-to-use interface to the
more comprehensive Printer class functionality without requiring direct instantiation
of a Printer object.

The functions are organized into several categories:
- Text styling: header(), title(), subtitle(), highlight(), etc.
- Content display: dfd() for DataFrames and Series, table() for tabular data, list_() for lists/arrays
- Feedback display: info(), success(), warning(), error() for status messages
- Visual elements: mermaid() for diagrams, code() for syntax highlighting
- Interactive elements: button() with callback functionality
- Progress tracking: progress() with tqdm-compatible interface
- Documentation: md() for markdown display
- File viewing: pdf_() for interactive PDF display

These functions simplify common display tasks and provide a clean, functional interface
to the library's rich display capabilities.

Example:
    ```python
    from colab_print.functions import header, info, success, table, dfd
    import pandas as pd
    
    # Display styled headers and text
    header("Data Analysis Results")
    info("Processing the dataset...")
    
    # Display a simple table
    table(
        headers=["Name", "Score", "Status"],
        rows=[
            ["Alice", 95, "Pass"],
            ["Bob", 82, "Pass"],
            ["Charlie", 65, "Fail"]
        ]
    )
    
    # Display a pandas DataFrame with highlighting
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Score": [95, 82, 65],
        "Status": ["Pass", "Pass", "Fail"]
    })
    dfd(df, highlight_cols=["Score"])
    
    # Show success message
    success("Analysis completed successfully!")
    ```
"""

# Text display shortcuts - primary display styles
from typing import Optional, Any, List, Dict, Union, Callable, Literal

import pandas as pd

from colab_print._core import Printer

P = Printer()

__all__ = [
    # Display shortcuts
    "header", "title", "subtitle", "section_divider", "subheader",
    "code", "card", "quote", "badge", "data_highlight", "footer",
    "highlight", "info", "success", "warning", "error", "muted",
    "primary", "secondary", "dfd", "table", "list_", "dict_",
    "progress", "mermaid", "md", "button", "pdf_", "text_box",
    "update_text_box"
]


def header(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a prominent header with top/bottom borders.
    
    Args:
        text: Text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='header', animate=animate, **override_styles)


def title(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a large centered title.
    
    Args:
        text: Text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='title', animate=animate, **override_styles)


def subtitle(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a medium-sized subtitle with italic styling.
    
    Args:
        text: Text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='subtitle', animate=animate, **override_styles)


def section_divider(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a section divider with bottom border.
    
    Args:
        text: Text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='section_divider', animate=animate, **override_styles)


def subheader(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a subheading with left accent border.
    
    Args:
        text: Text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='subheader', animate=animate, **override_styles)


# Content display shortcuts - specialized content formatting
def code(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a code block with monospaced font, background, and syntax highlighting.
    
    Args:
        text: Code text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties or configure highlighting options
    """
    P.display_code(text, style='code_block', animate=animate, **override_styles)


def card(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text in a card-like container with shadow and border.
    
    Args:
        text: Text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='card', animate=animate, **override_styles)


def quote(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a block quote with left border.
    
    Args:
        text: Quote text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='quote', animate=animate, **override_styles)


def badge(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a small rounded badge/label.
    
    Args:
        text: Short text to display as badge
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='badge', animate=animate, **override_styles)


def data_highlight(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text with emphasis suitable for important data points.
    
    Args:
        text: Data or numeric value to highlight
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='data_highlight', animate=animate, **override_styles)


def footer(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a footer with top border.
    
    Args:
        text: Footer text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='footer', animate=animate, **override_styles)


# Status/context display shortcuts - convey information status
def highlight(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text with standout styling to draw attention.
    
    Args:
        text: Text to highlight
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='highlight', animate=animate, **override_styles)


def info(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as informational content with blue styling.
    
    Args:
        text: Informational text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='info', animate=animate, **override_styles)


def success(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a success message with green styling.
    
    Args:
        text: Success message to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='success', animate=animate, **override_styles)


def warning(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as a warning notification with orange styling.
    
    Args:
        text: Warning message to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='warning', animate=animate, **override_styles)


def error(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text as an error message with red styling.
    
    Args:
        text: Error message to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='error', animate=animate, **override_styles)


def muted(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text with de-emphasized styling for secondary content.
    
    Args:
        text: Text to display with reduced emphasis
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='muted', animate=animate, **override_styles)


def primary(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text with primary styling for important content.
    
    Args:
        text: Primary text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='primary', animate=animate, **override_styles)


def secondary(text: str, *, animate: Optional[str] = None, **override_styles) -> None:
    """
    Display text with secondary styling for supporting content.
    
    Args:
        text: Secondary text to display
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **override_styles: Override any CSS style properties
    """
    P.display(text, style='secondary', animate=animate, **override_styles)


# Container display shortcuts - for structured data
def dfd(df: Union[pd.DataFrame, pd.Series], **display_options) -> None:
    """
    Display a pandas DataFrame or Series with enhanced styling.
    
    Args:
        df: DataFrame or Series to display
        **display_options: DataFrame display options (max_rows, max_cols, etc.)
    """
    style_options = {'style': 'df'}
    display_options = {**style_options, **display_options}
    P.display_df(df, **display_options)


def table(headers: List[str], rows: List[List[Any]], **table_options) -> None:
    """
    Display data as a formatted table.
    
    Args:
        headers: List of column headers
        rows: List of rows, each row being a list of cell values
        **table_options: Table styling options
    """
    style_options = {'style': 'table'}
    table_options = {**style_options, **table_options}
    P.display_table(headers, rows, **table_options)


# noinspection PyUnresolvedReferences,da
def list_(items: Any, **list_options) -> None:
    """
    Display a list with enhanced styling.
    
    Args:
        items: List, tuple, or any array-like object to display
        **list_options: List display options (ordered, item_style, etc.)

    Examples:
            >>> list_([1, 2, 3, 4])
            >>> list_([['a', 'b'], ['c', 'd']], matrix_mode=True)
            >>> list_(np.array([[1, 2], [3, 4]]))  # Auto-detects matrix mode
            
    Note:
        Supports automatic conversion from various array-like objects:
        - NumPy arrays: `np.array([1, 2, 3])`
        - Pandas Series/DataFrames: `pd.Series([1, 2, 3])`
        - PyTorch tensors: `torch.tensor([1, 2, 3])`
        - TensorFlow tensors: `tf.constant([1, 2, 3])`
        - JAX arrays: `jax.numpy.array([1, 2, 3])`
    """
    style_options = {'style': 'list'}
    list_options = {**style_options, **list_options}
    P.display_list(items, **list_options)


def dict_(data: Dict, **dict_options) -> None:
    """
    Display a dictionary with enhanced styling.
    
    Args:
        data: Dictionary to display
        **dict_options: Dictionary display options (key_style, value_style, etc.)
    """
    style_options = {'style': 'dict'}
    dict_options = {**style_options, **dict_options}
    P.display_dict(data, **dict_options)


def progress(iterable=None, *,
             total: Optional[int] = None,
             desc: str = "",
             style: str = "progress",
             color: str = "#3498DB",
             height: str = "20px",
             animated: bool = True,
             **inline_styles) -> Union[str, Any]:
    """
    Display a progress bar with either determined or undetermined progress.
    
    This function can be used in two ways:
    1. As a direct progress bar creator (returns progress_id)
    2. As an iterable wrapper like tqdm (returns a generator that updates progress)
    
    Args:
        iterable: Optional iterable to track progress over (list, tuple, etc.)
        total: Total number of steps or length of iterable if not provided
        desc: Description text to display with the progress bar
        style: Named style from available styles
        color: Color of the progress bar
        height: Height of the progress bar
        animated: Whether to animate the progress bar
        **inline_styles: Additional CSS styles to apply
        
    Returns:
        If iterable is None: Progress bar ID that can be used with P.update_progress()
        If iterable is provided: Generator that yields items and updates progress automatically
    """
    if iterable is not None:
        # Use as a tqdm-like wrapper
        return _progress_iter(iterable, total=total, desc=desc, style=style,
                              color=color, height=height, animated=animated,
                              **inline_styles)

    # Use as a direct progress bar creator
    return _create_progress_id(desc, style, color, height, animated, **inline_styles)


def _progress_iter(iterable, *,
                   total: Optional[int] = None,
                   desc: str = "",
                   style: str = "progress",
                   color: str = "#3498DB",
                   height: str = "20px",
                   animated: bool = True,
                   **inline_styles) -> Any:
    """Helper function to wrap an iterable with a progress bar."""
    # Determine total if not provided
    if total is None:
        total = _determine_iterable_length(iterable)

    if total is None:
        # Handle case where length cannot be determined
        return _handle_undetermined_progress(
            iterable, desc, style, color, height, animated, **inline_styles
        )
    else:
        # Handle case with known total
        return _handle_determined_progress(
            iterable, total, desc, style, color, height, animated, **inline_styles
        )


def _determine_iterable_length(iterable) -> Optional[int]:
    """Try to determine the length of an iterable."""
    try:
        return len(iterable)
    except (TypeError, AttributeError):
        return None


def _create_progress_id(desc, style, color, height, animated, **inline_styles) -> str:
    """Create a unique progress ID."""
    return P.display_progress(
        total=None,
        desc=desc,
        style=style,
        color=color,
        height=height,
        animated=animated,
        **inline_styles
    )


def _handle_undetermined_progress(iterable, desc, style, color, height, animated, **inline_styles) -> Any:
    """Handle progress tracking for iterables with unknown length."""
    progress_id = _create_progress_id(desc, style, color, height, animated, **inline_styles)

    try:
        # Yield items with undetermined progress
        for item in iterable:
            yield item

        # When finished, show as complete
        _finalize_progress(progress_id, 100, 100)
    except Exception:
        # Ensure progress is finalized even if iteration fails
        _finalize_progress(progress_id, 100, 100)
        raise


def _handle_determined_progress(iterable, total, desc, style, color, height, animated, **inline_styles) -> Any:
    """Handle progress tracking for iterables with known length."""
    progress_id = _create_progress_id(desc, style, color, height, animated, **inline_styles)

    # Yield items while updating progress
    i = 0
    try:
        for i, item in enumerate(iterable):
            P.update_progress(progress_id, i + 1, total)
            yield item
    except Exception:
        # Ensure the progress bar shows the error state
        _finalize_progress(progress_id, i + 1, total)  # Show partial completion
        raise


def _finalize_progress(progress_id, current, total):
    """Update progress to its final state."""
    P.update_progress(progress_id, current, total)


def mermaid(diagram: str, *,
            theme: str = 'default',
            style: str = 'default',
            custom_css: Optional[Dict[str, str]] = None,
            **inline_styles) -> None:
    """
    Display a Mermaid diagram with syntax highlighting.
    
    Args:
        diagram: Mermaid diagram code or file path
        theme: Mermaid theme ('default', 'forest', 'dark', 'neutral')
        style: Named style from available styles for the container
        custom_css: Optional dictionary mapping Mermaid CSS selectors to style properties
        **inline_styles: Additional CSS styles to apply to the container
        
    Examples:
        >>> # Display a simple diagram
        >>> mermaid('''
        ...    graph TD;
        ...    A-->B;
        ...    A-->C;
        ...    B-->D;
        ...    C-->D;
        ... '''
        ... )
        
        >>> # Read from a file
        >>> mermaid('diagrams/flow.mmd', theme='dark')
        
        >>> # Apply custom CSS
        >>> mermaid(diagram, custom_css={
        ... '.node rect': 'fill: #f9f9f9; stroke: #333; stroke-width: 2px;',
        ... '.edgeLabel': 'background-color: white; padding: 2px;'
        ... })
    """
    P.display_mermaid(
        diagram,
        theme=theme,
        style=style,
        custom_css=custom_css,
        **inline_styles
    )


def md(source: str, *,
       is_url: bool = False,
       style: str = 'default',
       animate: Optional[str] = None,
       **inline_styles) -> None:
    """
    Display markdown content from a URL or file with read more/less functionality.
    
    Args:
        source: The URL or file path of the markdown file to display
        is_url: If True, treat source as a URL; if False, treat as a file path
        style: Named style from available styles
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **inline_styles: Additional CSS styles to apply to the container
        
    Examples:
        >>> # Display markdown from a URL
        >>> md('https://raw.githubusercontent.com/user/repo/main/README.md', is_url=True)
        
        >>> # Display markdown from a file
        >>> md('diagrams/README.md', is_url=False, theme='dark')
    """
    P.display_md(
        source,
        is_url=is_url,
        style=style,
        animate=animate,
        **inline_styles
    )


def button(text: str, *,
           on_click: Optional[Callable] = None,
           style: str = "interactive_button",
           status_display: bool = True,
           hover_effect: bool = True,
           width: str = 'auto',
           height: str = 'auto',
           enabled: bool = True,
           animate: Optional[str] = None,
           position: Literal['left', 'mid', 'right'] = 'left',
           **inline_styles) -> str:
    """
    Display an interactive button with customizable events and Python callbacks.
    
    Args:
        text: Button text
        on_click: Python function to call when button is clicked
        style: Named style from available styles
        status_display: Whether to show a status display area below button
        hover_effect: Whether to enable hover effects
        width: Button width (CSS value)
        height: Button height (CSS value)
        enabled: Whether the button is initially enabled
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        position: Button alignment ('left', 'mid', 'right')
        **inline_styles: Additional CSS styles to apply
    
    Returns:
        Button ID that can be used with update_button_text() and enable_button()
    
    Examples:
        >>> def on_button_click():
        ...     print("Button was clicked!")
        ...     return "__UPDATE_BUTTON_TEXT__: Button Clicked!"
        >>> 
        >>> # Create a button with a click handler
        >>> btn_id = button("Click Me", on_click=on_button_click)
        >>> 
        >>> # Update button text programmatically
        >>> from colab_print import P
        >>> P.update_button_text(btn_id, "New Button Text")
        >>> 
        >>> # Disable the button
        >>> P.enable_button(btn_id, False)
    
    Notes:
        - To update button text from a callback, return a string with the format:
          "__UPDATE_BUTTON_TEXT__: New Text"
        - Button callbacks only work in Google Colab environment
        - Status display shows events like clicks, hover, and callback results
    """
    return P.display_button(
        text,
        on_click=on_click,
        style=style,
        status_display=status_display,
        hover_effect=hover_effect,
        width=width,
        height=height,
        enabled=enabled,
        animate=animate,
        position=position,
        **inline_styles
    )


def pdf_(source: Optional[str] = None, *,
         is_url: bool = False,
         style: str = "default",
         animate: Optional[str] = None,
         **inline_styles) -> None:
    """
    Display an interactive PDF viewer in Jupyter/Colab notebook.
    
    This function provides an interactive PDF viewer with page navigation controls.
    It can display PDFs from local files, URLs, or via a file picker interface.
    
    Args:
        source: Path to PDF file, URL to PDF, or None to show file picker
        is_url: Set to True if source is a URL, False if it's a local file path
        style: Named style from available styles
        animate: Animation effect from Animate.css (e.g., 'fadeIn', 'bounceOut')
        **inline_styles: Additional CSS styles to apply to the container
        
    Examples:
        >>> # Display with file picker
        >>> pdf_()
        
        >>> # Display from URL
        >>> pdf_("https://example.com/document.pdf", is_url=True)
        
        >>> # Display from local file
        >>> pdf_("documents/report.pdf")
        
        >>> # With custom styling
        >>> pdf_("documents/report.pdf", style="card", 
        ...       animate="fadeIn", width="100%", height="800px")
    
    Note:
        - Navigation controls include Previous/Next buttons and keyboard arrow keys
        - File picker allows users to select a different PDF at any time
        - For URLs, the file is downloaded to a temporary location first
        - PDF.js library is used for rendering PDFs in the browser
    """
    P.display_pdf(
        source=source,
        is_url=is_url,
        style=style,
        animate=animate,
        **inline_styles
    )


def text_box(title: str, *,
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
        
    Examples:
        >>> # Basic text box
        >>> text_box("Important Information", 
        ...          captions=["This is important to know."],
        ...          style="info")
        >>>
        >>> # Text box with progress bar
        >>> text_box("Download Status", 
        ...          captions=["Downloading files..."], 
        ...          progress={"value": 75, "max": 100, "label": "Progress"})
        >>>
        >>> # Text box with animation
        >>> text_box("New Feature", 
        ...          captions=["Check out our newest feature!"], 
        ...          style="success", 
        ...          animate="fadeIn")
        >>>
        >>> # Creating a text box and getting its ID for updates
        >>> box_id = text_box("Processing Files",
        ...                    captions=["Starting process..."],
        ...                    progress={"value": 0, "max": 100, "label": "Progress"})
        >>> # Later update the text box
        >>> update_text_box(box_id, 
        ...                 captions=["50% complete..."],
        ...                 progress={"value": 50, "max": 100, "label": "Progress"})
    """
    return P.display_text_box(
        title,
        captions=captions,
        progress=progress,
        style=style,
        animate=animate,
        **inline_styles
    )


def update_text_box(text_box_id: str, *,
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
            
    Examples:
        >>> # Create a text box with an ID
        >>> box_id = text_box("Processing Files",
        ...                    captions=["Starting process..."],
        ...                    progress={"value": 0, "max": 100, "label": "Progress"})
        >>>
        >>> # Update just the captions
        >>> update_text_box(box_id, captions=["Processing files..."])
        >>>
        >>> # Update progress bar only
        >>> update_text_box(box_id, progress={"value": 50, "max": 100, "label": "Progress"})
        >>>
        >>> # Update both captions and progress
        >>> update_text_box(box_id, 
        ...                 captions=["Almost done!"],
        ...                 progress={"value": 90, "max": 100, "label": "Progress"})
        >>>
        >>> # Update the title
        >>> update_text_box(box_id, title="File Processing Complete")
    """
    P.update_text_box(
        text_box_id,
        title=title,
        captions=captions,
        progress=progress
    )