from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


class ButtonedScrollPanel(QWidget):
    def __init__(
        self, editor, buttons=[("cancel", "Cancel"), ("go", "Go")], direction="column"
    ):
        super(ButtonedScrollPanel, self).__init__()
        self.editor = editor

        self.buttons = {}

        vlayout = QVBoxLayout()

        self.setLayout(vlayout)

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #757575; }")

        scroll_area.setWidgetResizable(1)

        button_row_widget = QWidget()
        button_row_layout = QHBoxLayout()
        # button_row_widget.setMaximumWidth(750)
        # button_row_layout.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_row_layout.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        
        button_row_widget.setLayout(button_row_layout)
        button_row_widget.setFixedHeight(40)

        for key, label in buttons:
            button = QPushButton(label)
            button.setAutoDefault(False)
            button_row_layout.addWidget(
                button, Qt.AlignCenter, Qt.AlignBottom
            )
            self.buttons[key] = button

        self.widget = QWidget()
        scroll_area.setWidget(self.widget)

        vlayout.addWidget(scroll_area)
        vlayout.addWidget(button_row_widget)

        if direction == "column":
            self.layout = QVBoxLayout()
        else:
            self.layout = QHBoxLayout()
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.widget.setLayout(self.layout)

    def clear(self):
        clear_layout(self.layout)

    def on_back(self):
        self.editor.setCurrentWidget( self.editor.configuration_tab)
