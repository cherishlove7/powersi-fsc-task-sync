# -*- encoding: utf-8 -*-
"""
@File:        main.py
@Author:      Little duo
@Time:        2023/7/10 17:40
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from utils.database import db, QueryTaskModel
from powersi.powersi import PowersiService
from utils.qt_utils import center_window, CheckBoxHeader
from window.batch_commit_task_dialog import BatchCommitTasksDialog
from window.batch_process_tasks_dialog import BatchProcessTasksDialog
from window.sync_all_task_window import SyncAllTasksDialog
from window.ui.task_edit_window_ui import Ui_TaskEditWindow


class TaskEditWindow(QMainWindow, Ui_TaskEditWindow):
    dialogClosed = pyqtSignal()

    def __init__(self):
        super(TaskEditWindow, self).__init__()
        self.powersi = PowersiService()
        self.setupUi(self)
        self.setWindowTitle("基金安全检查任务处理工具")
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setGeometry(0, 0, 1366, 768)
        center_window(self)
        self.column_en_name_list = []
        self.system_titles = []
        self.columns_mapping = []
        self.table_columns = []
        self.reset_query_condition()

        self.queryResetButton.clicked.connect(self.reset_query_condition)
        self.queryTaskButton.clicked.connect(self.query_task)
        self.systemProcessStatusQurtyComboBox.currentIndexChanged.connect(self.query_task)
        self.rowCountComboBox.currentIndexChanged.connect(self.query_task)
        self.titleComboBox.currentIndexChanged.connect(self.query_task)
        self.dialogClosed.connect(self.query_task)
        self.taskExecStatusQurtyComboBox.currentIndexChanged.connect(self.query_task)
        self.systemCommitStatusCheckBox.stateChanged.connect(self.query_task)
        self.editSelectedTaskButton.clicked.connect(self.show_batch_process_tasks_dialog)
        self.commitSelectedTaskButton.clicked.connect(self.batch_commit_selected_task)
        self.saveRowTaskButton.clicked.connect(self.save_row_task)
        self.updateTaskButton.clicked.connect(self.sync_all_task_scripts)
        self.init_table()

    def sync_all_task_scripts(self):
        """
        重新同步所有脚本
        """
        msg_box = QMessageBox()
        msg_box.setWindowTitle("同步所有任务脚本")
        msg_box.setText("此操作会从信息管理平台同步最新脚本，更新前请先备份历史任务，是否继续？")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        result = msg_box.exec_()
        if result == QMessageBox.Ok:
            sync_all_task_dialog = SyncAllTasksDialog(self, self.powersi)
            sync_all_task_dialog.exec_()

    def show_batch_process_tasks_dialog(self):
        """
        批量编辑任务
        :return:
        """
        selected_task = self.get_checkbox_selected_task()
        system_titles, system_task_ids = selected_task['system_titles'], selected_task['system_task_ids']
        if len(system_titles) == 0:
            QMessageBox.warning(self, "信息", '请先选择任务!')
            return
        if len(system_titles) > 1 and self.rowCountComboBox.currentIndex() != 1:
            QMessageBox.warning(self, "信息", '只能批量编辑相同基金安全主题或全部结果条数为0的任务!')
            return
        batch_process_tasks_dialog = BatchProcessTasksDialog(self)
        batch_process_tasks_dialog.start(system_titles, system_task_ids)
        batch_process_tasks_dialog.exec_()

    def save_row_task(self):
        effect_rows = db.update_task(
            system_task_ids=[self.systemTaskIdEdit.text()],
            reason=self.reasonTextEdit.toPlainText(),
            system_process_status=self.systemProcessStatusComboBox.currentText()
        )
        if effect_rows:
            QMessageBox.information(self, "信息", f'处理成功,影响行数{effect_rows}条!')
            self.query_task()
        else:
            QMessageBox.critical(self, "信息", '更新失败!')

    def batch_commit_selected_task(self):
        """
        批量提交复选框选中的任务
        :return:
        """
        query_conditions = self.get_current_query_conditions()
        if query_conditions.system_commit_status != "执行成功":
            QMessageBox.warning(self, "信息", '只能选择执行成功的任务进行提交')
            return
        if query_conditions.system_commit_status:
            QMessageBox.warning(self, "信息", '只能选择未提交的任务进行提交')
            return
        selected_task = self.get_checkbox_selected_task()
        task_data_list = selected_task['task_data_list']
        if len(task_data_list) == 0:
            QMessageBox.warning(self, "信息", '请先选择基金安全任务!')
            return

        msg_box = QMessageBox()
        msg_box.setWindowTitle("提交多个任务")
        msg_box.setText("此操作只提交执行成功且未处理完成的任务，确定要将选中任务提交至信息管理平台吗？该操作不可撤销!!!")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        result = msg_box.exec_()
        if result == QMessageBox.Ok:
            batch_commit_tasks_dialog = BatchCommitTasksDialog(self, task_data_list, self.powersi)
            batch_commit_tasks_dialog.exec_()

    def init_table(self):
        self.columns_mapping = {
            '任务编号': 'system_task_id',
            '主题编码': 'subject_code',
            '主题名称': 'system_title',
            '地市名称': 'city_name',
            '系统处理状态': 'system_process_status',
            '任务运行状态': 'task_exec_status',
            '任务运行时长': 'task_exec_time',
            'SQL语句': 'sql_content',
            'SQL运行结果': 'result_data',
            '结果条数': 'row_count',
            '检查结果说明': 'reason',
            '月份': 'task_month',
            '期望完成时间': 'expect_finish_date',
            '备注': 'memo',
            'SQL名称': 'sql_file_name',
        }
        self.table_columns = list(self.columns_mapping.keys())
        self.table_columns.insert(0, None)
        for column_cn_name in self.table_columns:
            if column_cn_name:
                column_en_name = self.columns_mapping[column_cn_name]
                self.column_en_name_list.append(column_en_name)

        self.tableWidget.setColumnCount(len(self.table_columns))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(self.table_columns)  # 设置表头标签
        header = CheckBoxHeader(Qt.Horizontal, self.tableWidget)  # 创建自定义表头对象
        self.tableWidget.setHorizontalHeader(header)  # 将自定义表头设置为表格的水平表头
        table_header = self.tableWidget.horizontalHeader()

        # 设置表格指定列宽
        table_header.resizeSection(0, 10)
        # table_header.resizeSection(2, 160)
        # table_header.resizeSection(3, 150)
        # table_header.resizeSection(4, 300)
        # table_header.resizeSection(9, 350)
        # table_header.resizeSection(12, 300)

        # 隐藏表格指定列
        self.tableWidget.setColumnHidden(15, True)
        # self.tableWidget.setColumnHidden(11, True)

        table_header.setSectionResizeMode(0, QHeaderView.Fixed)  # 设置表格视图的第一列为固定宽度且不可拉宽
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)  # 设置表格的选择行为为选择整行
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置将禁止对单元格的的编辑
        self.tableWidget.currentCellChanged.connect(self.on_current_cell_changed)  # 选中行改变时出发的函数

        self.query_task()

    def keyPressEvent(self, event):
        # 键盘按下事件的处理方法
        if event.key() == Qt.Key_Return:
            selected_row = self.tableWidget.currentRow()
            print(f"Enter key pressed on row: {selected_row}")
        super().keyPressEvent(event)

    def reset_query_condition(self):
        # 标题下拉菜单初始化
        system_titles = db.query_system_titles()
        system_titles.insert(0, '请选择...')
        self.system_titles = system_titles
        titles = [f'{index}.{title}' for index, title in enumerate(system_titles)]
        self.titleComboBox.clear()  # 删除所有元素
        self.titleComboBox.addItems(titles)  # 添加新元素
        self.titleComboBox.setCurrentIndex(0)

        self.systemProcessStatusQurtyComboBox.setCurrentIndex(0)
        self.taskExecStatusQurtyComboBox.setCurrentIndex(0)
        self.rowCountComboBox.setCurrentIndex(2)
        self.systemCommitStatusCheckBox.setChecked(True)
        self.subjectCodeQueryLineEdit.setText(str())

    def get_current_query_conditions(self):
        """
            获取当前查询条件
        :return:
        """
        # 任务标题
        current_system_title = self.system_titles[self.titleComboBox.currentIndex()]
        if self.titleComboBox.currentIndex() == 0:
            current_system_title = None
        # 系统处理状态
        current_system_process_status = self.systemProcessStatusQurtyComboBox.currentText()
        if self.systemProcessStatusQurtyComboBox.currentIndex() == 0:
            current_system_process_status = None
        # 任务执行状态
        current_task_exec_status = self.taskExecStatusQurtyComboBox.currentText()
        if self.taskExecStatusQurtyComboBox.currentIndex() == 0:
            current_task_exec_status = None
        # 基金主题编码
        current_subject_code = self.subjectCodeQueryLineEdit.text()
        if current_subject_code == '':
            current_subject_code = None
        # 结果条数条件
        row_count_zero_symbols = ['>', '=', '>=']
        # 结果条数条件
        current_row_count_zero_symbol = row_count_zero_symbols[self.rowCountComboBox.currentIndex()]
        # 任务提交状态
        current_system_commit_status = not self.systemCommitStatusCheckBox.isChecked()
        # 信息管理平台任务ID列表
        current_system_task_ids = []
        if not current_system_commit_status:
            status, system_task_ids = self.powersi.query_system_task_ids()
            if status:
                current_system_task_ids = system_task_ids
            else:
                QMessageBox.warning(self, "信息", '信息管理平台数据获取失败，请检查网络或重新登录!')
        query_conditions = QueryTaskModel(
            system_task_ids=current_system_task_ids,
            row_count_zero_symbol=current_row_count_zero_symbol,
            subject_code=current_subject_code,
            system_title=current_system_title,
            system_process_status=current_system_process_status,
            task_exec_status=current_task_exec_status,
            system_commit_status=current_system_commit_status
        )
        return query_conditions

    def query_task(self):
        """
        表格数据查询
        :return:
        """
        query_conditions = self.get_current_query_conditions()
        task_list = db.query_tasks_by_conditions(query_conditions)
        # 填充数据
        self.tableWidget.setRowCount(len(task_list))
        for r_idx, row_data in enumerate(task_list):
            for c_idx, column_en_name in enumerate(self.column_en_name_list):
                item = QTableWidgetItem(str(row_data[column_en_name]) if row_data[column_en_name] else str())
                self.tableWidget.setItem(r_idx, c_idx + 1, item)
        self.after_flush_table()

    def after_flush_table(self):
        """
        表格数据刷新或填充以后的必须操作
        :return:
        """
        # 状态栏显示
        self.statusbar.showMessage(f"查询成功, 共计{self.tableWidget.rowCount()}条数据!")
        # 表格设置复选框
        for row in range(self.tableWidget.rowCount()):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # 设置单元格的标志为可由用户勾选
            item.setCheckState(Qt.Unchecked)  # 设置初始状态为未选中
            self.tableWidget.setItem(row, 0, item)  # 将单元格对象设置到表格的第一列
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 禁止调整行高
        self.tableWidget.setAlternatingRowColors(True)  # 交替行颜色
        # 清空预览
        self.subjectCodeLineEdit.clear()
        self.cityNameEdit.clear()
        self.systemTaskIdEdit.clear()
        self.systemTitleEdit.clear()
        self.rowCountEdit.clear()
        self.systemProcessStatusComboBox.setCurrentIndex(0)
        self.sqlContentEdit.clear()
        self.reasonTextEdit.clear()

    def get_selected_table_row_data(self, current_row):
        """
        获取选中的表格行数据，可以是复选框、也可以是鼠标点击选中的
        :param current_row: 选中的行号
        :return: 单行数据
        """
        current_data = {}
        for index, column_en_name in enumerate(self.column_en_name_list):
            item = self.tableWidget.item(current_row, index + 1)
            item_text = item.text() if item is not None else str()
            current_data[column_en_name] = item_text
        system_task_id = current_data['system_task_id']
        subject_code = current_data['subject_code']
        system_title = current_data['system_title']
        city_name = current_data['city_name']
        system_process_status = current_data['system_process_status']
        task_exec_time = current_data['task_exec_time']
        sql_file_name = current_data['sql_file_name']
        sql_content = current_data['sql_content']
        task_exec_status = current_data['task_exec_status']
        result_data = current_data['result_data']
        row_count = current_data['row_count']
        reason = current_data['reason']
        task_month = current_data['task_month']
        expect_finish_date = current_data['expect_finish_date']
        memo = current_data['memo']
        return current_data

    def get_checkbox_selected_task(self):
        """
        获取复选框选中的全量任务数据
        :return:
        """

        # 获取复选框选中的所有行号
        selected_rows = []
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 0)  # 获取第一列的单元格
            if item and item.checkState() == Qt.Checked:  # 检查单元格的复选状态
                selected_rows.append(row)

        # 获取选中的数据
        task_data_list = []
        for row in selected_rows:
            current_data = self.get_selected_table_row_data(current_row=row)
            task_data_list.append(current_data)

        # 获取选中的任务编号和任务标题
        system_task_ids = []
        system_titles = []
        for data in task_data_list:
            system_task_ids.append(data['system_task_id'])
            system_titles.append(data['system_title'])
        system_titles = list(set(system_titles))

        data_dict = {
            'selected_rows': selected_rows,
            'task_data_list': task_data_list,
            'system_task_ids': system_task_ids,
            'system_titles': system_titles,
        }
        return data_dict

    def on_current_cell_changed(self, current_row, current_column, previous_row, previous_column):
        if current_row >= 0:  # 确保至少有一行被选择
            current_data = self.get_selected_table_row_data(current_row=current_row)
            self.subjectCodeLineEdit.setText(current_data['subject_code'])
            self.cityNameEdit.setText(current_data['city_name'])
            self.systemTaskIdEdit.setText(current_data['system_task_id'])
            self.systemTitleEdit.setText(current_data['system_title'])
            self.rowCountEdit.setText(current_data['row_count'])
            self.systemProcessStatusComboBox.setCurrentText(current_data['system_process_status'])
            self.sqlContentEdit.setText(current_data['sql_content'] + 3 * '\r\n' + current_data['result_data'])
            self.reasonTextEdit.setText(current_data['reason'])
            # print(f'当前索引：{self.systemProcessStatusComboBox.currentIndex()}')
