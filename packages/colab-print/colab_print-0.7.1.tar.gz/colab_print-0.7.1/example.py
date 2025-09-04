# -*- coding: utf-8 -*-
"""
Example usage of the colab-print library.

This script demonstrates various features of the colab-print library for displaying
styled text, lists, dictionaries, tables, and pandas DataFrames in environments
that support IPython display (like Jupyter notebooks or Google Colab).
"""

import time

import numpy as np  # Added for array examples
import pandas as pd

from colab_print import (
    Printer, header, title, subtitle, section_divider, subheader,
    code, card, quote, badge, data_highlight, footer,
    highlight, info, success, warning, error, muted, primary, secondary,
    dfd, table, list_, dict_, progress, mermaid, md, pdf_, text_box
)

P = Printer()


def demo_printer_class():
    """Demo using the Printer class directly."""

    print("=== DEMO: Using Printer Class Directly ===")
    P = Printer()
    print(f"Available styles: {P.get_available_styles()}")

    # --- Text Display --- 
    print("\n--- Text Display Examples ---")
    P.display("This is default text.")
    P.display("This is highlighted text.", style="highlight")
    P.display("This is info text.", style="info")
    P.display("This is success text.", style="success")
    P.display("This is warning text.", style="warning")
    P.display("This is error text.", style="error")
    P.display("This is muted text.", style="muted")
    P.display("Inline style example.", style="info", font_weight="bold", text_decoration="underline")

    # --- List Display --- 
    print("\n--- List Display Examples ---")
    simple_list = ['Apple', 'Banana', 'Cherry']
    nested_list = ['Fruit', ['Apple', 'Banana'], 'Vegetable', ['Carrot', 'Broccoli']]
    P.display_list(simple_list, style="success", item_style="padding-left: 15px;")
    P.display_list(nested_list, ordered=True, style="default")
    P.display_list(('Tuple', 'Item 1', 'Item 2'), style="warning")  # Also works with tuples

    # --- Dictionary Display --- 
    print("\n--- Dictionary Display Examples ---")
    simple_dict = {'Name': 'Bob', 'Role': 'Developer', 'Experience (Years)': 5}
    nested_dict = {
        'Project': 'Colab Print',
        'Version': '0.1.0',
        'Author': {'Name': 'Alaa', 'Contact': 'test@example.com'},
        'Features': ['Text', 'List', 'Dict', 'Table', 'DataFrame']
    }
    P.display_dict(simple_dict, style="info")
    P.display_dict(nested_dict, style="default", key_style="color: blue;", value_style="color: green;")

    # --- Table Display --- 
    print("\n--- Table Display Examples ---")
    headers = ["ID", "Product", "Price", "In Stock"]
    rows = [
        [101, "Laptop", 1200.50, True],
        [102, "Keyboard", 75.00, False],
        [103, "Mouse", 25.99, True]
    ]
    P.display_table(headers, rows, style="default", caption="Inventory")
    P.display_table(headers, rows, style="highlight", width="80%")

    # --- DataFrame Display --- 
    print("\n--- DataFrame Display Examples ---")
    data = {
        'StudentID': ['S101', 'S102', 'S103', 'S104', 'S105'],
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Score': [85.5, 92.0, 78.8, 88.1, 95.2],
        'Major': ['CompSci', 'Physics', 'Math', 'CompSci', 'Physics']
    }
    df = pd.DataFrame(data)

    P.display_df(df, caption="Student Scores")
    P.display_df(df, style="info", max_rows=3, precision=1, caption="Limited Rows & Precision")
    P.display_df(df, style="success",
                 index=False,
                 highlight_cols=['Name', 'Score'],
                 highlight_rows={1: "background-color: #DFF0D8;"},  # Bob
                 highlight_cells={(4, 'Score'): "background-color: yellow; font-weight: bold;"},  # Eve's score
                 caption="Styled DataFrame without Index")

    # --- Custom Styles & Themes --- 
    print("\n--- Custom Style & Theme Examples ---")

    # Add a single custom style
    P.add_style("custom_blue", "color: navy; border: 1px solid blue; padding: 5px;")
    P.display("This uses a custom added style.", style="custom_blue")
    print(f"Updated styles: {P.get_available_styles()}")

    # Initialize a new Printer with additional themes
    custom_themes = {
        'dark_mode': 'color: #E0E0E0; background-color: #282C34; font-family: Consolas, monospace;',
        'report': 'font-family: "Times New Roman", serif; font-size: 14px; color: #333;'
    }
    themed_printer = Printer(additional_styles=custom_themes)
    themed_printer.display("Dark mode style text.", style="dark_mode")
    themed_printer.display_dict({'report_section': 'Results'}, style="report")


