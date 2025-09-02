# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------


# ---- Third party imports
from qtpy.QtCore import Signal, QObject, QLocale, Qt
from qtpy.QtGui import QValidator
from qtpy.QtWidgets import QDoubleSpinBox, QWidget

# ---- Local imports
from qtapputils.qthelpers import block_signals


LOCALE = QLocale()


class DoubleSpinBox(QDoubleSpinBox):
    """
    A standard qt double spinbox that implements a workaround for
    the bug described at https://bugreports.qt.io/browse/QTBUG-77939.
    """

    def __init__(self, parent: QWidget = None,
                 consume_enter_events: bool = True):
        super().__init__(parent)

        # Whether to consume key press and key release events.
        # See jnsebgosselin/qtapputils#18
        self.consume_enter_events = consume_enter_events

    def keyReleaseEvent(self, event):
        """
        Override qt base method to consume key release events so that they are
        not propagated to the parent.
        """
        super().keyReleaseEvent(event)
        if (event.key() in (Qt.Key_Enter, Qt.Key_Return) and
                self.consume_enter_events):
            event.accept()

    def keyPressEvent(self, event):
        """
        Override qt base method to consume key press events so that they are
        not propagated to the parent.
        """
        super().keyPressEvent(event)
        if (event.key() in (Qt.Key_Enter, Qt.Key_Return) and
                self.consume_enter_events):
            event.accept()

    def textFromValue(self, value: float):
        """
        Override qt base method to work around the bug described at
        https://bugreports.qt.io/browse/QTBUG-77939 when a ',' is
        both used as thousands and decimal separator.
        """
        from qtpy.QtCore import QLocale
        LOCALE = QLocale()
        if self.isGroupSeparatorShown():
            return LOCALE.toString(value, 'f', self.decimals())
        else:
            tostr = LOCALE.toString(value, 'f', self.decimals())
            index = self.decimals()
            if index == 0:
                return tostr.replace(LOCALE.groupSeparator(), '')
            else:
                return (
                    tostr[:-index-1].replace(LOCALE.groupSeparator(), '') +
                    tostr[-1-index:]
                    )


