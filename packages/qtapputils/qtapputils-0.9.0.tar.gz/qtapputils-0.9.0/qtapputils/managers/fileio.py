# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

from __future__ import annotations
from typing import Callable

# ---- Standard imports
import os.path as osp

# ---- Third party imports
from qtpy.QtCore import QObject
from qtpy.QtWidgets import QMessageBox, QFileDialog, QWidget


class SaveFileManager(QObject):
    def __init__(self, namefilters: dict, onsave: Callable,
                 parent: QWidget = None):
        """
        A manager to save files.

        Parameters
        ----------
        namefilters : dict
            A dictionary containing the file filters to use in the
            'Save As' file dialog. Here is an example of a correctly
            formated namefilters dictionary:

                namefilters = {
                    '.pdf': 'Portable Document Format (*.pdf)',
                    '.svg': 'Scalable Vector Graphics (*.svg)',
                    '.png': 'Portable Network Graphics (*.png)',
                    '.jpg': 'Joint Photographic Expert Group (*.jpg)'
                    }

            Note that the first entry in the dictionary will be used as the
            default name filter to use in the 'Save As' dialog.
        onsave : Callable
            The callable that is used to save the file.
        parent: QWidget, optional
            The parent widget to use for the 'Save As' file dialog.
        """
        super().__init__()
        self.parent = parent
        self.namefilters = namefilters
        self.onsave = onsave

    def save_file(self, filename: str, *args, **kwargs) -> str:
        """
        Save in provided filename.

        Parameters
        ----------
        filename : str
            The abosulte path where to save the file.

        Returns
        -------
        filename : str
            The absolute path where the file was successfully saved. Returns
            'None' if the saving operation was cancelled or was unsuccessfull.
        """
        try:
            self.onsave(filename, *args, **kwargs)
        except PermissionError:
            QMessageBox.warning(
                self.parent,
                'File in Use',
                ("The save file operation cannot be completed because the "
                 "file is in use by another application or user."),
                QMessageBox.Ok)
            filename = self.save_file_as(filename, *args, **kwargs)
        return filename

    def save_file_as(self, filename: str, *args, **kwargs) -> str:
        """
        Save in a new file.

        Parameters
        ----------
        filename : dict
            The default or suggested absolute path where to save the file.

        Returns
        -------
        filename : str
            The absolute path where the file was successfully saved. Returns
            'None' if the saving operation was cancelled or was unsuccessfull.
        """
        root, ext = osp.splitext(filename)
        if ext not in self.namefilters:
            ext = next(iter(self.namefilters))
            filename += ext

        filename, filefilter = QFileDialog.getSaveFileName(
            self.parent,
            "Save As",
            filename,
            ';;'.join(self.namefilters.values()),
            self.namefilters[ext])
        if filename:
            # Make sur the filename has the right extension.
            ext = dict(map(reversed, self.namefilters.items()))[filefilter]
            if not filename.endswith(ext):
                filename += ext

            return self.save_file(filename, *args, **kwargs)