def demo_global_shortcuts():
    """Demo using the global shortcut functions."""

    print("\n=== DEMO: Using Global Shortcut Functions ===")

    # --- Heading & Structure Display ---
    print("\n--- Heading & Structure Display ---")
    title("Colab Print Demo")
    subtitle("A showcase of styling capabilities")
    header("Main Section Header")
    subheader("Important Subsection")
    section_divider("Section Break")

    # --- Content formatting ---
    print("\n--- Content Formatting ---")
    card("This is a card with important content that stands out from the rest of the text")
    quote("The best way to predict the future is to invent it. - Alan Kay")
    code("import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())")

    # Code with syntax highlighting (basic)
    code("""def example_function(param):
    \"\"\"An example function with a docstring.\"\"\"
    if param > 10:
        return param * 2
    else:
        return param""", highlighting_mode="block")

    # --- Status indicators ---
    print("\n--- Status Indicators ---")
    info("This is an informational message")
    success("Operation completed successfully!")
    warning("Please be cautious with this action")
    error("An error occurred during processing")
    muted("This is less important information")

    # --- Special elements ---
    print("\n--- Special Elements ---")
    data_highlight("99.8%")
    badge("NEW")
    badge("PRO", background_color="#9C27B0")  # Style override example
    primary("Primary action button")
    secondary("Secondary option")
    highlight("This text needs attention", font_size="20px")  # Style override example
    footer("© 2023 Colab Print Project")

    # --- Data Container Display ---
    print("\n--- Data Container Display ---")

    # Sample data
    sample_dict = {
        "key1": "value1",
        "key2": "value2",
        "nested": {"a": 1, "b": 2}
    }

    sample_list = ["Item 1", "Item 2", ["Nested 1", "Nested 2"]]

    headers = ["Name", "Value", "Description"]
    rows = [
        ["Alpha", 100, "First item in list"],
        ["Beta", 200, "Second item in list"],
        ["Gamma", 300, "Third item in list"]
    ]

    data = {
        'Category': ['A', 'B', 'C', 'D'],
        'Value1': [10, 20, 30, 40],
        'Value2': [100, 90, 80, 70]
    }
    df = pd.DataFrame(data)

    # Display with the shortcuts
    dict_(sample_dict, key_style="color: #1565C0; font-weight: bold;")
    list_(sample_list, ordered=True)
    table(headers, rows, caption="Sample Table Data")
    dfd(df, max_rows=3, caption="Sample DataFrame")

    # --- Style Override Examples ---
    print("\n--- Style Override Examples ---")
    header("Default Header")
    header("Custom Color Header", color="#E53935")
    header("Larger Header", font_size="32px")

    info("Default Info Message")
    info("Custom Info", background_color="rgba(3, 169, 244, 0.1)", border_radius="10px")

    card("Default Card")
    card("Custom Card", box_shadow="0 4px 8px rgba(0,0,0,0.2)", border_left="5px solid #673AB7")


def demo_progress_bars():
    """Demo using the progress bar feature."""

    print("\n--- Progress Bar Examples ---")

    # Determined progress bar example (manual style)
    print("\n--- Determined Progress Bar (Manual) ---")
    progress_id = progress(total=100, desc="Loading Data", color="#4a6fa5", height="25px")
    for i in range(101):
        P.update_progress(progress_id=progress_id, value=i)
        time.sleep(0.01)  # Simulate work being done

    # TQDM-like functionality (Automatic progress with iterables)
    print("\n--- TQDM-like Progress (Automatic) ---")

    # Example 1: With a list - automatically calculates total
    items = list(range(50))
    for item in progress(items, desc="Processing List"):
        time.sleep(0.02)  # Simulate work being done

    # Example 2: With a custom total
    items = range(100)
    for item in progress(items, total=100, desc="Processing Range", color="#2ecc71"):
        if item % 3 == 0:  # Only process every third item
            time.sleep(0.02)

    # Example 3: With a generator that doesn't have len() - undetermined progress
    def my_generator():
        for i in range(30):
            yield i

    for item in progress(my_generator(), desc="Processing Generator", color="#e74c3c"):
        time.sleep(0.05)

    # Traditional undetermined progress example
    print("\n--- Undetermined Progress Bar ---")
    progress_id2 = progress(desc="Processing Data", style="progress", color="#8E44AD", height="20px", animated=True)

    # Simulate some processing work
    time.sleep(2)

    # Important: Replace the undetermined progress with a completed one
    # This prevents the animation from running forever
    P.update_progress(progress_id2, 100, 100)

    # Alternative ways to show completion
    print("\n--- Completing Progress Examples ---")

    # Style 1: Show partial completion
    progress_id3 = progress(total=100, desc="Downloading Files", color="#16a085", height="20px")
    for i in range(0, 65, 5):
        P.update_progress(progress_id3, i)
        time.sleep(0.05)
    success("Download partially completed (65%)")

    # Style 2: Show error state
    progress_id4 = progress(total=100, desc="Installing Packages", color="#c0392b", height="20px")
    for i in range(0, 85, 5):
        P.update_progress(progress_id4, i)
        time.sleep(0.05)
    error("Installation failed at 85%")


