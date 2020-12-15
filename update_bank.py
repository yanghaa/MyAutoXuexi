#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: AutoXue
@file: update_bank.py
@author: alonik
@contact: https://github.com/kessil/AutoXue/
@time: 2020-10-16(星期五) 09:03
@Copyright © 2020. All rights reserved.
"""

from model import BankQuery
import re

file_path1 = 'questions.txt'
file_path2 = 'ques_bank.txt'
bank = BankQuery()
option = []
content = ''
line_num = 0
with open(file_path1, encoding='utf-8') as file_obj:
    lines = file_obj.readlines()
for line in lines:
    # print(f'处理到{line_num}行。')
    line_num += 1
    tt = line.strip("\r\n").strip("\t").strip("\n").strip()
    if tt == '':
        continue
    else:
        quiz_line = re.sub('_+', ' ', line)
        quiz_line = re.sub(r'(?<=。)(?![\w\W]*。)[\w\W]+', '', quiz_line)
    if "答案解析：" in quiz_line:
        continue
    if '正确答案[:：]' in quiz_line or '答案[:：]' in quiz_line:
        try:
            quiz_answer = quiz_line.strip("\r\n").split('：', 1)[1]
        except Exception as msg:
            print(msg)
            print(quiz_line)
        item = {
            "category": "单选题",
            "content": content,
            "options": option,
            "answer": quiz_answer,
            "excludes": "",
            "notes": ""
        }
        answer, result = bank.get(item)
        if result == 0:
            bank.put(item)
        elif quiz_answer != answer['answer']:
            bank.update(item)
        option = []
        content = ''
        answer = ''
    if '词语解析：' in quiz_line:
        item = {
            "category": "单选题",
            "content": content,
            "options": option,
            "answer": 'B',
            "excludes": "",
            "notes": ""
        }
        answer, result = bank.get(item)
        if result == 0:
            bank.put(item)
        option = []
        content = ''
        answer = ''
    elif re.split('[.：]', quiz_line)[0].isdigit():
        content = re.split('[.：]', quiz_line, 1)[1].strip("\r\n").strip()
        content = content.replace('_', ' ')
        # content = re.match(r'.*?\.(.*)', quiz_line).group(1).strip()
    elif re.split('[.、]', quiz_line)[0].upper() in 'ABCD':
        # option.append(re.match(r'.*?\.(.*)', quiz_line).group(1).strip())
        option.append(re.split('[.、]', quiz_line, 1)[1].strip("\r\n").strip())
print('程序执行完毕！')
# print(line)
