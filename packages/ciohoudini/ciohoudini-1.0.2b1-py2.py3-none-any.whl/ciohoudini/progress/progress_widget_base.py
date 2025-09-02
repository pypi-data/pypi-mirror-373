

from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide2 import QtCore


class ProgressWidgetBase(QWidget):
    """
    Styled progress bar widget base class.
    """

    def __init__(self, *args, **kwargs):
        LABEL = ""

        super(ProgressWidgetBase, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        labels_layout = QHBoxLayout()
        self.label_widget = QLabel()
        self.label_widget.setAlignment(QtCore.Qt.AlignLeft)  #
        self.label_widget.setStyleSheet("font-size: 14px;color: #757575;")
        self.progress_label = QLabel()
        self.progress_label.setAlignment(QtCore.Qt.AlignRight)
        self.progress_label.setStyleSheet("font-size: 14px;color: #757575;")

        labels_layout.addWidget(self.label_widget)
        labels_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar(parent=self)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setTextVisible(False)

        self.layout.addLayout(labels_layout)
        self.layout.addWidget(self.progress_bar)

        self.reset()

    def set_progress(self, percent, label=None):
        """Set the progress bar to a percentage.
        
        We prevent the progress bar from going backwards, because some progress
        objects may have zero progress.
        """
        if label:
            self.label_widget.setText(label)
        percent = int(percent * 10) / 10.0
        if percent > self.progress_bar.value():
            self.progress_label.setText(f"{percent}%")
            self.progress_bar.setValue(percent)

    def reset(self, *args, **kwargs):
        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        self.label_widget.setText(self.LABEL)
