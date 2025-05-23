# 🧩 jsontoqt

**jsontoqt** is a PySide6-based form builder that automatically generates interactive Qt widgets from a JSON Schema. It supports nested objects, enums, repeatable sections, multi-selects, and more — all with minimal code.

## ✨ Features

- ✅ Auto-generates PySide6 forms from JSON Schema
- 🧠 Supports:
  - `string`, `integer`, `number`, `boolean`, and `object` types
  - `enum` values and external enum sources
  - Multi-select combo boxes via `x-multiselect`
  - Dynamic group sections via `x-multiple-group`
  - Default values and constraints (`minimum`, `maximum`, etc.)
- 🧩 Clean widget registration and value extraction
- 📦 Easy integration and customization

## 📦 Installation

Install from PyPI:

`pip install jsontoqt`

## 🚀 Usage Example
```python
from jsontoqt import JsonForm
from PySide6.QtWidgets import QApplication

schema = {
    "title": "Example Form",
    "type": "object",
    "properties": {
        "name": { "type": "string", "title": "Full Name" },
        "age": { "type": "integer", "title": "Age", "minimum": 0 },
        "gender": {
            "type": "string",
            "title": "Gender",
            "enum": ["Male", "Female"]
        },
        "hobbies": {
            "type": "string",
            "title": "Hobbies",
            "enum": ["Reading", "Gaming", "Traveling", "Cooking"],
            "x-multiselect": True
        },
        "contact": {
            "type": "object",
            "title": "Contact Info",
            "properties": {
                "email": { "type": "string", "title": "Email" },
                "phone": { "type": "string", "title": "Phone" }
            }
        },
        "dynamic": {
            "type": "object",
            "title": "Dynamic Sections",
            "x-multiple-group": {
                "Address": {
                    "type": "object",
                    "properties": {
                        "street": { "type": "string", "title": "Street" },
                        "city": { "type": "string", "title": "City" }
                    }
                },
                "Contact": {
                    "type": "object",
                    "properties": {
                        "email": { "type": "string", "title": "Email" },
                        "phone": { "type": "string", "title": "Phone" }
                    }
                }
            }
        }
    }
}

app = QApplication([])
builder = JsonForm(schema)
form = builder.build_form()
form.show()

app.exec()
```
## 🛠 JSON Schema Extensions

- `x-multiselect: true`: Enables multi-select combo boxes
- `x-enum-source: "<key>"`: Pulls enum values from external data
- `x-multiple-group`: Allows adding repeatable groups of fields

## 🧪 Contribution

If you would like to contribute the JsonToQt project, submit an issue or open a PR on the [Github](https://github.com/TheJupiterDev/JsonToQt)!

## 📃 License

MIT License

---

Made with Python and PySide6
