# Colab Print

[![PyPI version](https://img.shields.io/pypi/v/colab-print.svg)](https://pypi.org/project/colab-print/)
[![Python versions](https://img.shields.io/pypi/pyversions/colab-print.svg)](https://pypi.org/project/colab-print/)
[![License](https://img.shields.io/github/license/alaamer12/colab-print.svg)](https://github.com/alaamer12/colab-print/blob/main/LICENSE)

**Colab Print** is a Python library that enhances the display capabilities of Jupyter and Google Colab notebooks, providing beautiful, customizable HTML outputs for text, lists, dictionaries, tables, pandas DataFrames, progress bars, and interactive elements.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Display Functions](#display-functions)
  - [Text Styling](#text-styling)
  - [Content Display](#content-display)
  - [Status Feedback](#status-feedback)
  - [Data Visualization](#data-visualization)
  - [Interactive Elements](#interactive-elements)
  - [TextBox Display](#textbox-display)
  - [PDF Display](#pdf-display)
- [Styling Options](#styling-options)
- [Advanced Usage](#advanced-usage)
- [Exception Handling](#exception-handling)
- [Contributing](#contributing)
- [License](#license)

<a id="features"></a>
## Features

- 🎨 **Rich Text Styling** - Display text with predefined styles or custom CSS
- 📊 **Beautiful DataFrame Display** - Present pandas DataFrames with extensive styling options
- 📑 **Customizable Tables** - Create HTML tables with headers, rows, and custom styling
- 📜 **Formatted Lists** - Display Python lists and tuples as ordered or unordered HTML lists
- 📖 **Readable Dictionaries** - Render dictionaries as structured definition lists
- 🎭 **Extensible Themes** - Use built-in themes or create your own custom styles
- 📏 **Smart Row/Column Limiting** - Automatically display large DataFrames with sensible limits
- 🔍 **Cell Highlighting** - Highlight specific rows, columns, or individual cells in tables and DataFrames
- 📊 **Progress Tracking** - Display elegant progress bars with tqdm compatibility
- 🔄 **Graceful Fallbacks** - Works even outside Jupyter/IPython environments
- 🧩 **Structured Data Detection** - Automatic handling of nested structures, matrices, and array-like objects
- 🖱️ **Interactive Buttons** - Create clickable buttons with Python callback functions
- 📦 **Dynamic TextBoxes** - Create styled containers with real-time updates for continuous data
- ✨ **Animation Effects** - Apply beautiful animations to any displayed element
- 📊 **Mermaid Diagrams** - Render Mermaid.js diagrams with customizable styling
- 📝 **Markdown Rendering** - Display Markdown content from strings, files, or URLs
- 📄 **PDF Display** - Render PDF files with interactive viewer, page navigation, and file picker

<a id="installation"></a>
## Installation

```bash
pip install colab-print
```

<a id="quick-start"></a>
## Quick Start

```python
from colab_print import Printer, header, success, progress, button, pdf_
import pandas as pd
import time

# Use pre-configured styling functions
header("Colab Print Demo")
success("Library loaded successfully!")

# Create a printer with default styles
printer = Printer()

# Display styled text
printer.display("Hello, World!", style="highlight")

# Display a list with nested elements (automatically detected and styled)
my_list = ['apple', 'banana', ['nested', 'item'], 'cherry', {'key': 'value'}]
printer.display_list(my_list, ordered=True, style="info")

# Interactive button with callback
def on_click_handler():
    print("Button clicked!")
    return "__UPDATE_BUTTON_TEXT__: Clicked!"
    
button("Click Me", on_click=on_click_handler, animate="pulse")

# Show a progress bar
for i in progress(range(10), desc="Processing"):
    time.sleep(0.2)  # Simulate work

# Display a dictionary
my_dict = {
    'name': 'Alice', 
    'age': 30, 
    'address': {'street': '123 Main St', 'city': 'Anytown'}
}
printer.display_dict(my_dict, style="success")

# Display a simple table
headers = ["Name", "Age", "City"]
rows = [
    ["Alice", 28, "New York"],
    ["Bob", 34, "London"],
    ["Charlie", 22, "Paris"]
]
printer.display_table(headers, rows, style="default")

# Display a pandas DataFrame with styling
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [28, 34, 22],
    'City': ['New York', 'London', 'Paris']
})
printer.display_df(df, 
                  highlight_cols=['Name'],
                  highlight_cells={(0, 'Age'): "background-color: #FFEB3B;"},
                  caption="Sample DataFrame")

# Display a PDF file
pdf_("path/to/document.pdf", animate="fadeIn")
```

<a id="display-functions"></a>
## Display Functions

Colab Print provides a variety of specialized display functions for different content types and purposes.

<a id="text-styling"></a>
## Text Styling

Text styling functions help you format and display text with various emphasis styles, borders, and visual treatments to create structured, visually appealing documents.

### Text Styling Functions

| Function                                                                                     | Description                            | Example                          |
|----------------------------------------------------------------------------------------------|----------------------------------------|----------------------------------|
| <a id="header-func"></a>`header(text, *, animate=None, **override_styles)`                   | Display text as a prominent header     | `header("Main Section")`         |
| <a id="title-func"></a>`title(text, *, animate=None, **override_styles)`                     | Display text as a large centered title | `title("Document Title")`        |
| <a id="subtitle-func"></a>`subtitle(text, *, animate=None, **override_styles)`               | Display text as a subtitle             | `subtitle("Supporting info")`    |
| <a id="section-divider-func"></a>`section_divider(text, *, animate=None, **override_styles)` | Display text as a section divider      | `section_divider("New Section")` |
| <a id="subheader-func"></a>`subheader(text, *, animate=None, **override_styles)`             | Display text as a subheading           | `subheader("Subsection")`        |

```python
from colab_print import header, title, subtitle

# Simple examples
header("Main Section")
title("Document Title", animate="fadeIn")
subtitle("Supporting information", color="#9C27B0")
```

<a id="content-display"></a>
## Content Display

Content display functions provide specialized formatting for different types of content, such as code blocks, cards, quotes, and other structured elements.

### Content Display Functions

| Function                                                                         | Description                      | Example                  |
|----------------------------------------------------------------------------------|----------------------------------|--------------------------|
| <a id="code-func"></a>`code(text, *, animate=None, **override_styles)`           | Display text as a code block     | `code("print('Hello')")` |
| <a id="card-func"></a>`card(text, *, animate=None, **override_styles)`           | Display text in a card container | `card("Card content")`   |
| <a id="quote-func"></a>`quote(text, *, animate=None, **override_styles)`         | Display text as a block quote    | `quote("Quoted text")`   |
| <a id="badge-func"></a>`badge(text, *, animate=None, **override_styles)`         | Display text as a small badge    | `badge("New")`           |
| <a id="highlight-func"></a>`highlight(text, *, animate=None, **override_styles)` | Display text with emphasis       | `highlight("Important")` |
| <a id="footer-func"></a>`footer(text, *, animate=None, **override_styles)`       | Display text as a footer         | `footer("Page footer")`  |

```python
from colab_print import code, card, quote, badge

# Content examples
code("def hello():\n    print('Hello world!')")
card("This is a card with content", box_shadow="0 4px 8px rgba(0,0,0,0.2)")
quote("The best way to predict the future is to invent it.")
badge("New Feature", background_color="#9C27B0", color="white")
```

<a id="status-feedback"></a>
## Status Feedback

Status feedback functions provide visual cues about operation status, from informational messages to warnings and errors, each with appropriate styling.

### Status Feedback Functions

| Function                                                                     | Description                   | Example                 |
|------------------------------------------------------------------------------|-------------------------------|-------------------------|
| <a id="info-func"></a>`info(text, *, animate=None, **override_styles)`       | Display informational message | `info("Processing...")` |
| <a id="success-func"></a>`success(text, *, animate=None, **override_styles)` | Display success message       | `success("Completed!")` |
| <a id="warning-func"></a>`warning(text, *, animate=None, **override_styles)` | Display warning message       | `warning("Caution")`    |
| <a id="error-func"></a>`error(text, *, animate=None, **override_styles)`     | Display error message         | `error("Failed")`       |
| <a id="muted-func"></a>`muted(text, *, animate=None, **override_styles)`     | Display de-emphasized text    | `muted("Side note")`    |

```python
from colab_print import info, success, warning, error

# Status examples
info("Loading data...", animate="fadeIn")
success("Operation completed successfully!")
warning("Proceed with caution", background_color="#FFF9C4")
error("An error occurred", font_weight="bold")
```

<a id="data-visualization"></a>
## Data Visualization

Data visualization functions help you display structured data like tables, DataFrames, lists, dictionaries, and diagrams with enhanced styling and interactivity.

### Data Visualization Functions

| Function                                                                   | Description                | Example                            |
|----------------------------------------------------------------------------|----------------------------|------------------------------------|
| <a id="dfd-func"></a>`dfd(df, **display_options)`                          | Display a pandas DataFrame | `dfd(df, highlight_cols=["Name"])` |
| <a id="table-func"></a>`table(headers, rows, **table_options)`             | Display tabular data       | `table(headers, rows)`             |
| <a id="list-func"></a>`list_(items, **list_options)`                       | Display a list/array       | `list_([1, 2, 3])`                 |
| <a id="dict-func"></a>`dict_(data, **dict_options)`                        | Display a dictionary       | `dict_({"a": 1, "b": 2})`          |
| <a id="mermaid-func"></a>`mermaid(diagram, *, theme='default', **options)` | Display a Mermaid diagram  | `mermaid("graph TD; A-->B;")`      |
| <a id="md-func"></a>`md(source, *, is_url=False, **options)`               | Display Markdown content   | `md("# Title\nContent")`           |

```python
from colab_print import dfd, table, list_, dict_, mermaid
import pandas as pd

# DataFrame example
df = pd.DataFrame({
    'Name': ['Alice', 'Bob'],
    'Score': [95, 82]
})
dfd(df, highlight_cols=['Score'], caption="Test Scores")

# Table example
table(
    headers=["Name", "Score"],
    rows=[["Alice", 95], ["Bob", 82]],
    highlight_rows=[0]
)

# List example
list_([1, 2, [3, 4]], matrix_mode=True)

# Dictionary example
dict_({'user': 'Alice', 'data': {'score': 95, 'rank': 1}})

# Mermaid diagram
mermaid('''
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
''', theme='forest')
```

<a id="interactive-elements"></a>
### Interactive Elements

| Function                                                            | Description                | Example                                |
|---------------------------------------------------------------------|----------------------------|----------------------------------------|
| <a id="button-func"></a>`button(text, *, on_click=None, **options)` | Display interactive button | `button("Click Me", on_click=handler)` |
| <a id="progress-func"></a>`progress(iterable, **options)`           | Display progress bar       | `progress(range(10), desc="Loading")`  |

```python
from colab_print import button, progress, P
import time

# Button with callback
def on_click():
    print("Button clicked!")
    return "__UPDATE_BUTTON_TEXT__: Clicked!"

btn_id = button("Click Me", 
                on_click=on_click, 
                animate="pulse",
                position="mid",
                width="200px")

# Update button programmatically
P.update_button_text(btn_id, "New Text")
P.enable_button(btn_id, False)  # Disable button

# Progress bar
for i in progress(range(10), desc="Processing", color="#9C27B0"):
    time.sleep(0.2)  # Simulate work
```

<a id="textbox-display"></a>
## TextBox Display

TextBox component allows you to create styled containers with titles, captions, and progress bars. It's particularly useful for presenting information in a structured, visually appealing format, with support for dynamic updates.

### TextBox Functions

| Function                                                                                                    | Description                                  | Example                                                |
|-------------------------------------------------------------------------------------------------------------|----------------------------------------------|--------------------------------------------------------|
| <a id="text-box-func"></a>`text_box(title, *, captions=None, progress=None, style="default", **options)`    | Display a styled text box with components    | `text_box("Information", captions=["Important note"])` |
| <a id="update-text-box-func"></a>`update_text_box(text_box_id, *, title=None, captions=None, progress=None)`| Update an existing text box dynamically      | `update_text_box(box_id, captions=["Updated info"])`   |

### Basic TextBox Examples

```python
from colab_print import text_box

# Simple text box with just a title
text_box("Simple Information Box")

# Text box with captions and a specific style
text_box(
    "Warning Notice",
    captions=[
        "This operation cannot be undone.",
        "Please proceed with caution."
    ],
    style="warning"
)

# Text box with progress bar
text_box(
    "Download Status",
    captions=["Downloading important files..."],
    progress={"value": 75, "max": 100, "label": "Progress"},
    style="primary"
)

# Custom styled text box
text_box(
    "Custom Box",
    captions=["This box uses custom styling."],
    background_color="#f5f5f5",
    border="1px solid #ddd",
    border_radius="10px",
    box_shadow="0 4px 8px rgba(0,0,0,0.1)"
)
```

### Dynamic Updates Example

TextBoxes support dynamic updates, making them perfect for displaying real-time information or continuous data:

```python
import time
from colab_print import text_box, update_text_box

# Create a text box and store its ID
timer_box_id = text_box(
    "Task Timer",
    captions=["Task started just now"],
    progress={"value": 0, "max": 60, "label": "Duration"},
    style="info"
)

# Update the text box with new information every second
start_time = time.time()
for i in range(1, 11):
    time.sleep(1)  # Wait for 1 second
    elapsed = int(time.time() - start_time)
    
    # Update both captions and progress
    update_text_box(
        timer_box_id,
        captions=[f"Task running for {elapsed} seconds"],
        progress={"value": elapsed, "max": 60, "label": "Duration"}
    )

# Final update with changed title
update_text_box(
    timer_box_id,
    title="Task Complete",
    captions=["Task finished successfully!"],
    progress={"value": int(time.time() - start_time), "max": 60, "label": "Total Time"}
)
```

This example creates a real-time timer that updates both text and progress bar, demonstrating how TextBoxes can be used for monitoring ongoing processes or displaying continuously changing data.

<a id="pdf-display"></a>
### PDF Display

| Function                                                        | Description                    | Example                                  |
|-----------------------------------------------------------------|--------------------------------|------------------------------------------|
| <a id="pdf-func"></a>`pdf_(source, *, is_url=False, **options)` | Display interactive PDF viewer | `pdf_("document.pdf", animate="fadeIn")` |

```python
from colab_print import pdf_, P

# Display PDF from local file
pdf_("path/to/document.pdf")

# Display PDF from URL
pdf_("https://example.com/sample.pdf", is_url=True)

# PDF with animation and styling
pdf_("path/to/document.pdf", 
     animate="fadeIn", 
     background_color="#f5f5f5",
     border_radius="10px")

# Use file picker (no source)
pdf_()

# Using the Printer class
P.display_pdf("path/to/document.pdf")
```

The PDF viewer includes:
- Interactive page navigation with previous/next buttons
- Keyboard navigation (arrow keys)
- File picker interface when no source is provided
- Support for local files and URLs
- Responsive design and customizable styling

<a id="styling-options"></a>
## Styling Options

### Predefined Styles

Colab Print includes a variety of built-in styles for different display needs:

| Style                | Description                           |
|----------------------|---------------------------------------|
| `default`            | Clean, professional styling           |
| `header`             | Large text with top/bottom borders    |
| `title`              | Large centered title                  |
| `subtitle`           | Medium-sized italic title             |
| `highlight`          | Stand-out text with emphasis          |
| `info`               | Informational blue text               |
| `success`            | Positive green message                |
| `warning`            | Attention-grabbing yellow alert       |
| `error`              | Critical red message                  |
| `muted`              | Subtle gray text                      |
| `primary`            | Primary blue-themed text              |
| `secondary`          | Secondary purple-themed text          |
| `code_block`         | Code-like display with monospace font |
| `card`               | Card-like container with shadow       |
| `quote`              | Styled blockquote                     |
| `notice`             | Attention-drawing notice              |
| `badge`              | Compact badge-style display           |
| `interactive_button` | Clickable button style                |

### Custom Styling

You can add your own styles or override existing ones:

```python
from colab_print import Printer

printer = Printer()

# Add a new style
printer.add_style("custom", "color: purple; font-size: 20px; font-weight: bold;")
printer.display("Custom styled text", style="custom")

# Override styles inline
printer.display("Inline styled text", style="default", 
                color="teal", font_size="18px", text_decoration="underline")

# Create a reusable styled display function
my_header = printer.create_styled_display("header", color="#FF5722", font_size="24px")
my_header("First Section")
my_header("Second Section")
```

<a id="advanced-usage"></a>
## Advanced Usage

### DataFrame Display Options

The `display_df` method and `dfd()` function support numerous customization options:

```python
from colab_print import dfd
import pandas as pd

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [28, 34, 22],
    'City': ['New York', 'London', 'Paris']
})

dfd(df,
    style='default',           # Base style
    max_rows=20,               # Max rows to display
    max_cols=10,               # Max columns to display
    precision=2,               # Decimal precision for floats
    header_style="...",        # Custom header styling
    odd_row_style="...",       # Custom odd row styling
    even_row_style="...",      # Custom even row styling
    index=True,                # Show index
    width="100%",              # Table width
    caption="My DataFrame",    # Table caption
    highlight_cols=["col1"],   # Highlight columns
    highlight_rows=[0, 2],     # Highlight rows
    highlight_cells={(0,0): "..."}, # Highlight specific cells
    font_size="14px",          # Custom font size for all cells
    text_align="center")       # Text alignment for all cells
```

### Interactive Buttons

Create interactive buttons with Python callbacks (introduced in v0.5.0):

```python
from colab_print import button, P

# Define a callback function
def on_button_click():
    print("Button was clicked!")
    # Return a special string to update button text
    return "__UPDATE_BUTTON_TEXT__: Clicked!"

# Create a basic button
btn_id = button("Click Me", on_click=on_button_click)

# Update button programmatically
P.update_button_text(btn_id, "New Button Text")

# Disable the button
P.enable_button(btn_id, False)

# Create a styled button with animation
button("Fancy Button",
       on_click=on_button_click,
       animate="pulse",
       position="mid",  # 'left', 'mid', or 'right'
       width="200px",
       background_color="linear-gradient(135deg, #3498db, #9b59b6)",
       color="white",
       border_radius="30px",
       box_shadow="0 4px 8px rgba(0,0,0,0.2)")
```

### Progress Tracking

Colab Print offers powerful progress tracking with tqdm compatibility:

```python
from colab_print import progress, Printer
import time

# Simple progress bar using iterable
for i in progress(range(100), desc="Processing"):
    time.sleep(0.01)  # Do some work

# Manual progress
printer = Printer()
progress_id = printer.display_progress(total=50, desc="Manual progress")
for i in range(50):
    time.sleep(0.05)  # Do some work
    printer.update_progress(progress_id, i+1)

# Progress with customization
for i in progress(range(100), 
                 desc="Custom progress", 
                 color="#9C27B0", 
                 height="25px",
                 style="card"):
    time.sleep(0.01)

# Undetermined progress (loading indicator)
progress_id = printer.display_progress(total=None, desc="Loading...", animated=True)
time.sleep(3)  # Do some work with unknown completion time
printer.update_progress(progress_id, 100, 100)  # Mark as complete
```

### Animation Support

Apply animations to any displayed element using Animate.css:

```python
from colab_print import header, info, success, error, button

# Simple animations
header("Fade In Header", animate="fadeIn")
info("Slide Down Info", animate="slideInDown")
success("Bounce Success", animate="bounceIn")
error("Shake Error", animate="shakeX")

# Animation with duration and delay
header("Custom Animation", 
       animate="zoomIn",
       animation_duration="1.5s",
       animation_delay="0.5s")

# Button with animation
button("Pulse Button", animate="pulse", animation_iteration="infinite")
```

### The Printer Class API

<a id="printer-api"></a>
The `Printer` class is the main entry point for the library's functionality:

```python
from colab_print import Printer

# Create a printer instance
printer = Printer()

# Text display methods
printer.display(text, style="default", animate=None, **inline_styles)
printer.display_code(code, style="code_block", animate=None, **inline_styles)

# Data display methods
printer.display_list(items, ordered=False, style="default", **list_options)
printer.display_dict(data, style="default", **dict_options)
printer.display_table(headers, rows, style="default", **table_options)
printer.display_df(df, style="default", **df_options)

# Interactive elements
printer.display_progress(total, desc="", style="default", **progress_options)
printer.update_progress(progress_id, current, total=None)
printer.display_button(text, on_click=None, style="interactive_button", **button_options)
printer.update_button_text(button_id, new_text)
printer.enable_button(button_id, enabled)

# Visualization
printer.display_mermaid(diagram, theme="default", style="default", **options)
printer.display_md(source, is_url=False, style="default", animate=None, **options)
printer.display_pdf(source, is_url=False, style="default", animate=None, **options)

# Styling methods
printer.add_style(style_name, style_definition)
printer.create_styled_display(style, **default_style_overrides)
```

<a id="exception-handling"></a>
## Exception Handling

Colab Print includes a comprehensive exception hierarchy for robust error handling:

```python
from colab_print.exception import (
    ColabPrintError,        # Base exception
    StyleNotFoundError,     # When a style isn't found
    DataFrameError,         # DataFrame-related issues
    InvalidParameterError,  # Parameter validation failures
    HTMLRenderingError,     # HTML rendering problems
    ButtonError,            # Button-related issues
    PDFError,               # PDF-related issues
    # ...                   # Import More As Needed
)

try:
    printer.display("Some text", style="non_existent_style")
except StyleNotFoundError as e:
    print(f"Style error: {e}")
    
try:
    button("Test", on_click=123)  # Invalid callback
except InvalidParameterError as e:
    print(f"Parameter error: {e}")
```

<a id="contributing"></a>
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

<a href="https://github.com/alaamer12/colab-print/blob/main/CHANGELOG.md" id="changelog"></a>
## [CHANGELOG.md](https://github.com/alaamer12/colab-print/blob/main/CHANGELOG.md)

We maintain a detailed changelog following semantic versioning (e.g., v1.0.0, v1.1.0-beta) that documents all notable changes to this project. Changes are categorized as:

- **Added** - New features
- **Changed** - Changes in existing functionality 
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

See the [CHANGELOG.md](https://github.com/alaamer12/colab-print/blob/main/CHANGELOG.md) file for the full version history.

<a href="https://github.com/alaamer12/colab-print/blob/main/LICENSE" id="license"></a>
## [License](https://github.com/alaamer12/colab-print/blob/main/LICENSE)

This project is licensed under the MIT License - see the LICENSE file for details.
