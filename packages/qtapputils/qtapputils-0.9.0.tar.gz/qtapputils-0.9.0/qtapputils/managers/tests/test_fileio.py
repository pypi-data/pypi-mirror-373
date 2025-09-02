# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Tests for the fileio managers.
"""

# ---- Standard imports
import os.path as osp

# ---- Third party imports
import pytest
from qtpy.QtWidgets import QFileDialog, QMessageBox

# ---- Local imports
from qtapputils.managers import SaveFileManager

FILECONTENT = "Test save file manager."


# =============================================================================
# ---- Fixtures
# =============================================================================
@pytest.fixture
def savefile_manager(qtbot):

    def onsave(filename, filecontent):
        if 'blocked' in filename:
            raise PermissionError

        with open(filename, 'w') as f:
            f.write(filecontent)

    manager = SaveFileManager(
        namefilters={
            '.txt': 'Text File (*.txt)',
            '.docx': 'Microsoft Word Document (*.docx)'
            },
        onsave=onsave
        )
    return manager


# =============================================================================
# ---- Tests
# =============================================================================
def test_save_file(savefile_manager, qtbot, tmp_path):
    """
    Test that saving a file is working as expected.
    """
    filename = osp.join(tmp_path, 'test_savefile.txt')
    assert not osp.exists(filename)

    returned_filename = savefile_manager.save_file(filename, FILECONTENT)

    assert osp.exists(filename)
    assert filename == returned_filename
    with open(filename, 'r') as f:
        assert FILECONTENT == f.read()


def test_save_file_error(savefile_manager, qtbot, tmp_path, mocker):
    """
    Test that selecting a new file when an error is raised is
    working as expected.
    """
    qmsgbox_patcher = mocker.patch.object(
        QMessageBox, 'warning', return_value=QMessageBox.Ok
        )

    filename = osp.join(tmp_path, 'test_savefile')
    assert not osp.exists(filename)

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(filename, 'Text File (*.txt)')
        )
    returned_filename = savefile_manager.save_file(
        filename + '_blocked', FILECONTENT)

    assert qfdialog_patcher.call_count == 1
    assert qmsgbox_patcher.call_count == 1
    assert returned_filename == filename + '.txt'
    assert osp.exists(filename + '.txt')


def test_save_file_error_cancelled(savefile_manager, qtbot, tmp_path, mocker):
    """
    Test that cancelling the saving process when an error is raised is
    working as expected.
    """
    qmsgbox_patcher = mocker.patch.object(
        QMessageBox, 'warning', return_value=QMessageBox.Ok
        )

    # Test that cancelling the saving process when an error is raised is
    # working as expected.

    filename = osp.join(tmp_path, 'test_savefile_blocked.txt')
    assert not osp.exists(filename)

    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(None, None)
        )
    returned_filename = savefile_manager.save_file(filename, FILECONTENT)

    assert qfdialog_patcher.call_count == 1
    assert qmsgbox_patcher.call_count == 1
    assert returned_filename is None
    assert not osp.exists(filename)


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-v', '-rw', '-s'])
