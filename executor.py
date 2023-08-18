# -*- encoding: utf-8 -*-
"""
@File:        executor.py
@Author:      Little duo
@Time:        2023/8/18 18:01
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
import argparse
import ctypes
import os
import queue
import threading
from datetime import datetime
from typing import List
import pandas as pd
import psycopg2
# from dbutils.pooled_db import PooledDB
from loguru import logger
import threading

from utils.database import db, QueryTaskModel


class MyThread(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func

    def run(self):
        try:
            self.func()
        except Exception as e:
            logger.error(e)


condition = QueryTaskModel(task_exec_status='未执行')
data = db.query_tasks_by_conditions(condition)
print(data)
