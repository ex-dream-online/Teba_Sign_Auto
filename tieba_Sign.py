# coding=utf-8
# @Software : PyCharm
# @Time : 2023/5/19 0:35
# @File : tieba_Sign.py
# @Python Version : Python3.10
# @Core : 向'http://tieba.baidu.com/sign/add'提交kw与tbs数据即可完成签到,使用前请先运行get_into.py

import datetime
import json
import os
import random
import time

import requests

import setting


class Tieba:
    def __init__(self):
        self.like_url = setting.like_url
        self.sign_url = setting.sign_url
        self.headers = setting.headers
        self.tbs = setting.tbs
        self.bars = []
        self.journal = None

    def bars_get(self):
        content = requests.Session().get(self.like_url, headers=self.headers).json()['data']['like_forum']
        for element in content:
            self.bars.append(element['forum_name'])
        random.shuffle(self.bars)  # 打乱签到顺序
        return self.bars

    def sign(self):
        self.bars_get()
        date = datetime.datetime.now().strftime('%Y-%m-%d')

        n = 0
        failed_signed_bar = []
        nu_successes = 0
        retry_count = 0
        max_retry = 5
        while n < len(self.bars):
            data = {  # 提交数据实现签到
                'ie': 'utf-8',
                'kw': self.bars[n],  # 贴吧名字
                'tbs': self.tbs
            }
            try:
                raw = requests.Session().post(self.sign_url, data=data, headers=self.headers)
                if raw.status_code == 200:
                    mark = raw.json()['no']
                    if mark == 0 or 1101:
                        nu_successes += 1
                    elif mark == 2150040 and retry_count < max_retry:
                        time.sleep(10 + random.randint(0, 5))
                        n -= 1
                        retry_count += 1
                    elif mark == 2150040:
                        retry_count = 0
                        failed_signed_bar.append(self.bars[n])
                else:
                    failed_signed_bar.append(self.bars[n])
            except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
                failed_signed_bar.append(self.bars[n])
            time.sleep(2 + random.randint(0, 1))
            n += 1

        self.journal = {
            str(date):
                {
                    "签到成功数": nu_successes,
                    "签到失败数": len(failed_signed_bar),
                    "签到失败目录": failed_signed_bar
                }
        }
        return self.journal

    def log(self, path):
        # 获取简易日志
        self.sign()
        directory_path = os.path.abspath('.') + '/'
        if os.path.exists(directory_path + 'log'):
            pass
        else:
            os.mkdir(directory_path + 'log')
        filename = directory_path + 'log' + '/' + path
        renew = {}
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                renew = json.load(file)
        except IOError:  # 假如json文件不存在则报错.
            pass
        renew.update(self.journal)
        with open(filename, 'w', encoding='utf-8') as file:  # file是指使用括号内参数打开文件作为file变量
            json.dump(renew, file, indent=4, ensure_ascii=False)  # 缩进，不默认使用ascii码
            file.write('\n')


if __name__ == '__main__':
    s = Tieba()
    s.log(path='log.json')
