# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Tests for widgets in the path.py module.
"""

# ---- Standard imports
import os.path as osp

# ---- Third party imports
import pytest
from qtpy.QtCore import Qt

# ---- Local imports
from qtapputils.widgets.path import PathBoxWidget, QFileDialog


# =============================================================================
# ---- Fixtures
# =============================================================================
@pytest.fixture
def pathbox(qtbot):
    pathbox = PathBoxWidget(
        parent=None,
        path='',
        directory='',
        path_type='getSaveFileName',
        filters=None
        )
    qtbot.addWidget(pathbox)
    pathbox.show()
    return pathbox


# =============================================================================
# ---- Tests for the PathBoxWidget
# =============================================================================
def test_getopen_filename(qtbot, pathbox, mocker, tmp_path):
    """Test that getting a file name is working as expected."""
    assert not pathbox.is_valid()
    assert pathbox.is_empty()
    assert pathbox.path() == ''
    assert osp.samefile(pathbox.directory(), osp.expanduser('~'))

    # Create an empty file.
    selectedfilter = 'Text File (*.txt)'
    selectedfilename = osp.join(tmp_path, 'pathbox_testfile.txt')
    with open(selectedfilename, 'w') as txtfile:
        txtfile.write('test')

    # Patch the open file dialog and select the test file.
    qfdialog_patcher = mocker.patch.object(
        QFileDialog,
        'getSaveFileName',
        return_value=(selectedfilename, selectedfilter)
        )
    qtbot.mouseClick(pathbox.browse_btn, Qt.LeftButton)

    assert qfdialog_patcher.call_count == 1
    assert pathbox.is_valid()
    assert not pathbox.is_empty()
    assert pathbox.path() == selectedfilename
    assert osp.samefile(pathbox.directory(), tmp_path)


if __name__ == "__main__":
    pytest.main(['-x', osp.basename(__file__), '-v', '-rw'])
