# -*- encoding: utf-8 -*-
"""
@File:        batch_commit_task_dialog.py
@Author:      Little duo
@Time:        2023/7/10 17:40
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
import os
from typing import List
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog

from powersi.powersi import PowersiService
from window.ui.batch_commit_task_dialog_ui import Ui_BatchCommitTasksDialog


class BatchCommitTasksDialog(QDialog, Ui_BatchCommitTasksDialog):
    def __init__(self, parent, task_data_list: List, powersi_service: PowersiService):
        super(BatchCommitTasksDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("多个任务提交")
        self.commitProgressBar.setValue(0)
        self.titleLabel.setText("正在准备提交任务...")
        self.setModal(True)

        self.cancelButton.clicked.connect(self.close)  # 取消按钮关闭窗口
        self.task_thread = BatchCommitTasksThread(task_data_list, powersi_service)
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


class BatchCommitTasksThread(QThread):
    progress_changed = pyqtSignal(int, str, str)

    def __init__(self, task_data_list: List, powersi_service: PowersiService):
        super().__init__()
        self.task_data_list = task_data_list
        self.powersi = powersi_service
        self.is_running = True

    def run(self):
        total_tasks = len(self.task_data_list)
        for index, data in enumerate(self.task_data_list, 1):
            if not self.is_running:
                break
            system_task_id = data['system_task_id']
            subject_code = data['subject_code']
            reason = data['reason']
            row_count = data['row_count']
            system_process_status = data['system_process_status']
            file_export_path = task_export_to_file(task_data=data)
            file_id = self.powersi.upload_file(system_task_id=system_task_id, file_path=file_export_path)
            if file_id:
                if reason:
                    self.powersi.commit_task(
                        system_task_id=system_task_id,
                        file_id=file_id,
                        system_process_status=system_process_status,
                        row_count=row_count,
                        result_desc=reason
                    )
                else:
                    print('任务检查结果说明不能为空!!!')
            # 进度条
            current_progress_value = int((index / total_tasks) * 100)
            message = f"正在提交 {subject_code} ..."
            format_value = str(index) + "/" + str(total_tasks)
            self.progress_changed.emit(current_progress_value, message, format_value)

    def stop(self):
        self.is_running = False


def task_export_to_file(task_data):
    export_path = os.path.join(os.getcwd(), 'export')
    os.makedirs(export_path, exist_ok=True)
    sql_file_content = task_data['sql_file_content']
    result_data = task_data['result_data']
    file_name = task_data['subject_code'] + '.sql'
    file_content = sql_file_content + '\r\n\r\n' + result_data
    file_export_path = os.path.join(export_path, file_name)
    try:
        with open(file_export_path, mode='w', encoding='utf-8', newline='') as f:
            f.write(sql_file_content.strip())
            print(f'导出成功：{file_export_path}')
            return file_export_path
    except Exception as e:
        print(f'导出失败：{file_export_path}, {e}')