def demo_enhanced_lists():
    """Demo showcasing the enhanced list display features."""

    title("Enhanced List Display Features")
    subtitle("Showcasing new styling and formatting capabilities")

    # Create a Printer instance for custom configurations
    P = Printer()

    # --- Simple color-coded nested lists ---
    header("Color-coded Nested Lists")

    nested_list = [
        "Top Level",
        ["Level 1 - Item 1", "Level 1 - Item 2"],
        "Another Top Level",
        ["Level 1 - Item 3",
         ["Level 2 - Nested A", "Level 2 - Nested B",
          ["Level 3 - Deep Nested", "Level 3 - Another Deep"]
          ]
         ],
        "Final Top Level"
    ]

    info("Default color-coded nesting scheme:")
    list_(nested_list)

    # --- Custom nesting colors ---
    subheader("Custom Nesting Colors")

    # Use warm color scheme (reds to yellows)
    warm_colors = [
        "#E53935",  # Red
        "#F57C00",  # Orange
        "#FDD835",  # Yellow
        "#7CB342",  # Light Green
        "#039BE5",  # Light Blue
    ]

    info("Warm color scheme for nesting:")
    list_(nested_list, nesting_colors=warm_colors)

    # --- Matrix display ---
    header("Matrix Display")

    # Simple matrix (2D array)
    matrix_data = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]

    info("Simple 2D matrix (automatically detected):")
    list_(matrix_data)

    # Create a NumPy matrix
    np_matrix = np.array([
        [1.2, 3.4, 5.6],
        [7.8, 9.0, 1.2],
        [3.4, 5.6, 7.8],
        [9.0, 1.2, 3.4]
    ])

    info("NumPy matrix with auto-detection:")
    list_(np_matrix)

    # Force list display for 2D data
    info("Forcing list display for matrix data:")
    list_(matrix_data, matrix_mode=False)

    # --- Array-like objects ---
    header("Array-like Objects Support")

    # NumPy array (1D)
    np_array = np.array([10, 20, 30, 40, 50])
    info("NumPy 1D array:")
    list_(np_array)

    # Pandas Series
    pd_series = pd.Series([1, 2, 3, 4, 5], index=['a', 'b', 'c', 'd', 'e'])
    info("Pandas Series:")
    list_(pd_series)

    # Creating a pandas DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    info("Pandas DataFrame (displayed as matrix):")
    list_(df)

    # --- Complex nested structures ---
    header("Complex Nested Structures")

    # Combined nested structure with different types
    complex_structure = [
        "Mixed Types Example",
        {"dict_in_list": "value", "nested_dict": {"a": 1, "b": 2}},
        ["List in list", ["Deeper", np.array([1, 2, 3])]],
        pd.Series([10, 20, 30], index=['x', 'y', 'z']),
        [
            [1, 2, 3],
            [4, 5, 6]
        ]
    ]

    info("Complex nested structure with different data types:")
    list_(complex_structure)

    # --- Generator and iterator examples ---
    header("Generators and Iterators")

    # Generator example
    def sample_generator(n):
        for i in range(n):
            yield f"Generated item {i}"

    info("Generator output:")
    list_(sample_generator(5))

    # Iterator example (map object)
    map_iterator = map(lambda x: x * 10, range(5))
    info("Map iterator output:")
    list_(map_iterator)


