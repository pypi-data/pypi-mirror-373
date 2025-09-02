# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""About app dialog."""


# ---- Third party imports
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap, QIcon
from qtpy.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, QLabel, QFrame,
    QWidget, QTextEdit, QVBoxLayout
    )


class AboutDialog(QDialog):

    def __init__(self, icon: QIcon, title: str,
                 copyright_holder: str,
                 longdesc: str,
                 appname: str,
                 website_url: str,
                 banner_fpath: str,
                 system_info: str = None,
                 license_fpath: str = None,
                 parent: QWidget = None,
                 ):
        """Create an About dialog with general information."""
        super().__init__(parent=parent)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(icon)
        self.setWindowTitle(title)

        pixmap = QPixmap(banner_fpath)
        self.label_pic = QLabel(self)
        self.label_pic.setPixmap(
            pixmap.scaledToWidth(450, Qt.SmoothTransformation))
        self.label_pic.setAlignment(Qt.AlignTop)

        # Get current font properties
        font = self.font()
        font_family = font.family()
        font_size = font.pointSize()

        text = (
            """
            <div style='font-family: "{font_family}";
                        font-size: {font_size}pt;
                        font-weight: normal;
                        '>
            <p>
            <br><b>{appname}</b><br>
            Copyright &copy; {copyright_holder}<br>
            <a href="{website_url}">{website_url}</a>
            </p>
            <p>{longdesc}</p>
            """.format(
                appname=appname,
                website_url=website_url,
                font_family=font_family,
                font_size=font_size,
                copyright_holder=copyright_holder,
                longdesc=longdesc)
        )
        if system_info is not None:
            text += "<p>" + system_info + "</p>"
        text += "</div>"

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignTop)
        self.label.setOpenExternalLinks(True)
        self.label.setTextInteractionFlags(Qt.TextBrowserInteraction)

        content_frame = QFrame(self)
        content_frame.setStyleSheet(
            "QFrame {background-color: white}")
        content_layout = QGridLayout(content_frame)
        content_layout.addWidget(self.label_pic, 0, 0)
        content_layout.addWidget(self.label, 1, 0)
        content_layout.setContentsMargins(15, 15, 15, 15)

        if license_fpath is not None:
            content_layout.setRowMinimumHeight(2, 10)

            license_title = QLabel('<b>License Info :</b>')

            license_textedit = QTextEdit()
            license_textedit.insertPlainText(open(license_fpath).read())
            license_textedit.setTextInteractionFlags(Qt.TextBrowserInteraction)
            license_textedit.moveCursor(license_textedit.textCursor().Start)

            content_layout.addWidget(license_title, 3, 0)
            content_layout.addWidget(license_textedit, 4, 0)

        bbox = QDialogButtonBox(QDialogButtonBox.Ok)
        bbox.accepted.connect(self.accept)

        # Setup the layout.
        layout = QVBoxLayout(self)
        layout.addWidget(content_frame)
        layout.addWidget(bbox)
        layout.setSizeConstraint(layout.SetFixedSize)

    def show(self):
        """Overide Qt method."""
        super().show()
        self.activateWindow()
        self.raise_()
