#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: AutoXue
@file: model.py
@author: alonik
@contact: https://github.com/kessil/AutoXue/
@time: 2019-10-27(星期天) 10:43
@Copyright © 2019. All rights reserved.
"""
import json
import traceback
import datetime
import pymysql
import sqlite3
from pymysql import NUMBER
import requests
# from datetime import datetime
from unit import cfg, logger


class Structure:
    _fields = []

    def __init__(self, *args, **kwargs):
        if len(args) > len(self._fields):
            raise TypeError('Expected {} arguments'.format(len(self._fields)))

        # Set all of the positional arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

        # Set the remaining keyword arguments
        for name in self._fields[len(args):]:
            setattr(self, name, kwargs.pop(name))

        # Check for any remaining unknown arguments
        if kwargs:
            raise TypeError('Invalid argument(s): {}'.format(','.join(kwargs)))


class Bank(Structure):
    _fields = ['id', 'category', 'content', 'options',
               'answer', 'excludes', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.content = None

    def __repr__(self):
        return f'{self.content}'

    def to_json(self):
        pass

    @classmethod
    def from_json(cls, item):
        filename = "questions.json"
        question_data = json.loads(open(filename).read())
        for question in question_data:
            if question['content'] == item['content']:
                logger.debug(f'GET item success')
                print("返回的数据类型是：")
                print(type(filename))
                print('----------------')
                print(filename)
                print('----------------')
                return filename
        logger.debug(f'GET item failure')
        return None


class BankQuery:
    def __init__(self):
        # 数据库参数
        self.data_platform = cfg.get('database', 'data_platform')
        if self.data_platform == 'mysql':
            self.host = cfg.get('mysql', 'host')
            self.user = cfg.get('mysql', 'user')
            self.password = cfg.get('mysql', 'password')
            self.port = cfg.getint('mysql', 'port')
            self.dbname = cfg.get('mysql', 'db')
            self.table = cfg.get('mysql', 'table')
            self.db = pymysql.connect(host=self.host, user=self.user,
                                      password=self.password, port=self.port, db=self.dbname)
        elif self.data_platform == 'sqlite3':
            self.dbname = cfg.get('sqlite3', 'db')
            self.table = cfg.get('sqlite3', 'table')
            self.db = sqlite3.connect(self.dbname)

        self.cursor = self.db.cursor()
        self.url = cfg.get('api', 'url')
        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/63.0.3239.132 Safari/537.36 "
        }
        self.titles = ["id", "category", "content",
                       "options", "answer", "excludes", "notes"]

    def post(self, item, url=None):
        if not url:
            url = self.url
        if "" == item["content"]:
            logger.debug(f'content is empty')
            return False
        logger.debug(
            f'POST {item["content"]} {item["options"]} {item["answer"]} {item["excludes"]}...')

        try:
            res = requests.post(url=url, headers=self.headers, json=item)
            if 201 == res.status_code:
                return True
        except:
            return False

    def update(self, item):
        result, num = self.get(item)
        if num == 0:
            try:
                if self.data_platform == 'mysql':
                    sql = f'UPDATE {self.table} SET answer={item["answer"]} WHERE content="{item["content"]}" AND options="{item["options"]}"'
                    self.cursor.execute(sql)
                elif self.data_platform == 'sqlite3':
                    sql = f'UPDATE {self.table} SET answer={item["answer"]} WHERE content="{item["content"]}" AND options="{item["options"]}"'
                    self.cursor.execute(sql)
                print('更新记录Successful')
                self.db.commit()
                return True
            except:
                # traceback.print_exc()
                print('更新记录Failed')
                self.db.rollback()
                return False

    def put(self, item):
        if item["content"] == '':
            logger.debug(f'content is empty')
            return False
        else:
            item['content'] = item['content'].strip('\r\n').replace(
                u'\u3000', u' ').replace(u'\xa0', u' ').strip()
            item['content'] = ' '.join(item['content'].split())
        item['options'] = str(item['options']).strip('\r\n').replace('\'', '"').replace(
            u'\u3000', u' ').replace(u'\xa0', u' ').strip()
        keys = ','.join(item.keys())
        values = ','.join(['%s'] * len(item))
        logger.debug(f'\033[34m 现在准备向题库加入新题目。')
        logger.info(
            f'\033[34m PUT  {item["category"]} {item["content"]} {item["options"]} {item["answer"]} {item["excludes"]}... ')
        try:
            if self.data_platform == 'mysql':
                sql = f'INSERT INTO {self.table} ({keys}) VALUES ({values})'
                self.cursor.execute(sql, tuple(item.values()))
            elif self.data_platform == 'sqlite3':
                sql = f'INSERT INTO {self.table}(category,content,options,answer,excludes,notes) VALUES {tuple(item.values())}'
                self.cursor.execute(sql)
            print('更新记录Successful')
            self.db.commit()
            return True
        except:
            traceback.print_exc()
            print('更新记录Failed')
            self.db.rollback()
            return False

    def get(self, item):
        sql = ''
        # if "" == item["content"]:
        #     logger.debug(f'content is empty')
        #     return None, 0
        content = item['content'].strip('\r\n').replace(
            u'\u3000', u' ').replace(u'\xa0', u' ').strip()
        content = ' '.join(content.split())
        if item['options'] is None:
            if self.data_platform == 'mysql':
                sql = f"SELECT * FROM {self.table} WHERE replace(content,' ','') LIKE CONCAT('%',replace('{content}',' ',''),'%')"
            elif self.data_platform == 'sqlite3':
                sql = f"SELECT * FROM {self.table} WHERE replace(content,' ','') LIKE '%'||replace('{content}',' ','')||'%'"
        elif item['content'] is None:
            if self.data_platform == 'mysql':
                sql = f"SELECT * FROM {self.table} WHERE replace(options,' ','') LIKE CONCAT('%',replace('{item['options']}',' ',''),'%')"
            elif self.data_platform == 'sqlite3':
                sql = f"SELECT * FROM {self.table} WHERE replace(options,' ','') LIKE '%'||replace('{item['options']}',' ','')||'%'"
        elif item['options'] == '':
            options = '[""]'
            if self.data_platform == 'mysql':
                sql = f"SELECT * FROM {self.table} WHERE replace(content,' ','') LIKE CONCAT('%',replace('{content}',' ',''),'%') AND replace(options,' ','') LIKE CONCAT('%',replace('{options}',' ',''),'%')"
            elif self.data_platform == 'sqlite3':
                sql = f"SELECT * FROM {self.table} WHERE replace(content,' ','') LIKE '%'||replace('{content}',' ','')||'%' AND replace(options,' ','') LIKE '%'||replace('{options}',' ','')||'%'"
        else:
            options = '['
            for i in item['options']:
                options += '"' + i + '",'
            options = options[:-1] + ']'
            options = options.strip('\r\n').replace(u'\u3000', u' ').replace(
                u'\xa0', u' ').replace(', "', ',"').strip()
            if self.data_platform == 'mysql':
                sql = f"SELECT * FROM {self.table} WHERE replace(content,' ','') LIKE CONCAT('%',replace('{content}',' ',''),'%') AND replace(options,' ','') LIKE CONCAT('%',replace('{options}',' ',''),'%')"
            elif self.data_platform == 'sqlite3':
                sql = f"SELECT * FROM {self.table} WHERE replace(content,' ','') LIKE '%'||replace('{content}',' ','')||'%' AND replace(options,' ','') LIKE '%'||replace('{options}',' ','')||'%'"
        # 注意content里面的有些时候空格是\xa0
        # sql = f"SELECT * FROM {self.table} WHERE trim(replace((content),'{blank}',' ')) LIKE CONCAT('%',trim(replace('{content.strip()}','{blank}',' ')),'%') AND trim(replace((options),' ','')) LIKE CONCAT('%',trim(replace('{options.strip()}',' ','')),'%')"

        try:
            self.cursor.execute(sql)
            # 输出长度
            # self.cursor.fetchall()
            # result_num = self.cursor.rowcount
            # 获取结果的第一条数据
            rows = self.cursor.fetchall()
            if rows is not None or rows!=[]:
                result_num = len(rows)
                # logger.info(f'\033[31;40m搜索结果数量：{result_num}\033[0m')
                rtn = list(rows[0])
                question = dict(zip(self.titles, rtn))
                return question, result_num
            else:
                # logger.info(f'\033[7;31m 题库里没有该题 \033[1;31;40m')
                return None, 0
        except Exception as msg:
            # logger.info(f'\033[7;31m 题库里没有该题 \033[1;31;40m')
            # traceback.print_exc()
            # self.put(item)
            return None, 0

    def update_answer_record(self, item: list):
        # SQL 更新语句
        answer_table = 'answer_rec'
        win_times = item[3]
        loss_times = item[4]
        keys = 'username, date, module, win_times, loss_times'
        # 先看看有没有相关记录
        sql = f'SELECT * FROM {answer_table} WHERE username= "{item[0]}" AND date="{item[1]}" AND module="{item[2]}"'
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            if len(rows) == 0:
                sql = f'INSERT INTO {answer_table}({keys}) VALUES {tuple(item)}'
                self.cursor.execute(sql)
                self.db.commit()
                return [win_times, loss_times]
            if len(rows) == 1:
                for row in rows:
                    win_times += row[4]
                    loss_times += row[5]
            # 提交到数据库执行
            sql = f'UPDATE {answer_table} SET win_times=win_times+{item[3]},loss_times=loss_times+{item[4]} WHERE username= "{item[0]}" AND date="{item[1]}" AND module="{item[2]}" '
            self.cursor.execute(sql)
            self.db.commit()
            return [win_times, loss_times]
        except:
            # 发生错误时回滚
            traceback.print_exc()
            print('出错了！')
            self.db.rollback()
        # 关闭数据库连接
        self.db.close()

        # sql = f"UPDATE {answer_table} SET win_times=win_times+{item[3]}, " + \
        #       f"loss_times=loss_times+{item[4]} WHERE date='{item[1]}' AND module='{item[2]}' "
        # if self.data_platform == 'mysql':
        #     sql = f"INSERT INTO {answer_table}({keys}) VALUES {tuple(item)} ON DUPLICATE KEY UPDATE " +\
        #           f"win_times=win_times+{item[3]},loss_times=loss_times+{item[4]}"
        #     try:
        #         # 执行SQL语句
        #         self.cursor.execute(sql)
        #         print('更新success！')
        #         # 提交到数据库执行
        #         self.db.commit()
        #     except:
        #         # 发生错误时回滚
        #         traceback.print_exc()
        #         print('更新出错了！')
        #         self.db.rollback()
        #     # 关闭数据库连接
        #     self.db.close()
        #     return
        # elif self.data_platform == 'sqlite3':
        #     sql1 = f'INSERT OR REPLACE INTO {answer_table}({keys}) VALUES {tuple(item)}  ' + \
        #           f'ON CONFLICT(ID) DO UPDATE SET  ' +\
        #           f'win_times=win_times+{item[3]},loss_times=loss_times+{item[4]}'
        #     sql2 = f'UPDATE answer_rec SET win_times=win_times+{item[3]},loss_times=loss_times+{item[4]} where date="{item[1]}" and module="{item[2]}";'
        #     try:
        #         # 执行SQL语句
        #         self.cursor.execute(sql1)
        #         self.cursor.execute(sql2)
        #         print('更新success！')
        #         # 提交到数据库执行
        #         self.db.commit()
        #     except:
        #         # 发生错误时回滚
        #         traceback.print_exc()
        #         print('更新出错了！')
        #         self.db.rollback()
        #     # 关闭数据库连接
        #     self.db.close()

    # 去除原先数据一些含有特殊字符的数据

    def organize(self):
        """
        整理表，把题干中的多个空格合并成一个，并去除题干中的一些特殊空格符号
        把选项中的空格（特殊的空格符号）去掉
        """
        new_table = 'new_questions'
        sql = 'select * from questions'
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            for row in rows:
                question = list(row)
                question[2] = question[2].strip('\r\n').replace(
                    u'\u3000', u' ').replace(u'\xa0', u' ').strip()
                question[2] = ' '.join(question[2].split())
                question[3] = question[3].strip('\r\n').replace(
                    u'\u3000', u' ').replace(u'\xa0', u' ').replace(', "', ',"').replace(' 、', '、').strip()
                question[3] = ' '.join(question[3].split())
                values = ','.join(['%s'] * len(question))
                sql = f'INSERT INTO {new_table} VALUES ({values})'
                try:
                    self.cursor.execute(sql, question)
                    self.db.commit()
                except:
                    traceback.print_exc()
                    print('更新记录Failed')
                    self.db.rollback()
        except:
            pass
        print('记录更新完成。')


if __name__ == "__main__":
    bank = BankQuery()
    # bank.organize()
    # bank.get({"content": '2020年4月24日，国家航天局宣布将我国首次火星探测任务命名为“ ”，同时公布了首次火星探测任务标识“ ”。',
    #           "options": ["天问一号\u3000揽星九天", "巡天一号\u3000辰宿列张", "探天一号\u3000追问星辰", "天索一号\u3000寻秘宇宙"]})
    # q = bank.get({"content": '2020年4月24日，国家航天局宣布将我国首次火星探测任务命名为“ ”，同时公布了首次火星探测任务标识“ ”。',
    #               "options": None})
    # q = bank.get({"content": '我国',
    #               "options": None})
    # item = [datetime.date.today(), '争上游答题', 1, 3]
    # bank.update_answer_record(item)
    answer, result = bank.get(
        {"category": "单选题", "content": '', "options": ["粪-口传播", "血液传播", "母婴传播", "空气飞沫传播"], "answer": "A",
         "excludes": "", "notes": ""})
    print(f'结果【{answer}】,搜索到{result}条')
    # tt=datetime.date.today()
    # print(tt)
    # result = bank.update_answer_record(
    #     ['user1', f'{datetime.date.today()}', "争上游答题", 1, 2])
    # print(result[0], result[1], result[0] + result[1])