def demo_mermaid_diagrams():
    """Demo showcasing the Mermaid diagram rendering feature."""

    title("Mermaid Diagram Examples")
    subtitle("Rendering diagrams with the new mermaid feature")

    # --- Flowchart Example ---
    header("Flowchart Diagram")

    flow_diagram = """
    graph TD
        A[Start] --> B{Is it working?}
        B -->|Yes| C[Great!]
        B -->|No| D[Debug]
        D --> B
        C --> E[Continue]
        E --> F[End]
    """

    info("Basic flowchart diagram with default theme:")
    mermaid(flow_diagram)

    # --- Sequence Diagram Example ---
    header("Sequence Diagram")

    sequence_diagram = """
    sequenceDiagram
        participant User
        participant Client
        participant Server
        participant Database
        
        User->>Client: Submit Form
        Client->>Server: POST /api/data
        Server->>Database: Insert Data
        Database-->>Server: Confirm Insert
        Server-->>Client: 201 Created
        Client-->>User: Show Success
    """

    info("Sequence diagram with forest theme:")
    mermaid(sequence_diagram, theme="forest")

    # --- Class Diagram Example ---
    header("Class Diagram")

    class_diagram = """
    classDiagram
        class Animal {
            +String name
            +int age
            +makeSound()
        }
        class Dog {
            +fetch()
        }
        class Cat {
            +scratch()
        }
        Animal <|-- Dog
        Animal <|-- Cat
    """

    info("Class diagram with dark theme and custom container style:")
    mermaid(class_diagram, theme="dark", background_color="#282c34", padding="20px", border_radius="8px")

    # --- Gantt Chart Example ---
    header("Gantt Chart")

    gantt_chart = """
    gantt
        title Project Timeline
        dateFormat  YYYY-MM-DD
        section Planning
        Requirements     :done,    des1, 2023-01-01, 2023-01-05
        Design           :active,  des2, 2023-01-06, 2023-01-10
        section Development
        Implementation   :         des3, after des2, 2023-01-20
        Testing          :         des4, after des3, 7d
        Deployment       :         des5, after des4, 3d
    """

    info("Gantt chart with neutral theme:")
    mermaid(gantt_chart, theme="neutral")

    # --- State Diagram Example ---
    header("State Diagram")

    state_diagram = """
    stateDiagram-v2
        [*] --> Still
        Still --> [*]
        Still --> Moving
        Moving --> Still
        Moving --> Crash
        Crash --> [*]
    """

    info("State diagram with custom styling:")
    mermaid(state_diagram, border_left="4px solid #3498db")

    # --- Entity Relationship Diagram ---
    header("Entity Relationship Diagram")

    er_diagram = """
    erDiagram
        CUSTOMER ||--o{ ORDER : places
        ORDER ||--|{ LINE-ITEM : contains
        CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
    """

    info("Entity relationship diagram:")
    mermaid(er_diagram)

    # --- Using Printer class directly ---
    header("Using Printer Class")

    pie_chart = """
    pie title Product Distribution
        "Electronics" : 35
        "Clothing" : 25
        "Food" : 20
        "Books" : 15
        "Other" : 5
    """

    info("Using the Printer class to display a pie chart:")
    P = Printer()
    P.display_mermaid(pie_chart, theme="default", style="card")


def display_mermaid_2():
    # Create a simple diagram file for demonstration
    import os
    os.makedirs('examples/diagrams', exist_ok=True)

    with open('examples/diagrams/flow.mmd', 'w') as f:
        f.write('''
    graph TD
        A[Start] --> B{Is it working?}
        B -->|Yes| C[Great!]
        B -->|No| D[Debug]
        D --> B
    ''')

    # Example 1: Basic diagram display
    print("Example 1: Basic diagram display")
    mermaid('''
    graph TD
        A --> B
        A --> C
        B --> D
        C --> D
    ''')

    # Example 2: Reading from a file
    print("\nExample 2: Reading diagram from a file")
    mermaid('examples/diagrams/flow.mmd', theme='forest')

    # Example 3: Using custom CSS
    print("\nExample 3: Applying custom CSS")
    custom_styles = {
        '.node rect': 'fill: #f0f8ff; stroke: #4682b4; stroke-width: 2px;',
        '.node circle': 'fill: #f0f8ff; stroke: #4682b4; stroke-width: 2px;',
        '.node polygon': 'fill: #f0f8ff; stroke: #4682b4; stroke-width: 2px;',
        '.node.default > rect': 'fill: #e6f7ff;',
        '.edgeLabel': 'background-color: #ffffff; padding: 4px; border-radius: 4px;',
        '.edgePath .path': 'stroke: #4682b4; stroke-width: 2px;'
    }

    mermaid('''
    graph TD
        A[Start] --> B{Decision}
        B -->|Option 1| C[Result 1]
        B -->|Option 2| D[Result 2]
        C --> E[End]
        D --> E
    ''', theme='default', custom_css=custom_styles)

    # Example 4: Using P instance with custom CSS
    print("\nExample 4: Using Printer instance with custom CSS")
    P = Printer()

    # Custom styles focused on dark theme
    dark_styles = {
        '.node rect': 'fill: #2d2d2d; stroke: #6a9ec0; stroke-width: 2px;',
        '.node circle': 'fill: #2d2d2d; stroke: #6a9ec0; stroke-width: 2px;',
        '.node polygon': 'fill: #2d2d2d; stroke: #6a9ec0; stroke-width: 2px;',
        '.edgeLabel': 'color: #ffffff; background-color: #2d2d2d; padding: 4px;',
        '.edgePath .path': 'stroke: #6a9ec0; stroke-width: 2px;',
        '.label': 'color: #ffffff;',
        '.nodeLabel': 'color: #ffffff;'
    }

    P.display_mermaid('''
    sequenceDiagram
        participant User
        participant System
        User->>System: Action
        System-->>User: Response
        User->>System: Another Action
        System-->>User: Another Response
    ''', theme='dark', custom_css=dark_styles)

    print("\nAll examples completed.")


