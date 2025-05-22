from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox,
    QDoubleSpinBox, QComboBox, QRadioButton, QCheckBox, QGroupBox,
    QPushButton, QListView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

import json


class MultiSelectComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(QStandardItemModel(self))
        self.setView(QListView())
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setPlaceholderText("Select options")
        self.model().dataChanged.connect(self.on_data_changed)

    def addItems(self, items):
        for item in items:
            if isinstance(item, tuple):
                text, value = item
            else:
                text = value = item
            std_item = QStandardItem(text)
            std_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            std_item.setData(value, Qt.UserRole)
            std_item.setCheckState(Qt.Unchecked)
            self.model().appendRow(std_item)

    def on_data_changed(self, topLeft, bottomRight, roles):
        if Qt.CheckStateRole in roles:
            self.update_text()

    def update_text(self):
        selected = [
            self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]
        self.lineEdit().setText(", ".join(selected))

    def get_selected_items(self):
        return [
            self.model().item(i).text()
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]

    def get_selected_values(self):
        return [
            self.model().item(i).data(Qt.UserRole)
            for i in range(self.model().rowCount())
            if self.model().item(i).checkState() == Qt.Checked
        ]

    def set_selected_items(self, selected_texts):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Checked if item.text() in selected_texts else Qt.Unchecked)
        self.update_text()

    def clear_selection(self):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Unchecked)
        self.update_text()


