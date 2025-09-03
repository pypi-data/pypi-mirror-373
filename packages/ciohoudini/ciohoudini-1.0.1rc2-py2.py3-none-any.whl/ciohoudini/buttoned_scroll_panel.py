

from PySide2 import QtWidgets


def clear_layout(layout):
    """
    Recursively clear all widgets and sub-layouts from a given layout.

    Args:
        layout: The Qt layout (QLayout) to clear.

    Notes:
        - Removes and deletes widgets using deleteLater() to ensure proper cleanup.
        - Recursively clears nested layouts.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)  # Get the next item in the layout
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


class ButtonedScrollPanel(QtWidgets.QWidget):
    """
    Module for creating a scrollable panel with buttons in a PySide2-based UI.

    This module provides a `ButtonedScrollPanel` class that creates a widget with a scrollable
    area and a row of buttons, suitable for dialogs or forms. It also includes a utility function
    to clear layouts recursively.

    A widget containing a scrollable area and a row of buttons.

    The scrollable area can contain widgets arranged in a vertical or horizontal layout,
    and a button row is displayed below the scroll area. This is useful for dialog windows
    requiring a scrollable content area with action buttons.

    Attributes:
        dialog: The parent dialog or widget hosting this panel.
        buttons: Dictionary mapping button keys to QPushButton instances.
        layout: The layout (QVBoxLayout or QHBoxLayout) for the scrollable content.
        widget: The widget inside the scroll area that holds the content.
    """

    def __init__(self, dialog, buttons=[("cancel", "Cancel"), ("go", "Go")], direction="column"):
        """
        Initialize the ButtonedScrollPanel.

        Args:
            dialog: The parent dialog or widget hosting this panel.
            buttons: List of tuples, each containing (key, label) for a button.
                     Default: [("cancel", "Cancel"), ("go", "Go")].
            direction: Layout direction for the scrollable content ("column" for vertical,
                       or any other value for horizontal). Default: "column".
        """
        super().__init__()  # Initialize the base QWidget class
        self.dialog = dialog
        self.buttons = {}

        # Create the main vertical layout for the panel
        vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(vlayout)

        # Set up the scroll area
        scroll_area = QtWidgets.QScrollArea()
        vlayout.addWidget(scroll_area)
        scroll_area.setWidgetResizable(True)  # Allow the scroll area to resize its content

        # Create a widget and layout for the button row
        button_row_widget = QtWidgets.QWidget()
        button_row_layout = QtWidgets.QHBoxLayout()
        button_row_widget.setLayout(button_row_layout)

        # Add buttons to the button row
        for key, label in buttons:
            button = QtWidgets.QPushButton(label)
            button.setAutoDefault(False)  # Prevent button from being the default action
            button_row_layout.addWidget(button)
            self.buttons[key] = button  # Store button reference
        vlayout.addWidget(button_row_widget)

        # Create the widget for the scrollable content
        self.widget = QtWidgets.QWidget()
        scroll_area.setWidget(self.widget)

        # Set the layout direction for the scrollable content
        if direction == "column":
            self.layout = QtWidgets.QVBoxLayout()
        else:
            self.layout = QtWidgets.QHBoxLayout()
        self.widget.setLayout(self.layout)

    def clear(self):
        """
        Clear all widgets from the scrollable content layout.

        Uses the clear_layout utility function to recursively remove and delete
        all widgets and sub-layouts.
        """
        clear_layout(self.layout)