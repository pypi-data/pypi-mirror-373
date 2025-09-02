# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING, Callable


# ---- Standard library imports
import os.path as osp

# ---- Third party imports
from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QCheckBox, QFrame, QLineEdit, QLabel, QFileDialog, QPushButton,
    QGridLayout, QWidget)


class PathBoxWidget(QFrame):
    """
    A widget to display and select a directory or file location.
    """
    sig_path_changed = Signal(str)

    def __init__(self, parent: QWidget = None, path: str = '',
                 directory: str = '', path_type: str = 'getExistingDirectory',
                 filters: str = None, gettext: Callable = None):
        super().__init__(parent)

        _ = gettext if gettext else lambda x: x
        if path_type == 'getExistingDirectory':
            self._caption = _('Select Existing Directory')
        elif path_type == 'getOpenFileName':
            self._caption = _('Select File')
        elif path_type == 'getSaveFileName':
            self._caption = _('Save File')

        self._directory = directory
        self.filters = filters
        self._path_type = path_type

        self.browse_btn = QPushButton(_("Browse..."))
        self.browse_btn.setDefault(False)
        self.browse_btn.setAutoDefault(False)
        self.browse_btn.clicked.connect(self.browse_path)

        self.path_lineedit = QLineEdit()
        self.path_lineedit.setReadOnly(True)
        self.path_lineedit.setText(path)
        self.path_lineedit.setToolTip(path)
        self.path_lineedit.setFixedHeight(
            self.browse_btn.sizeHint().height() - 2)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.addWidget(self.path_lineedit, 0, 0)
        layout.addWidget(self.browse_btn, 0, 1)

    def is_valid(self):
        """Return whether path is valid."""
        return osp.exists(self.path())

    def is_empty(self):
        """Return whether the path is empty."""
        return self.path_lineedit.text() == ''

    def path(self):
        """Return the path of this pathbox widget."""
        return self.path_lineedit.text()

    def set_path(self, path: str):
        """Set the path to the specified value."""
        if path == self.path:
            return

        self.path_lineedit.setText(path)
        self.path_lineedit.setToolTip(path)
        self.set_directory(osp.dirname(path))
        self.sig_path_changed.emit(path)

    def browse_path(self):
        """Open a dialog to select a new directory."""
        if self._path_type == 'getExistingDirectory':
            path = QFileDialog.getExistingDirectory(
                self, self._caption, self.directory(),
                options=QFileDialog.ShowDirsOnly)
        elif self._path_type == 'getOpenFileName':
            path, ext = QFileDialog.getOpenFileName(
                self, self._caption, self.directory(), self.filters)
        elif self._path_type == 'getSaveFileName':
            path, ext = QFileDialog.getSaveFileName(
                self, self._caption, self.directory(), self.filters)

        if path:
            self.set_path(path)

    def directory(self):
        """Return the directory that is used by the QFileDialog."""
        return (self._directory if osp.exists(self._directory) else
                osp.expanduser('~'))

    def set_directory(self, directory: str = path):
        """Set the default directory that will be used by the QFileDialog."""
        if directory is not None and osp.exists(directory):
            self._directory = directory


class CheckboxPathBoxWidget(QFrame):
    """
    A widget to display and select a directory or file location, with
    a checkbox to enable or disable the widget and a group label.
    """

    def __init__(self, parent: QWidget = None, label: str = '',
                 is_enabled: bool = True, **kwargs):
        super().__init__(parent)
        self.label = label

        self.pathbox_widget = PathBoxWidget(parent, **kwargs)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(
            lambda _: self.pathbox_widget.setEnabled(self.is_enabled()))
        self.checkbox.setChecked(is_enabled)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox, 0, 0)
        layout.addWidget(QLabel(label if label else label), 0, 1)
        layout.addWidget(self.pathbox_widget, 1, 1)

    def is_enabled(self):
        """Return whether this pathbox widget is enabled or not."""
        return self.checkbox.isChecked()

    def set_enabled(self, enabled: bool):
        """Enabled or disabled this widget according to 'enabled'."""
        self.checkbox.setChecked(enabled)

    # ---- PathBoxWidget public API
    def is_valid(self):
        return self.pathbox_widget.is_valid()

    def is_empty(self):
        return self.pathbox_widget.is_empty()

    def path(self):
        return self.pathbox_widget.path()

    def set_path(self, path: str):
        return self.pathbox_widget.set_path(path)

    def browse_path(self):
        return self.pathbox_widget.browse_path()

    def directory(self):
        return self.pathbox_widget.directory()

    def set_directory(self, directory: str):
        return self.pathbox_widget.set_workdir(directory)


if __name__ == '__main__':
    import sys
    from qtapputils.qthelpers import create_qapplication
    qapp = create_qapplication()

    widget = QWidget()
    layout = QGridLayout(widget)

    pathbox = PathBoxWidget(
        parent=widget,
        path="D:/Desktop/test.txt",
        path_type='getOpenFileName')
    layout.addWidget(pathbox, 0, 0)

    layout.setRowMinimumHeight(1, 10)

    checkpathbox = CheckboxPathBoxWidget(
        parent=widget,
        path="D:/Desktop/test.txt",
        label='Use this configuration file:',
        path_type='getOpenFileName')
    layout.addWidget(checkpathbox, 2, 0)

    widget.setMinimumWidth(350)
    widget.show()

    sys.exit(qapp.exec_())
