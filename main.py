# -*- encoding: utf-8 -*-
"""
@File:        main.py
@Author:      Little duo
@Time:        2023/7/10 17:40
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
import sys
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel, QMainWindow

from window.task_edit_window import TaskEditWindow


class MySplashScreen(QSplashScreen):
    def mousePressEvent(self, event):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = MySplashScreen(QPixmap('resource/images/powersi.png'))
    splash.show()
    main_window = TaskEditWindow()
    splash.finish(main_window)
    main_window.show()
    sys.exit(app.exec_())
