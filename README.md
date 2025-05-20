# JsonToQt

**Convert JSON schemas into dynamic PySide6 GUI forms - no manual UI coding needed!**

---

## Overview

JsonToQt lets you define Qt-based forms declaratively in JSON. It parses the schema and generates forms with:

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

pip install jsontoqt

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

### Import JsonToQt and create a form

## Usage

### Define your form schema (`example.json`):

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

### Load the schema, create the form, bind callbacks, and run the app:

```python
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from jsontoqt import JsonForm

# Load the JSON schema from file
schema_path = Path("example.json")
with schema_path.open("r", encoding="utf-8") as f:
    schema = json.load(f)

def on_submit():
    print("Submit button clicked!")

def on_cancel():
    print("Cancel button clicked!")

app = QApplication([])

# Create the form
form = JsonForm(schema)

# Bind callbacks from JSON to Python functions
form.bind_callbacks({
    "on_submit": on_submit,
    "on_cancel": on_cancel,
})

form.show()

app.exec()
```
---

## Requirements

- Python 3.8+  
- jsontoqt

---

## License

MIT License

---

## Contribution

Contributions and issues are welcome! Feel free to open a PR or suggest new features.
