# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_commit_task_dialog_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BatchCommitTasksDialog(object):
    def setupUi(self, BatchCommitTasksDialog):
        BatchCommitTasksDialog.setObjectName("BatchCommitTasksDialog")
        BatchCommitTasksDialog.resize(550, 162)
        BatchCommitTasksDialog.setMinimumSize(QtCore.QSize(550, 162))
        BatchCommitTasksDialog.setMaximumSize(QtCore.QSize(550, 162))
        self.verticalLayout = QtWidgets.QVBoxLayout(BatchCommitTasksDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleLabel = QtWidgets.QLabel(BatchCommitTasksDialog)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.commitProgressBar = QtWidgets.QProgressBar(BatchCommitTasksDialog)
        self.commitProgressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.commitProgressBar.setProperty("value", 30)
        self.commitProgressBar.setObjectName("commitProgressBar")
        self.verticalLayout.addWidget(self.commitProgressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(208, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cancelButton = QtWidgets.QPushButton(BatchCommitTasksDialog)
        self.cancelButton.setMinimumSize(QtCore.QSize(120, 0))
        self.cancelButton.setMaximumSize(QtCore.QSize(120, 16777215))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        spacerItem2 = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(BatchCommitTasksDialog)
        self.label.setText("")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(BatchCommitTasksDialog)
        QtCore.QMetaObject.connectSlotsByName(BatchCommitTasksDialog)

    def retranslateUi(self, BatchCommitTasksDialog):
        _translate = QtCore.QCoreApplication.translate
        BatchCommitTasksDialog.setWindowTitle(_translate("BatchCommitTasksDialog", "Dialog"))
        self.titleLabel.setText(_translate("BatchCommitTasksDialog", ""))
        self.commitProgressBar.setFormat(_translate("BatchCommitTasksDialog", ""))
        self.cancelButton.setText(_translate("BatchCommitTasksDialog", "取消"))
