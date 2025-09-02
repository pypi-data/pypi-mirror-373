# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

"""Tests for the qthelpers functions."""

# ---- Standard imports
from math import pi
from itertools import product

# ---- Third party imports
from PyQt5.QtWidgets import QWidget
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QColor
import pytest

# ---- Local imports
from qtapputils.qthelpers import (
    format_tooltip, create_waitspinner, qtwait, get_qcolor,
    set_widget_palette)


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def spinner(qtbot):
    spinner = create_waitspinner(size=48, n=24)
    qtbot.addWidget(spinner)
    return spinner


# =============================================================================
# ---- Tests
# =============================================================================
def test_format_tooltip():
    """Test that tooltip are formatted correctly."""
    texts = ['TEXT', None, '']
    shortcuts = ['S', None, '', 'BADSHORTCUT']
    tips = ['TOOLTIPTEXT', None, '']
    for text, shortcut, tip in product(texts, shortcuts, tips):
        keystr = 'S' if shortcut == 'S' else ''
        if text and keystr and tip:
            expected_ttip = ("<p style='white-space:pre'><b>TEXT (S)</b></p>"
                             "<p>TOOLTIPTEXT</p>")
        elif text and keystr:
            expected_ttip = "<p style='white-space:pre'><b>TEXT (S)</b></p>"
        elif text and tip:
            expected_ttip = ("<p style='white-space:pre'><b>TEXT</b></p>"
                             "<p>TOOLTIPTEXT</p>")
        elif keystr and tip:
            expected_ttip = ("<p style='white-space:pre'><b>(S)</b></p>"
                             "<p>TOOLTIPTEXT</p>")
        elif text:
            expected_ttip = "<p style='white-space:pre'><b>TEXT</b></p>"
        elif keystr:
            expected_ttip = "<p style='white-space:pre'><b>(S)</b></p>"
        elif tip:
            expected_ttip = "<p>TOOLTIPTEXT</p>"
        else:
            expected_ttip = ""

        tooltip = format_tooltip(text=text, shortcuts=shortcut, tip=tip)
        assertion_error = {'text': text, 'shortcut': shortcut, 'tip': tip}

        assert tooltip == expected_ttip, assertion_error


def test_create_waitspinner(spinner, qtbot):
    """Test that creating a waitspinner is working as expected."""
    n = 24
    size = 48
    dot_padding = 1

    dot_size = (pi * size - n * dot_padding) / (n + pi)
    inner_radius = (size - 2 * dot_size) / 2

    assert spinner._numberOfLines == 24
    assert spinner.lineLength() == dot_size
    assert spinner.lineWidth() == dot_size
    assert spinner.innerRadius() == inner_radius
    assert spinner.isTrailSizeDecreasing() is True
    assert spinner.color() == Qt.black

    assert spinner.isVisible() is False
    assert spinner.isSpinning() is False
    assert spinner._currentCounter == 0

    # Start the spinner.
    spinner.start()
    qtbot.wait(100)

    assert spinner.isVisible() is True
    assert spinner.isSpinning() is True
    assert spinner._currentCounter > 0

    # Stop the spinner.
    spinner.stop()
    qtbot.wait(100)

    assert spinner.isVisible() is False
    assert spinner.isSpinning() is False
    assert spinner._currentCounter == 0


def test_qtwait_success(qtbot):
    """
    Test that qtwait returns successfully when the condition becomes
    True before timeout.

    This test simulates an asynchronous change: a variable is set to True
    after 200 ms via a singleShot QTimer. We then call qtwait with a timeout
    of 1 second and expect it to finish without raising any exception.
    """
    state = {'ready': False}

    def set_ready():
        state['ready'] = True

    QTimer.singleShot(200, set_ready)

    assert state['ready'] is False
    qtwait(lambda: state['ready'], timeout=1)
    assert state['ready'] is True


def test_qtwait_timeout(qtbot):
    """
    Test that qtwait raises a TimeoutError if the condition is never
    met within the timeout.

    The condition lambda always returns False, so qtwait should raise a
    TimeoutError after the specified timeout (0.1 seconds).

    The error message should match the one provided.
    """
    with pytest.raises(TimeoutError) as excinfo:
        qtwait(lambda: False, timeout=0.1, error_message="Timeout reached!")
    assert "Timeout reached!" in str(excinfo.value)


def test_get_qcolor():
    """
    Test that get_qcolor correctly creates a QColor from various
    input formats.
    """
    # Test from QColor.
    color = QColor(10, 20, 30)
    result = get_qcolor(color)
    assert isinstance(result, QColor)
    assert result == color

    # Test from RGB tuple.
    result = get_qcolor((100, 150, 200))
    assert isinstance(result, QColor)
    assert result.red() == 100
    assert result.green() == 150
    assert result.blue() == 200

    # Test from RGBA list.
    result = get_qcolor([10, 20, 30, 40])
    assert isinstance(result, QColor)
    assert result.red() == 10
    assert result.green() == 20
    assert result.blue() == 30
    assert result.alpha() == 40

    # Test from HEX string.
    result = get_qcolor("#336699")
    assert isinstance(result, QColor)
    assert result.red() == 51
    assert result.green() == 102
    assert result.blue() == 153

    # Test from color name.
    result = get_qcolor("red")
    assert isinstance(result, QColor)
    assert result.red() == 255
    assert result.green() == 0
    assert result.blue() == 0

    # Test from invalid string.
    with pytest.raises(ValueError):
        get_qcolor("notacolor")

    # Test from invalid type.
    with pytest.raises(ValueError):
        get_qcolor(12345)


def test_set_widget_palette(qtbot):
    """
    Test set_widget_palette for background, foreground, both, and None cases.
    """
    # Background only
    widget = QWidget()
    set_widget_palette(widget, bgcolor=(10, 20, 30))

    bg_color = widget.palette().color(widget.backgroundRole())
    assert isinstance(bg_color, QColor)
    assert (bg_color.red(), bg_color.green(), bg_color.blue()) == (10, 20, 30)
    assert widget.autoFillBackground() is True

    # Foreground only
    widget = QWidget()
    set_widget_palette(widget, fgcolor="#FF00AA")

    fg_color = widget.palette().color(widget.foregroundRole())
    assert isinstance(fg_color, QColor)
    assert (fg_color.red(), fg_color.green(), fg_color.blue()) == (255, 0, 170)

    # Both background and foreground
    widget = QWidget()
    set_widget_palette(widget, bgcolor="blue", fgcolor="yellow")

    bg_color = widget.palette().color(widget.backgroundRole())
    fg_color = widget.palette().color(widget.foregroundRole())
    assert (bg_color.red(), bg_color.green(), bg_color.blue()) == (0, 0, 255)
    assert (fg_color.red(), fg_color.green(), fg_color.blue()) == (255, 255, 0)

    # None for both
    widget = QWidget()
    orig_palette = widget.palette()
    set_widget_palette(widget, bgcolor=None, fgcolor=None)

    assert widget.palette() == orig_palette


if __name__ == "__main__":
    pytest.main(['-x', __file__, '-v', '-rw'])
