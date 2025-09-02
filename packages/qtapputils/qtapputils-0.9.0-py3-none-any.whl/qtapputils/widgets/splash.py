# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

# ---- Third party imports
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    def __init__(self, imgpath: str, msg=None):
        super().__init__(QPixmap(imgpath))
        if msg is not None:
            self.showMessage(msg)
        self.show()
        self.activateWindow()
        self.raise_()

    def showMessage(self, msg):
        """Override Qt method."""
        super().showMessage(msg, Qt.AlignBottom | Qt.AlignCenter)
