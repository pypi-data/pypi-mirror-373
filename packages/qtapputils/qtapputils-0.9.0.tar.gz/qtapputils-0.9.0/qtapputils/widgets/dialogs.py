# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Callable


# ---- Third party imports
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QPushButton,
    QWidget, QStackedWidget, QVBoxLayout, QGridLayout, QTextBrowser, QLabel)

# ---- Local imports
from qtapputils.icons import get_standard_icon, get_standard_iconsize
from qtapputils.qthelpers import get_default_contents_margins
from qtapputils.widgets.statusbar import ProcessStatusBar


class UserMessage(QWidget):

    def __init__(self, parent=None,
                 icon: QIcon = None, iconsize: int = 24, text: str = None,
                 spacing: int = 5, contents_margin: list = None):
        super().__init__(parent)
        self._iconsize = iconsize

        # Setup the container for the text.
        class LabelBrowser(QTextBrowser):
            def text(self):
                return self.toPlainText()

            def minimumSizeHint(self):
                return QLabel().minimumSizeHint()

            def sizeHint(self):
                return QLabel().sizeHint()
        self._label = LabelBrowser()
        self._label.setLineWrapMode(LabelBrowser.WidgetWidth)
        self._label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextBrowserInteraction)
        self._label.setOpenExternalLinks(True)
        self._label.setFocusPolicy(Qt.NoFocus)
        self._label.setFrameStyle(0)
        self._label.setStyleSheet("background-color:transparent;")

        # Setup the container for the icon
        self._icon = QLabel()

        # Setup layout.
        layout = QGridLayout(self)
        if contents_margin is None:
            contents_margin = [0, 0, 0, 0]
        layout.setContentsMargins(*contents_margin)
        layout.setSpacing(spacing)

        layout.addWidget(self._icon, 0, 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self._label, 0, 1)

        if icon is not None:
            self.set_icon(icon)
        if text is not None:
            self.set_text()

    def set_icon(self, icon: QIcon):
        """Set the icon of the user message."""
        self._icon.setPixmap(
            icon.pixmap(QSize(self._iconsize, self._iconsize))
            )

    def set_text(self, text: str):
        """Set the text of the user message."""
        self._label.setText(text)


class UserMessageDialogBase(QDialog):
    """
    Basic functionalities to implement a dialog window that provide
    the capability to show messages to the user.

    This class was taken from the Sardes project.
    See sardes/widgets/dialogs.py at https://github.com/geo-stack/sardes
    """

    def __init__(self, parent=None, minimum_height: int = 100,
                 minimum_width: int = None):
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__setup__(minimum_height, minimum_width)

    def __setup__(self, minimum_height, minimum_width):
        """Setup the dialog with the provided settings."""

        self._buttons = []

        # Setup the main widget.
        self.central_widget = QWidget()
        self.central_layout = QGridLayout(self.central_widget)

        # Setup the main layout.
        main_layout = QVBoxLayout(self)
        main_layout.setSizeConstraint(main_layout.SetDefaultConstraint)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Setup the stacked widget.
        self._dialogs = []

        self.stackwidget = QStackedWidget()
        self.stackwidget.addWidget(self.central_widget)
        self.stackwidget.setMinimumHeight(minimum_height)
        if minimum_width is not None:
            self.stackwidget.setMinimumWidth(minimum_width)

        main_layout.addWidget(self.stackwidget)

        # Setup the button box.
        self.button_box = QDialogButtonBox()
        self.button_box.layout().addStretch(1)

        main_layout.addWidget(self.button_box)

        # Note that we need to set the margins of the button box after
        # adding it to the main layout or else, it has no effect.
        self.button_box.layout().setContentsMargins(
            *get_default_contents_margins())

    # ---- Helpers Methods
    def create_button(
            self, text: str, enabled: bool = True,
            triggered: Callable = None, default: bool = False
            ) -> QPushButton:
        """Create a pushbutton to add to the button box."""
        button = QPushButton(text)
        button.setDefault(default)
        button.setAutoDefault(False)
        if triggered is not None:
            button.clicked.connect(triggered)
        button.setEnabled(enabled)
        return button

    def add_button(self, button):
        """Add a new pushbutton to the button box."""
        self._buttons.append(button)
        self.button_box.layout().addWidget(button)

    def create_msg_dialog(
            self, std_icon_name: str, buttons: list[QPushButton]
            ) -> UserMessage:
        """Create a new message dialog."""
        dialog = UserMessage(
            spacing=10,
            iconsize=get_standard_iconsize('messagebox'),
            contents_margin=get_default_contents_margins())
        dialog.set_icon(get_standard_icon(std_icon_name))

        dialog.setAutoFillBackground(True)
        dialog._buttons = buttons

        palette = QApplication.instance().palette()
        palette.setColor(dialog.backgroundRole(), palette.light().color())
        dialog.setPalette(palette)

        # Hide the buttons of the dialogs.
        for btn in buttons:
            btn.setVisible(False)

        return dialog

    def add_msg_dialog(self, dialog: UserMessage):
        """Add a new message dialog to the stack widget."""
        self._dialogs.append(dialog)
        self.stackwidget.addWidget(dialog)
        for button in dialog._buttons:
            self.add_button(button)

    # ---- Public Interface
    def show_message_dialog(
            self, dialog: ProcessStatusBar, message: str, beep: bool = True):
        """Show to the user the specified dialog with the provided message."""
        self.show()
        for btn in self._buttons:
            btn.setVisible(btn in dialog._buttons)
        dialog.set_text(message)
        self.stackwidget.setCurrentWidget(dialog)
        if beep is True:
            QApplication.beep()

    def close_message_dialogs(self):
        """Close all message dialogs and show the main interface."""
        for btn in self._buttons:
            btn.setVisible(True)
        for dialog in self._dialogs:
            for btn in dialog._buttons:
                btn.setVisible(False)
        self.stackwidget.setCurrentWidget(self.central_widget)

    def show(self):
        """
        Override Qt method to raise window to the top when already visible.
        """
        if self.windowState() == Qt.WindowMinimized:
            self.setWindowState(Qt.WindowNoState)
        super().show()
        self.activateWindow()
        self.raise_()
