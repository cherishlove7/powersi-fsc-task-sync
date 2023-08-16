# -*- encoding: utf-8 -*-
"""
@File:        config.py
@Author:      Little duo
@Time:        2023/8/16 11:12
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""

import configparser
import os

# 配置文件路径
from distutils.util import strtobool

config_file = 'config.ini'

# 如果配置文件不存在，则创建并写入默认值
if not os.path.exists(config_file):
    config = configparser.ConfigParser()
    config['User'] = {'username': 'username', 'password': 'password', 'login_timer_minutes': 10}
    config['Database'] = {'url': '', 'echo': False}
    # config['DatabasePGModel'] = {'url': 'postgresql://user:password@host:port/database'}
    # config['DatabaseSQLiteModel'] = {'url': 'sqlite:///powersi.db?check_same_thread=False'}
    with open(config_file, 'w') as f:
        config.write(f)

# 读取配置文件
config = configparser.ConfigParser()
config.read(config_file)


# 信息管理平台用户名密码
username = config.get('User', 'username')
password = config.get('User', 'password')
# 每隔login_timer_minutes分钟登录一次信息管理平台，防止session失效
login_timer_minutes = int(config.get('User', 'login_timer_minutes'))
# sqlalchemy数据库连接地址
database_url = config.get('Database', 'url')
# 是否开启数据库日志
database_echo = bool(strtobool(config.get('Database', 'echo')))
