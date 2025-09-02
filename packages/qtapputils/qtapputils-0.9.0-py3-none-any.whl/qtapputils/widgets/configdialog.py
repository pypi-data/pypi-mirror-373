# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/qtapputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------

# ---- Standard library imports
import sys

# ---- Third party imports
from qtpy.QtCore import (
    Qt, Signal, Slot, QRect, QPoint)
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import (
    QAbstractButton, QApplication, QStyle, QStylePainter,
    QDialog, QPushButton, QDialogButtonBox, QWidget, QTabWidget,
    QGridLayout, QTabBar, QStyleOptionTab, QLabel)


class HorizontalTabBar(QTabBar):
    """
    A custom tabbar to show tabs on the side, while keeping the text
    orientation horitontal.
    """
    # https://www.manongdao.com/q-367474.html

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            # We are painting the text ourselves so to align it
            # horizontally to the left.
            text = opt.text
            opt.text = ''

            # Set state to 'Enable' to avoid vertical flickering of the
            # icon when tab is selected.
            opt.state = QStyle.State_Enabled

            c = self.tabRect(i).center()
            painter.save()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

            # Draw text.
            rect = self.tabRect(i)
            hspacing = QApplication.instance().style().pixelMetric(
                QStyle.PM_ButtonMargin)
            if not opt.icon.isNull():
                hspacing += self.iconSize().width() + 8
            rect.translate(hspacing, 0)
            painter.drawItemText(
                rect, int(Qt.AlignLeft | Qt.AlignVCenter),
                self.palette(), True, text)


class ConfDialog(QDialog):
    """
    A dialog window to manage app preferences.
    """

    def __init__(self, main, icon: QIcon = None, resizable: bool = True,
                 min_height: int = None, sup_message: str = None,
                 btn_labels: dict = None, win_title: str = 'Preferences'):
        super().__init__(main)
        self.main = main

        self.setWindowTitle(win_title)
        if icon is not None:
            self.setWindowIcon(icon)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        if min_height is not None:
            self.setMinimumHeight(min_height)

        self.confpages_tabwidget = QTabWidget()
        self.confpages_tabwidget.setTabBar(HorizontalTabBar())
        self.confpages_tabwidget.setTabPosition(QTabWidget.West)
        self._confpages = {}

        # Setup the dialog button box.
        btn_labels = {} if btn_labels is None else btn_labels

        self.ok_button = QPushButton(btn_labels.get('ok', 'OK'))
        self.ok_button.setDefault(False)
        self.ok_button.setAutoDefault(False)
        self.apply_button = QPushButton(btn_labels.get('apply', 'Apply'))
        self.apply_button.setDefault(True)
        self.apply_button.setEnabled(False)
        self.cancel_button = QPushButton(btn_labels.get('cancel', 'Cancel'))
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)

        button_box = QDialogButtonBox()
        button_box.addButton(self.ok_button, button_box.ApplyRole)
        button_box.addButton(self.cancel_button, button_box.RejectRole)
        button_box.addButton(self.apply_button, button_box.ApplyRole)
        button_box.layout().insertSpacing(1, 100)
        button_box.clicked.connect(self._handle_button_click_event)

        # Setup the main layout.
        main_layout = QGridLayout(self)

        row = 0
        if sup_message is not None:
            label = QLabel(sup_message)
            label.setWordWrap(True)
            label.setMargin(10)
            main_layout.addWidget(label, row, 0)
            row += 1
        main_layout.addWidget(self.confpages_tabwidget, row, 0)
        main_layout.setRowStretch(row, 1)
        main_layout.addWidget(button_box, row+1, 0)
        if resizable is False:
            main_layout.setSizeConstraint(main_layout.SetFixedSize)

    def count(self):
        "Return the number of configuration pages added to this dialog."
        return len(self._confpages)

    def get_confpage(self, confpage_name):
        """Return the confpage corresponding to the given name."""
        return self._confpages.get(confpage_name, None)

    def add_confpage(self, confpage):
        """Add confpage to this config dialog."""
        self._confpages[confpage.name()] = confpage
        self.confpages_tabwidget.addTab(
            confpage, confpage.icon(), confpage.label())
        confpage.sig_configs_changed.connect(
            self._handle_confpage_configs_changed)

    @Slot(QAbstractButton)
    def _handle_button_click_event(self, button):
        """
        Handle when a button is clicked on the dialog button box.
        """
        if button == self.cancel_button:
            self.close()
        elif button == self.apply_button:
            for confpage in self._confpages.values():
                confpage.apply_changes()
        elif button == self.ok_button:
            for confpage in self._confpages.values():
                confpage.apply_changes()
            self.close()
        self.apply_button.setEnabled(False)

    def closeEvent(self, event):
        """
        Override this QT to revert confpage configs to the value saved in
        the user configuration files.
        """
        for confpage in self._confpages.values():
            if confpage.is_modified():
                confpage.load_configs_from_conf()
        self.apply_button.setEnabled(False)
        super().closeEvent(event)

    def _handle_confpage_configs_changed(self):
        """
        Handle when the configs in one of the registered pages changed.
        """
        for confpage in self._confpages.values():
            if confpage.is_modified():
                self.apply_button.setEnabled(True)
                break
        else:
            self.apply_button.setEnabled(False)


class ConfPageBase(QWidget):
    """
    Basic functionality for app configuration pages.

    WARNING: Don't override any methods or attributes present here unless you
    know what you are doing.
    """
    sig_configs_changed = Signal()

    def __init__(self, name: str, label: str, icon: QIcon = None):
        super().__init__()
        self._name = name
        self._label = label
        if icon is None:
            empty_pixmap = QPixmap(20, 20)
            empty_pixmap.fill(Qt.transparent)
            icon = QIcon(empty_pixmap)
        self._icon = QIcon() if icon is None else icon

        self.setup_page()
        self.load_configs_from_conf()

    def name(self):
        """
        Return the name that will be used to reference this confpage
        in the code.
        """
        return self._name

    def label(self):
        """
        Return the label that will be used to reference this confpage in the
        graphical interface.
        """
        return self._label

    def icon(self):
        """Return configuration page icon"""
        return self._icon

    def is_modified(self):
        return self.get_configs() != self.get_configs_from_conf()

    def apply_changes(self):
        """Apply changes."""
        self.save_configs_to_conf()


class ConfPage(ConfPageBase):
    """
    App configuration page class.

    All configuration page *must* inherit this class and
    reimplement its interface.
    """

    def __init__(self, name: str, label: str, icon: QIcon = None):
        """
        Parameters
        ----------
        name: str
            The name that is used to reference this confpage in the code.
        label: str
            The label that is used to reference this confpage in the
            graphical interface.
        icon: QIcon
            The icon that appears in the tab for that confpage
            in the tab bar of the configuration dialog
        """
        super().__init__(name, label, icon)

    def setup_page(self):
        """Setup configuration page widget"""
        raise NotImplementedError

    def get_configs(self):
        """Return the configs that are set in this configuration page."""
        raise NotImplementedError

    def get_configs_from_conf(self):
        """Get configs from the user configuration files."""
        raise NotImplementedError

    def load_configs_from_conf(self):
        """Load configs from the user configuration files."""
        raise NotImplementedError

    def save_configs_to_conf(self):
        """Save configs to the user configuration files."""
        raise NotImplementedError


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.exit(app.exec_())