class JsonForm:
    def __init__(self, schema: dict, enum_data: dict = None):
        if schema.get("type") != "object":
            raise ValueError("Top-level schema type must be 'object'.")
        self.schema = schema
        self.enum_data = enum_data or {}
        self.widgets = {}
        self.dynamic_groups = {}

    def build_form(self) -> QWidget:
        self.root_widget = QWidget()
        layout = QVBoxLayout(self.root_widget)
        self._add_properties(self.schema.get("properties", {}), layout)
        return self.root_widget

    def _register_widget(self, key, widget):
        self.widgets[key] = widget

    def _add_properties(self, properties: dict, layout: QVBoxLayout, prefix: str = ""):
        for key, prop in properties.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if "x-multiple-group" in prop:
                self._add_dynamic_group(full_key, prop["x-multiple-group"], layout)
            else:
                self._add_single_widget(prop, layout, full_key)

    def _add_single_widget(self, schema: dict, layout: QVBoxLayout, key: str):
        title = schema.get("title", key)
        description = schema.get("description")
        prop_type = schema.get("type", "string")
        default = schema.get("default")

        # Handle enum or dynamic enum source
        enum_vals = schema.get("enum")
        enum_source_key = schema.get("x-enum-source")
        if enum_source_key:
            enum_vals = self.enum_data.get(enum_source_key, [])

        multiselect = schema.get("x-multiselect", False)

        if description:
            layout.addWidget(QLabel(f"<i>{description}</i>"))

        if enum_vals is not None:
            layout.addWidget(QLabel(title))
            if multiselect:
                combo = MultiSelectComboBox()
                combo.addItems([str(e) for e in enum_vals])
                if default:
                    combo.set_selected_items([str(d) for d in default])
                combo.setObjectName(key)
                self._register_widget(key, combo)
                layout.addWidget(combo)
            elif len(enum_vals) <= 3:
                group = QGroupBox(title)
                group_layout = QVBoxLayout(group)
                for val in enum_vals:
                    rb = QRadioButton(str(val))
                    if default == val:
                        rb.setChecked(True)
                    group_layout.addWidget(rb)
                group.setObjectName(key)
                self._register_widget(key, group)
                layout.addWidget(group)
            else:
                combo = QComboBox()
                combo.addItems([str(e) for e in enum_vals])
                if default:
                    index = combo.findText(str(default))
                    if index >= 0:
                        combo.setCurrentIndex(index)
                combo.setObjectName(key)
                self._register_widget(key, combo)
                layout.addWidget(combo)
            return

        if prop_type == "boolean":
            cb = QCheckBox(title)
            if default:
                cb.setChecked(bool(default))
            cb.setObjectName(key)
            self._register_widget(key, cb)
            layout.addWidget(cb)
            return

        if prop_type in ["integer", "number"]:
            layout.addWidget(QLabel(title))
            spin = QDoubleSpinBox() if prop_type == "number" else QSpinBox()
            spin.setMinimum(schema.get("minimum", 0))
            spin.setMaximum(schema.get("maximum", 100))
            if default is not None:
                spin.setValue(default)
            spin.setObjectName(key)
            self._register_widget(key, spin)
            layout.addWidget(spin)
            return

        if prop_type == "object":
            group = QGroupBox(title)
            group_layout = QVBoxLayout(group)
            self._add_properties(schema.get("properties", {}), group_layout, prefix=key)
            layout.addWidget(group)
            return

        layout.addWidget(QLabel(title))
        line = QLineEdit()
        if default:
            line.setText(str(default))
        line.setObjectName(key)
        self._register_widget(key, line)
        layout.addWidget(line)

    def _add_dynamic_group(self, key: str, groups: dict, layout: QVBoxLayout):
        box = QGroupBox(key.split(".")[-1].replace("_", " ").title())
        box_layout = QVBoxLayout(box)

        control_layout = QHBoxLayout()
        combo = QComboBox()
        combo.addItems(groups.keys())
        add_btn = QPushButton("[+]")
        control_layout.addWidget(combo)
        control_layout.addWidget(add_btn)
        box_layout.addLayout(control_layout)

        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        box_layout.addWidget(container_widget)

        self.dynamic_groups[key] = []

        def on_add():
            selected = combo.currentText()
            group_schema = groups[selected]
            wrapper = QWidget()
            wrapper_layout = QVBoxLayout(wrapper)

            group_box = QGroupBox(selected)
            group_box_layout = QVBoxLayout(group_box)

            entry_index = len(self.dynamic_groups[key])
            nested_prefix = f"{key}.{entry_index}"

            self._add_properties(group_schema.get("properties", {}), group_box_layout, prefix=nested_prefix)
            wrapper_layout.addWidget(group_box)

            remove_btn = QPushButton("[-]")
            wrapper_layout.addWidget(remove_btn, alignment=Qt.AlignRight)

            def on_remove():
                container_layout.removeWidget(wrapper)
                wrapper.setParent(None)
                self.dynamic_groups[key].remove(wrapper)

            remove_btn.clicked.connect(on_remove)
            self.dynamic_groups[key].append(wrapper)
            container_layout.addWidget(wrapper)

        add_btn.clicked.connect(on_add)
        layout.addWidget(box)

    def _extract_widget_value(self, widget):
        from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QComboBox, QGroupBox, QRadioButton
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox) and not isinstance(widget, MultiSelectComboBox):
            return widget.currentText()
        elif isinstance(widget, MultiSelectComboBox):
            return widget.get_selected_items()
        elif isinstance(widget, QGroupBox):
            for rb in widget.findChildren(QRadioButton):
                if rb.isChecked():
                    return rb.text()
        return None

    def _insert_nested(self, data_dict, path, value):
        keys = path.split(".")
        for i, k in enumerate(keys[:-1]):
            next_k = keys[i + 1]
            is_next_index = next_k.isdigit()

            if k.isdigit():
                k = int(k)
                if not isinstance(data_dict, list):
                    raise ValueError("Expected list while traversing numeric index")
                while len(data_dict) <= k:
                    data_dict.append({})
                if not isinstance(data_dict[k], (dict, list)):
                    data_dict[k] = {} if not is_next_index else []
                data_dict = data_dict[k]
            else:
                if k not in data_dict:
                    data_dict[k] = [] if is_next_index else {}
                elif is_next_index and not isinstance(data_dict[k], list):
                    data_dict[k] = []
                data_dict = data_dict[k]

        last_key = keys[-1]
        if last_key.isdigit():
            index = int(last_key)
            if not isinstance(data_dict, list):
                data_dict = []
            while len(data_dict) <= index:
                data_dict.append(None)
            data_dict[index] = value
        else:
            data_dict[last_key] = value

    def _extract_from_widget_tree(self, widget: QWidget, visited=None) -> dict:
        if visited is None:
            visited = set()
        if widget in visited:
            return {}
        visited.add(widget)

        data = {}
        for key, w in self.widgets.items():
            if widget is w or widget.isAncestorOf(w):
                value = self._extract_widget_value(w)
                if value is not None:
                    self._insert_nested(data, key, value)

        for group_key, wrappers in self.dynamic_groups.items():
            for wrapper in wrappers:
                if wrapper in visited:
                    continue
                if wrapper.parent() and widget is wrapper.parent():
                    entry = self._extract_from_widget_tree(wrapper, visited)
                    if group_key not in data:
                        data[group_key] = []
                    data[group_key].append(entry)

        return data

    def get_form_data(self) -> dict:
        return self._extract_from_widget_tree(self.root_widget)


def load_json_schema(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
