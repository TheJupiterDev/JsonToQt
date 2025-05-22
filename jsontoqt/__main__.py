import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox, QScrollArea, QPushButton
from .form import JsonForm


class DemoWindow(QWidget):
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("JsonToQt Demo")

        # Load schema from example.json in the project root
        try:
            with open("example.json", "r") as f:
                schema = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schema:\n{e}")
            sys.exit(1)

        self.form = JsonForm(schema)
        self.widg = self.form.build_form()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.widg)

        button = QPushButton('Get Data')
        button.clicked.connect(self.submit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        main_layout.addWidget(button)
        self.setLayout(main_layout)
    
    def submit(self):
        print(self.form.get_form_data())


def main():
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
