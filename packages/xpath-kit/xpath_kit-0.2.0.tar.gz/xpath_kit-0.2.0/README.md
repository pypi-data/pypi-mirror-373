# xpath-kit

[![PyPI Version](https://img.shields.io/pypi/v/xpath-kit.svg)](https://pypi.org/project/xpath-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/xpath-kit.svg)](https://pypi.org/project/xpath-kit/)

**xpath-kit** is a Python library that provides a fluent, object-oriented, and Pythonic interface for building and executing XPath queries on top of `lxml`. It transforms complex XPath string composition into a readable and maintainable chain of objects and methods.

Say goodbye to messy, hard-to-read XPath strings:

`//div[@id="main" and contains(@class, "content")]/ul/li[position()=1]`

And say hello to a more intuitive and IDE-friendly way of writing queries:

`E.div[(A.id == "main") & A.class_.any("content")] / E.ul / E.li[1]`

---

## Features

-   **✨ Fluent & Pythonic Interface**: Chain methods and operators (`/`, `//`, `[]`, `&`, `|`) to build complex XPath expressions naturally using familiar Python logic.
-   **💡 IDE-Friendly Builders**: Use `E` (for elements) and `A` (for attributes) for a highly readable syntax with excellent autocompletion support.
-   **📖 Readability & Maintainability**: Complex queries become self-documenting. It's easier to understand, debug, and modify your selectors.
-   **💪 Powerful Selection**: Easily create sophisticated predicates for attributes, including checking for multiple class names (`any`, `all`, `none`).
-   **🔩 DOM Manipulation**: The result objects are powerful wrappers around `lxml` elements, allowing for easy DOM traversal and manipulation (e.g., `append`, `remove`, `parent`).
-   **🔒 Type-Hinted**: The entire library is fully type-hinted for a better development experience with modern IDEs.

---

## Installation

Install `xpath-kit` from PyPI using pip:

```bash
pip install xpath-kit
```

The library requires `lxml` as a dependency, which will be installed automatically.

---

## Quick Start

Here's a simple example of how to use `xpath-kit` to parse a piece of HTML and extract information.

```python
from xpathkit import html, E, A

html_content = """
<html>
  <body>
    <div id="main">
      <h2>Article Title</h2>
      <p>This is the first paragraph.</p>
      <ul class="item-list">
        <li class="item active">Item 1</li>
        <li class="item">Item 2</li>
        <li class="item disabled">Item 3</li>
      </ul>
    </div>
  </body>
</html>
"""

# Parse the HTML content
root = html(html_content)

# Build a query to find the active list item
# This translates to: .//ul[contains(@class, "item-list")]/li[contains(@class, "active")]
query = E.ul[A.class_.any("item-list")] / E.li[A.class_.any("active")]

# Execute the query and get a single element
active_item = root.descendant(query)

# Print its content and attributes
print(f"Tag: {active_item.tag}")
print(f"Text: {active_item.string()}")
print(f"Class attribute: {active_item['class']}")

# --- Output ---
# Tag: li
# Text: Item 1
# Class attribute: item active
```

---

## Core Concepts

### 1. Parsing and Entrypoint

The `html()` function is the main entry point. It takes a string, bytes of HTML/XML content, or a file path and returns the root `XPathElement`.

```python
from xpathkit import html

root = html("<p>Hello</p>")
# Or from a file
# root = html(path="index.html")
```

### 2. Building Expressions with `E` and `A` (Recommended)

The `E` and `A` objects are convenient builders that provide a more readable and autocompletion-friendly way to create expressions.

-   **`E` (Element Builder)**: Represents an element node. Access common tags as properties (e.g., `E.div`, `E.a`, `E.p`).
-   **`A` (Attribute Builder)**: Represents an attribute within a predicate. Access common attributes as properties (e.g., `A.id`, `A.href`).

For **custom tags or attributes**, use them as functions: `E("my-tag")` or `A("data-id")`.

Because `class` and `for` are reserved keywords in Python, use a trailing underscore: `A.class_` and `A.for_`.

### 3. Path Selection (`/` and `//`)

Use the division operators to define relationships between elements.

-   **`/`**: Selects a direct child.
-   **`//`**: Selects a descendant at any level.

```python
# Selects a <p> that is a direct child of a <div>
# Equivalent to: div/p
query_child = E.div / E.p

# You can also use strings for simplicity
query_child_str = E.div / "p"

# Selects an <a> that is a descendant of the <body>
# Equivalent to: body//a
query_descendant = E.body // E.a
```

### 4. Predicates (`[]`)

Use square brackets on an `E` object to add conditions (predicates).

#### Attribute Predicates with `A`

```python
# Find an input with name="username"
# Equivalent to: //input[@name="username"]
query = E.input[A.name == "username"]

# Find an element with a specific class
# Equivalent to: //div[contains(@class, "widget")]
query = E.div[A.class_.any("widget")]

# Find an element that has ALL of the given classes
# Equivalent to: //li[contains(@class, "item") and contains(@class, "active")]
query = E.li[A.class_.all("item", "active")]

# Find an element that does NOT contain any of the given classes
# Equivalent to: //button[not(contains(@class, "disabled")) and not(contains(@class, "hidden"))]
query = E.button[A.class_.none("disabled", "hidden")]
```

#### Combining Predicates with `&` and `|`

-   **`&`**: Logical `and`.
-   **`|`**: Logical `or`.

```python
# Find a link that has a specific href AND a target attribute
# //a[@href="/home" and @target]
query_and = E.a[(A.href == "/home") & A.target]

# Find an element with id="sidebar" OR class="nav"
# //div[@id="sidebar" or contains(@class,"nav")]
query_or = E.div[(A.id == "sidebar") | A.class_.any("nav")]
```

**Note:** Due to Python's operator precedence, it's highly recommended to wrap combined conditions in parentheses `()`.

#### Positional Predicates

Use integers to specify position (1-based index).

```python
# Select the second list item
# //ul/li[2]
query = E.ul / E.li[2]

# Select the first list item
# //ul/li[1]
query_first = E.ul / E.li[1]
```

### 5. Working with Results

Queries return either an `XPathElement` (for `.child()`/`.descendant()`) or an `XPathElementList` (for `.children()`/`.descendants()`).

#### `XPathElement` (Single Result)

-   `.tag`: The element's tag name (e.g., `'div'`).
-   `.attr`: A dictionary of attributes.
-   `element['name']`: Access an attribute directly.
-   `.string()`: Get all concatenated text from the element and its children.
-   `.text()`: Get only the direct text nodes of the element.
-   `.parent()`: Get the parent element.

#### `XPathElementList` (Multiple Results)

-   `.one()`: Returns the single element in the list. Raises an error if the list doesn't contain exactly one element.
-   `.first()` / `.last()`: Get the first or last element. Returns `None` if the list is empty.
-   `len()`: Get the number of elements.
-   `.filter(func)`: Filter the list based on a function.
-   `.map(func)`: Apply a function to each element and return a list of results.
-   Can be iterated over directly: `for e in element_list: ...`

```python
links = root.descendants(E.a)

# Map to get all hrefs
hrefs = links.map(lambda link: link["href"])

# Filter for external links
external_links = links.filter(lambda link: link["href"].startswith("http"))
```

### 6. DOM Manipulation

`XPathElement` provides methods to modify the XML/HTML tree.

```python
from xpathkit import XPathElement

# Find an element
ul = root.descendant(E.ul)

# Create a new element
new_li = XPathElement.create("li", attr={"class": "new-item"}, text="Item 4")

# Append it
ul.append(new_li)

# Remove an element
item_to_remove = ul.child(E.li[A.class_.any("disabled")])
if item_to_remove:
    ul.remove(item_to_remove)

print(root.tostring()) # See the modified HTML
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.