class PreciseSpinBox(DoubleSpinBox):
    """
    QDoubleSpinBox that optionally preserves full float64 precision when values
    are set programmatically, while still displaying only as many decimals as
    configured.

    Parameters
    ----------
    precise : bool, optional
        If True (default), the spinbox preserves full float64 precision for
        programmatically set values. If False, it behaves like a standard
        QDoubleSpinBox without storing an internal precise value.
    """
    sig_value_changed = Signal(float)

    def __init__(self, *args, precise: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.setKeyboardTracking(False)
        self._precise = precise
        self._true_value = super().value()
        self.valueChanged.connect(self._handle_user_change)

    def _handle_user_change(self, value: float):
        """Update internal value when the user edits the widget."""
        if self._precise:
            self._true_value = value
        self.sig_value_changed.emit(value)

    # ---- QDoubleSpinBox Interface
    def value(self) -> float:
        """
        Return the precise stored value if enabled,
        otherwise the standard UI value.
        """
        if self._precise:
            return self._true_value
        return super().value()

    def setValue(self, new_value: float):
        """Set the value without losing precision due to display rounding."""
        old_value = self.value()
        new_value = float(max(min(new_value, self.maximum()), self.minimum()))

        with block_signals(self):
            super().setValue(new_value)

        if self._precise:
            self._true_value = new_value

        if old_value != self.value():
            self.sig_value_changed.emit(self.value())


class RangeSpinBox(PreciseSpinBox):
    """
    A spinbox that allow to enter values that are lower or higher than the
    minimum and maximum value of the spinbox.

    When editing is finished, the value is corrected to the maximum if the
    value entered was above the maximum and to the minimum if it was below
    the minimum.
    """

    def __init__(self, parent: QWidget = None, maximum: float = None,
                 minimum: float = None, singlestep: float = None,
                 decimals: int = None, value: float = None,
                 precise: bool = False):
        super().__init__(parent=parent, precise=precise)
        if minimum is not None:
            self.setMinimum(minimum)
        if maximum is not None:
            self.setMaximum(maximum)
        if singlestep is not None:
            self.setSingleStep(singlestep)
        if decimals is not None:
            self.setDecimals(decimals)
        if value is not None:
            self.setValue(value)

    def sizeHint(self):
        """
        Override Qt method to add a buffer to the hint width of the spinbox,
        so that there is enough space to hold the maximum value in the spinbox
        when editing.
        """
        qsize = super().sizeHint()
        qsize.setWidth(qsize.width() + 8)
        return qsize

    def fixup(self, value):
        """Override Qt method."""
        if value in ('-', '', '.', ','):
            return super().fixup(value)

        num, success = LOCALE.toDouble(value)
        if not success:
            return super().fixup(value)

        num = float(num)
        if float(num) > self.maximum():
            return self.textFromValue(self.maximum())
        elif float(num) < self.minimum():
            return self.textFromValue(self.minimum())
        else:
            return self.textFromValue(num)

    def validate(self, value, pos):
        """Override Qt method."""
        if value in ('-', '', '.', ','):
            return QValidator.Intermediate, value, pos

        num, success = LOCALE.toDouble(value)
        if success is False:
            return QValidator.Invalid, value, pos

        num = float(num)
        if num > self.maximum() or num < self.minimum():
            return QValidator.Intermediate, value, pos

        # Check if the number has more decimals than allowed.
        if value != self.textFromValue(num):
            return QValidator.Intermediate, value, pos

        return QValidator.Acceptable, value, pos


class RangeWidget(QObject):
    """
    A Qt object that link two double spinboxes that can be used to define
    the start and end value of a range.

    The RangeWidget does not come with a layout and both the spinbox_start
    and spinbox_end must be added to a layout independently.
    """
    sig_range_changed = Signal(float, float)

    def __init__(self, parent: QWidget = None, maximum: float = 99.99,
                 minimum: float = 0, singlestep: float = 0.01,
                 decimals: int = 2, null_range_ok: bool = True):
        super().__init__()
        self.decimals = decimals
        self.null_range_ok = null_range_ok

        self._start = minimum
        self._end = maximum

        self.spinbox_start = RangeSpinBox(
            minimum=minimum, singlestep=singlestep, decimals=decimals,
            value=minimum)

        self.spinbox_start.sig_value_changed.connect(
            lambda: self._handle_value_changed())

        self.spinbox_end = RangeSpinBox(
            maximum=maximum, singlestep=singlestep, decimals=decimals,
            value=maximum)

        self.spinbox_end.sig_value_changed.connect(
            lambda: self._handle_value_changed())

        self._update_spinbox_range()

    def start(self):
        """Return the start value of the range."""
        return self.spinbox_start.value()

    def end(self):
        """Return the end value of the range."""
        return self.spinbox_end.value()

    def set_range(self, start: float, end: float):
        """Set the start and end value of the range."""
        old_start = self.start()
        old_end = self.end()
        step = 0 if self.null_range_ok else 10**-self.decimals

        self._block_spinboxes_signals(True)

        # Reset the spin boxes range.
        self.spinbox_start.setMaximum(self.spinbox_end.maximum() - step)
        self.spinbox_end.setMinimum(self.spinbox_start.minimum() + step)

        self.spinbox_start.setValue(start)
        self.spinbox_end.setValue(end)

        self._block_spinboxes_signals(False)

        if old_start != self.start() or old_end != self.end():
            self._handle_value_changed()

    def set_minimum(self, minimum: float):
        """Set the minimum allowed value of the start of the range."""
        old_start = self.start()

        self._block_spinboxes_signals(True)
        self.spinbox_start.setMinimum(minimum)
        self._block_spinboxes_signals(False)

        if old_start != self.start():
            self._handle_value_changed()

    def set_maximum(self, maximum: float):
        """Set the maximum allowed value of the end of the range."""
        old_end = self.end()

        self._block_spinboxes_signals(True)
        self.spinbox_end.setMaximum(maximum)
        self._block_spinboxes_signals(False)

        if old_end != self.end():
            self._handle_value_changed()

    # ---- Private methods and handlers
    def _block_spinboxes_signals(self, block: bool):
        """Block signals from the spinboxes."""
        self.spinbox_start.blockSignals(block)
        self.spinbox_end.blockSignals(block)

    def _update_spinbox_range(self):
        """
        Make sure lowcut and highcut spinbox ranges are
        mutually exclusive
        """
        self._block_spinboxes_signals(True)

        step = 0 if self.null_range_ok else 10**-self.decimals
        self.spinbox_start.setMaximum(self.spinbox_end.value() - step)
        self.spinbox_end.setMinimum(self.spinbox_start.value() + step)

        self._block_spinboxes_signals(False)

    def _handle_value_changed(self, silent: bool = False):
        """
        Handle when the value of the lowcut or highcut spinbox changed.
        """
        self._update_spinbox_range()
        if self._start != self.start() or self._end != self.end():
            self._start = self.start()
            self._end = self.end()
            self.sig_range_changed.emit(self.start(), self.end())
