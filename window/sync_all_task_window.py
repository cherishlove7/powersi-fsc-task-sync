# -*- encoding: utf-8 -*-
"""
@File:        sync_all_task_window.py
@Author:      Little duo
@Time:        2023/7/18 16:45
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
import datetime
import re
import uuid
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog

from powersi.powersi import PowersiService
from utils.database import db, TaskInModel
from window.ui.sync_all_task_dialog_ui import Ui_SyncAllTaskDialog


class SyncAllTasksDialog(QDialog, Ui_SyncAllTaskDialog):
    def __init__(self, parent, powersi_service: PowersiService):
        super(SyncAllTasksDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("任务同步")
        self.setFont(QFont("Microsoft YaHei", 10))
        self.commitProgressBar.setValue(0)
        self.titleLabel.setText("正在准备同步任务...")
        self.setModal(True)

        self.cancelButton.clicked.connect(self.close)  # 取消按钮关闭窗口
        self.task_thread = SyncAllTasksThread(powersi_service)
        self.task_thread.progress_changed.connect(self.update_progress)
        self.task_thread.finished.connect(self.close)  # 完成后自动关闭窗口
        self.task_thread.start()

    def update_progress(self, value, message, format_value):
        self.commitProgressBar.setValue(value)
        self.titleLabel.setText(message)
        self.commitProgressBar.setFormat(format_value)

    def stop_thread(self):
        if self.task_thread.isRunning():
            self.task_thread.stop()
            self.task_thread.wait()  # 等待线程执行完成

    def closeEvent(self, event):
        self.stop_thread()
        super().closeEvent(event)
        self.parent().dialogClosed.emit()


class SyncAllTasksThread(QThread):
    progress_changed = pyqtSignal(int, str, str)

    def __init__(self, powersi_service: PowersiService):
        super().__init__()
        self.powersi = powersi_service
        self.is_running = True

    def run(self):
        # -- 备份表数据 清空表数据 此处可清空表数据
        status, system_task_list = self.powersi.query_system_task_ids(query_all=True)
        if not status:
            return
        total_tasks = len(system_task_list['rows'])
        for index, row in enumerate(system_task_list['rows'], 1):
            task_id = str(uuid.uuid4()).upper().replace('-', '')
            system_task_id = row['task_id']
            subject_code = row['subject_code']
            sql_str = row['sql_str']
            expect_finish_date = row['expect_finish_date']
            system_title = row['title'].split('-')[1]
            matches = re.findall(r"（(.*?)）", row['system_name'])
            city_name = matches[0].replace('实施', '') if matches else str()
            task_date = datetime.datetime.now().strftime("%Y-%m-%d")
            task_month = row['month']
            status, sql_content = self.powersi.preview_sql_file(file_id=sql_str)
            if status:
                task_info = TaskInModel(
                    system_task_id=system_task_id,
                    subject_code=subject_code,
                    system_title=system_title,
                    city_name=city_name,
                    sql_file_name=subject_code + '.sql',
                    sql_content=sql_content,
                    task_month=task_month,
                    expect_finish_date=expect_finish_date
                )
                db.add_task(task_info)
            else:
                print(f'未获取到sql内容，已忽略此任务 {subject_code}')
            current_progress_value = int((index / total_tasks) * 100)
            message = f"正在同步 {city_name}-{system_title} ..."
            format_value = str(index) + "/" + str(total_tasks)
            self.progress_changed.emit(current_progress_value, message, format_value)


    def stop(self):
        self.is_running = False