def demo_enhanced_code_display():
    """Demo showcasing the enhanced code display features."""

    title("Enhanced Code Display Features")
    subtitle("Showcasing Python prompt detection and syntax highlighting")

    # --- Basic code display ---
    header("Basic Code Display")

    simple_code = """def greet(name):
    \"\"\"Simple greeting function\"\"\"
    return f"Hello, {name}!"

print(greet("World"))"""

    info("Basic code display with block-level highlighting:")
    code(simple_code, highlighting_mode="block")

    info("Basic code display with gradient highlighting:")
    code(simple_code, highlighting_mode="gradient")

    # --- Python REPL prompt recognition ---
    header("Python REPL Prompt Recognition")

    repl_code = """>>> x = 5
>>> y = 10
>>> x + y
15
>>> for i in range(3):
...     print(i)
...     i += 1
0
1
2
>>> def factorial(n):
...     if n <= 1:
...         return 1
...     else:
...         return n * factorial(n-1)
... 
>>> factorial(5)
120"""

    info("Code with Python REPL prompts (block highlighting):")
    code(repl_code, highlighting_mode="block")

    info("Code with Python REPL prompts (gradient highlighting):")
    code(repl_code, highlighting_mode="gradient",
         background_color="#f8f9fa")

    # --- Shell prompt recognition ---
    header("Shell Prompt Recognition")

    shell_code = """> ls -la
> cd /home/user
> mkdir new_folder
> python script.py
Processing...
Done!
> echo "Hello World"
Hello World"""

    info("Code with shell prompts:")
    code(shell_code, highlighting_mode="block")

    # --- Mixed prompts and customization ---
    header("Mixed Prompts and Customization")

    mixed_code = """# Python example
>>> import random
>>> random.randint(1, 100)
42

# Shell commands
> pip install pandas
Successfully installed pandas
> python
>>> import pandas as pd
>>> df = pd.DataFrame({"A": [1, 2, 3]})
>>> df
   A
0  1
1  2
2  3"""

    info("Mixed Python and shell prompts with custom styling:")
    code(mixed_code,
         highlighting_mode="block",
         background_color="#2d2d2d",
         color="#f8f8f2",
         font_family="'Fira Code', monospace",
         border_radius="8px",
         line_height="1.5")

    # --- Complex code example ---
    header("Complex Code Example")

    complex_code = """# A more complex example with nested indentation
def process_data(data):
    \"\"\"Process a data structure with nested elements.\"\"\"
    if not data:
        return None
    
    results = []
    for item in data:
        if isinstance(item, dict):
            # Process dictionaries
            processed = {}
            for key, value in item.items():
                if isinstance(value, list):
                    processed[key] = [x * 2 for x in value]
                else:
                    processed[key] = str(value).upper()
            results.append(processed)
        elif isinstance(item, list):
            # Process lists
            results.append([
                x + 1 if isinstance(x, int) else x
                for x in item
            ])
        else:
            # Process primitives
            results.append(item)
    
    return results
"""

    info("Complex code with block-level highlighting to show indentation:")
    code(complex_code, highlighting_mode="block")

    # --- Error handling example ---
    header("Error Cases (Try in a notebook)")

    info("Examples of error handling (these would raise exceptions in a notebook):")

    code("""# These would normally raise errors:
# code(123)  # Not a string
# code("print('hello')", highlighting_mode="invalid")  # Invalid mode
# code("print('hello')", background_color="invalid")  # Invalid color""")


def demo_animation():
    """Demo animation effects."""

    print("\n=== DEMO: Animation Effects ===")

    # --- Basic Animations ---
    title("Animation Effects Demo", animate="fadeIn")
    subtitle("Showcasing Animate.css integration", animate="slideInRight")

    section_divider("Attention Seekers", animate="pulse")

    time.sleep(0.5)
    info("Pulse Effect", animate="pulse")
    time.sleep(0.5)
    warning("Shake Effect", animate="shakeX")
    time.sleep(0.5)
    error("Bounce Effect", animate="bounce")
    time.sleep(0.5)
    success("Flash Effect", animate="flash")

    section_divider("Entrances", animate="flipInX")

    time.sleep(0.5)
    card("Fade In", animate="fadeIn")
    time.sleep(0.5)
    card("Slide In Left", animate="slideInLeft")
    time.sleep(0.5)
    card("Slide In Right", animate="slideInRight")
    time.sleep(0.5)
    card("Bounce In", animate="bounceIn")

    section_divider("Exits", animate="flipInY")

    time.sleep(0.5)
    code("# This code block will fade out\nprint('Hello, world!')", animate="fadeOut", delay="3s")
    time.sleep(0.5)
    badge("Slide Out Up", animate="slideOutUp", delay="3s")
    time.sleep(0.5)
    highlight("Slide Out Down", animate="slideOutDown", delay="3s")
    time.sleep(0.5)
    quote("This quote will disappear to the right", animate="slideOutRight", delay="3s")

    section_divider("Complex Combinations", animate="fadeInUp")

    time.sleep(0.5)
    headers = ["Animation", "Duration", "Delay"]
    rows = [
        ["bounce", "1s", "0s"],
        ["flash", "2s", "1s"],
        ["pulse", "3s", "2s"]
    ]
    table(headers, rows, caption="Animation Properties", animate="zoomIn")

    time.sleep(0.5)
    sample_dict = {
        "name": "Animate.css",
        "version": "4.1.1",
        "animations": ["Attention seekers", "Entrances", "Exits", "Others"]
    }
    dict_(sample_dict, animate="rotateIn")

    # Animation with custom styling
    time.sleep(0.5)
    header("Custom Animation Styling", animate="fadeInLeft", animation_duration="2s", animation_delay="0.5s")


