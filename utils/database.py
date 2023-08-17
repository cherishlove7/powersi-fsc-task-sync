# -*- encoding: utf-8 -*-
"""
@File:        database.py.py
@Author:      Little duo
@Time:        2023/7/11 9:16
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
from typing import List, Optional
from sqlalchemy import Column, String, create_engine, Integer, TEXT, update, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, validator
from config import database_url, database_echo
import psycopg2
import sqlite3

# 创建对象的基类:
Base = declarative_base()


class TaskTable(Base):
    __tablename__ = 'powersi_fsc_task'
    system_task_id = Column(String(200), primary_key=True, comment='系统任务编号')
    subject_code = Column(String(200), comment='基金安全主题编码')
    system_title = Column(String(200), comment='基金安全主题')
    city_name = Column(String(200), comment='地市名称')
    system_process_status = Column(String(200), default='正常', comment='系统处理状态[正常,异常,可疑,无法执行,优化脚本]')
    task_exec_time = Column(String(200), comment='任务执行时长')
    sql_file_name = Column(String(200), comment='SQL文件名')
    sql_content = Column(TEXT, comment='SQL语句')
    task_exec_status = Column(String(200), default='未执行', comment='执行状态[未执行,正在执行,执行失败,执行成功]')
    result_data = Column(TEXT, comment='执行结果')
    row_count = Column(BigInteger, default=99999999, comment='SQL执行结果条数')
    reason = Column(TEXT, comment='异常数据原因')
    task_month = Column(String(200), comment='月份')
    expect_finish_date = Column(String(200), comment='期望完成时间')
    memo = Column(TEXT, comment='备注')

    @classmethod
    def get_sorted_query(cls, session):
        return session.query(cls).order_by(cls.subject_code, cls.system_process_status, cls.sql_content)


class TaskInModel(BaseModel):
    system_task_id: str
    subject_code: str
    system_title: str
    city_name: str
    sql_file_name: str
    sql_content: str
    task_month: str
    expect_finish_date: str


class QueryTaskModel(BaseModel):
    system_task_ids: Optional[List[str]] = None
    row_count_zero_symbol: Optional[str] = '>='
    subject_code: Optional[str] = None
    system_title: Optional[str] = None
    system_process_status: Optional[str] = None
    task_exec_status: Optional[str] = None
    system_commit_status: Optional[bool] = False

    @validator("system_task_ids", pre=True, always=True)
    def exclude_empty_list(cls, v):
        if not v:
            return None
        return v


class SqliteSqlalchemy:
    def __init__(self):
        self.connection_is_active = False
        self.engine = None
        self.get_db_connection()

    def get_db_connection(self):
        try:
            self.engine = create_engine(database_url, echo=database_echo)
            Base.metadata.create_all(self.engine, checkfirst=True)
        except Exception as e:
            print("数据库连接失败：", e)

    def get_db_session(self):
        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()
            return session
        except Exception as e:
            print("获取数据库会话失败：", e)

    def add_task(self, powersiFscTaskInModel: TaskInModel):
        session = self.get_db_session()
        try:
            session.add(TaskTable(**powersiFscTaskInModel.dict()))
            session.commit()
        except Exception as e:
            print("新增任务数据失败：", e)
        finally:
            session.close()

    def query_tasks_by_conditions(self, param: QueryTaskModel):
        """
        根据条件查询任务数据
            打印SQL语句： print(str(statement))
        """
        session = self.get_db_session()
        try:
            statement = TaskTable.get_sorted_query(session)
            if not param.system_commit_status and param.system_task_ids:
                statement = statement.filter(TaskTable.system_task_id.in_(param.system_task_ids))
            if param.row_count_zero_symbol == '>=':
                statement = statement.filter(TaskTable.row_count >= 0)
            if param.row_count_zero_symbol == '>':
                statement = statement.filter(TaskTable.row_count > 0)
            if param.row_count_zero_symbol == '=':
                statement = statement.filter(TaskTable.row_count == 0)
            if param.subject_code:
                statement = statement.filter(TaskTable.subject_code.like(f'%{param.subject_code}%'))
            if param.system_title:
                statement = statement.filter(TaskTable.system_title.like(f'%{param.system_title}%'))
            param.__delattr__('system_task_ids')
            param.__delattr__('row_count_zero_symbol')
            param.__delattr__('subject_code')
            param.__delattr__('system_title')
            param.__delattr__('system_commit_status')
            statement = statement.filter_by(**param.dict(exclude_unset=True, exclude_none=True))
            result = statement.all()
            data = [item.__dict__ for item in result]
            return data
        except Exception as e:
            print('任务数据查询失败：', e)
        finally:
            session.close()

    def query_system_titles(self, system_commit_status: bool = False, system_task_ids: List[str] = None):
        """
        标题列表(每查询一次数更新一次)
        :param system_commit_status: 任务提交状态 false代表只查询未提交任务
        :param system_task_ids: 未提交任务id列表
        :return:
        """
        session = self.get_db_session()
        try:
            statement = session.query(TaskTable.system_title)
            if not system_commit_status and system_task_ids:
                statement = statement.filter(TaskTable.system_task_id.in_(system_task_ids))
            statement = statement.group_by(TaskTable.system_title).order_by(TaskTable.system_title)
            results = statement.all()
            data = [row.system_title for row in results]
            session.close()
            return data
        except Exception as e:
            print("查询任务标题失败：", e)
        finally:
            session.close()

    def update_task(self, system_task_ids: List[str], reason: str, system_process_status: str):
        session = self.get_db_session()
        try:
            session = sessionmaker(bind=self.engine)()
            stmt = update(TaskTable).where(TaskTable.system_task_id.in_(system_task_ids)).values(
                {
                    TaskTable.reason: reason,
                    TaskTable.system_process_status: system_process_status
                }
            )
            rs = session.execute(stmt)
            session.commit()
            print(f'任务更新成功，影响行数：{rs.rowcount}')
            return rs.rowcount
        except Exception as e:
            print("更新任务数据失败：", e)
        finally:
            session.close()


db = SqliteSqlalchemy()
