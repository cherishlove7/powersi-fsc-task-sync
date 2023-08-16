# -*- encoding: utf-8 -*-
"""
@File:        powersi.py
@Author:      Little duo
@Time:        2023/7/11 10:41
@Contact:     1049041957@qq.com
@License:     (C)Copyright 2021-2022, Little duo
"""
import threading
import ddddocr
import hashlib
import os
import time
from urllib.parse import urlencode
import requests
from datetime import datetime

from config import username as input_username, password as input_password, login_timer_minutes


class PowersiService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0'
        }
        self.username = None
        retries = 1
        while retries <= 5:
            retries += 1
            self.auto_login()
            if self.username:
                break
        # 每隔login_timer_minutes分钟登录一次
        threading.Timer(login_timer_minutes*60, self.__init__).start()


    def auto_login(self):
        try:
            self.headers['Cookie'] = None
            response = requests.post(url="https://im.powersi.com/PowerSiIM/", headers=self.headers)
            cookie = response.headers['Set-Cookie']
            self.headers['Cookie'] = cookie
            response = requests.post(
                url=f"https://im.powersi.com/PowerSiIM/login/verifycode.action?timesamp={datetime.now().timestamp()}",
                headers=self.headers,
                timeout=5
            )
            ocr = ddddocr.DdddOcr(show_ad=False)
            verifycode = ocr.classification(response.content)
            print(f'验证码识别结果：{verifycode}')
            return self.login(input_username, input_password, verifycode)
        except Exception as e:
            print(e)
            return False

    def flush_verifycode(self):
        """
        先请求登陆页面获取response的cookie,将返回的cookie带入请求头请求验证码
        :return:
        """
        try:
            # 获取 JSESSIONID
            self.headers['Cookie'] = None
            response = requests.post(url="https://im.powersi.com/PowerSiIM/", headers=self.headers)
            cookie = response.headers['Set-Cookie']
            self.headers['Cookie'] = cookie
            # 获取验证码
            response = requests.post(
                url=f"https://im.powersi.com/PowerSiIM/login/verifycode.action?timesamp={datetime.now().timestamp()}",
                headers=self.headers,
                timeout=5
            )
            with open("resource/images/verifycode.png", mode='wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(e)
            return False

    def login(self, username, password, verifycode):
        md5 = hashlib.md5()  # 创建md5加密对象
        md5.update(password.encode('utf-8'))  # 指定需要加密的字符串
        md5_password = md5.hexdigest().upper()  # 加密后的字符串
        self.headers['Cookie'] = f'loginUser={username};' + self.headers['Cookie']
        try:
            response = requests.post(
                url=f"https://im.powersi.com/PowerSiIM/login/admin.action?password={{md5}}{md5_password}&pwdResult=&loginUser={username}&inputPwd=&verifycode={verifycode}",
                headers=self.headers,
                allow_redirects=False,
                timeout=5
            )
            if 'Set-Cookie' in response.headers.keys():
                finally_cookies = self.headers['Cookie'] + ';' + response.headers['Set-Cookie']
                self.headers['Cookie'] = finally_cookies
                return self.current_user_info(username=username)
            else:
                return False, None
        except Exception as e:
            return False, None

    def current_user_info(self, username):
        try:
            response = requests.post(
                url="https://im.powersi.com/PowerSiIM/attend/AttendUtilRuleAction!getPersonInfo4Home.action",
                headers=self.headers,
                timeout=5
            )
            psn_info = response.json()
            if psn_info['data']['staff_name'] == "":
                return False, 'cookie已过期，请重新登录!'
            current_user_info = {
                'username': username,
                'name': psn_info['data']['staff_name'],
                'message': f"欢迎{psn_info['data']['staff_name']}({psn_info['data']['dept_name']})",
                'dept_name': psn_info['data']['dept_name']
            }
            self.username = username
            # with open(self.cookie_path, mode='w') as f:
            #     f.write(self.headers['Cookie'])
            print(current_user_info)
            return True, current_user_info
        except Exception as e:
            print(e)
            return False, None

    def preview_sql_file(self, file_id, retries=0):
        while retries <= 5:
            try:
                response = requests.post(
                    url=f"https://im.powersi.com/PowerSiIM/fund/risk-subject/preview.action?fileid={file_id}",
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Connection": "keep-alive",
                        'Cookie': self.headers['Cookie'],
                        "Host": "im.powersi.com",
                        "Referer": "https://im.powersi.com/PowerSiIM/main.action",
                        "Sec-Fetch-Dest": "iframe",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-User": "?1",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": '"Windows"'
                    }
                )
                response.encoding = "gbk"
                return True, response.text
            except Exception as e:
                retries += 1
                time.sleep(1)
                return self.preview_sql_file(file_id, retries)
        return False, None

    def upload_file(self, system_task_id, file_path):
        """
        文件上传
        :param system_task_id:
        :param file_path:
        :return: file_id
        """
        try:
            filename = os.path.basename(file_path)
            r = requests.post(
                url="https://im.powersi.com/PowerSiIM/file/saveFile.action",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': 'https://im.powersi.com',
                    'Connection': 'keep-alive',
                    'Referer': f'https://im.powersi.com/PowerSiIM/fund/check-task/toDeal.action?taskId={system_task_id}',
                    'Cookie': self.headers['Cookie'],
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin'
                },
                files={'uploads': (filename, open(file_path, 'rb'), 'application/octet-stream')}
            )
            print(f'文件上传响应: {r.content}')
            response_json = r.json()
            if str(response_json['errortype']) == '0':
                print(f'文件上传成功: {system_task_id}, {file_path}')
                file_id = response_json['data']['file_id']
                return file_id
            else:
                print(f'文件上传失败: {system_task_id}, {file_path}')
        except Exception as e:
            print(e)

    def query_system_task_ids(self, query_all=False):
        """
        获取待检查任务列表
        :return:
        """
        try:
            now = datetime.now()
            first_day = datetime(year=now.year, month=now.month, day=1)
            start_date = first_day.strftime('%Y-%m-%d')
            end_date = '2099-12-31'
            r = requests.post(
                url=f"https://im.powersi.com/PowerSiIM/fund/check-task/loadList.action?login_user={self.username}&month=&check_result=&subject_code=&system_name=&is_great=&is_data_platform=&start_date={start_date}&end_date={end_date}&page=1&pagesize=1000&codetable=%5B%7B%22type%22%3A%22sys_dept_lp%22%2C%22data%22%3A%22sp_dept_id%22%2C%22display%22%3A%22sp_dept_id%22%7D%2C%7B%22type%22%3A%22staff_all%22%2C%22data%22%3A%22sp_staff_id%22%2C%22display%22%3A%22sp_staff_id%22%7D%2C%7B%22type%22%3A%22fund_check_result%22%2C%22data%22%3A%22check_result%22%2C%22display%22%3A%22check_result%22%7D%2C%7B%22type%22%3A%22yes_or_no%22%2C%22data%22%3A%22is_data_platform%22%2C%22display%22%3A%22is_data_platform%22%7D%2C%7B%22type%22%3A%22fund_check_state%22%2C%22data%22%3A%22state%22%2C%22display%22%3A%22state%22%7D%5D",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': 'https://im.powersi.com',
                    'Connection': 'keep-alive',
                    'Referer': f'https://im.powersi.com/PowerSiIM/fund/check-task/loadList.action',
                    'Cookie': self.headers['Cookie'],
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin'
                }
            )
            if query_all:
                return True, r.json()
            else:
                system_task_ids = [row['task_id'] for row in r.json()['rows']]
                return True, system_task_ids
        except Exception as e:
            return False, e

    def commit_task(self, system_task_id, file_id, system_process_status, row_count, result_desc):
        """
        任务提交至管理平台
        :param system_task_id: 任务ID
        :param file_id: 附件ID
        :param system_process_status: 处理状态 "01" 正常 "02" 异常 "03" 可疑 "04" 无法执行 "05" 优化脚本
        :param row_count: 结果条数
        :param result_desc: 检查结果说明
        :desc 备注
        :return:
        """
        desc = None
        if len(result_desc) >= 450:
            desc = result_desc
            result_desc = "检查结果说明有文本长度限制，已在备注中说明"
        try:
            data = {
                'taskId': system_task_id,
                'state': '02',
                'sp_staff_id': "",
                'check_result': system_process_status,
                'results': row_count,
                'result_desc': result_desc,
                'file_str': file_id,
                'is_upload': '1',
                'desc': desc,
            }
            r = requests.post(
                url="https://im.powersi.com/PowerSiIM/fund/check-task/deal.action",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': 'https://im.powersi.com',
                    'Connection': 'keep-alive',
                    'Referer': f'https://im.powersi.com/PowerSiIM/fund/check-task/toDeal.action?taskId={system_task_id}',
                    'Cookie': self.headers['Cookie'],
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin'
                },
                params=urlencode(data, encoding='gbk')
            )
            # print("任务提交响应代码", r.status_code)  # 200
            print("任务提交响应结果:", r.content)  #  b'{"errortype":"0","data":"\xb2\xd9\xd7\xf7\xb3\xc9\xb9\xa6...","message":""}'
            response_json = r.json()
            if str(response_json['errortype']) == '0':
                print(f'任务提交成功：{data}')
                return True
            else:
                print(f'任务提交失败：{data}')
        except Exception as e:
            print("任务提交响应结果:", e)
