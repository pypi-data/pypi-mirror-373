"""
Module for creating a custom notice group widget in the Conductor plugin for Houdini.

This module defines a PySide2-based QFrame widget that displays a notice with an icon, text,
and an optional clickable URL, styled according to a specified severity level.
"""

import os
from PySide2 import QtWidgets, QtCore, QtGui
from ciohoudini.const import PLUGIN_DIR
import webbrowser


class NoticeGrp(QtWidgets.QFrame):
    """
    A custom QFrame widget for displaying notices with an icon and optional URL link.

    Displays a notice with a severity-based icon (info, warning, error, success) and either
    a text label or a clickable button if a URL is provided.

    Attributes:
        url (str): Optional URL to open when the button is clicked.
        scale_factor (float): Scaling factor based on screen DPI for UI adjustments.
    """

    def __init__(self, text, severity="info", url=None):
        """
        Initialize the notice group widget.

        Args:
            text (str): The text to display in the notice.
            severity (str): The severity level ('info', 'warning', 'error', 'success').
                           Defaults to 'info'. Falls back to 'error' if invalid.
            url (str, optional): URL to open when clicked, if provided.
        """
        super(NoticeGrp, self).__init__()

        self.url = url
        # Validate and default severity to 'error' if invalid
        if severity not in ["info", "warning", "error", "success"]:
            severity = "error"

        # Calculate scaling factor based on screen DPI
        self.scale_factor = self.logicalDpiX() / 96.0
        # Set icon size based on DPI
        icon_size = 24 if self.logicalDpiX() < 150 else 48

        # Configure frame style and line width
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.setLineWidth(2)

        # Create horizontal layout for the widget
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        # Construct icon file path
        icon_filename = f"Conductor{severity.capitalize()}_{icon_size}x{icon_size}.png"
        iconPath = os.path.join(PLUGIN_DIR, "icons", icon_filename)

        # Create and configure icon label
        img_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(iconPath)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        img_label.setFixedWidth(40 * self.scale_factor)
        layout.addWidget(img_label)

        # Create either a button (for URL) or a label (for text)
        if self.url:
            widget = QtWidgets.QPushButton(text)
            widget.setAutoDefault(False)
            widget.clicked.connect(self.on_click)
        else:
            widget = QtWidgets.QLabel()
            widget.setMargin(10)
            widget.setWordWrap(True)
            widget.setText(text)

        # Add the text/button widget to the layout
        layout.addWidget(widget)

    def on_click(self):
        """
        Open the stored URL in a web browser when the button is clicked.
        """
        webbrowser.open(self.url)