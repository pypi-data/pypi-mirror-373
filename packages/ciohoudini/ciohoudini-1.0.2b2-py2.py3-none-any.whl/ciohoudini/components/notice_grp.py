import os
from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)
from ciohoudini import const as k
import webbrowser

LINK_STYLESHEET = """
QPushButton { 
    color: #2C8BB3;  
    background-color: rgba(255, 255, 255, 0);
}
QPushButton:hover { 
    color: #51B2DA;
    background-color: rgba(255, 255, 255, 0);
}
"""


class NoticeGrp(QFrame):
    def __init__(self, text, severity="info", url=None, details=None):
        super(NoticeGrp, self).__init__()

        if severity not in ["info", "warning", "error", "success"]:
            severity = "error"

        icon_size = 24

        self.details = details
        self.url = url

        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLineWidth(2)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(QtCore.Qt.AlignTop)

        icon_filename = "Conductor{0}_{1}x{1}.png".format(
            severity.capitalize(), icon_size
        )
        iconPath = os.path.join(k.PLUGIN_DIR, "icons", icon_filename)

        img_label = QLabel(self)
        img_label.setStyleSheet("margin-top: 10px;")

        pixmap = QtGui.QPixmap(iconPath)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        img_label.setFixedWidth(80)

        layout.addWidget(img_label)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)

        widget = QLabel()

        widget.setWordWrap(True)
        widget.setText(text)

        content_layout.addWidget(widget)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        if url or details:
            if url:
                label, link = url
                link_button = QPushButton(label)
                link_button.setAutoDefault(False)
                link_button.clicked.connect(lambda: webbrowser.open(link))
                link_button.setFlat(True)
                link_button.setStyleSheet(LINK_STYLESHEET)

                button_layout.addWidget(link_button)

            if details:
                self.details_button = QPushButton("Show details")
                self.details_button.setAutoDefault(False)
                self.details_button.setCheckable(True)
                self.details_button.setChecked(False)
                self.details_button.toggled.connect(self.toggle_details)
                self.details_button.setFlat(True)
                self.details_button.setStyleSheet(LINK_STYLESHEET)
                button_layout.addWidget(self.details_button)

                self.details_widget = QTextEdit()
                self.details_widget.setReadOnly(True)
                self.details_widget.setHidden(True)
                self.details_widget.setWordWrapMode(QtGui.QTextOption.NoWrap)
                self.details_widget.setFontFamily("Courier")

                content_layout.addWidget(self.details_widget)

        content_layout.addLayout(button_layout)

        layout.addLayout(content_layout)
        content_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

    def toggle_details(self, checked):
        if checked:
            self.details_widget.setPlainText(self.details)

            self.details_widget.setHidden(False)
            self.details_button.setText("Hide details")
        else:
            self.details_widget.setHidden(True)
            self.details_button.setText("Show details")
