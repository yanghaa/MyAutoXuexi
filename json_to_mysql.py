# encoding: utf-8
"""
@project: AutoXue
@file: json_to_mysql.py
@author: alonik
@contact: https://github.com/my-autoxuexi/myAutoXuexi
@time: 2020-10-16(星期五) 09:03
@Copyright © 2020. All rights reserved.

注意事项：
    将questions.json的题集更新到本地的数据库中
    需要将questions.json与本文件放在同一个目录中
"""


import json
import re
import ijson

from model import BankQuery
from unit import cfg, logger

QuestionBank = BankQuery()

# with open('questions.json', 'r', encoding='utf-8') as f:
# # filename = "questions.json"
#     question_data=ijson.items(f,'')
# # question_data = ijson.loads(open(filename).read())
# for question in question_data:
#     item = QuestionBank.get(question)
#     if item==None:
#         print(question['id'])
#         QuestionBank.put(question)

with open('data\data1.json', 'r', encoding='utf-8') as f:
    objects = ijson.items(f, 'item')
    # 这个objects在这里就是相当于一个生成器，可以调用next函数取它的下一个值
    while True:
        try:
            question = objects.__next__()
            item = QuestionBank.get(question)
            if item is None:
                print(f"源文件中第{question['content']}题在数据库搜索不到，现在将其加入到数据库中。")
                QuestionBank.put(question)
        except StopIteration as e:
            print("数据读取完成")
            break