def demo_md():
    """Demo showcasing the Markdown display feature."""

    title("Markdown Display Examples")
    subtitle("Rendering Markdown content with read more/less functionality")

    # Creating example markdown files for demonstration
    import os
    os.makedirs('examples/markdown', exist_ok=True)

    # Basic markdown example
    basic_markdown = """# Markdown Example

This is a basic markdown example demonstrating the `MDDisplayer` class functionality.

## Features

- **Syntax highlighting** for code blocks
- *Formatted text* with Markdown
- Tables and lists
- Read more/less functionality

## Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

## Table Example

| Name | Age | Occupation |
|------|-----|------------|
| John | 28  | Developer  |
| Jane | 32  | Designer   |
| Bob  | 45  | Manager    |

"""

    with open('examples/markdown/basic.md', 'w', encoding='utf-8') as f:
        f.write(basic_markdown)

    # Longer markdown example with more content
    longer_markdown = basic_markdown + """
## Additional Content

This section demonstrates the 'read more' functionality by adding more content.

### Lists

1. First item
2. Second item
   - Nested item 1
   - Nested item 2
3. Third item

### Blockquotes

> This is a blockquote.
> It can span multiple lines.

### Horizontal Rule

---

### Links and Images

[Link to Google](https://www.google.com)

![Image placeholder](https://via.placeholder.com/150)

## Final Section

This is the end of our markdown example document.
"""

    with open('examples/markdown/longer.md', 'w', encoding='utf-8') as f:
        f.write(longer_markdown)

    # --- Basic Examples ---
    header("Basic Markdown Example")
    info("Display markdown from a file:")

    # Using the Printer class directly
    P = Printer()
    P.display_md('examples/markdown/basic.md')

    # --- Styled Examples ---
    header("Styled Markdown Example")
    info("Displaying markdown with custom styling:")
    md('examples/markdown/longer.md', style="card", border_left="5px solid #4CAF50")

    # --- Animated Example ---
    header("Animated Markdown")
    info("Markdown content with animation effects:")
    md('examples/markdown/basic.md', animate="fadeIn")

    # --- Inline Styles Example ---
    header("Custom Styled Markdown")
    info("Applying custom inline styles:")
    md('examples/markdown/longer.md', background_color="#f8f8f8", padding="20px", border_radius="10px")

    # --- URL Example ---
    # We'll use a public markdown file URL for this example
    header("Loading Markdown from URL")
    info("Loading markdown content from a URL:")
    md('https://raw.githubusercontent.com/adam-p/markdown-here/master/README.md', is_url=True)


