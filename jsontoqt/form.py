from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QCheckBox,
    QRadioButton, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
    QVBoxLayout, QGroupBox, QFormLayout, QGridLayout, QHBoxLayout,
    QListView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel


class CheckableComboBox(QComboBox):
    def __init__(self, options: list[str], default: list[str] = None):
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setPlaceholderText("Select...")

        self.setInsertPolicy(QComboBox.NoInsert)
        self.setView(QListView())

        model = QStandardItemModel()
        self.setModel(model)

        self._options = options
        self._default = default or []

        for opt in options:
            item = QStandardItem(opt)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Checked if opt in self._default else Qt.Unchecked, Qt.CheckStateRole)
            model.appendRow(item)

        model.itemChanged.connect(self.update_display)
        self.update_display()

    def update_display(self):
        selected = self.get_selected()
        self.lineEdit().setText(", ".join(selected))

    def get_selected(self):
        return [
            self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]


class JsonForm(QWidget):
    def __init__(self, schema: dict, parent=None, layout_type=QVBoxLayout):
        super().__init__(parent)
        self.schema = schema
        self.fields = {}
        self.layout_type = layout_type
        self.build_ui()

    def build_ui(self):
        layout = self.layout_type()
        self._build_schema(self.schema, layout, [])
        self.setLayout(layout)

    def _build_schema(self, schema: dict, layout, path: list):
        if schema.get("type") == "object":
            props = schema.get("properties", {})
            for name, prop in props.items():
                self._build_field(name, prop, layout, path)

    def _build_field(self, name: str, field: dict, layout, path: list):
        full_path = path + [name]
        key = ".".join(full_path)
        title = field.get("title", name)

        field_type = field.get("type")

        # Handle nested object
        if field_type == "object":
            group = QGroupBox(title)
            group_layout = self.layout_type()
            self._build_schema(field, group_layout, full_path)
            group.setLayout(group_layout)
            layout.addWidget(group)
            return

        # Handle oneOf-based multi-toggle
        if field_type == "array" and "items" in field and "oneOf" in field["items"]:
            layout.addWidget(QLabel(title))

            options = [item.get("title", f"Option {i}") for i, item in enumerate(field["items"]["oneOf"])]
            row = QHBoxLayout()
            combo = QComboBox()
            combo.addItems(options)
            add_btn = QPushButton("Add")
            row.addWidget(combo)
            row.addWidget(add_btn)
            layout.addLayout(row)

            container = QVBoxLayout()
            layout.addLayout(container)

            self.fields[key] = []

            def add_child_group():
                idx = combo.currentIndex()
                if idx < 0:
                    return

                child_schema = field["items"]["oneOf"][idx]
                selected_title = child_schema.get("title", f"Option {idx}")

                group = QGroupBox(selected_title)
                group_layout = self.layout_type()
                remove_btn = QPushButton("Remove")
                remove_row = QHBoxLayout()
                remove_row.addStretch()
                remove_row.addWidget(remove_btn)
                group_layout.addLayout(remove_row)

                self._build_schema(child_schema, group_layout, full_path + [f"{selected_title}_{len(self.fields[key])}"])
                group.setLayout(group_layout)
                container.addWidget(group)

                self.fields[key].append((selected_title, group))

                def remove():
                    container.removeWidget(group)
                    group.setParent(None)
                    self.fields[key] = [pair for pair in self.fields[key] if pair[1] != group]

                remove_btn.clicked.connect(remove)

            add_btn.clicked.connect(add_child_group)
            return

        # Handle array of strings/numbers
        if field_type == "array" and "items" in field:
            enum = field["items"].get("enum")
            if enum:
                widget = CheckableComboBox(enum)
            else:
                widget = QTextEdit()  # fallback
            self.fields[key] = widget
            layout.addWidget(QLabel(title))
            layout.addWidget(widget)
            return

        # Handle enum (dropdown)
        if "enum" in field:
            widget = QComboBox()
            widget.addItems(field["enum"])
            self.fields[key] = widget
            layout.addWidget(QLabel(title))
            layout.addWidget(widget)
            return

        # Format-based UI hints
        fmt = field.get("format")
        if field_type == "string" and fmt == "textarea":
            widget = QTextEdit()
        elif field_type == "string":
            widget = QLineEdit()
        elif field_type == "integer":
            widget = QSpinBox()
            widget.setMinimum(field.get("minimum", 0))
            widget.setMaximum(field.get("maximum", 100))
        elif field_type == "number":
            widget = QDoubleSpinBox()
            widget.setMinimum(field.get("minimum", 0.0))
            widget.setMaximum(field.get("maximum", 100.0))
        elif field_type == "boolean":
            widget = QCheckBox(title)
            self.fields[key] = widget
            layout.addWidget(widget)
            return
        else:
            widget = QLineEdit()  # fallback

        self.fields[key] = widget
        layout.addWidget(QLabel(title))
        layout.addWidget(widget)

    def get_data(self):
        result = {}

        def set_nested(d, keys, value):
            for i, k in enumerate(keys[:-1]):
                is_index = k.isdigit()
                next_k = keys[i + 1]
                next_is_index = next_k.isdigit()

                if is_index:
                    k = int(k)
                    if not isinstance(d, list):
                        raise TypeError(f"Expected list at {keys[:i]}, got {type(d).__name__}")
                    while len(d) <= k:
                        d.append([] if next_is_index else {})
                    d = d[k]
                else:
                    if not isinstance(d, dict):
                        raise TypeError(f"Expected dict at {keys[:i]}, got {type(d).__name__}")
                    if k not in d or d[k] is None:
                        d[k] = [] if next_is_index else {}
                    d = d[k]

            last = keys[-1]
            if last.isdigit():
                last = int(last)
                if not isinstance(d, list):
                    raise TypeError(f"Expected list at {keys[:-1]}, got {type(d).__name__}")
                while len(d) <= last:
                    d.append(None)
                d[last] = value
            else:
                if not isinstance(d, dict):
                    raise TypeError(f"Expected dict at {keys[:-1]}, got {type(d).__name__}")
                d[last] = value

        for key, widget in self.fields.items():
            keys = key.split(".")
            value = None
            if isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                value = widget.value()
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, CheckableComboBox):
                value = widget.get_selected()

            set_nested(result, keys, value)

        return result
