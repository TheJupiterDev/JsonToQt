import sys
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QCheckBox,
    QRadioButton, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
    QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QMessageBox
)


class JsonForm(QWidget):
    """
    A dynamic PySide6 form generated from a JSON schema.
    Supports widget construction and callback binding for buttons.
    """
    def __init__(self, schema: dict, parent=None):
        super().__init__(parent)
        self.schema = schema
        self.fields = {}    # Data fields
        self.buttons = {}   # QPushButton widgets
        self.build_ui()

    def build_ui(self):
        """Builds the form layout based on the JSON schema."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        for field_name, field in self.schema.get("properties", {}).items():
            widget = self.create_widget(field_name, field)
            if widget:
                title = field.get("title", field_name)

                if isinstance(widget, QLabel):
                    layout.addWidget(widget)

                elif isinstance(widget, QPushButton):
                    self.buttons[field_name] = widget
                    layout.addWidget(widget)

                elif field.get("widget") == "radio":
                    group_box = QGroupBox(title)
                    group_layout = QVBoxLayout()
                    for btn in widget:
                        group_layout.addWidget(btn)
                    group_box.setLayout(group_layout)
                    layout.addWidget(group_box)

                else:
                    form_layout.addRow(title, widget)

        layout.addLayout(form_layout)
        self.setLayout(layout)

    def create_widget(self, name, field):
        """
        Creates and returns a widget based on the field definition.
        Also registers widgets into self.fields/buttons.
        """
        widget_type = field.get("widget")
        field_type = field.get("type")
        enum = field.get("enum")

        if widget_type == "label":
            return QLabel(field.get("text", ""))

        elif widget_type == "button":
            return QPushButton(field.get("text", "Submit"))

        elif widget_type == "textarea":
            widget = QTextEdit()
            self.fields[name] = widget
            return widget

        elif widget_type == "radio" and enum:
            buttons = []
            self.fields[name] = []
            for val in enum:
                btn = QRadioButton(val)
                self.fields[name].append(btn)
                buttons.append(btn)
            return buttons

        elif field_type == "string":
            if enum:
                widget = QComboBox()
                widget.addItems(enum)
                self.fields[name] = widget
                return widget
            else:
                widget = QLineEdit()
                self.fields[name] = widget
                return widget

        elif field_type == "integer":
            widget = QSpinBox()
            widget.setMinimum(field.get("minimum", 0))
            widget.setMaximum(field.get("maximum", 100))
            self.fields[name] = widget
            return widget

        elif field_type == "number":
            widget = QDoubleSpinBox()
            widget.setMinimum(field.get("minimum", 0.0))
            widget.setMaximum(field.get("maximum", 100.0))
            widget.setSingleStep(field.get("step", 0.1))
            self.fields[name] = widget
            return widget

        elif field_type == "boolean":
            widget = QCheckBox(field.get("title", name))
            self.fields[name] = widget
            return widget

        return None

    def bind_callbacks(self, callback_map: dict):
        """
        Binds buttons to functions by matching callback names from schema
        to the supplied function dictionary.
        """
        for name, button in self.buttons.items():
            callback_name = self.schema["properties"][name].get("callback")
            if callback_name:
                func = callback_map.get(callback_name)
                if func:
                    button.clicked.connect(func)

    def get_data(self):
        """
        Collects and returns data from form widgets.
        """
        data = {}
        for key, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text()
            elif isinstance(widget, QTextEdit):
                data[key] = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                data[key] = widget.value()
            elif isinstance(widget, QCheckBox):
                data[key] = widget.isChecked()
            elif isinstance(widget, list):  # Radio buttons
                for btn in widget:
                    if btn.isChecked():
                        data[key] = btn.text()
                        break
        return data


class TestFormWindow(QWidget):
    """
    Testing container for rendering a JsonForm.
    Connects buttons to local callback methods via schema bindings.
    """
    def __init__(self, schema_path):
        super().__init__()
        self.setWindowTitle("Test Form Window")
        self.resize(600, 500)

        with open(schema_path, "r") as f:
            schema = json.load(f)

        self.form = JsonForm(schema)
        self.form.bind_callbacks({
            "on_submit": self.on_submit,
            "on_cancel": self.on_cancel
        })

        layout = QVBoxLayout()
        layout.addWidget(self.form)
        self.setLayout(layout)

    def on_submit(self):
        """Handles submission from the form."""
        data = self.form.get_data()
        QMessageBox.information(self, "Form Submitted", json.dumps(data, indent=2))

    def on_cancel(self):
        """Handles cancellation logic."""
        QMessageBox.warning(self, "Cancelled", "The form has been cancelled.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestFormWindow("example.json")
    window.show()
    sys.exit(app.exec())
