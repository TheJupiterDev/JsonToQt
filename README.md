# JsonToQt

**Convert JSON schemas into dynamic PySide6 GUI forms - no manual UI coding needed!**

---

## Overview

JsonToQt lets you define Qt-based forms declaratively in JSON. It parses the schema and genreates forms with:

- Buttons, radio buttons, checkboxes  
- Combo boxes, line edits, text edits  
- Spin boxes (int & double), and labels  
- Built-in support for wiring button callbacks by name

Use JsonToQt to speed up GUI prototyping, build dynamic config panels, or integrate with low-code workflows.

---

## Features

- Supports common PySide6 widgets from a JSON schema  
- Bind button callbacks by name to Python functions  
- Easily extendable for more widgets or custom behaviors  
- Simple to use with minimal dependencies (just PySide6)

---

## Installation

```bash
pip install PySide6
```

Clone this repo or download source to get started.

---

## Usage

### Define your form schema (`example.json`):

```json
{
  "title": "User Registration",
  "type": "object",
  "properties": {
    "username": {
      "type": "string",
      "title": "Username"
    },
    "submit": {
      "widget": "button",
      "text": "Submit",
      "callback": "on_submit"
    }
  }
}
```

### Run the demo app

From the project root:
```bash
python -m jsontoqt
```

This will launch a window showing the form defined in `example.json`.

---

## How to Bind Callbacks

In your python code, bind functions to button callbacks declared in the JSON:

```python
form.bind_callbacks({
    "on_submit": your_submit_function,
    "on_cancel": your_cancel_function,
})
```

---

## Project Structure

```
jsontoqt/          # Package source code
  ├── __init__.py
  ├── form.py       # Core JsonForm class
  └── __main__.py   # Demo launcher

example.json        # Sample schema file
README.md           # This file
pyproject.toml      # Packaging config
```

---

## Requirements

- Python 3.8+
- PySide6

---

## License

MIT License

---

## Contribution

Contributions and issues are welcome! Feel free to open a PR or suggest new features.