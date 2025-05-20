from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QCheckBox,
    QRadioButton, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
    QVBoxLayout, QGroupBox, QFormLayout, QGridLayout, QHBoxLayout
)


class JsonForm(QWidget):
    """
    A dynamic PySide6 form generated from a JSON schema.
    """
    def __init__(self, schema: dict, parent=None, layout_type=QVBoxLayout):
        super().__init__(parent)
        self.schema = schema
        self.fields = {}    # maps full_field_key -> widget or list of widgets or dict for composites
        self.buttons = {}
        self.layout_type = layout_type
        self.build_ui()

    def build_ui(self):
        main_layout = self.layout_type()
        # kick off recursion with empty prefix
        self._build_form(self.schema.get("properties", {}), main_layout, prefix=[])
        self.setLayout(main_layout)

    def _build_form(self, properties: dict, layout, prefix: list):
        row = 0
        for name, field in properties.items():
            full_key = prefix + [name]
            key_str = ".".join(full_key)
            widget_type = field.get("widget")
            title = field.get("title", name)

            # ----- GROUP -----
            if widget_type == "group":
                group_box = QGroupBox(title)
                group_layout = self.layout_type()
                # recurse with new prefix
                self._build_form(field.get("properties", {}), group_layout, full_key)
                group_box.setLayout(group_layout)
                self._add_to_layout(layout, group_box, title, row)
                row += isinstance(layout, QGridLayout)

            # ----- STATIC LABEL -----
            elif widget_type == "label":
                label = QLabel(field.get("text", ""))
                self.fields[key_str] = label
                self._add_to_layout(layout, label, "", row)
                row += isinstance(layout, QGridLayout)

            # ----- BUTTON -----
            elif widget_type == "button":
                btn = QPushButton(field.get("text", "Submit"))
                self.fields[key_str] = btn
                self.buttons[name] = btn
                self._add_to_layout(layout, btn, "", row)
                row += isinstance(layout, QGridLayout)

            # ----- RADIO GROUP -----
            elif widget_type == "radio" and field.get("enum"):
                group_box = QGroupBox(title)
                grp_layout = self.layout_type()
                btns = []
                for val in field["enum"]:
                    r = QRadioButton(val)
                    r.field_key = key_str
                    btns.append(r)
                    grp_layout.addWidget(r)
                self.fields[key_str] = btns
                group_box.setLayout(grp_layout)
                self._add_to_layout(layout, group_box, title, row)
                row += isinstance(layout, QGridLayout)

            # ----- OTHER WIDGETS (including toggle & multi_toggle) -----
            else:
                created = self._create_widget(key_str, field)
                if not created:
                    continue

                # unpack composite vs single widget
                if isinstance(created, dict):
                    # toggle or multi_toggle dict
                    # store the dict under key_str (done in _create_widget)
                    # add control & container
                    control = created.get("control") or created.get("button")
                    container = created["container"]
                    self._add_to_layout(layout, control, "", row)
                    row += isinstance(layout, QGridLayout)
                    self._add_to_layout(layout, container, "", row)
                    row += isinstance(layout, QGridLayout)
                    # for toggle, build its children
                    if field.get("widget") == "toggle":
                        self._build_form(field.get("children", {}), container.layout(), full_key)
                elif isinstance(created, (list, tuple)):
                    # multi_toggle returns (control_widget, container)
                    control, container = created
                    self._add_to_layout(layout, control, "", row)
                    row += isinstance(layout, QGridLayout)
                    self._add_to_layout(layout, container, "", row)
                    row += isinstance(layout, QGridLayout)
                else:
                    # simple widget
                    self._add_to_layout(layout, created, title, row)
                    row += isinstance(layout, QGridLayout)

    def _add_to_layout(self, layout, widget_or_layout, title, row=None):
        """
        Add widget(s) to the layout. If layout is QFormLayout or QVBoxLayout, add normally.
        If QGridLayout, add widgets at given row (title in column 0, widget in column 1).
        """
        # Determine if we should add a label
        def should_add_label(w):
            # No label for group boxes or buttons
            if isinstance(w, QGroupBox):
                return False
            if isinstance(w, QPushButton):
                return False
            return True

        if isinstance(layout, QGridLayout) and row is not None:
            if should_add_label(widget_or_layout):
                label = QLabel(title)
                layout.addWidget(label, row, 0)
                # Widget(s) in column 1
                if isinstance(widget_or_layout, (list, tuple)):
                    col = 1
                    for w in widget_or_layout:
                        layout.addWidget(w, row, col)
                        col += 1
                else:
                    layout.addWidget(widget_or_layout, row, 1)
            else:
                # Just add widget(s) spanning both columns or in column 0 and 1 without label
                if isinstance(widget_or_layout, (list, tuple)):
                    col = 0
                    for w in widget_or_layout:
                        layout.addWidget(w, row, col)
                        col += 1
                else:
                    layout.addWidget(widget_or_layout, row, 0)
        else:
            if isinstance(layout, QFormLayout):
                if should_add_label(widget_or_layout):
                    if isinstance(widget_or_layout, (list, tuple)):
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
                    # Just add widget without label in QFormLayout
                    if isinstance(widget_or_layout, (list, tuple)):
                        for w in widget_or_layout:
                            layout.addWidget(w)
                    else:
                        layout.addWidget(widget_or_layout)
            else:
                if isinstance(widget_or_layout, (list, tuple)):
                    for w in widget_or_layout:
                        layout.addWidget(w)
                else:
                    layout.addWidget(widget_or_layout)


    def _create_widget(self, key_str, field):
        """
        Create each widget, tag .field_key, and store in self.fields.
        Returns either:
          - a single QWidget
          - a list (for radio buttons)
          - a dict with 'container' plus control/button keys (toggle, multi_toggle)
        """
        wtype = field.get("widget")
        enum = field.get("enum")

        # -- LABEL handled in _build_form --

        # -- TEXT AREA --
        if wtype == "textarea":
            w = QTextEdit()
            w.field_key = key_str
            self.fields[key_str] = w
            return w

        # -- CHECKBOX --
        if wtype == "checkbox":
            w = QCheckBox(field.get("title", key_str))
            w.field_key = key_str
            self.fields[key_str] = w
            return w

        # -- SPINBOX / DOUBLE SPINBOX --
        if wtype == "spinbox" or field.get("type") == "integer":
            w = QSpinBox()
            w.setMinimum(field.get("minimum", 0))
            w.setMaximum(field.get("maximum", 100))
            w.field_key = key_str
            self.fields[key_str] = w
            return w

        if wtype == "doublespinbox" or field.get("type") == "number":
            w = QDoubleSpinBox()
            w.setMinimum(field.get("minimum", 0.0))
            w.setMaximum(field.get("maximum", 100.0))
            w.setSingleStep(field.get("step", 0.1))
            w.field_key = key_str
            self.fields[key_str] = w
            return w

        # -- LINE EDIT / STRING --
        if wtype == "lineedit" or field.get("type") == "string":
            if enum:
                w = QComboBox()
                w.addItems(enum)
            else:
                w = QLineEdit()
            w.field_key = key_str
            self.fields[key_str] = w
            return w

        # -- COMBOBOX for enum fallback --
        if wtype == "combobox" and enum:
            w = QComboBox()
            w.addItems(enum)
            w.field_key = key_str
            self.fields[key_str] = w
            return w

        # -- RADIO fallback handled in _build_form --

        # -- TOGGLE (collapsible) --
        if wtype == "toggle":
            btn = QPushButton("[+]")
            container = QWidget()
            container.setLayout(QVBoxLayout())
            container.setVisible(False)
            btn.field_key = key_str + ".__toggle_btn__"
            container.field_key = key_str + ".__toggle_container__"
            self.fields[key_str] = {"button": btn, "container": container}

            def toggle():
                show = not container.isVisible()
                container.setVisible(show)
                btn.setText("[-]" if show else "[+]")
            btn.clicked.connect(toggle)
            return {"button": btn, "container": container}

        # -- MULTI_TOGGLE (dynamic repeats) --
        if wtype == "multi_toggle":
            container = QWidget()
            container.setLayout(QVBoxLayout())
            combo = QComboBox()
            combo.addItems(enum or [])
            add_btn = QPushButton("[+]")
            control = QWidget()
            hl = QHBoxLayout(control); hl.setContentsMargins(0,0,0,0)
            hl.addWidget(combo); hl.addWidget(add_btn)

            def add_child():
                sel = combo.currentText()
                props = field["children_map"][sel]["properties"]
                inst = QWidget()
                inst.setLayout(QHBoxLayout())
                left = QWidget(); left.setLayout(QVBoxLayout())
                # build inside left side
                self._build_form(props, left.layout(), prefix=key_str.split(".") + [sel, str(container.layout().count())])
                right = QPushButton("[-]")
                def rem():
                    container.layout().removeWidget(inst)
                    inst.deleteLater()
                right.clicked.connect(rem)
                inst.layout().addWidget(left); inst.layout().addWidget(right)
                container.layout().addWidget(inst)

            add_btn.clicked.connect(add_child)
            self.fields[key_str] = {"container": container, "control": control}
            return (control, container)

        return None

    def bind_callbacks(self, callback_map: dict):
        for name, btn in self.buttons.items():
            cb = self.schema["properties"][name].get("callback")
            if cb and callback_map.get(cb):
                btn.clicked.connect(callback_map[cb])

    def get_data(self):
        """
        Walks through the widget tree and returns a nested dict/lists
        matching your original JSON schema structure.
        """
        def recurse_properties(props, prefix):
            out = {}
            for name, cfg in props.items():
                key = ".".join(prefix + [name])
                wtype = cfg.get("widget")

                # -- GROUP --
                if wtype == "group":
                    out[name] = recurse_properties(cfg["properties"], prefix + [name])

                # -- TOGGLE --
                elif wtype == "toggle":
                    sub = {}
                    for child_name in cfg["children"]:
                        child_key = ".".join(prefix + [name, child_name])
                        w = self.fields.get(child_key)
                        if w:
                            sub[child_name] = self._value_of(w)
                    out[name] = sub

                # -- MULTI_TOGGLE --
                elif wtype == "multi_toggle":
                    arr = []
                    container = self.fields[key]["container"]
                    for i in range(container.layout().count()):
                        inst = container.layout().itemAt(i).widget()
                        # gather all widgets under this instance
                        inst_data = {}
                        def walk(widget):
                            for i in range(widget.layout().count()):
                                child = widget.layout().itemAt(i).widget()
                                if hasattr(child, "field_key") and "__toggle" not in child.field_key:
                                    # get the short name after last dot
                                    inst_data[ child.field_key.split(".")[-1] ] = self._value_of(child)
                                # recurse deeper if it's a container
                                if child.layout():
                                    walk(child)
                        walk(inst)
                        arr.append(inst_data)
                    out[name] = arr

                # -- PRIMITIVE --
                else:
                    w = self.fields.get(key)
                    if w is not None:
                        out[name] = self._value_of(w)

            return out

        return recurse_properties(self.schema["properties"], [])

    def _value_of(self, w):
        """Extract a Python value from any widget or list-of-widgets."""
        if isinstance(w, list):
            for btn in w:
                if btn.isChecked():
                    return btn.text()
            return None
        if isinstance(w, QLineEdit):
            return w.text()
        if isinstance(w, QTextEdit):
            return w.toPlainText()
        if isinstance(w, QComboBox):
            return w.currentText()
        if isinstance(w, (QSpinBox, QDoubleSpinBox)):
            return w.value()
        if isinstance(w, QCheckBox):
            return w.isChecked()
        return None
