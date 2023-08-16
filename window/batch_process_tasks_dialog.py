# -*- encoding: utf-8 -*-
"""
@File:        batch_process_tasks_dialog.py
@Author:      Little duo
@Time:        2023/7/10 17:40
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QMessageBox

from window.ui.batch_process_tasks_dialog_ui import Ui_BatchProcessTasksDialog
from utils.database import db


class BatchProcessTasksDialog(QDialog, Ui_BatchProcessTasksDialog):
    def __init__(self, parent=None):
        super(BatchProcessTasksDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("任务批处理")
        self.setFont(QFont("Microsoft YaHei", 10))

        self.acceptedButton.clicked.connect(self.confirmation)
        self.cancelButton.clicked.connect(self.cancel)

        self.system_titles = []
        self.system_task_ids = []

    def start(self, system_titles, system_task_ids):
        self.system_titles = system_titles
        self.system_task_ids = system_task_ids
        if len(system_titles) == 1:
            self.titleEdit.setText(system_titles[0])
        else:
            self.titleEdit.setText("多任务")

    def confirmation(self):
        current_system_process_status = self.systemProcessStatusComboBox.currentText()
        reason = self.resultDescTextEdit.toPlainText()
        effect_rows = db.update_task(
            system_task_ids=self.system_task_ids,
            reason=reason,
            system_process_status=current_system_process_status,
        )
        if effect_rows:
            QMessageBox.information(self, "信息", f'批量处理成功,影响行数{effect_rows}条!')
            self.close()
        else:
            QMessageBox.critical(self, "信息", '任务批量更新失败!')

    def cancel(self):
        self.close()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.parent().dialogClosed.emit()

