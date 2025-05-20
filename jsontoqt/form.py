from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QCheckBox,
    QRadioButton, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
    QVBoxLayout, QGroupBox, QFormLayout, QGridLayout, QLayout, QHBoxLayout
)


class JsonForm(QWidget):
    """
    A dynamic PySide6 form generated from a JSON schema.
    Supports widget construction and callback binding for buttons.
    """
    def __init__(self, schema: dict, parent=None, layout_type=QVBoxLayout):
        super().__init__(parent)
        self.schema = schema
        self.fields = {}
        self.buttons = {}
        self.layout_type = layout_type
        self.build_ui()

    def build_ui(self):
        """Builds the form layout based on the JSON schema (supports nesting)."""
        main_layout = self.layout_type()
        self._build_form(self.schema.get("properties", {}), main_layout)
        self.setLayout(main_layout)

    def _build_form(self, schema: dict, layout):
        """
        Recursively builds widgets from nested schema objects into the given layout.
        Supports QVBoxLayout, QFormLayout, QGridLayout, and custom layouts.
        """
        properties = schema.get("properties", schema)
        row = 0  # For QGridLayout row tracking

        for name, field in properties.items():
            widget_type = field.get("widget")
            title = field.get("title", name)

            if widget_type == "group":
                group_box = QGroupBox(title)
                group_layout = self.layout_type()
                self._build_form(field, group_layout)
                group_box.setLayout(group_layout)
                if isinstance(layout, QGridLayout):
                    self._add_to_layout(layout, group_box, title, row)
                    row += 1
                else:
                    self._add_to_layout(layout, group_box, title)

            elif widget_type == "label":
                label = self.create_widget(name, field)
                if isinstance(layout, QGridLayout):
                    self._add_to_layout(layout, label, "", row)
                    row += 1
                else:
                    self._add_to_layout(layout, label, "")

            elif widget_type == "button":
                button = self.create_widget(name, field)
                self.buttons[name] = button
                if isinstance(layout, QGridLayout):
                    self._add_to_layout(layout, button, "", row)
                    row += 1
                else:
                    self._add_to_layout(layout, button, "")

            elif widget_type == "radio" and field.get("enum"):
                group_box = QGroupBox(title)
                group_layout = self.layout_type()
                for btn in self.create_widget(name, field):
                    group_layout.addWidget(btn)
                group_box.setLayout(group_layout)
                if isinstance(layout, QGridLayout):
                    self._add_to_layout(layout, group_box, title, row)
                    row += 1
                else:
                    self._add_to_layout(layout, group_box, title)

            else:
                widget = self.create_widget(name, field)
                if widget:
                    if isinstance(widget, dict) and "button" in widget and "container" in widget:
                        # Toggle widget (button + container)
                        if isinstance(layout, QGridLayout):
                            self._add_to_layout(layout, widget["button"], "", row)
                            row += 1
                            self._add_to_layout(layout, widget["container"], "", row)
                            row += 1
                        else:
                            self._add_to_layout(layout, widget["button"], "")
                            self._add_to_layout(layout, widget["container"], "")
                        if "children" in field:
                            self._build_form(field["children"], widget["container"].layout())
                    elif isinstance(widget, (list, tuple)) and len(widget) == 2:
                        # Could be multi_toggle returning (control_widget, container)
                        control_widget, container = widget
                        if isinstance(layout, QGridLayout):
                            self._add_to_layout(layout, control_widget, "", row)
                            row += 1
                            self._add_to_layout(layout, container, "", row)
                            row += 1
                        else:
                            self._add_to_layout(layout, control_widget, "")
                            self._add_to_layout(layout, container, "")
                    else:
                        if isinstance(layout, QGridLayout):
                            self._add_to_layout(layout, widget, title, row)
                            row += 1
                        else:
                            self._add_to_layout(layout, widget, title)

        # No longer adding form_layout here; layout is used directly

    def _add_to_layout(self, layout, widget_or_layout, title, row=None):
        """
        Add widget(s) to the layout. If layout is QFormLayout or QVBoxLayout, add normally.
        If QGridLayout, add widgets at given row (title in column 0, widget in column 1).
        """
        if isinstance(layout, QGridLayout) and row is not None:
            # Title in column 0
            label = QLabel(title)
            layout.addWidget(label, row, 0)
            # Widget(s) in column 1
            if isinstance(widget_or_layout, (list, tuple)):
                # Add each widget horizontally next to the label
                col = 1
                for w in widget_or_layout:
                    layout.addWidget(w, row, col)
                    col += 1
            else:
                layout.addWidget(widget_or_layout, row, 1)
        else:
            # For QFormLayout or QVBoxLayout
            if isinstance(layout, QFormLayout):
                if isinstance(widget_or_layout, (list, tuple)):
                    # For multiple widgets in a form row, add a horizontal container (e.g. QWidget + QHBoxLayout)
                    container = QWidget()
                    from PySide6.QtWidgets import QHBoxLayout
                    h_layout = QHBoxLayout(container)
                    h_layout.setContentsMargins(0, 0, 0, 0)
                    for w in widget_or_layout:
                        h_layout.addWidget(w)
                    layout.addRow(title, container)
                else:
                    layout.addRow(title, widget_or_layout)
            else:
                # QVBoxLayout or others
                if isinstance(widget_or_layout, (list, tuple)):
                    for w in widget_or_layout:
                        layout.addWidget(w)
                else:
                    layout.addWidget(widget_or_layout)

    def create_widget(self, name, field):
        """
        Creates and returns a widget based on the field definition.
        Also registers widgets into self.fields/buttons.
        """
        widget_type = field.get("widget")
        field_type = field.get("type")
        enum = field.get("enum")

        # Explicit widget overrides
        if widget_type == "label":
            return QLabel(field.get("text", ""))

        elif widget_type == "button":
            return QPushButton(field.get("text", "Submit"))

        elif widget_type == "textarea":
            widget = QTextEdit()
            self.fields[name] = widget
            return widget

        elif widget_type == "checkbox":
            widget = QCheckBox(field.get("text", field.get("title", name)))
            self.fields[name] = widget
            return widget

        elif widget_type == "spinbox":
            widget = QSpinBox()
            widget.setMinimum(field.get("minimum", 0))
            widget.setMaximum(field.get("maximum", 100))
            self.fields[name] = widget
            return widget

        elif widget_type == "doublespinbox":
            widget = QDoubleSpinBox()
            widget.setMinimum(field.get("minimum", 0.0))
            widget.setMaximum(field.get("maximum", 100.0))
            widget.setSingleStep(field.get("step", 0.1))
            self.fields[name] = widget
            return widget

        elif widget_type == "toggle":
            button = QPushButton("[+]")
            container = QWidget()
            container.setLayout(QVBoxLayout())
            container.setVisible(False)

            def toggle():
                visible = container.isVisible()
                container.setVisible(not visible)
                button.setText("[-]" if not visible else "[+]")

            button.clicked.connect(toggle)

            # Return a dict so your build_form branch matches
            widget = {"button": button, "container": container}
            self.fields[name] = widget
            return widget

        elif widget_type == "combobox" and enum:
            widget = QComboBox()
            widget.addItems(enum)
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
        
        elif widget_type == "lineedit":
            widget = QLineEdit()
            self.fields[name] = widget
            return widget

        # Fallbacks based on "type"
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
        
        elif widget_type == "multi_toggle":
            # Container widget to hold multiple child sets
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(container_layout)

            # Horizontal layout for ComboBox + [+] button
            control_widget = QWidget()
            control_layout = QHBoxLayout()
            control_layout.setContentsMargins(0, 0, 0, 0)
            control_widget.setLayout(control_layout)

            combo = QComboBox()
            combo.addItems(enum if enum else [])
            add_button = QPushButton("[+]")
            control_layout.addWidget(combo)
            control_layout.addWidget(add_button)

            # Function to add a new child set based on current combo selection
            def add_child_set():
                selected_key = combo.currentText()
                # Get children schema for the selected key
                children_schema = field.get("children_map", {}).get(selected_key, {})
                if not children_schema:
                    return

                # Container for this child set with a remove button
                child_container = QWidget()
                child_layout = QHBoxLayout()
                child_layout.setContentsMargins(0, 0, 0, 0)
                child_container.setLayout(child_layout)

                # Widget container for child fields (vertical layout)
                fields_container = QWidget()
                fields_layout = QVBoxLayout()
                fields_layout.setContentsMargins(0, 0, 0, 0)
                fields_container.setLayout(fields_layout)

                # Build the child form into fields_container layout
                self._build_form(children_schema.get("properties", {}), fields_layout)

                # Remove button
                remove_btn = QPushButton("[-]")
                def remove_child():
                    # Remove child container widget from parent layout
                    container_layout.removeWidget(child_container)
                    child_container.deleteLater()
                remove_btn.clicked.connect(remove_child)

                child_layout.addWidget(fields_container)
                child_layout.addWidget(remove_btn)

                container_layout.addWidget(child_container)

            add_button.clicked.connect(add_child_set)

            # Return a composite widget dict for multi_toggle
            # We'll return a dict similar to toggle but with combo & control widget
            self.fields[name] = {
                "container": container,
                "control": control_widget,
                "combo": combo,
                "add_button": add_button,
            }

            # Return the control (combo + [+]) and the container (holds all child sets)
            return (control_widget, container)

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