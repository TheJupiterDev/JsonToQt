# JsonToQt

**Convert JSON schemas into dynamic PySide6 GUI forms - no manual UI coding needed!**

> ⚠️ This documentation is possibly outdated or false! New documentation coming soon™️

---

## Overview

JsonToQt is broken & not currently maintained

---

## Features

- Supports common PySide6 widgets from a JSON schema-like syntax
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
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "title": "Your Name"
    },
    "age": {
      "type": "integer",
      "title": "Age",
      "minimum": 0,
      "maximum": 120
    },
    "bio": {
      "type": "string",
      "title": "Short Bio",
      "widget": "textarea"
    },
  }
}
```

Note that it must be a valid schema!

### Load the schema, create the form, bind callbacks, and run the app:

```python
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from jsontoqt import JsonForm

def on_submit():
    print("Submit button clicked!")

def on_cancel():
    print("Cancel button clicked!")

app = QApplication([])

# Create the form
form = JsonForm(schema)

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
