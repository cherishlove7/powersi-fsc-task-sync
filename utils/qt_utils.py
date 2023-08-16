# -*- encoding: utf-8 -*-
"""
@File:        qt_utils.py
@Author:      Little duo
@Time:        2023/7/10 17:40
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHeaderView, QCheckBox, QTableWidget


def center_window(parent=None):
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    window_geometry = parent.geometry()
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2
    parent.move(x, y)


class CheckBoxHeader(QHeaderView):
    def __init__(self, orientation, parent: QTableWidget):
        super(CheckBoxHeader, self).__init__(orientation, parent)
        self.checkBox = QCheckBox(self)
        self.checkBox.clicked.connect(self.on_state_changed)
        self.tableWidget = parent

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        if logicalIndex == 0:
            checkbox_rect = self.checkBox.geometry()
            checkbox_rect.moveCenter(rect.center())  # 将复选框的中心移动到表头单元格的中心
            checkbox_rect.moveLeft(rect.left() + 4)  # 向左移动4个像素
            self.checkBox.setGeometry(checkbox_rect)
        painter.restore()

    def on_state_changed(self):
        state = self.checkBox.isChecked()  # 获取复选框的状态
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 0)  # 获取第一列的单元格
            if item:
                item.setCheckState(Qt.Checked if state else Qt.Unchecked)  # 设置单元格的复选状态
