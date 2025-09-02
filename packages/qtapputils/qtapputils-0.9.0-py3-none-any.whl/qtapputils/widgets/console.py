# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © SARDES Project Contributors
# https://github.com/cgq-qgc/sardes
#
# This file is part of SARDES.
# Licensed under the terms of the GNU General Public License.
# -----------------------------------------------------------------------------

# ---- Standard library imports
import sys
import os.path as osp
import datetime

# ---- Third party imports
from qtpy.QtCore import Qt
from qtpy.QtGui import QTextCursor, QIcon
from qtpy.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QGridLayout, QPushButton,
    QTextEdit, QWidget)

# ---- Local imports
from qtapputils.managers import SaveFileManager


class StandardStreamConsole(QTextEdit):
    """
    A Qt text edit to hold and show the standard input and output of the
    Python interpreter.
    """

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def write(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)


class SystemMessageDialog(QDialog):
    """
    A dialog to show and manage the standard input and ouput
    of the Python interpreter.
    """

    def __init__(self, title: str, icon: QIcon = None, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() &
            ~Qt.WindowContextHelpButtonHint |
            Qt.WindowMinMaxButtonsHint)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setWindowTitle(title)
        self.setMinimumSize(700, 500)

        def _save_file(filename, content):
            with open(filename, 'w') as txtfile:
                txtfile.write(content)

        self.savefile_manager = SaveFileManager(
            namefilters={'.txt': "Text File (*.txt)"},
            onsave=_save_file,
            parent=self
            )
        self.std_console = StandardStreamConsole()

        # Setup the dialog button box.
        self.saveas_btn = QPushButton('Save As')
        self.saveas_btn.setDefault(False)
        self.saveas_btn.clicked.connect(lambda checked: self.save_as())

        self.close_btn = QPushButton('Close')
        self.close_btn.setDefault(True)
        self.close_btn.clicked.connect(self.close)

        self.copy_btn = QPushButton('Copy')
        self.copy_btn.setDefault(False)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        button_box = QDialogButtonBox()
        button_box.addButton(self.copy_btn, button_box.ActionRole)
        button_box.addButton(self.saveas_btn, button_box.ActionRole)
        button_box.addButton(self.close_btn, button_box.AcceptRole)

        # self.setCentralWidget(self.std_console)
        layout = QGridLayout(self)
        layout.addWidget(self.std_console, 0, 0)
        layout.addWidget(button_box, 1, 0)

    def write(self, text):
        self.std_console.write(text)

    def plain_text(self):
        """
        Return the content of the console as plain text.
        """
        return self.std_console.toPlainText()

    def save_as(self):
        """
        Save the content of the console to a text file.
        """
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = osp.join(
            osp.expanduser('~'),
            'HydrogeolabLog_{}.txt'.format(now)
            )
        filename = self.savefile_manager.save_file_as(
            filename, self.plain_text())

    def copy_to_clipboard(self):
        """
        Copy the content of the console on the clipboard.
        """
        QApplication.clipboard().clear()
        QApplication.clipboard().setText(self.plain_text())

    def show(self):
        """
        Override Qt method.
        """
        if self.windowState() == Qt.WindowMinimized:
            self.setWindowState(Qt.WindowNoState)
        super().show()
        self.activateWindow()
        self.raise_()


if __name__ == '__main__':
    from qtapputils.qthelpers import create_application
    app = create_application()

    console = SystemMessageDialog()
    console.show()

    sys.exit(app.exec_())
