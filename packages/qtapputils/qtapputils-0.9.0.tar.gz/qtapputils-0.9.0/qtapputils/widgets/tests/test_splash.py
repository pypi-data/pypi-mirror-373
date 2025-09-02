# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""
Tests for widgets in the splash.py module.
"""

# ---- Standard imports
import os.path as osp

# ---- Third party imports
import pytest
from qtpy.QtWidgets import QWidget

# ---- Local imports
from qtapputils.widgets import SplashScreen


# =============================================================================
# ---- Tests for the PathBoxWidget
# =============================================================================
def test_splash(qtbot):
    """Test that getting a file name is working as expected."""
    splash = SplashScreen(
        imgpath=osp.join(osp.dirname(__file__), 'test_splash.png'),
        msg='Initializing splash test...'
        )

    assert splash.isVisible() is True
    assert splash.message() == 'Initializing splash test...'

    splash.showMessage('Create main widget...')
    assert splash.message() == 'Create main widget...'

    main = QWidget()
    splash.finish(main)
    main.show()

    assert splash.isVisible() is False


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-v', '-rw'])
