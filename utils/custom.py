# -*- encoding: utf-8 -*-
"""
@File:        custom.py
@Author:      Little duo
@Time:        2023/8/18 18:02
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
from datetime import datetime


def calculate_run_time(start_time: datetime, end_time: datetime):
    """
    计算运行时间
    :param start_time:
    :param end_time:
    :return:
    """
    run_time = end_time - start_time
    total_seconds = int(run_time.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{}小时{}分钟{}秒".format(hours, minutes, seconds)