def divider(title: str) -> None:
    """Print a divider with title."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50 + "\n")


def demo_basic_tables() -> None:
    """Demonstrate basic table creation with different data structures."""
    divider("BASIC TABLES")

    # Simple table with list inputs
    print("Basic table with list data:")
    P.display_table(
        ["Name", "Age", "City"],
        [
            ["Alice", 30, "New York"],
            ["Bob", 25, "San Francisco"],
            ["Charlie", 35, "Chicago"]
        ]
    )

    # Table with tuple inputs
    print("\nTable with tuple data:")
    P.display_table(
        ["Product", "Price", "Stock"],
        [
            ("Laptop", 1299.99, 10),
            ("Phone", 799.99, 25),
            ("Headphones", 149.99, 50)
        ]
    )

    # Table with mixed input types
    print("\nTable with mixed data types:")
    P.display_table(
        ["ID", "Name", "Active", "Data"],
        [
            [1, "Project Alpha", True, [1, 2, 3]],
            [2, "Project Beta", False, {"x": 1, "y": 2}],
            [3, "Project Gamma", True, (4, 5, 6)]
        ]
    )


def demo_numpy_arrays() -> None:
    """Demonstrate tables with NumPy arrays."""
    divider("NUMPY ARRAYS")

    # Create a 2D numpy array
    data = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ])

    print("Table from NumPy array:")
    P.display_table(
        ["Col 1", "Col 2", "Col 3", "Col 4"],
        data.tolist()
    )

    # Table with mixed numpy data
    print("\nTable with mixed NumPy data types:")
    P.display_table(
        ["Array Type", "Sample Data", "Shape", "Mean"],
        [
            ["1D integers", np.array([1, 2, 3, 4, 5]), "(5,)", np.mean([1, 2, 3, 4, 5])],
            ["2D floats", np.array([[1.1, 2.2], [3.3, 4.4]]), "(2, 2)", np.mean([[1.1, 2.2], [3.3, 4.4]])],
            ["Boolean", np.array([True, False, True]), "(3,)", None]
        ]
    )


def demo_dictionary_source() -> None:
    """Demonstrate using dictionaries as data sources."""
    divider("DICTIONARY SOURCES")

    # Dictionary with scalar values (single row)
    print("Dictionary with scalar values:")
    P.display_table(source_dict={
        "Product": "Widget X",
        "Price": 19.99,
        "Stock": 42,
        "Available": True
    })

    # Dictionary with list values (multiple rows)
    print("\nDictionary with list values (column-oriented data):")
    P.display_table(source_dict={
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [30, 25, 35],
        "City": ["New York", "San Francisco", "Chicago"]
    })

    # Dictionary with mixed value types
    print("\nDictionary with mixed value types:")
    P.display_table(source_dict={
        "Category": ["Electronics", "Furniture", "Books"],
        "Items": [
            ["Laptop", "Phone", "Tablet"],
            ["Chair", "Table", "Desk"],
            ["Fiction", "Non-fiction"]
        ],
        "In Stock": [True, False, True]
    })


def demo_large_data() -> None:
    """Demonstrate handling of large data that gets condensed."""
    divider("LARGE DATA CONDENSING")

    # Create a large list
    large_list = list(range(100))

    print("Table with large lists that get condensed:")
    P.display_table(
        ["Data Type", "Sample"],
        [
            ["Large list", large_list],
            ["Large tuple", tuple(range(50))],
            ["Large array", np.arange(75)],
            ["Nested large lists", [list(range(30)), list(range(20))]],
        ]
    )


def demo_styling_options() -> None:
    """Demonstrate various styling options."""
    divider("STYLING OPTIONS")

    # Basic styling with width
    print("Custom width (50%):")
    P.display_table(
        ["Name", "Value"],
        [["Alpha", 10], ["Beta", 20], ["Gamma", 30]],
        width="50%"
    )

    # Using caption
    print("\nTable with caption:")
    P.display_table(
        ["Quarter", "Revenue", "Growth"],
        [["Q1", "$10M", "+5%"], ["Q2", "$12M", "+20%"], ["Q3", "$15M", "+25%"]],
        caption="Quarterly Financial Results"
    )

    # Custom header and row styles
    print("\nCustom header and row styles:")
    P.display_table(
        ["Name", "Score"],
        [["Team A", 95], ["Team B", 88], ["Team C", 92]],
        custom_header_style="background-color: #4CAF50; color: white; padding: 10px;",
        custom_row_style="padding: 8px; text-align: center;"
    )

    # Inline styles
    print("\nInline styles:")
    P.display_table(
        ["Product", "Status"],
        [["Widget A", "In Stock"], ["Widget B", "Out of Stock"], ["Widget C", "On Order"]],
        border_radius="10px",
        box_shadow="0 4px 8px rgba(0,0,0,0.1)",
        margin_bottom="20px"
    )


def demo_compact_parameter() -> None:
    """Demonstrate the compact parameter."""
    divider("COMPACT PARAMETER")

    # Create a large list
    large_list = list(range(100))

    print("Large data with compact=True (default):")
    P.display_table(
        ["Data Type", "Sample"],
        [
            ["Large list", large_list],
            ["Large tuple", tuple(range(50))],
            ["Large array", np.arange(75)]
        ],
        compact=True
    )

    print("\nLarge data with compact=False (no condensing):")
    P.display_table(
        ["Data Type", "Sample"],
        [
            ["Large list", large_list],
            ["Large tuple", tuple(range(50))],
            ["Large array", np.arange(75)]
        ],
        compact=False
    )


def demo_table_display():
    """Demo showcasing the table display feature."""

    title("Table Display Examples")
    demo_basic_tables()

    try:
        demo_numpy_arrays()
    except ImportError:
        print("NumPy not available, skipping NumPy demos.")

    demo_dictionary_source()
    demo_large_data()
    demo_styling_options()
    demo_compact_parameter()


def pdf_examples():
    """Demo using the PDF display functionality."""

    print("\n=== DEMO: PDF Display Functionality ===")

    section_divider("PDF Display Examples")

    # Basic PDF display
    header("Basic PDF Display")
    info("Display a PDF file from a local path")

    # NOTE: In a real environment, replace with an actual PDF file path
    pdf_("path/to/sample.pdf")

    # PDF from URL
    header("PDF from URL")
    info("Display a PDF file from a URL")

    # Example with a sample PDF URL
    pdf_("https://www.africau.edu/images/default/sample.pdf", is_url=True)

    # PDF with styling
    header("Styled PDF Display")
    info("Display PDF with custom styling and animation")

    pdf_("path/to/sample.pdf",
         animate="fadeIn",
         background_color="#f5f5f5",
         border_radius="10px",
         box_shadow="0 4px 8px rgba(0,0,0,0.2)")

    # Using the Printer class
    header("Using Printer Class for PDF Display")
    info("Display PDF using the Printer class API")

    P.display_pdf("path/to/sample.pdf",
                  animate="zoomIn",
                  border="1px solid #e0e0e0")

    # PDF file picker (no source provided)
    header("PDF File Picker")
    info("When no source is provided, a file picker interface is displayed")

    pdf_()


def demo_text_box():
    """Demo using the text box feature."""
    
    print("\n=== DEMO: Text Box Display ===")
    
    # Basic text box with just a title
    text_box("Simple Text Box", style="default")
    
    # Text box with captions
    text_box(
        "Information",
        captions=[
            "This is a text box with multiple paragraphs of information.",
            "You can use it to display important notices or instructions to users.",
            "The text is formatted as separate paragraphs for better readability."
        ],
        style="info"
    )
    
    # Text box with warning style
    text_box(
        "Warning!",
        captions=["This operation cannot be undone. Please proceed with caution."],
        style="warning",
        border_radius="4px",
        border_left="5px solid #F39C12"
    )
    
    # Text box with progress bar
    text_box(
        "Download Status",
        captions=["Downloading important files..."],
        progress={"value": 75, "max": 100, "label": "Progress"},
        style="primary"
    )
    
    # Text box with animation
    text_box(
        "New Feature",
        captions=[
            "We've just released our newest feature!",
            "Check it out by visiting the settings page."
        ],
        style="success",
        animate="fadeIn"
    )
    
    # Custom styled text box
    text_box(
        "Custom Styled Box",
        captions=["This text box uses custom inline styles for a unique appearance."],
        background_color="#f5f5f5",
        border="1px solid #ddd",
        border_radius="10px",
        box_shadow="0 4px 8px rgba(0,0,0,0.1)",
        padding="20px"
    )
    
    # Text box with error style
    text_box(
        "Error Occurred",
        captions=[
            "The operation could not be completed due to the following errors:",
            "• Invalid input parameters",
            "• Missing required permissions",
            "Please correct these issues and try again."
        ],
        style="error"
    )
    
    # Text box with dynamic progress bar demonstration
    progress_box_id = text_box(
        "Processing Files",
        captions=["Starting file processing operation..."],
        progress={"value": 0, "max": 100, "label": "Files Processed"},
        style="text_box"
    )
    
    # Simulate processing with progress updates
    for i in range(0, 101, 20):
        time.sleep(0.5)  # Simulate work
        update_text_box(
            progress_box_id,
            captions=[f"Processing files: {i}% complete"],
            progress={"value": i, "max": 100, "label": "Files Processed"}
        )
    
    # Text box with continuous timer updates
    print("\n=== DEMO: Text Box with Continuous Updates (Timer) ===")
    
    # Create a text box with a timer
    timer_box_id = text_box(
        "Real-Time Task Timer",
        captions=["Task started just now"],
        progress={"value": 0, "max": 60, "label": "Task Duration"},
        style="info",
        border_radius="8px",
        box_shadow="0 4px 8px rgba(0,0,0,0.1)"
    )
    
    # Update the timer every second for 10 seconds
    start_time = time.time()
    for i in range(1, 11):
        time.sleep(1)  # Wait for 1 second
        elapsed = int(time.time() - start_time)
        update_text_box(
            timer_box_id,
            captions=[f"Task running for {elapsed} seconds"],
            progress={"value": min(elapsed, 60), "max": 60, "label": "Task Duration"}
        )
    
    # Final update
    final_elapsed = int(time.time() - start_time)
    update_text_box(
        timer_box_id,
        title="Task Complete",
        captions=[
            f"Task completed in {final_elapsed} seconds",
            "All operations were successful!"
        ],
        progress={"value": final_elapsed, "max": 60, "label": "Total Duration"}
    )


def main():
    """Run all demo functions."""
    title("Colab Print Demo")
    subtitle("A showcase of various display capabilities")

    # Core display features
    demo_printer_class()
    demo_global_shortcuts()
    demo_progress_bars()
    demo_enhanced_lists()
    demo_mermaid_diagrams()
    demo_enhanced_code_display()
    demo_animation()
    demo_md()
    
    # Table display features
    section_divider("Table Display Features")
    demo_table_display()
    
    # PDF display features
    section_divider("PDF Display Features")
    pdf_examples()
    
    # Text Box display features
    section_divider("Text Box Display Features")
    demo_text_box()


if __name__ == "__main__":
    main()
