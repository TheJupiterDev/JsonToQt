import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox, QGridLayout, QFormLayout
from .form import JsonForm


class DemoWindow(QWidget):
    def __init__(self, layout_type=QVBoxLayout):
        super().__init__()
        self.setWindowTitle("JsonToQt Demo")

        # Load schema from example.json in the project root
        try:
            with open("example.json", "r") as f:
                schema = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schema:\n{e}")
            sys.exit(1)

        # Pass the layout_type to JsonForm
        self.form = JsonForm(schema, layout_type=layout_type)

        # Bind callbacks defined in the schema to local methods
        self.form.bind_callbacks({
            "on_submit": self.on_submit,
            "on_cancel": self.on_cancel
        })

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form)
        self.setLayout(main_layout)

    def on_submit(self):
        data = self.form.get_data()
        QMessageBox.information(self, "Form Submitted", json.dumps(data, indent=2))

    def on_cancel(self):
        QMessageBox.warning(self, "Cancelled", "The form has been cancelled.")
        self.close()


def main():
    app = QApplication(sys.argv)
    # Example: use QGridLayout for the form, or change to QFormLayout/QVBoxLayout
    window = DemoWindow(layout_type=QGridLayout)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
