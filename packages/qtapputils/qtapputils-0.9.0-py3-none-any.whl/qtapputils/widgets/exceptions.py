# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © SARDES Project Contributors
# https://github.com/cgq-qgc/sardes
#
# This file is part of SARDES.
# Licensed under the terms of the GNU General Public License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING, Callable

# ---- Standard library imports
import os
import os.path as osp
import sys
import datetime
import tempfile


# ---- Third party imports
from qtapputils.icons import get_standard_icon, get_standard_iconsize
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QGridLayout, QLabel, QPushButton,
    QTextEdit, QWidget)


# ---- Local imports
from hydrogeolab.config.main import TEMP_DIR


class ExceptDialog(QDialog):
    """
    A dialog to report internal errors encountered by the application during
    execution.
    """

    def __init__(self, appname: str, appver: str, system_info: str = None,
                 icon: QIcon = None, issue_tracker: str = None,
                 issue_email: str = None, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle(f"{appname} Internal Error")
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        if icon is not None:
            self.setWindowIcon(icon)

        self.log_msg = None
        self.detailed_log = None

        self.appname = appname
        self.appver = appver
        self.system_info = system_info

        self.logmsg_textedit = QTextEdit()
        self.logmsg_textedit.setReadOnly(True)
        self.logmsg_textedit.setMinimumWidth(400)
        self.logmsg_textedit.setLineWrapMode(self.logmsg_textedit.NoWrap)

        icon = get_standard_icon('SP_MessageBoxCritical')
        iconsize = get_standard_iconsize('messagebox')
        info_icon = QLabel()
        info_icon.setScaledContents(False)
        info_icon.setPixmap(icon.pixmap(iconsize))

        # Setup dialog buttons.
        self.ok_btn = QPushButton('OK')
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.close)

        self.copy_btn = QPushButton('Copy')
        self.copy_btn.setDefault(False)
        self.copy_btn.clicked.connect(self.copy)

        button_box = QDialogButtonBox()
        button_box.addButton(self.copy_btn, button_box.AcceptRole)
        button_box.addButton(self.ok_btn, button_box.ActionRole)

        # Setup the dialog button box.
        self.showlog_btn = QPushButton('Detailed Log')
        self.showlog_btn.setDefault(False)
        self.showlog_btn.clicked.connect(self.show_detailed_log)
        button_box.addButton(self.showlog_btn, button_box.ResetRole)

        # Setup dialog main message.
        message = (
            '<b>{namever} has encountered an internal problem.</b>'
            '<p>We are sorry, but {appname} encountered an internal error '
            'that might preventing it from running correctly. You might want '
            'to save your work and restart {appname} if possible.</p>'
            ).format(
                namever=f"{appname} {appver}",
                appname=appname)
        if issue_tracker is not None:
            message += (
                '<p>Please report this error by copying the information below '
                'in our <a href="{issue_tracker}">issues tracker</a> and by '
                'providing a step-by-step description of what led to the '
                'problem.</p>'
                ).format(issue_tracker=issue_tracker)
        elif issue_email is not None:
            message += (
                '<p>Please report this error by sending the information below '
                'to <a href="mailto:{issue_email}">{issue_email}</a> and by '
                'providing a step-by-step description of what led to the '
                'problem.</p>'
                ).format(issue_email=issue_email)
        if any([issue_tracker, issue_email]):
            if self.detailed_log is not None and len(self.detailed_log):
                message += (
                    '<p>If possible, please also attach to your report the '
                    'detailed log file accessible by clicking on the '
                    '<i>Detailed Log</i> button.</p>'
                    )
        msg_labl = QLabel(message)
        msg_labl.setWordWrap(True)
        msg_labl.setOpenExternalLinks(True)

        # Setup layout.
        left_side_layout = QGridLayout()
        left_side_layout.setContentsMargins(0, 0, 10, 0)
        left_side_layout.addWidget(info_icon)
        left_side_layout.setRowStretch(1, 1)

        right_side_layout = QGridLayout()
        right_side_layout.setContentsMargins(0, 0, 0, 0)
        right_side_layout.addWidget(msg_labl)
        right_side_layout.addWidget(self.logmsg_textedit)

        main_layout = QGridLayout(self)
        main_layout.addLayout(left_side_layout, 0, 0)
        main_layout.addLayout(right_side_layout, 0, 1)
        main_layout.addWidget(button_box, 1, 0, 1, 2)

    def set_log_message(self, log_msg):
        """
        Set the log message related to the encountered error.
        """
        self.logmsg_textedit.setText(self._render_error_infotext(log_msg))

    def get_error_infotext(self):
        """
        Return the text containing the information relevant to the
        encountered error that can be copy-pasted directly
        in an issue on GitHub.
        """
        return self.logmsg_textedit.toPlainText()

    def _render_error_infotext(self, log_msg):
        """
        Render the information relevant to the encountered error in a format
        that can be copy-pasted directly in an issue on GitHub.
        """
        message = f"{self.appname} {self.appver}\n\n"
        if self.system_info is not None:
            message += f"{self.system_info}\n\n"
        message += log_msg

        return message

    def show_error(self, log_msg: str = None, detailed_log=None):
        self.log_msg = log_msg
        self.detailed_log = detailed_log
        self.log_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        self.showlog_btn.setVisible(
            detailed_log is not None and len(detailed_log))
        self.set_log_message(log_msg)

        self.exec_()

    def show_detailed_log(self):
        """
        Open the detailed log file in an external application that is
        chosen by the OS.
        """
        name = '{}Log_{}.txt'.format(self.appname, self.log_datetime)
        temp_path = tempfile.mkdtemp(dir=TEMP_DIR)
        temp_filename = osp.join(temp_path, name)
        with open(temp_filename, 'w') as txtfile:
            txtfile.write(self.detailed_log)
        os.startfile(temp_filename)

    def copy(self):
        """
        Copy the issue on the clipboard.
        """
        QApplication.clipboard().clear()
        QApplication.clipboard().setText(self.get_error_infotext())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = ExceptDialog(
        'MyApp', appver='0.1.3', issue_email="info@geostack.ca"
        )
    dialog.show_error("Some Traceback\n")
    sys.exit(app.exec_())
