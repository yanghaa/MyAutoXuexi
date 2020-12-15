#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: AutoXue
@file: autoxue.py
@author: alonik
@contact: https://github.com/my-autoxuexi/myAutoXuexi
@time: 2020-10-16(星期五) 09:03
@Copyright © 2019. All rights reserved.
"""

import datetime
import logging
import math
import multiprocessing
import re
import string
import subprocess
import threading
import time
import winsound
from collections import defaultdict
from configparser import NoOptionError, NoSectionError
from itertools import accumulate
from sched import scheduler
from urllib.parse import quote
import requests
from tqdm import tqdm
from uiautomator2.exceptions import XPathElementNotFoundError, UiObjectNotFoundError
from model import BankQuery
from secureRandom import SecureRandom as random
from secureRandom import decrypt
from unit import caps, cfg, logger, rules
import uiautomator2 as u2
import pysnooper


class Automation:
    # 初始化 Appium 基本参数

    def __init__(self, appargs):
        # self.connect()
        # self.device_id = devices.connect_device()
        self.driver = None
        self.username = None
        self.app_args = {
            'id': '1',
            'username': '',
            'password': '',
            'emuname': '',
            'udid': '',
            'host': '127.0.0.1',
            'port': 0,
            'systemPort': 8200,
            'testapp': False
        }
        self.app_args = appargs
        self.run_modules = []
        self.desired_caps = {
            "platformName": caps["platformname"],
            "platformVersion": caps["platformversion"],
            "automationName": caps["automationname"],
            "unicodeKeyboard": caps["unicodekeyboard"],
            "resetKeyboard": caps["resetkeyboard"],
            "noReset": caps["noreset"],
            'newCommandTimeout': 800,
            "deviceName": caps["devicename"],
            "udid": self.app_args['udid'],
            "systemPort": self.app_args['systemPort'],
            "appPackage": caps["apppackage"],
            "appActivity": caps["appactivity"]
        }
        # logger.info('打开 appium 服务,正在配置...')
        # self.appium_start()
        while True:
            try:
                logger.info('启动 connect 服务,正在配置...')
                # self.conn = u2.connect(self.app_args['udid'])
                # self.driver = self.conn.session(cfg.get('capability', 'apppackage'), 15)
                self.driver = u2.connect(self.app_args['udid'])
                break
            except Exception as msg:
                # adb kill-server
                # adb start-server
                logger.info(f'【异常】{msg},启动connect出现问题,稍后5秒再尝试连接...')
                time.sleep(5)
        self.size = self.driver.window_size()
        self.driver.implicitly_wait(10)
        self.driver.xpath.logger.setLevel(logging.DEBUG)
        # 屏幕方法

    def swipe_up(self, times=1):
        """ 向上滑动屏幕  """
        for _ in range(times):
            self.driver.swipe(self.size[0] * random.uniform(0.55, 0.65),
                              self.size[1] * random.uniform(0.75, 0.95),
                              self.size[0] * random.uniform(0.55, 0.65),
                              self.size[1] * random.uniform(0.15, 0.25))
            logger.debug('向上滑动屏幕')

    def swipe_down(self, times=1):
        """ 向下滑动屏幕 """
        for _ in range(times):
            self.driver.swipe(self.size[0] * random.uniform(0.55, 0.65),
                              self.size[1] * random.uniform(0.15, 0.25),
                              self.size[0] * random.uniform(0.55, 0.65),
                              self.size[1] * random.uniform(0.75, 0.95))
            logger.debug('向下滑动屏幕')

    def swipe_right(self, times=1):
        """ 向右滑动屏幕 """
        for _ in range(times):
            self.driver.swipe(self.size[0] * random.uniform(0.01, 0.11),
                              self.size[1] * random.uniform(0.75, 0.89),
                              self.size[0] * random.uniform(0.89, 0.98),
                              self.size[1] * random.uniform(0.75, 0.89))
            logger.debug('向右滑动屏幕')

    def swipe_left(self, times=1):
        """ 向右滑动屏幕 """
        for _ in range(times):
            self.driver.swipe(self.size[0] * random.uniform(0.89, 0.98),
                              self.size[1] * random.uniform(0.75, 0.89),
                              self.size[0] * random.uniform(0.01, 0.11),
                              self.size[1] * random.uniform(0.75, 0.89))
            logger.debug('向左滑动屏幕')

    def find_element(self, ele: str):
        element = None
        logger.debug(f'find elements by xpath: {ele}')
        try:
            element = self.driver.xpath(ele)
        except (XPathElementNotFoundError, XPathElementNotFoundError):
            logger.error(f'找不到元素: {ele}')
            # raise e
        return element

    def find_elements(self, ele: str):
        elements = None
        logger.debug(f'find elements by xpath: {ele}')
        try:
            elements = self.driver.xpath(ele)
        except XPathElementNotFoundError:
            logger.error(f'找不到元素: {ele}')
            # raise e
        return elements

    # 返回事件
    def safe_back(self, msg='default msg'):  # 你用msg里面含有home字符的特点，看看是不是已经退到了主页了
        if not self.driver.xpath(rules['home_entry']).wait(0.5):
            logger.debug(f'[{self.username}]返回到【{msg}】页面。')
            self.driver.press('back')  # 模拟按下返回键
            time.sleep(1)
            return
        else:
            logger.info(f'[{self.username}]已经到了主页面，再返回就退出APP啦')
            return

    def safe_click(self, ele: str):
        logger.debug(f'safe click {ele}')
        try:
            if self.driver.xpath(ele).click_exists(5):
                time.sleep(0.5)
                return True
        except XPathElementNotFoundError:
            logger.debug(f'没找到学习或者答题入口...')
            return False

    # def __del__(self):
    #     try:
    #         self.driver.app_stop(cfg.get('capability', 'apppackage'))
    #         # self.driver.terminate_app('cn.xuexi.android')
    #     except :
    #         pass


class AutoApp(Automation):
    def __init__(self, appargs):
        super().__init__(appargs)
        self.study_titles = ["登录", "我要选读文章", "视听学习", "视听学习时长", "每日答题", "每周答题", "专项答题", "挑战答题", "争上游答题", "双人对战", "订阅",
                             "分享", "发表观点", "本地频道", "强国运动"]
        self.workdays = cfg.get("prefers", "workdays")
        self.username = appargs['username']
        self.password = appargs['password']
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/63.0.3239.132 Safari/537.36 "
        }
        self.query = BankQuery()
        self.app_modules = (self.watch, self.read, self.daily, self.challenge, self.who_first, self.one_vs_one,
                            self.weekly, self.special_answer, self.subscribe, self.kaleidoscope)
        self.run_modules = []
        self.bank = None
        self.one_vs_one_finished = False
        self.who_first_finished = False
        self.star_share_comments_count = 1
        self.subscribe_times = 0
        self.read_count = 1
        self.daily_count = 5
        self.video_count = 5
        self.has_bgm = cfg.get('prefers', 'radio_switch')
        self.score = defaultdict(tuple)
        # self.driver = self.driver.session(cfg.get('capability', 'apppackage'))
        # self.driver.wait_activity('com.alibaba.android.rimet.biz.home.activity.HomeActivity', 15)
        # self.driver = self.driver.session(cfg.get('capability', 'apppackage'))

        # self.driver.press('volume_mute')
        self.mute()
        self.driver.app_start(cfg.get('capability', 'apppackage'), cfg.get('capability', 'appactivity'), wait=True)
        self.driver.wait_activity('com.alibaba.android.rimet.biz.home.activity.HomeActivity', 15)
        self.login_or_not()
        # 因为挑战答题、每周答题、专项答题都用到每日答题模块
        # 所以先初始化每日答题部分变量
        self._daily_init()

    @staticmethod
    def shuffle(funcs):
        """
        运行模块乱序执行
        """
        random.shuffle(funcs)
        for func in funcs:
            func()
            time.sleep(3)

    @staticmethod
    def click_callback(text: str, d: u2.Device):
        d.xpath(text).click()

    @staticmethod
    def _blank_answer_divide(ans: str, arr: list):
        accu_revr = [x for x in accumulate(arr)]
        # print(accu_revr)
        temp = list(ans)
        for c in accu_revr[-2::-1]:
            temp.insert(c, " ")
        return "".join(temp)

    def mute(self):
        # print(self.driver.info)
        self.driver.press('volume_mute')
        # for times in range(10):
        #     if 0 != subprocess.check_call(f'adb -s {self.app_args["udid"]} shell input keyevent 25',
        #                                   shell=True, stdout=subprocess.PIPE):
        #         logger.info(f'音量无须调节或调节完毕。')

    def back_to_home(self):
        try:
            while not self.driver.xpath(rules['home_entry']).wait(0.5):
                self.driver.press('back')
                self.driver(text='退出').click_exists(0.5)
            self.home_button_click()
            return True
        except Exception as msg:
            logger.debug(f'返回主页出现异常{msg}')
            return False

    def quiz_entry_warning(self):
        # 新更新的提示页面三个按钮的xpath一样的
        for _ in range(3):
            try:
                self.driver.xpath(rules["quiz_next_button"]).click_exists(1)
                # next_button = self.driver.xpath(
                #     rules["quiz_next_button"])
                # next_button.click()
            except XPathElementNotFoundError:
                return False
        time.sleep(1)
        return True

    def home_button_click(self):
        try:
            self.driver.xpath(rules['home_entry']).click_exists(1)
        except (XPathElementNotFoundError, UiObjectNotFoundError):
            time.sleep(1)
            self.back_to_home()

    def login_or_not(self):
        # com.alibaba.android.user.login.SignUpWithPwdActivity
        # time.sleep(15)
        if self.driver(resourceId=rules['home_entry'][18:65]).exists:
            # self.driver.xpath(rules["home_entry"])
            logger.debug(f'不需要登录')
            return
        else:
            logger.debug(self.driver.app_current)
            logger.debug(f"非首页，先进行登录")
            time.sleep(2)
        if not self.username or not self.password:
            logger.error(f'未提供有效的username和password')
            logger.info(f'也许你可以通过下面的命令重新启动:')
            logger.info(
                f'\tpython -m xuexi -u "your_username" -p "your_password"')
            raise ValueError('需要提供登录的用户名和密钥，或者提前在App登录账号后运行本程序')
        while True:
            try:
                username = self.driver.xpath(rules['login_username'])
                password = self.driver.xpath(rules['login_password'])
                username.set_text(self.username)
                password.set_text(self.password)
                break
            except XPathElementNotFoundError:
                pass
        self.driver(text='登录').click_exists(3)
        time.sleep(2)
        self.driver(text='同意并继续').click_exists(3)
        time.sleep(2)
        self.driver(text='同意').click_exists(3)
        time.sleep(2)

    def start(self):
        # i = random.random()
        # times防止程序不停验证是否答题完毕
        self.view_score()
        # self._play_radio_background()
        times = 0
        # 再查看一次分数
        # 根据再次查询分数的结果看看哪些项目是没有满分的
        while self.run_modules:
            self.shuffle(self.run_modules)
            self.view_score()
            if self.run_modules is None:
                logger.info(
                    f'[{self.username}]\033[1;31;43m所有答题和学习已经完成，退出程序。\033[0m')
                break
            if times == cfg.getint('prefers', 'check_times'):
                break
            logger.info(
                f'[{self.username}] \033[7;33;41m复核第{times + 1}遍，看看是不是全部阅读答题完毕。\033[0m')
            times += 1
        # logger.info(f'[{self.username}]\033[1;31;43m【{total_score}】')
        for score in self.score:
            if not self.is_workday() and (score == '专项答题' or score == '每周答题') and self.score[score][0] == 0:
                logger.info(
                    f'[{self.username}]\033[1;31;43m【{score}】不是答题日，无需答题。\033[0m')
            elif self.score[score][1] == self.score[score][0]:
                logger.info(
                    f'[{self.username}]\033[7;41m【{score}】 应完成{self.score[score][1]}分，' +
                    f'实际完成{self.score[score][0]}分，无需重复获取积分。\033[0m')
            else:
                logger.info(
                    f'[{self.username}]\033[41;4m【{score}】 应完成{self.score[score][1]}分，' +
                    f'实际完成{self.score[score][0]}分，有可能未完成该项学习。\033[0m')
        self.logout_or_not()
        # sys.exit(0)

    def test(self):
        """ 测试运行模块

        根据配置文件的设置
        调用set_test_module方法，将需要测试的模块加入到测试过程
        """
        self.back_to_home()
        try:
            test_times = cfg.getint('test', 'test_times')
        except (NoOptionError, NoSectionError):
            test_times = 1
        self.set_test_module()
        if self.run_modules:
            while test_times:
                logger.info(
                    f'[{self.username}] \033[1;31m 测试还剩{test_times}组完毕 \033[0m')
                test_times -= 1
                self.shuffle(self.run_modules)
                logger.info(f'测试完毕')
                if test_times == 0:
                    break
        self.logout_or_not()

    def set_test_module(self):
        """
        设置测试模块
        """
        self.run_modules.clear()
        if cfg.getint('test', 'app_watch'):
            self.run_modules.append(self.watch)
        if cfg.getint('test', 'app_read'):
            self.run_modules.append(self.read)
        # if cfg.getint('test', 'app_music'):
        #     self.run_modules.append(self.music)
        if cfg.getint('test', 'app_daily'):
            self.run_modules.append(self.daily)
        if cfg.getint('test', 'app_challenge'):
            self.run_modules.append(self.challenge)
        if cfg.getint('test', 'app_who_first'):
            self.run_modules.append(self.who_first)
        if cfg.getint('test', 'app_one_vs_one'):
            self.run_modules.append(self.one_vs_one)
        if cfg.getint('test', 'app_weekly'):
            self.run_modules.append(self.weekly)
        if cfg.getint('test', 'app_special_answer'):
            self.run_modules.append(self.special_answer)
        if cfg.getint('test', 'app_subscribe'):
            self.run_modules.append(self.subscribe)
        if cfg.getint('test', 'app_kaleidoscope'):
            self.run_modules.append(self.kaleidoscope)

    def study_is_over(self):
        funcs = []
        is_over = True
        if self.score["我要选读文章"][0] != self.score["我要选读文章"][1] or self.score["视听学习时长"][0] != self.score["视听学习时长"][1]:
            funcs.append(self.read)
            is_over = False

        if self.score["视听学习"][0] != self.score["视听学习"][1] or self.score["视听学习时长"][0] != self.score["视听学习时长"][1]:
            funcs.append(self.watch)
            is_over = False

        if self.score["每日答题"][0] != self.score["每日答题"][1]:
            funcs.append(self.daily)
            is_over = False

        if self.score["挑战答题"][0] != self.score["挑战答题"][1]:
            funcs.append(self.challenge)
            is_over = False

        if self.score["订阅"][0] != self.score["订阅"][1]:
            funcs.append(self.subscribe)
            is_over = False

        if self.score["分享"][0] < 1 or self.score["发表观点"][0] < 1:
            # 在多读一条，然后执行分享和发表观点操作
            if self.read_count == 0:
                self.read_count = 1
            funcs.append(self.read)
            is_over = False
            pass

        if self.score["本地频道"][0] != self.score["本地频道"][1]:
            self.kaleidoscope()
            is_over = False
            pass

        return is_over, funcs

    def leaveout_answer(self):
        # 先看看分享和发表观点是否做完
        # 每周答题和专项答题排除在验证之外
        for individual_score in self.score:
            if individual_score[0] == individual_score[1]:
                pass
        self.start()
        pass

    def logout_or_not(self):
        tscore = ["总计积分"]
        self.safe_click(rules['score_entry'])
        try:
            total_score = self.driver.xpath(rules["total_score"]).all()
        except XPathElementNotFoundError:
            self.back_to_home()
            self.safe_click(rules['score_entry'])
        else:
            for total_title, total in zip(tscore, total_score):
                score = total.text
                # 打印当日总分
                logger.info(
                    f'[{self.username}]\033[27;31;44m {total_title}：{score} \033[0m')
            # print(s1)
            if cfg.getboolean("prefers", "keep_alive"):
                logger.debug("无需自动注销账号")
                return
            self.back_to_home()
            self.safe_click(rules["mine_entry"])
            self.safe_click(rules["setting_submit"])
            self.safe_click(rules["logout_submit"])
            self.safe_click(rules["logout_confirm"])
        logger.info("已注销")

    def back_to_answer(self, item_name):
        # 首先让程序回到主界面
        # 然后从主界面，根据item_name返回到相应的答题项目
        while True and item_name:
            try:
                self.driver.xpath(rules["home_entry"])
                logger.debug(f'[{self.username}]已经到了主页面，再返回就退出APP啦')
                break
            except XPathElementNotFoundError:
                logger.debug(f'准备前往{item_name}答题')
                self.driver.keyevent(4)  # 模拟按下返回键
                time.sleep(1)

    def is_workday(self):
        day_of_week = datetime.datetime.now().isoweekday()
        if str(day_of_week) in self.workdays:
            return True
        else:
            return False

    def view_score(self):
        """
        查看得分情况
        根据得分情况，运行未完成得分的相应模块
        """
        self.run_modules.clear()
        while not self.safe_click(rules['score_entry']):
            time.sleep(3)
            self.back_to_home()
        time.sleep(3)
        # 第一次或者版本更新会有一到两个提示窗出现
        self.driver.xpath(rules['score_remind']).click_exists(2)
        while True:
            try:
                total_score = self.driver.xpath(rules["total_score"]).wait(5).text
                logger.info(f'[{self.username}]\033[1;31;43m【{total_score}】')
                score_list = self.driver.xpath(rules['score_list']).all()
                break
            except (AttributeError,XPathElementNotFoundError):
                logger.info(f'[{self.username}]\033[1;31;43m分数获取出错！\033[0m')
                time.sleep(3)
        for t, score in zip(self.study_titles, score_list):
            s = score.text
            self.score[t] = tuple([int(x) for x in re.findall(r'\d+', s)])
            if self.score[t][0] < self.score[t][1]:
                self.set_run_modules(t)
        for num in self.score:
            logger.debug(f'{num}, {self.score[num]}')
        self.back_to_home()

    def set_run_modules(self, module_name):
        if module_name == '我要选读文章' and (self.read not in self.run_modules):
            self.run_modules.append(self.read)
        if module_name == '视听学习' and (self.watch not in self.run_modules):
            self.run_modules.append(self.watch)
        if module_name == '视听学习时长' and (self.watch not in self.run_modules):
            self.run_modules.append(self.watch)
        if module_name == '每日答题' and (self.daily not in self.run_modules):
            self.run_modules.append(self.daily)
        if module_name == '争上游答题' and (self.who_first not in self.run_modules) and self.who_first_finished is False:
            self.run_modules.append(self.who_first)
        if module_name == '双人对战' and (self.one_vs_one not in self.run_modules) and self.one_vs_one_finished is False:
            self.run_modules.append(self.one_vs_one)
        if module_name == '每周答题' and (self.weekly not in self.run_modules) and self.is_workday():
            self.run_modules.append(self.weekly)
        if module_name == '专项答题' and (self.special_answer not in self.run_modules) and self.is_workday():
            self.run_modules.append(self.special_answer)
        if module_name == '挑战答题' and (self.challenge not in self.run_modules):
            self.run_modules.append(self.challenge)
        if module_name == '订阅' and (self.subscribe not in self.run_modules) \
                and 0 != cfg.getint('users', 'subscribed_pages_' + self.app_args['id']):
            self.run_modules.append(self.subscribe)
        if (module_name == '分享' or module_name == '发表观点') and (self.read not in self.run_modules):
            self.run_modules.append(self.read)
        if module_name == '本地频道' and (self.read not in self.run_modules):
            self.run_modules.append(self.kaleidoscope)

    def back_or_not(self, title):
        # return False
        if self.app_args['testapp'] is False:
            g, t = self.score[title]
            if g == t:
                logger.info(
                    f' [{self.username}]\033[7;41m【{title}】 应完成{t}分，实际完成{g}分，无需重复获取积分。\033[0m')
                return True
            return False
        else:
            return False

    def _search(self, content, options, exclude=''):
        """
        网上搜索模块
        搜狗引擎较百度引擎，搜索结果全为零的机会应该会大幅降低
        """
        logger.debug(f'搜索 {content} <exclude = {exclude}>')
        logger.info(f"选项 {options}")
        content = re.sub(r'[(（]出题单位.*', "", content)
        if options[-1].startswith("以上") and chr(len(options) + 64) not in exclude:
            logger.info(f'根据经验: {chr(len(options) + 64)} 很可能是正确答案')
            return chr(len(options) + 64)
        # url = quote('https://www.baidu.com/s?wd=' +
        #             content, safe=string.printable)
        # https://www.3gmfw.cn/so/***********/
        url = quote("https://www.sogou.com/web?query=" +
                    content, safe=string.printable)
        response = requests.get(url, headers=self.headers).text
        counts = []
        for letter, option in zip(['A', 'B', 'C', 'D', 'E', 'F'], options):
            count = response.count(option)
            counts.append((count, letter))
            logger.info(f'{letter}. {option}: {count} 次')
        counts = sorted(counts, key=lambda x: x[0], reverse=True)
        counts = [x for x in counts if x[1] not in exclude]
        c, letter = counts[0]
        if 0 == c:
            # 替换了百度引擎为搜狗引擎，结果全为零的机会应该会大幅降低
            _, letter = random.choice(counts)
            logger.info(f'搜索结果全0，随机一个 {letter}')
        logger.info(f'根据搜索结果: {letter} 很可能是正确答案')
        return letter

    def _verify(self, category, content, options):
        """
        答案获取模块
        """
        # 职责: 检索题库 查看提示
        letters = list("ABCDEFGHIJKLMN")
        content = content.strip('\r\n').replace(
            u'\u3000', u' ').replace(u'\xa0', u' ').strip()
        content = ' '.join(content.split())
        if "填空题" == category:
            self.bank, result_num = self.query.get({
                "category": category,
                "content": content,
                "options": ""
            })
        else:
            self.bank, result_num = self.query.get({
                "category": category,
                "content": content,
                "options": options
            })
        if self.bank and self.bank["answer"]:
            logger.info(f'[{self.username}]已知的正确答案: {self.bank["answer"]}')
            return self.bank["answer"]
        excludes = self.bank["excludes"] if self.bank else ""
        tips = self._view_tips()
        if not tips:
            logger.debug("本题没有提示")
            if "填空题" == category:
                return None
            elif "多选题" == category:
                return "ABCDEFG"[:len(options)]
            elif "单选题" == category:
                return self._search(content, options, excludes)
            else:
                logger.debug("题目类型非法")
        else:
            if "填空题" == category:
                dest = re.findall(r'.{0,2}\s+.{0,2}', content)
                logger.debug(f'dest: {dest}')
                if 1 == len(dest):
                    dest = dest[0]
                    logger.debug(f'单处填空题可以尝试正则匹配')
                    pattern = re.sub(r'\s+', '(.{' + options + '}?)', dest)
                    logger.debug(f'匹配模式 {pattern}')
                    res = re.findall(pattern, tips)
                    if 1 == len(res):
                        return res[0]
                logger.debug(f'多处填空题难以预料结果，索性不处理')
                return None

            elif "多选题" == category:
                check_res = [letter for letter, option in zip(
                    letters, options) if option in tips]
                if len(check_res) > 1:
                    logger.debug(f'根据提示，可选项有: {check_res}')
                    return "".join(check_res)
                return "ABCDEFG"[:len(options)]
            elif "单选题" == category:
                radio_in_tips, radio_out_tips = "", ""
                for letter, option in zip(letters, options):
                    if len(option) > 0:  # 后加的
                        if option in tips:
                            logger.debug(f'{option} in tips')
                            logger.debug(f'{len(option)}')
                            radio_in_tips += letter
                        else:
                            logger.debug(f'{option} out tips')
                            logger.debug(f'{len(option)}')
                            radio_out_tips += letter

                logger.debug(f'含 {radio_in_tips} 不含 {radio_out_tips}')
                if 1 == len(radio_in_tips) and radio_in_tips not in excludes:
                    logger.debug(f'根据提示 {radio_in_tips}')
                    return radio_in_tips
                if 1 == len(radio_out_tips) and radio_out_tips not in excludes:
                    logger.debug(f'根据提示 {radio_out_tips}')
                    return radio_out_tips
                return self._search(content, options, excludes)
            else:
                logger.debug("题目类型非法")

    def _update_bank(self, item):  # 向题库增加新题
        if not self.bank or not self.bank["answer"]:
            self.query.put(item)

    # 订阅模块
    def _subscribe_init(self):
        """
        订阅初始化模块 +2
        """
        if self.app_args['testapp']:
            self.subscribe_times = 0
        else:
            self.subscribe_times, self.subscribe_total = self.score["订阅"]

    def _subscribe(self):
        """
        执行订阅模块 +2
        """
        logger.info(f'[{self.username}]开始执行订阅操作...')
        # 根据ini文件的提供已订阅页数，先直接翻页
        try:
            page = cfg.getint(
                'users', 'subscribed_pages_' + self.app_args['id'])
        except (NoOptionError, NoSectionError):
            page = 1
        if page == 0:
            return
        for num in range(page):
            self.swipe_up()
        sub_cat = re.split(r'[,，;；、/.\s]', cfg.get("prefers", "subscribed_category"))
        while self.subscribe_times < 2:
            # subscribe_titles = self.wait.until(EC.presence_of_all_elements_located(
            #     (By.XPATH, rules["subscribe_title"])))
            for cat in sub_cat:
                self.driver(text=cat).click_exists(3)
                subscribe_buttons = self.driver.xpath(rules["subscribe_subs_buttons"]).all()
                for subs_button in subscribe_buttons:
                    if subs_button.attrib["content-desc"] == '订阅':
                        subs_button.click()
                        self.subscribe_times += 1
                        time.sleep(1)
                        logger.info(
                            f'[{self.username}]\033[7;41m 在{page}页有订阅内容，完成第{self.subscribe_times}次订阅。\033[0m')
                    if self.subscribe_times == 2:
                        logger.info(
                            f'[{self.username}]\033[7;41m 已经执行【订阅】{self.subscribe_times}次，完成【订阅】。\033[0m')
                        return
                self.swipe_up()
                time.sleep(1)
                page += 1
                try:
                    if self.driver.xpath(rules["subscribe_list_endline"]).exists:
                        subscribe_buttons = self.driver.xpath(rules["subscribe_subs_buttons"]).all()
                        for subs_button in subscribe_buttons:
                            if subs_button.attrib["content-desc"] == '订阅':
                                subs_button.click()
                                self.subscribe_times += 1
                                logger.info(
                                    f'[{self.username}]\033[7;41m 在{page}页有订阅内容，完成第{self.subscribe_times}次订阅。\033[0m')
                            if self.subscribe_times == 2:
                                logger.info(
                                    f'[{self.username}]\033[7;41m 已经执行【订阅】{self.subscribe_times}次，完成【订阅】。\033[0m')
                                return
                        if self.subscribe_times < 2:
                            logger.info(
                                f'[{self.username}]在翻动{page}页到订阅页底部，今天完成了{self.subscribe_times}次订阅后，无可订阅的频道。')
                            return
                except XPathElementNotFoundError:
                    pass

    def subscribe(self):
        """
        订阅模块 +2
        """
        self._subscribe_init()
        if self.subscribe_times < 2:
            self.safe_click(rules["mine_entry"])
            self.safe_click(rules["subscribe_entry"])
            self.safe_click(rules["subscribe_add"])
            self._subscribe()
            self.back_to_home()

    # 专项答题
    def _special_answer_init(self):
        self.endofspecial = False
        g, t = self.score["专项答题"]
        if g > 0:
            self.endofspecial = True

    def _special_answer(self):
        """
        专项答题执行模块 +10
        """
        # titles = self.wait.until(
        #     EC.presence_of_all_elements_located((By.XPATH, rules["special_titles"])))
        is_end = True
        try:
            page = cfg.getint('prefers', 'special_answer_begin_page')
        except (NoOptionError, NoSectionError):
            page = 1
        try:
            special_count = cfg.getint('prefers', 'special_count_each_group')
        except (NoOptionError, NoSectionError):
            special_count = 10
        while is_end and page > 0:
            try:
                states = self.driver.xpath(rules["special_answer_entry"]).all()
                for state in states:
                    # if not first and title.location_in_view["y"]>0:
                    #     first = title
                    if self.size[1] - state.bounds[3] < 10:
                        logger.debug(f'[{self.username}]屏幕内没有未作答试卷')
                        break
                    if "开始答题" == state.text:
                        #  or "继续答题" == state.get_attribute(
                        #         "name") or "重新答题" == state.get_attribute("name"):
                        #  or "已满分" == state.get_attribute("name"):
                        logger.info(f'{state.text}！')
                        state.click()
                        time.sleep(random.uniform(1, 3))
                        self._dispatch(special_count)  # 这里直接采用每日答题
                        # self.safe_back('quit special answer')
                        is_end = False
                        break
                    elif ("继续答题" == state.text or "已满分" == state.text) and \
                            self.app_args['testapp']:
                        # elif "开始答题" == state.text and self.app_args['testapp']:
                        logger.info(
                            f'\033[7;41m[【专项答题】{state.text}！\033')
                        state.click()
                        time.sleep(random.uniform(1, 3))
                        self._dispatch(special_count)  # 这里直接采用每日答题
                        # self.safe_back('quit special answer')
                        is_end = False
                        break
                    elif "已过期" == state.text:
                        # self.safe_back('quit special answer')
                        is_end = False
                        # 如果发现已过期，说明以下的题组已经失效，翻页也没有用了，直接退出
                        page = 0
                        break
                # 如果该页没有可以答题的题组，翻页寻找
                self.swipe_up()
                page -= 1
                time.sleep(2)
            except XPathElementNotFoundError:
                logger.info(
                    f'\033[7;41m[{self.username}]没有可以学习的专项答题，可能所有题目组已经答完。\033')
                self.safe_back('special answer->special answer list')
                self.safe_back('special answer list -> quiz')
                return None
        self.safe_back('special answer->special answer list')
        self.safe_back('special answer list -> quiz')

    def special_answer(self):
        """
        专项答题模块 +10
        """
        # self._special_answer_init()

        if not self.is_workday() and self.app_args['testapp'] is False:
            return
        if self.app_args['testapp']:
            self.safe_click(rules["mine_entry"])
            self.safe_click(rules["quiz_entry"])
            try:
                self.driver.xpath(rules['quiz_updateinfo']).click_exists(0.5)
            except (XPathElementNotFoundError, XPathElementNotFoundError):
                pass
        else:
            g, t = self.score["专项答题"]
            if g == 0 or self.app_args['testapp']:
                self.safe_click(rules["mine_entry"])
                self.safe_click(rules["quiz_entry"])
                # 更新后会出现一个提示窗口，需要确定关闭掉
                try:
                    self.driver.xpath(rules['quiz_updateinfo']).click_exists(0.5)
                except (XPathElementNotFoundError, XPathElementNotFoundError):
                    pass
                # 翻过新更新的提示页面（三个按钮的xpath一样的）
            else:
                logger.info(
                    f'\033[7;41m [{self.username}]【专项答题】应完成{self.score["专项答题"][1]}分，'
                    + f'实际完成{self.score["专项答题"][0]}分，已经完成答题。\033[0m')
                return
        self.quiz_entry_warning()
        self.safe_click(rules["special_entry"])
        self._special_answer()
        self.back_to_home()

    # @pysnooper.snoop()
    def _simple_verify(self, content, options):
        """ 搜索单选题模块 """
        quiz_option = None
        if content != '':
            content = re.match(r'.*?\.(.*)', content).group(1).strip()
            content = content.strip('\r\n').replace(
                u'\u3000', u' ').replace(u'\xa0', u' ').strip()
            content = ' '.join(content.split())
        if options is not None:
            quiz_option = [re.match(r'.*?\.(.*)', x).group(1).strip() for x in options]
        letters = 'ABCD'
        answer = ''
        self.bank, result_count = self.query.get({
            "category": "单选题",
            "content": content,
            "options": quiz_option
        })
        if self.bank and self.bank["answer"]:
            logger.debug(
                f'[{self.username}]答案是: 【{self.bank["answer"]}】，题目是：{content}')
            answer = self.bank["answer"]
        elif self.bank is None:
            logger.debug(f'[{self.username}]准备更新题库,随机选个答案')
            answer = random.choice(letters[:len(options)])
            self._update_bank({
                "category": "单选题",
                "content": content,
                "options": quiz_option,
                "answer": answer,
                "excludes": "待验证",
                "notes": ""
            })
        return answer, result_count

    # 争上游答题
    def _who_first_init(self):
        """
        争上游答题初始化模块 +5
        """
        pass

    def is_finish_page(self, wf_begin_time, wf_end_time, module='争上游答题'):
        try:
            xpath = '//*[contains(@text,"获得胜利") or contains(@text,"挑战失败")]'
            result = self.driver.xpath(xpath).get_text().strip()
        except XPathElementNotFoundError:
            logger.debug(f'\033[7;41m还没到结束答题页面\033[0m')
            return None
        else:
            if '获得胜利！' == result:
                win_times, loss_times = self.query.update_answer_record(
                    [f'user{self.app_args["id"]}', f'{datetime.date.today()}', module, 1, 0])
            else:
                win_times, loss_times = self.query.update_answer_record(
                    [f'user{self.app_args["id"]}', f'{datetime.date.today()}', module, 0, 1])
            logger.info(
                f'\033[7;41m [{self.username}]本次{module}答题总计耗时：{wf_end_time - wf_begin_time}。' +
                f'【本次{result}】 今天完成【{module}】' +
                f' 共计{win_times + loss_times}次，获得{win_times}次胜利，失利{loss_times}次。\033[0m')
            return True

    # @pysnooper.snoop()
    def _who_first(self, module_name):
        """
            争上游答题执行模块 +5
        """
        time.sleep(random.uniform(7.5, 8.5))
        wf_begin_time = datetime.datetime.now()
        wf_end_time = datetime.datetime.now()
        quiz_num = 1
        while quiz_num < 6:
            try:
                if self.driver(textStartsWith=f'{quiz_num}. ').wait(5):
                    content = self.driver(textStartsWith=f'{quiz_num}. ').get_text()
                else:
                    continue
                options = None
                answer, result_count = self._simple_verify(content, options)
                if result_count == 1:
                    choose_index = ord(answer) - 65
                    x, y = self.driver(className='android.widget.RadioButton')[choose_index].center()
                    # time.sleep(random.uniform(0.01, 0))
                    for _ in range(5):
                        self.driver.click(x, y)
                        # time.sleep(random.uniform(0.01, 0))
                    # self.driver(className='android.widget.RadioButton')[choose_index].click()
                    wf_end_time = datetime.datetime.now()
                    quiz_num += 1
                    logger.info(f'\033[7;41m 【答案】{answer}\033[0m')
                else:
                    option_elements = self.driver.xpath(rules["who_first_options"]).all()
                    options = [x.text for x in option_elements]
                    answer, result_count = self._simple_verify(content, options)
                    choose_index = ord(answer) - 65
                    # self.driver(className='android.widget.RadioButton')[choose_index].click()
                    x, y = option_elements[choose_index].center()
                    # time.sleep(random.uniform(0.01, 0))
                    for _ in range(5):
                        self.driver.click(x, y)
                        # time.sleep(random.uniform(0.01, 0))
                    wf_end_time = datetime.datetime.now()
                    logger.info(f'\033[7;41m 【2.答案】{answer}\033[0m')
                    quiz_num += 1
            except (AttributeError, IndexError, UiObjectNotFoundError, XPathElementNotFoundError) as msg:
                logger.info(f'异常信息：{msg}')
                self.driver.watcher.when('游戏开始超时！').click()
                dur_time = datetime.datetime.now() - wf_begin_time
                if dur_time.seconds > 30:
                    if self.is_finish_page(wf_begin_time, wf_end_time, module_name):
                        logger.info(f'\033[7;41m 第一层返回\033[0m')
                        return
        if self.is_finish_page(wf_begin_time, wf_end_time, module_name):
            logger.info(f'\033[7;41m 第一层返回\033[0m')
            return

    def who_first(self):
        """
        争上游答题模块 +5
        """
        if self.app_args['testapp']:
            run_times = cfg.getint('test', 'app_who_first')
        else:
            g, t = self.score["争上游答题"]
            if g == 0:
                run_times = cfg.getint('prefers', 'who_first_times')
            elif g > 3 or self.who_first_finished:
                return
            else:
                run_times = cfg.getint('prefers', 'who_first_times') - 1
        self._who_first_init()
        self.safe_click(rules["mine_entry"])
        self.safe_click(rules["quiz_entry"])
        # 更新后会出现一个提示窗口，需要确定关闭掉
        self.driver.xpath(rules['quiz_updateinfo']).click_exists(2)
        # 翻过新更新的提示页面（三个按钮的xpath一样的）
        self.quiz_entry_warning()
        self.safe_click(rules["who_first_entry"])
        for num in range(run_times):
            time.sleep(random.uniform(0.75, 1.15))
            logger.info(
                f'\033[7;30;43m[{self.username}]今天进行【争上游答题】{run_times}次，现在开始第{num + 1}次争上游答题。\033[0m')
            self.safe_click(rules["who_first_begin"])
            try:
                if self.driver.xpath(rules['who_first_times_exceeded']).exists:
                    self.driver.xpath(rules['who_first_know']).click_exists(0.5)
                    self.who_first_finished = True
                    logger.info(f'\033[7;30;43m【争上游答题】已超过今日对战次数，请明日再来。\033[0m')
                    win_times, loss_times = self.query.update_answer_record(
                        [f'user{self.app_args["id"]}', f'{datetime.date.today()}', '争上游答题', 0, 0])
                    logger.info(f'[{self.username}]\033[7;41m 今天已经完成【争上游答题】' +
                                f' 共计{win_times + loss_times}次，获得{win_times}次胜利，失利{loss_times}次。\033[0m')
                    self.back_to_home()
                    return
                else:
                    logger.info(f'\033[7;30;43m[{self.username}]进入【争上游答题】\033[0m')
                    self._who_first('争上游答题')
                    if self.driver.xpath(rules['who_first_no_point']).exists and not self.app_args['testapp']:
                        self.who_first_finished = True
                        break
                self.driver.xpath(rules['who_first_retry']).click_exists(1)
            except XPathElementNotFoundError:
                pass
        self.back_to_home()
        pass  # 调试用

    # 双人对战1v1
    def _one_vs_one_init(self):
        """
        双人对战答题初始化模块 +2
        """
        pass

    @pysnooper.snoop()
    def _one_vs_one(self):
        """
        双人对战答题执行模块 +2
        双人对战因为对手是机器人
        所以对答题时间没有太迫切的要求
        """
        time.sleep(random.uniform(5))
        for _ in range(20):
            self.driver.click(100, 100)
            time.sleep(0.1)
        wf_begin_time = datetime.datetime.now()
        wf_end_time = datetime.datetime.now()
        while True:
            try:
                content = self.driver.xpath(rules["who_first_content"]).wait(10).text
                opt_eles = self.driver.xpath('//android.widget.RadioButton').all()
                options = None
                answer, result_count = self._simple_verify(content, options)
                if result_count == 1:
                    logger.info(f'\033[7;41m 【答案】{answer}\033[0m')
                    choose_index = ord(answer[0]) - 65
                    # xpath = f'//android.widget.ListView/android.view.View[{choose_index}]'
                    # option = self.driver(xpath).wait(5).all()
                    # x, y = option.center()
                    x, y = opt_eles[choose_index].center()
                    wf_end_time = datetime.datetime.now()
                    for _ in range(10):
                        self.driver.click(x, y)
                        time.sleep(0.01)
                        # self.driver.click(x, y)
                else:
                    option_elements = self.driver.xpath(rules["who_first_options"]).all()
                    options = [x.text for x in option_elements]
                    answer, result_count = self._simple_verify(content, options)
                    logger.info(f'\033[7;41m 【2.答案】{answer}\033[0m')
                    choose_index = ord(answer[0]) - 65
                    # answer_text = options[choose_index]
                    x, y = option_elements[choose_index].center()
                    wf_end_time = datetime.datetime.now()
                    wf_end_time = datetime.datetime.now()
                    for _ in range(10):
                        self.driver.click(x, y)
                        time.sleep(0.01)
            except Exception as msg:
                logger.info(f'异常信息：{msg}')
                self.driver.watcher.when('游戏开始超时！').click()
                self.driver.watcher.run()
                dur_time = datetime.datetime.now() - wf_begin_time
                if dur_time.seconds > 30:
                    if self.is_finish_page(wf_begin_time, wf_end_time, '双人对战'):
                        logger.info(f'\033[7;41m 第一层返回\033[0m')
                        self.driver.watcher.stop()
                        self.driver.watcher.remove()
                        return
                continue

    def one_vs_one(self):
        """
        双人对战答题模块 +2
        有异常情况：房间人数不足，快来邀请好友参加吧  知道了
        """
        run_times = 1
        if self.app_args['testapp'] is False:
            g, t = self.score["双人对战"]
            if g == t:
                return
            if self.one_vs_one_finished:
                return
        else:
            run_times = cfg.getint('test', 'app_one_vs_one')
        try:
            self._who_first_init()
            self.safe_click(rules["mine_entry"])
            self.safe_click(rules["quiz_entry"])
            # 更新后会出现一个提示窗口，需要确定关闭掉
            self.driver.xpath(rules['quiz_updateinfo']).click_exists(2)
            # 翻过新更新的提示页面（三个按钮的xpath一样的）
            self.quiz_entry_warning()
            for _ in range(run_times):
                self.driver(text='继续挑战').click_exists(3)
                self.safe_click(rules["1v1_entry"])
                self.safe_click(rules["1v1_invite_entry"])
                self.safe_click(rules["1v1_begin"])
                if self.driver.xpath(rules['who_first_times_exceeded']).wait(0.5):
                    self.driver.xpath('//*[@text="知道了"]').click_exists(2)
                    logger.info(f'\033[7;30;43m【争上游答题】已超过今日对战次数，请明日再来。\033[0m')
                    win_times, loss_times = self.query.update_answer_record(
                        [f'user{self.app_args["id"]}', f'{datetime.date.today()}', '双人对战', 0, 0])
                    logger.info(f'[{self.username}]\033[7;41m 今天已经完成【双人对战】' +
                                f' 共计{win_times + loss_times}次，获得{win_times}次胜利，失利{loss_times}次。\033[0m')
                    self.back_to_home()
                    return
                else:
                    self.driver.xpath('//*[@text="知道了"]').click_exists(0.5)
                    logger.info(
                        f'\033[7;30;43m[{self.username}]现在进行【双人对战】。\033[0m')
                    self._who_first('双人对战')
                    # self._one_vs_one()
            self.safe_back('1v1_answer->1v1_page')
            self.safe_back('1v1_page->quiz')
            self.safe_click(rules['1v1_exit'])
            self.back_to_home()
            return
        except XPathElementNotFoundError:
            logger.info('双人对战找不到相应的按钮！')
            pass

    # 挑战答题模块
    # class Challenge(App):
    def _challenge_init(self):
        """
        挑战答题初始化模块 +5
        """
        # super().__init__()
        self.challenge_delay_bot = cfg.getint('prefers', 'challenge_delay_min')
        self.challenge_delay_top = cfg.getint('prefers', 'challenge_delay_max')
        try:
            if self.app_args['testapp']:
                self.challenge_count = cfg.getint('test', 'app_challenge')
                return
            else:
                self.challenge_count = cfg.getint('prefers', 'challenge_count')
        except (NoOptionError, NoSectionError):
            pass
        g, t = self.score["挑战答题"]
        if t == g:
            self.challenge_count = 0
        else:
            self.challenge_count = random.randint(
                cfg.getint('prefers', 'challenge_count_min'),
                cfg.getint('prefers', 'challenge_count_max'))

    def _challenge_cycle(self, num):
        """
        挑战答题循环执行模块 +6
        """
        self.safe_click(rules['challenge_entry'])
        offset = 0  # 自动答错的偏移开关
        total = num
        while num > -1:
            try:
                content = self.driver.xpath(rules['challenge_content']).get_text()
                option_elements = self.driver.xpath(rules['challenge_options']).all()
                options = [x.text for x in option_elements]
                length_of_options = len(options)
                logger.info(
                    f'[{self.username}]共{self.challenge_count}题，第<{total - num + 1}>题，题目是：{content}')
                logger.info(
                    f'[{self.username}]共{self.challenge_count}题，第<{total - num + 1}>题，答案是：{options}')
                answer = self._verify(
                    category='单选题', content=content, options=options)
                delay_time = random.randint(self.challenge_delay_bot, self.challenge_delay_top)
                if 0 == num:
                    offset = random.randint(1, length_of_options)
                    logger.info(
                        f'[{self.username}]//**//已完成指定题量，设置提交选项偏移 -{offset}')
                    logger.info(
                        f'[{self.username}]<{total - num + 1}>随机延时 {delay_time} 秒提交答案: {answer}-{offset}')
                    logger.info(
                        f'[{self.username}]' + '--------------------------------------------------------------------\n')
                    # 利用python切片的特性，即使索引值为-offset，可以正确取值
                    option_elements[ord(answer) - 65 - offset].click()
                    time.sleep(delay_time)
                    if self.driver.xpath(rules['challenge_end']).click_exists(1):
                        break
                    else:
                        continue
                else:
                    logger.info(
                        f'[{self.username}]<{total - num + 1}>随机延时 {delay_time} 秒提交答案: {answer}')
                    logger.info(
                        f'[{self.username}]' + '--------------------------------------------------------------------\n')
                # 利用python切片的特性，即使索引值为-offset，可以正确取值
                option_elements[ord(answer) - 65 - offset].click()
                time.sleep(delay_time)
                if self.driver.xpath(rules['challenge_revival']).click_exists(1):
                    logger.info(f'[{self.username}]很遗憾本题回答错误')
                    logger.info(
                        f'[{self.username}]\033[7;31;43m 回答错误题目是：{content},错误答案是：{answer}\033[0m')
                    self._update_bank({
                        "category": "单选题",
                        "content": content,
                        "options": options,
                        "answer": "",
                        "excludes": answer,
                        "notes": ""
                    })
                    break
                else:
                    logger.debug(f'[{self.username}]恭喜本题回答正确')
                    num -= 1
                    self._update_bank({
                        "category": "单选题",
                        "content": content,
                        "options": options,
                        "answer": answer,
                        "excludes": "",
                        "notes": ""
                    })
            except XPathElementNotFoundError:
                return num
        self.safe_back('challenge -> share_page')
        try:
            self.driver.xpath(rules['challenge_save_exit']).click_exists(3)
            logger.debug(f'不保存退出')
        except XPathElementNotFoundError:
            logger.debug(f'没有出现挑战答题保存界面')
        time.sleep(2)
        self.safe_back('share_page -> quiz')
        return num

    def _challenge(self):
        """
        挑战答题执行模块 +6
        """
        logger.info(
            f'[{self.username}]\033[7;41m 【挑战答题】目标 {self.challenge_count} 题, Go!\033[0m')
        while True:
            result = self._challenge_cycle(self.challenge_count)
            if 0 >= result:
                logger.info(f'延时5秒')
                logger.info(f'已成功挑战 {self.challenge_count} 题，正在返回')
                logger.info(
                    f'\033[7;41m [{self.username}]【挑战答题】 积分已达成，无需重复获取积分。\033[0m')
                break
            else:
                delay_time = random.randint(5, 10)
                logger.info(
                    f'[{self.username}]本次挑战 {self.challenge_count - result} 题，{delay_time} 秒后再来一组')
                time.sleep(delay_time)
                continue

    def challenge(self):
        """
        挑战答题模块 +6
        """
        # if self.app_args['testapp']:
        #     self.challenge_count = random.randint(
        #         cfg.getint('prefers', 'challenge_count_min'),
        #         cfg.getint('prefers', 'challenge_count_max'))
        self._challenge_init()
        if 0 == self.challenge_count:
            logger.info(
                f'\033[7;41m [{self.username}]【挑战答题】 积分已达成，无需重复挑战。\033[0m')
            return
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        # 更新后会出现一个提示窗口，需要确定关闭掉
        try:
            self.driver.xpath(rules['quiz_updateinfo']).click_exists(0.5)
        except (XPathElementNotFoundError, XPathElementNotFoundError):
            pass
        # 处理新更新的提示页面三个按钮的xpath一样的
        self.quiz_entry_warning()
        time.sleep(3)
        self._challenge()
        # 这个地方经常会出现问题
        self.back_to_home()

    # 每日答题模块
    # class Daily(App):

    def _daily_init(self):
        """
        每日答题初始化模块 +5
        """
        # super().__init__()
        # self.g, self.t = 0, 6
        # self.count_of_each_group = cfg.getint(
        #     'prefers', 'daily_count_each_group')
        try:
            self.daily_count = cfg.getint('prefers', 'daily_count_each_group')
            self.daily_force = self.daily_count > 0
        except (NoOptionError, NoSectionError):
            logger.info(
                f'[{self.username}]请在default.ini文件中配置“每日答题”每组答题数目（daily_count_each_group值）。')
            # self.g, self.t = self.score["每日答题"]
            # self.daily_count = self.t - self.g
            # self.daily_force = False
        self.daily_delay_bot = cfg.getint('prefers', 'daily_delay_min')
        self.daily_delay_top = cfg.getint('prefers', 'daily_delay_max')
        self.delay_group_bot = cfg.getint('prefers', 'daily_group_delay_min')
        self.delay_group_top = cfg.getint('prefers', 'daily_group_delay_max')

    def _submit(self, delay=None):
        if not delay:
            delay = random.randint(self.daily_delay_bot, self.daily_delay_top)
            logger.info(f'随机延时 {delay} 秒...')
        time.sleep(delay)
        self.safe_click(rules["daily_submit"])
        # time.sleep(random.randint(1, 3))

    def _view_tips(self):
        """
        答题提示处理模块
        根据答题提示做相应的处理
        """
        # content = ""
        if self.driver.xpath(rules["daily_tips_open"]).exists:
            self.driver.xpath(rules["daily_tips_open"]).click_exists(3)
        else:
            logger.debug("没有可点击的【查看提示】按钮")
            return ""
        time.sleep(2)
        if self.driver.xpath(rules["daily_tips"]).exists:
            content = self.driver.xpath(rules["daily_tips"]).get_text()
            logger.debug(f'提示 {content}')
        else:
            logger.error(f'无法查看提示内容')
            return ""
        time.sleep(2)
        try:
            self.driver.xpath(rules["daily_tips_close"]).click_exists(3)
        except XPathElementNotFoundError:
            logger.debug("没有可点击的【X】按钮")
        time.sleep(2)
        return content

    def _blank(self):
        """
        填空题答题模块
        """
        length_of_spaces = 0
        contents = self.driver.xpath(rules["daily_blank_content"]).all()
        # contents = self.find_elements(rules["daily_blank_content"])
        # content = " ".join([x.get_attribute("name") for x in contents])
        logger.debug(f'len of blank contents is {len(contents)}')
        if 1 < len(contents):
            # 针对作妖的UI布局某一版
            # 题干会分成几段显示在几个android.view.View里面
            content, spaces = "", []
            for item in contents:
                content_text = item.text
                if "" != content_text:
                    content += content_text
                else:
                    length_of_spaces = len(self.driver.xpath('//android.widget.EditText/following-sibling::*').all())
                    # print(f'空格数 {length_of_spaces}')
                    spaces.append(length_of_spaces)
                    content += " " * length_of_spaces

        else:
            # 针对作妖的UI布局某一版
            contents = self.driver.xpath(rules["daily_blank_container"]).all()
            content, spaces, _spaces = "", [], 0
            for item in contents:
                content_text = item.text
                if "" != content_text:
                    content += content_text
                    if _spaces:
                        spaces.append(_spaces)
                        _spaces = 0
                else:
                    content += " "
                    _spaces += 1
            else:  # for...else...
                # 如果填空处在最后，需要加一个判断
                if _spaces:
                    spaces.append(_spaces)
                logger.debug(
                    f'[填空题] {content} [{" ".join([str(x) for x in spaces])}]')

        blank_edits = self.driver.xpath(rules["daily_blank_edits"]).all()
        # blank_edits = self.find_elements(rules["daily_blank_edits"])
        length_of_edits = len(blank_edits)
        logger.info(f'填空题 {content}')
        # 把空格数量当做option传入_verify里面
        # 原语句是 answer = self._verify("填空题", content, "")
        answer = self._verify("填空题", content, str(length_of_spaces))
        if not answer:
            # words = (''.join(random.sample(string.ascii_letters + string.digits, 8))
            #          for num in range(length_of_edits))
            words = (''.join(random.sample(string.ascii_letters + string.digits, length_of_edits)))
        else:
            words = answer.split(" ")
        logger.debug(f'提交答案 {words}')
        logger.debug(f'[{self.username}]\033[7;41m 填空题答案是：{words}\033[0m')
        for k, v in zip(range(length_of_edits), words):
            self.driver(className='android.widget.EditText')[(k - 1)].set_text(v)
            time.sleep(1)
        self._submit()
        time.sleep(1)
        try:
            if self.driver.xpath(rules["daily_wrong_or_not"]).exists:
                right_answer = self.driver.xpath(rules["daily_answer"]).get_text()
                answer = re.sub(r'正确答案： ', '', right_answer)
                logger.info(f"答案 {answer}")
                notes = self.driver.xpath(rules["daily_notes"]).get_text()
                logger.debug(f"解析 {notes}")
                self._submit(2)
                if 1 == length_of_edits:
                    self._update_bank({
                        "category": "填空题",
                        "content": content,
                        "options": [""],
                        "answer": answer,
                        "excludes": "",
                        "notes": notes
                    })
                else:
                    logger.error("多位置的填空题待验证正确性")
                    self._update_bank({
                        "category": "填空题",
                        "content": content,
                        "options": [""],
                        "answer": self._blank_answer_divide(answer, spaces),
                        "excludes": "",
                        "notes": notes
                    })
            else:
                logger.info("填空题回答正确")
        except (UiObjectNotFoundError, XPathElementNotFoundError) as msg:
            logger.info(f'【多选题】出错信息：{msg}')

    def _radio(self):
        """
        单选题答题模块
        """
        content = self.driver.xpath(rules["daily_content"]).wait(10).text
        # content = self.find_element(rules["daily_content"]).get_attribute("name")
        option_elements = self.driver.xpath(rules["daily_options"]).all()
        # option_elements = self.driver.find_elements(rules["daily_options"])
        options = [x.text for x in option_elements]
        # length_of_options = len(options)
        logger.info(f"单选题 {content}")
        logger.info(f"选项 {options}")
        answer = self._verify("单选题", content, options)
        choose_index = ord(answer) - 65
        logger.info(f"提交答案 {answer}")
        option_elements[choose_index].click()
        # 提交答案
        self._submit()
        try:
            if self.driver.xpath(rules["daily_wrong_or_not"]).exists:
                right_answer = self.driver.xpath(rules["daily_answer"]).get_text()
                right_answer = re.sub(r'正确答案： ', '', right_answer)
                logger.info(f"答案 {right_answer}")
                self._submit(2)
                self._update_bank({
                    "category": "单选题",
                    "content": content,
                    "options": options,
                    "answer": right_answer,
                    "excludes": "",
                    "notes": ""
                })
            else:
                self._update_bank({
                    "category": "单选题",
                    "content": content,
                    "options": options,
                    "answer": answer,
                    "excludes": "",
                    "notes": ""
                })
        except (UiObjectNotFoundError, XPathElementNotFoundError) as msg:
            logger.info(f'【单选题】出错信息：{msg}')

    def _check(self):
        """
        多选题答题处理模块
        """
        content = self.driver.xpath(rules["daily_content"]).wait(10).text
        # content = self.find_element(rules["daily_content"]).get_attribute("name")
        option_elements = self.driver.xpath(rules["daily_options"]).all()
        # option_elements = self.driver.find_elements(rules["daily_options"])
        options = [x.text for x in option_elements]
        # length_of_options = len(options)
        logger.info(f"多选题 {content}\n{options}")
        answer = self._verify("多选题", content, options)
        logger.debug(f'[{self.username}]提交答案 {answer}')
        for k, option in zip(list("ABCDEFG"), option_elements):
            if k in answer:
                option.click()
                time.sleep(1)
            else:
                continue
        # 提交答案
        self._submit()
        try:
            if self.driver.xpath(rules["daily_wrong_or_not"]).exists:
                right_answer = self.driver.xpath(rules["daily_answer"]).wait(3).text
                right_answer = re.sub(r'正确答案： ', '', right_answer)
                logger.info(f"答案 {right_answer}")
                # notes = self.driver.xpath(rules["daily_notes"]).get_attribute("name")
                # logger.debug(f"解析 {notes}")
                self._submit(2)
                self._update_bank({
                    "category": "多选题",
                    "content": content,
                    "options": options,
                    "answer": right_answer,
                    "excludes": "",
                    "notes": ""
                })
            else:
                self._update_bank({
                    "category": "多选题",
                    "content": content,
                    "options": options,
                    "answer": answer,
                    "excludes": "",
                    "notes": ""
                })
        except (UiObjectNotFoundError, XPathElementNotFoundError) as msg:
            logger.info(f'【多选题】出错信息：{msg}')

    def _dispatch(self, count_of_each_group):
        """
        答题类型分派模块
        根据题目类型分配到相应的处理模块
        """
        for num in range(count_of_each_group):
            category = None
            logger.debug(
                f'[{self.username}]每日答题 第 {count_of_each_group - 1 - num} 题')
            try:
                category = self.driver.xpath(rules["daily_category"]).wait(10).text
            except XPathElementNotFoundError:
                logger.error(f'[{self.username}]无法获取题目类型')
            if "填空题" == category[0:3]:
                self._blank()
            elif "单选题" == category[0:3]:
                self._radio()
            elif "多选题" == category[0:3]:
                self._check()
            else:
                logger.error(f"未知的题目类型: {category}")
            time.sleep(2)

    def _daily(self, num):
        """
        每日答题执行模块 +5
        """
        self.safe_click(rules["daily_entry"])
        while True:
            logger.info(
                f'[{self.username}]\033[7;37;45m 每日答题开始！\033[0m')
            self._dispatch(num)
            # if self.driver.xpath('//*[@text="book@2x.432e6b57"]').exists:
            #     logger.info(f"今日答题已完成，返回")
            try:
                accuracy_text = self.driver.xpath(rules["daily_accuracy"]).wait(10).text
                if accuracy_text == "正确率：100%":
                    break
                delay = random.randint(self.delay_group_bot, self.delay_group_top)
                logger.info(f'每日答题未完成 {delay} 秒后再来一组')
                time.sleep(delay)
                self.safe_click(rules['daily_again'])
            except Exception as msg:
                logger.info(f"今日答题出错{msg}")
                return

    # @pysnooper.snoop()
    def daily(self):
        """
        每日答题模块 +5
        """
        run_times = 1
        if self.app_args['testapp']:
            run_times = cfg.getint('test', 'app_daily')
            self.daily_count = 5
        elif self.score["每日答题"][0] == self.score["每日答题"][1] and self.app_args['testapp'] is False:
            logger.info(
                f'[{self.username}]\033[7;41m 【每日答题】 积分已达成，无需重复答题。\033[0m')
            return
        self.safe_click(rules['mine_entry'])
        time.sleep(2)
        self.safe_click(rules['quiz_entry'])
        # 更新后会出现一个提示窗口，需要确定关闭掉
        try:
            self.driver.xpath(rules['quiz_updateinfo']).click_exists(0.5)
        except (XPathElementNotFoundError, XPathElementNotFoundError):
            pass
        # 处理新更新的有个提示页面，提示页面三个按钮的xpath一样的
        self.quiz_entry_warning()
        time.sleep(3)
        for num in range(run_times):
            logger.info(
                f'[{self.username}]\033[7;41m 【每日答题】 第{num + 1}组开始。\033[0m')
            self._daily(self.daily_count)
            self.driver(text='再来一组').click_exists(3)
        self.safe_back('daily -> quiz')
        self.driver.xpath(rules["daily_back_confirm"]).click_exists(2)
        self.back_to_home()

    # 我要选读文章模块 阅读文章
    # class Read(App):
    def _read_init(self):
        """
        我要选读文章初始化模块
        """
        # super().__init__()
        # self.read_time = 360
        self.read_time = cfg.getint("prefers", "article_read_time")
        self.read_count = random.randint(
            cfg.getint('prefers', 'article_count_min'),
            cfg.getint('prefers', 'article_count_max'))
        self.read_delay = self.read_time // self.read_count
        # 2020.9 月更新后，计分调整，学习时长减少
        # self.read_time = 720 原先是720
        # self.volume_title = cfg.get("prefers", "article_volume_title")
        # 新闻学习栏目,逗号分隔，随机挑选栏目进行学习
        self.titles = list()
        self.volume_title = random.choice(
            re.split(r'[,，;；、/.\s]', cfg.get("prefers", "article_volume_title")))
        logger.info(f'准备进入[{self.username}]\033[7;41m 【{self.volume_title}】进行学习\033[0m')
        if self.app_args['testapp']:
            self.read_count = cfg.getint('test', 'app_read')
            self.star_share_comments_count = cfg.getint('prefers', 'star_share_comments_count')
            self.read_delay = 30
            return
        g, t = self.score["我要选读文章"]
        if t == g:
            self.read_count = 0
        elif g != 0:
            self.read_count = math.ceil((t - g) / t * random.randint(
                cfg.getint('prefers', 'article_count_min'),
                cfg.getint('prefers', 'article_count_max')))
        if self.score["发表观点"][0] == 0 or self.score["分享"][0] == 0:
            self.star_share_comments_count = cfg.getint(
                'prefers', 'star_share_comments_count')
            # 如果选读文章完成，而订阅和评论没完成，加读一次完成订阅和评论
            if self.read_count == 0:
                self.read_count = 1
        else:
            self.star_share_comments_count = 0

    def _star_once(self):
        """
        收藏
        """
        if self.back_or_not("收藏") and self.app_args['testapp'] is False:
            return
        logger.debug(f'[{self.username}]这篇文章真是妙笔生花呀！收藏啦！')
        self.safe_click(rules['article_stars'])
        # self.safe_click(rules['article_stars']) # 取消收藏

    def _comments_once(self, title="好好学习，天天强国"):
        """
        发表评论模块
        """
        # return # 拒绝留言
        if self.back_or_not("发表观点") and self.app_args['testapp'] is False:
            return
        logger.debug(f'[{self.username}]哇塞，这么精彩的文章必须留个言再走！')
        self.safe_click(rules['article_comments'])
        time.sleep(1)
        edit_area = self.driver.xpath(rules['article_comments_edit'])
        # edit_area = self.find_element(rules['article_comments_edit'])
        edit_area.set_text(title)
        time.sleep(1)
        self.safe_click(rules['article_comments_publish'])
        time.sleep(1)
        self.safe_click(rules['article_comments_list'])
        self.safe_click(rules['article_comments_delete'])
        self.safe_click(rules['article_comments_delete_confirm'])

    def _share_once(self):
        """
        分享模块
        """
        if self.back_or_not("分享") and self.app_args['testapp'] is False:
            return
        logger.debug(f'[{self.username}]好东西必须和好基友分享，走起，转起！')
        self.safe_click(rules['article_share'])
        self.safe_click(rules['article_share_xuexi'])
        time.sleep(1)
        self.safe_back('share -> article')

    def _star_share_comments(self, title):
        """
        发表观点和收藏执行模块
        发布一次观点
        收藏两次
        """
        # 2020年9月更新，收藏不加分了，所以全部注释屏蔽了
        logger.info(f'[{self.username}]哟哟，切克闹，收藏转发来一套')
        self._share_once()
        self._comments_once(title)
        self._share_once()

    def _read(self, num, ssc_count):
        """
        新闻阅读模块 +6
        """
        logger.info(f'[{self.username}]预计阅读新闻{num}则')
        time.sleep(3)
        while num > 0:  # or ssc_count:
            while True:
                articles = self.driver.xpath(rules["article_list1"]).all()
                break
            for article in articles:
                title = article.text
                if title in self.titles:
                    continue
                if article.parent().info['resourceName'] == "cn.xuexi.android:id/st_feeds_card_mask_pic_num":
                    logger.debug(f'这绝对是摄影集，直接下一篇')
                    continue
                article.click()
                num -= 1
                logger.info(f'[{self.username}]<{num + 1}> {title}')
                article_delay = random.randint(
                    self.read_delay, self.read_delay + min(10, self.read_count))
                # 如果测试，设置就看3秒
                # if self.app_args['testapp']:
                #     article_delay = 3
                logger.info(f'[{self.username}]阅读时间估计 {article_delay} 秒...')
                pbar = tqdm(
                    total=article_delay, bar_format='{l_bar}|{bar}| 已读{n_fmt}秒/总计需阅读{total_fmt}秒', nrows=10, ncols=50,
                    smoothing=0.1)
                while article_delay > 0:
                    if article_delay < 20:
                        delay = article_delay
                    else:
                        delay = random.randint(
                            min(3, article_delay), min(5, article_delay))
                    for sec in range(delay):
                        time.sleep(1)
                        pbar.update(1)
                    # time.sleep(delay)
                    logger.debug(f'延时 {delay} 秒...')
                    article_delay -= delay
                    self.swipe_up()
                    # time.sleep(1)
                else:
                    logger.debug(f'[{self.username}]完成阅读 {title}')
                pbar.close()
                if ssc_count > 0:
                    try:
                        self.driver.xpath(rules['article_comments'])
                        self._star_share_comments(title)
                        ssc_count -= 1
                    except XPathElementNotFoundError:
                        logger.debug('[{self.username}]这是一篇关闭评论的文章，收藏分享留言过程出现错误')
                self.titles.append(title)
                self.safe_back('article -> list')
                time.sleep(0.5)
                if 0 >= num:
                    break
            else:
                self.swipe_up()
                time.sleep(1)

    def kaleidoscope(self):
        """
        本地频道积分 +1
        """
        volumes = None
        if self.app_args['testapp']:
            delay = random.randint(5, 15)
        elif self.back_or_not("本地频道"):
            return
        else:
            delay = random.randint(5, 15)
        try:
            self.driver.xpath('//android.widget.TextView[@text="推荐"]').click_exists(0.5)
            if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
                volumes = self.driver.xpath(rules['xy_article_volume']).all()
            elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
                volumes = self.driver.xpath(rules['nox_article_volume']).all()
            elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
                volumes = self.driver.xpath(rules['nox_article_volume']).all()
            volumes[3].click()
            self.driver(className="android.widget.TextView",
                        resourceId="cn.xuexi.android:id/confirm_button").click_exists(0.5)
        except (XPathElementNotFoundError, IndexError):
            pass
        # time.sleep(5)
        # self.safe_click(rules['article_kaleidoscope'])
        self.back_to_home()
        try:
            target = self.driver.xpath(rules['article_kaleidoscope'])
            if target:
                target.click()
                logger.info(f"[{self.username}]在本地学习平台驻足 {delay} 秒")
                pbar = tqdm(
                    total=delay, bar_format='{l_bar}|{bar}| 驻足{n_fmt}秒/总计{total_fmt}秒 ', nrows=10, ncols=50,
                    smoothing=0.1)
                for sec in range(delay):
                    time.sleep(1)
                    pbar.update(1)
                pbar.close()
        except XPathElementNotFoundError:
            logger.error(f'[{self.username}]没有找到城市万花筒入口')
            return

    def scroll_find_volume(self, title: str):
        vol_found = False
        volumes = None
        xpath = ''
        if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
            xpath = '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[' \
                    '1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.view.ViewGroup[1] '
        elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
            xpath = '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[' \
                    '1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.view.View[1] '
        elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
            xpath = '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[' \
                    '1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.view.View[1] '
        bound = self.driver.xpath(xpath).info['bounds']
        # // android.widget.FrameLayout[1] / android.widget.LinearLayout[1] / android.widget.FrameLayout[1] / \
        #    android.widget.LinearLayout[1] / android.widget.FrameLayout[1] / android.widget.LinearLayout[1] / \
        #    android.widget.FrameLayout[1] / android.widget.RelativeLayout[1] / android.widget.LinearLayout[1] / \
        #    android.widget.FrameLayout[2] / android.widget.FrameLayout[1] / android.support.v4.view.ViewPager[1] / \
        #    android.widget.FrameLayout[1] / android.widget.LinearLayout[1] / android.widget.LinearLayout[1] / \
        #    android.view.View[1]
        x1 = bound['left']
        x2 = bound['right']
        y1 = bound['top']
        y2 = bound['bottom']
        # 先向右滑动到最左边的“推荐”版块
        while True:
            # if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
            #     volumes = self.driver.xpath(rules['xy_article_volume']).all()
            # elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
            #     volumes = self.driver.xpath(rules['nox_article_volume']).all()
            # for vol in volumes:
            #     if '推荐' == vol.text:
            #         vol_found = True
            #         break
            # if vol_found:
            #     vol_found = False
            #     break
            if self.driver.xpath('//android.widget.TextView[@text="推荐"]').click_exists(0.5):
                break
            else:
                self.driver.swipe_ext("right", box=(x1, y1, x2, y2), scale=0.65)

        while True:
            if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
                volumes = self.driver.xpath(rules['xy_article_volume']).all()
            elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
                volumes = self.driver.xpath(rules['nox_article_volume']).all()
            elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
                volumes = self.driver.xpath(rules['nox_article_volume']).all()
            for vol in volumes:
                if vol.text == title:
                    vol.click()
                    time.sleep(2)
                    # 多点home按钮，确保刷新
                    self.home_button_click()
                    vol_found = True
                    break
            if vol_found:
                break
            else:
                self.driver.swipe_ext("left", box=(x1, y1, x2, y2), scale=0.65)
        pass

    def read(self):
        """
        新闻阅读执行模块 +6
        """
        # volumes = None
        self._read_init()
        if self.read_count <= 0:
            logger.info(
                f'\033[7;41m [{self.username}]【新闻阅读】积分已达成，无需重复获取积分。\033[0m')
            return
        logger.debug(f'正在进行新闻学习...')
        self.kaleidoscope()
        self.back_to_home()
        # 点击一下home按钮，确保在新闻阅读页面
        self.scroll_find_volume(self.volume_title)
        self._read(self.read_count, self.star_share_comments_count)
        self.back_to_home()

    # 视听学习模块
    # class View(App):
    def _view_init(self):
        """
        视听学习初始化模块 +6
        """
        # super().__init__()
        self.view_time = cfg.getint("prefers", "video_view_time")
        if self.app_args['testapp']:
            self.video_count = cfg.getint("test", "app_watch")
            self.view_delay = self.read_delay = cfg.getint("test", "test_delay")
        else:
            self.radio_channel = cfg.get("prefers", "radio_channel")
            self.view_delay = self.view_time // self.video_count
            g, t = self.score["视听学习"]
            if t == g:
                self.video_count = 0
            else:
                self.video_count = random.randint(cfg.getint('prefers', 'video_count_min'),
                                                  cfg.getint('prefers', 'video_count_max')) - g

    def music(self):
        if "disable" == self.has_bgm:
            logger.debug(f'广播开关 关闭')
        elif "enable" == self.has_bgm:
            logger.debug(f'广播开关 开启')
            self._music()
        else:
            logger.debug(f'广播开关 默认')
            g, t = self.score["视听学习时长"]
            if g == t:
                logger.debug(
                    f'\033[7;41m [{self.username}]【视听学习】 积分已达成，无需重复观看。\033[0m')
                return
            else:
                self._music()

    def _music(self):
        logger.debug(f'[{self.username}]正在打开《{self.radio_channel}》...')
        self.safe_click(
            '//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_mine"]')
        self.safe_click('//*[@text="听新闻广播"]')
        self.safe_click(f'//*[@text="{self.radio_channel}"]')
        self.safe_click(rules['home_entry'])

    def _play_radio_background(self):
        # 打开电台，选择“听广播”页面，开启后台播放
        self.driver.xpath(rules['radio_entry']).click_exists(5)
        self.driver(text='听广播').click_exists(5)
        self.driver.xpath(rules['radio_play_button']).click_exists(5)
        self.back_to_home()

    def _watch(self, video_count=None):
        """
        视听学习执行模块 +6
        """
        if not video_count:
            logger.info(
                f'\033[7;41m [{self.username}]【视听学习】 积分已达成，无需重复获观看。\033[0m')
            return
        logger.info(f" [{self.username}]开始浏览百灵视频...")
        # 重新安装以后，在百灵视频开始前会有一个提示框，点击关闭
        self.safe_click(rules['bailing_enter'])
        try:
            self.driver.xpath(rules['bailing_tv_close']).click_exists(3)
        except XPathElementNotFoundError:
            pass
        self.safe_click(rules['bailing_enter'])  # 再点一次刷新短视频列表
        time.sleep(2)
        self.safe_click(rules['video_first'])
        logger.info(f'[{self.username}]预计观看视频 {video_count} 则')
        # 划走提示示例页面
        # 或者点击两次
        self.swipe_up()
        time.sleep(0.3)
        self.swipe_down()
        while video_count:
            video_count -= 1
            # video_delay = random.randint(
            #     self.view_delay, self.view_delay + min(10, self.video_count))
            # 因为2020年8月的升级，减少了视听收看的时长（6分钟）
            # 所以有view_time=720秒需要减少一半时长
            video_delay = self.view_delay
            logger.info(
                f'[{self.username}]正在观看视频 <{video_count + 1}#> {video_delay} 秒进入下一则...')
            pbar = tqdm(
                total=video_delay, bar_format='{l_bar}|{bar}| 观看到{n_fmt}秒/总计需观看{total_fmt}秒 ', nrows=10, ncols=50,
                smoothing=0.1)
            for sec in range(video_delay):
                time.sleep(1)
                pbar.update(1)
            pbar.close()
            # time.sleep(video_delay)
            self.swipe_up()
            time.sleep(1)
        else:
            logger.info(f'[{self.username}]视听学习完毕，正在返回...')
            self.back_to_home()

    def _watch_video(self, video_count=None):
        if not video_count:
            logger.info(
                f'\033[7;41m [{self.username}]【视听学习】 积分已达成，无需重复获观看。\033[0m')
            return
        logger.info(f" [{self.username}]开始浏览电视台视频...")
        # 打开电视台频道
        self.driver.xpath(rules['tv_entry']).click_exists(5)
        time.sleep(1)
        video_title_list = []
        channel = self.volume_title = random.choice(
            re.split(r'[,，;；、/.\s]', cfg.get("prefers", "tv_volume_title")))
        self.driver(text=channel).click_exists(5)
        time.sleep(1)
        self.swipe_up(random.randint(0, 5))
        while True:
            video_list = self.driver.xpath(rules['article_list1']).all()
            for video in video_list:
                if video.text not in video_title_list:
                    video_title_list.append(video.text)
                    video.click()
                    video_count -= 1
                    if video_count < 0:
                        break
                    logger.info(f'[{self.username}]' + video.text)
                    video_delay = self.view_delay
                    logger.info(f"[{self.username}] 观看[{self.view_delay}]秒视频")
                    time.sleep(video_delay)
                    self.safe_back()
                else:
                    continue
            if video_count < 0:
                break
            else:
                self.swipe_up()
        logger.info(f'[{self.username}]视听学习完毕，正在返回...')
        self.back_to_home()

    def watch(self):
        """
        视听学习模块 +6
        """
        self._view_init()
        if self.app_args['testapp']:
            self.video_count = cfg.getint('test', 'app_watch')
        # self._watch(self.video_count)
        self._watch(self.video_count)
        # self._watch_video(self.video_count)

    # class Weekly(App):

    def _weekly_init(self):
        self.workdays = cfg.get("prefers", "workdays")

    def _weekly(self):
        """
        每周答题执行模块 +5
        """
        self.safe_click(rules["weekly_entry"])
        question_count = 0
        # 看看ini文件里面第几页是没有作答的每周答题
        # 逐页翻动，并检查没有是否有没做过的
        try:
            page = cfg.getint('prefers', 'weekly_page')
            question_count = cfg.getint('prefers', 'weekly_count_each_group')
        except (NoOptionError, NoSectionError):
            page = 1
        cur_page = 0
        while page > cur_page:
            titles = self.driver.xpath(rules["weekly_titles"]).all()
            states = self.driver.xpath(rules["weekly_states"]).all()
            for title, state in zip(titles, states):
                # if self.size[1] - title.location_in_view["y"] < 10:
                if self.size[1] - title.bounds[3] < 10:
                    logger.debug(f'[{self.username}]屏幕内没有未作答试卷')
                    break
                # logger.info(
                #     f'{title.get_attribute("name")} {state.get_attribute("name")}')
                # if "未作答" == state.get_attribute("name"):
                # if "2019年12月第五周答题" == title.get_attribute("name").strip() or "未作答" == state.get_attribute("name"):
                if "未作答" == state.text and self.app_args['testapp'] is False:
                    logger.info(
                        f'[{self.username}]在翻到第{cur_page}页时，发现答题项！{title.text}, 开始！')
                    state.click()
                    time.sleep(random.randint(3, 6))
                    self._dispatch(question_count)  # 这里直接采用每日答题
                    # cur_page = page
                    self.safe_back('weekly report -> weekly list')
                    self.safe_back('weekly list -> quiz')
                    return True
                # 测试模块
                if ("未作答" == state.text or "已作答" == state.text) and \
                        self.app_args['testapp']:
                    logger.info(
                        f'[{self.username}]在翻到第{cur_page}页时，发现答题项！{title.text}, 开始！')
                    state.click()
                    time.sleep(random.randint(3, 6))
                    self._dispatch(question_count)  # 这里直接采用每日答题
                    # cur_page = page
                    self.safe_back('weekly report -> weekly list')
                    self.safe_back('weekly list -> quiz')
                    return True
                # 准备用来测试每周答题的功能的
                # if "已作答" == state.get_attribute("name"):
                #     logger.info(f'{title.get_attribute("name")}, 开始！')
                #     state.click()
                #     time.sleep(random.randint(3, 6))
                #     self._dispatch(5)  # 这里直接采用每日答题
                #     cur_page = page
                #     self.safe_back('weekly report -> weekly list')
                #     self.safe_back('weekly list -> quiz')
                #     return True
            self.swipe_up()
            # print(f'[{self.username}]每周答题开始翻页，还需要翻动{page-cur_page}页。')
            cur_page += 1
            time.sleep(1)
            # 保留：下面语句是看看是不是到了题库底部
            # try:
            #     weekly_list_endline = self.wait.until(
            #         EC.presence_of_element_located((By.XPATH, rules["weekly_list_endline"])))
            #     cur_page = page
            # except:
            #     pass
        self.safe_back('weekly list -> quiz')
        return False

    def weekly(self):
        """
        每周答题 +5
        复用每日答题的方法，无法保证每次得满分，如不能接受，请将配置workdays设为0
        """
        self._weekly_init()
        if self.app_args['testapp']:
            pass
        elif not self.is_workday():
            logger.debug(
                f'[{self.username}]今日不宜每周答题/ {self.workdays}')
            return
        # 如果得分大于0，表示已经做过一套题，可能没得满分，不再继续做题。
        elif self.score['每周答题'][0]:
            logger.info(
                f'\033[7;41m [{self.username}]【每周答题】应完成{self.score["每周答题"][1]}分，实际完成{self.score["每周答题"][0]}分，已经完成答题。 '
                f'\033[0m')
            return
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        # 更新后会出现一个提示窗口，需要确定关闭掉
        try:
            self.driver.xpath(rules['quiz_updateinfo']).click_exists(0.5)
        except (XPathElementNotFoundError, XPathElementNotFoundError):
            pass
        # 处理新更新的提示页面三个按钮的xpath一样的
        self.quiz_entry_warning()
        time.sleep(3)
        self._weekly()
        self.back_to_home()


emu_name = ('MEmu', 'MEmu_1', 'MEmu_2', 'MEmu_3', 'MEmu_4', 'MEmu_5', 'MEmu_6')
nox_port = ('62001', '62025', '62026', '62027', '62028', '62029')
leidian_port = ('5555', '5557', '5559', '5561', '5563', '5565')
app_args_list = []
udid = ''

microvirt_string = r'start /b /D "D:\Program Files\Microvirt\MEmu" MEmuConsole.exe'
nox_string = r'start /b /D "D:\Program Files\Nox\bin" NoxConsole.exe launch -name:'
leidian_string = r'start /b /D "D:\Program Files\Nox\bin" NoxConsole.exe launch -name:'

user_list = list(
    set(re.split(r'[,，;；、/.\s]', cfg.get('users', 'study_users'))))
try:
    if cfg.get('test', 'is_test') == '0' or cfg.get('test', 'is_test').upper() == 'False':
        is_test = False
    else:
        is_test = True
except (NoOptionError, NoSectionError):
    print("请检查default.ini文件中[test]中is_test是否设置为True、1或者False、0（大小写都无所谓）。")
    is_test = False

for i in user_list:
    if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
        emu_name = cfg.get('users', f'emu_mv_{i}')
        udid = f'127.0.0.1:215{int(i) - 1}3'
    elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
        emu_name = cfg.get('users', f'emu_nox_{i}')
        udid = f'127.0.0.1:{nox_port[int(i) - 1]}'
    elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
        emu_name = cfg.get('users', f'emu_nox_{i}')
        udid = f'127.0.0.1:{5555 + 2 * (int(i) - 1)}'
    if cfg.get('emu_args', 'true_machine') == '1' or cfg.get('emu_args', 'true_machine').lower() == 'true':
        udid = 'xxxxxx'
    app_args_list.append(
        {
            'id': i,
            'username': decrypt(cfg.get('users', f'username{i}'), cfg.get('users', 'prikey_path')),
            'password': decrypt(cfg.get('users', f'password{i}'), cfg.get('users', 'prikey_path')),
            'emu_name': emu_name,
            'udid': udid,
            'host': '127.0.0.1',
            'port': 4723 + (int(i) - 1) * 2,
            'systemPort': 8200 + (int(i) - 1),
            'testapp': is_test
        })


def appium_start(**args):
    """
    启动Appium服务器
    可以为多用户启动不同的Appium服务
    """
    bootstrap_port = args['port'] + 1
    port = str(args['port'])
    appium_start_str = cfg.get('driver_args', 'appium_string')
    # appium_start_str = r"start /b node C:\Users\Long\AppData\Local\Programs\Appium\resources\app\node_modules
    # \appium\build\lib\main.js -a "
    cmd = appium_start_str + args['host'] + ' -p ' + port + ' -bp ' + str(
        bootstrap_port) + ' --session-override --no-reset'
    logger.info(
        f'[{args["username"]}]\033[27;31;44m {cmd}\033[0m')
    logger.info(
        f'[{args["username"]}]\033[27;31;44m 启动Appium服务器(端口：{port})...\033[0m')
    while True:
        try:
            subprocess.call(cmd, shell=True, stdout=open(
                '.\\logs\\' + port + '.log', 'a'), stderr=subprocess.STDOUT)
            time.sleep(2)
            status = subprocess.getoutput(f'netstat -ano | findstr {port}')
            if status:
                logger.debug('启动成功。。。。')
                break
            else:
                logger.debug('启动失败，3s后重试')
                time.sleep(3)
        except subprocess.CalledProcessError:
            logger.debug('启动失败，3s后重试')
            time.sleep(3)


def emu_start(**args):
    """
    启动逍遥模拟器
    """
    if cfg.get('emu_args', 'true_machine') == '1' or cfg.get('emu_args', 'true_machine').lower() == 'true':
        return
    cmd = ''
    logger.info(f"[{args['username']}]\033[27;32;41m启动模拟器\033[0m")
    port = str(args['port'])
    if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'microvirt_path') + '" MEmuConsole.exe' + \
              ' "' + args['emu_name'] + '"'
    elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'nox_path') + '" NoxConsole.exe launch -name:' + args['emu_name']
    elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'leidian_path') + '" dnconsole.exe launch --name ' + args[
            'emu_name']
    # cmd = f'start /b /D "D:\Program Files\Microvirt\MEmu\" MEmuConsole.exe "' + \
    #     args['emu_name']+'"'
    try:
        subprocess.Popen(cmd, shell=True, stdout=open(
            '.\\logs\\' + port + '.log', 'a'), stderr=subprocess.PIPE)
    except Exception as e:
        logger.dubeg(e)
        pass


def adb_connect(**args):
    """
    启动adb连接模块
    """
    cmd = ''
    logger.info(
        f'[{args["username"]}]\033[27;31;46m 正在连接模拟器 {args["udid"]}，请稍候...\033[0m')
    while True:
        try:
            if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
                cmd = 'start /b /D "' + cfg.get('emu_args', 'microvirt_path') + '" adb connect ' + args["udid"]
            elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
                cmd = 'start /b /D "' + cfg.get('emu_args', 'nox_path') + '" adb.exe connect ' + args["udid"]
            elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
                cmd = 'start /b /D "' + cfg.get('emu_args', 'leidian_path') + '" adb.exe connect ' + args["udid"]
            rtn_msg = subprocess.Popen(cmd, shell=True, stdout=open('.\\logs\\' + 'adbconnect.log', 'a'),
                                       stderr=subprocess.STDOUT)
            # print(rtn_msg)
            break
            # if 0 == subprocess.Popen(f'adb connect {args["udid"]}', shell=True, stdout=open(
            #         '.\\logs\\' + 'adbconnect.log', 'a'), stderr=subprocess.STDOUT):
            #     logger.info(
            #         f'[{args["username"]}]\033[27;31;46m 模拟器 {args["udid"]} 连接成功\033[0m')
            #     break
            # else:
            #     logger.info(
            #         f'[{args["username"]}]\033[27;31;46m 模拟器 {args["udid"]} 连接失败\033[0m')
        except subprocess.CalledProcessError as msg:
            logger.info(f'{msg},adb连接失败，5秒后重试...')
            time.sleep(5)


def begin_study(**args):
    """
    启动学习或者测试模块
    """
    cmd = ''
    logger.info(
        f'\033[7;41m {args["username"]}开始学习。\033[0m')
    xuexi_app = AutoApp(args)
    if args['testapp']:
        xuexi_app.test()
    else:
        xuexi_app.start()
    logger.info(
        f'\033[7;41m 关闭{args["username"]}使用的模拟器！\033[0m')
    if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
        cmd = r'start /b /D "D:\Program Files\Microvirt\MEmu\" memuc stop -n  "' + \
              args['emu_name'] + '"'
    elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
        cmd = fr'start /b /D "D:\Program Files\Nox\bin\" nox -clone:Nox_{int(args["id"]) - 1} -quit'
    elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'leidian_path') + '" dnconsole.exe quit --name ' + args[
            'emu_name']
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

    # win32api.MessageBox(0, f'{app_args_list["username"]}今日学习完成！', "恭喜你学习完成", win32con.MB_OK)


def restart_adb_server():
    """
    清理appium环境,杀node.exe的进程
    :return:
    """
    # res = subprocess.Popen('tasklist | find "node.exe"',
    #                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out = res.stdout.readlines()
    # if len(out) > 0:
    #     logger.info(f'\033[7;41m 关闭所有的Appium服务！\033[0m')
    #     # if len(server_list) > 0:
    #     subprocess.call("taskkill -F -PID node.exe",
    #                     shell=True, stderr=subprocess.STDOUT)
    cmd = ''
    if cfg.get('emu_args', 'emu_name').lower() == 'microvirt':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'microvirt_path') + '" adb.exe '
    elif cfg.get('emu_args', 'emu_name').lower() == 'nox':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'nox_path') + '" adb.exe '
    elif cfg.get('emu_args', 'emu_name').lower() == 'leidian':
        cmd = 'start /b /D "' + cfg.get('emu_args', 'leidian_path') + '" adb.exe '

    if 0 == subprocess.check_call(cmd + 'disconnect', shell=True, stdout=open(
            '.\\logs\\' + 'adbconnect.log', 'a'), stderr=subprocess.STDOUT):
        logger.info(
            f'\033[27;31;46m adb disconnect成功\033[0m')
    else:
        logger.info(
            f']\033[27;31;46m adb disconnect失败\033[0m')
    time.sleep(1)
    if 0 == subprocess.check_call(cmd + 'kill-server', shell=True, stdout=open(
            '.\\logs\\' + 'adbconnect.log', 'a'), stderr=subprocess.STDOUT):
        logger.info(
            f'\033[27;31;46m adb kill-server成功\033[0m')
    else:
        logger.info(
            f']\033[27;31;46m adb kill-server失败\033[0m')
    time.sleep(1)
    if 0 == subprocess.check_call(cmd + 'start-server', shell=True, stdout=open(
            '.\\logs\\' + 'adbconnect.log', 'a'), stderr=subprocess.STDOUT):
        logger.info(
            f'\033[27;31;46m adb start-server成功\033[0m')
    else:
        logger.info(
            f'\033[27;31;46m adb start-server失败\033[0m')


xuexi_process = []

if __name__ == "__main__":
    begin_time = datetime.datetime.now()
    subprocess.check_call(f"cls", shell=True)
    restart_adb_server()
    multiprocessing.freeze_support()
    sche = scheduler()
    # for run_args in app_args_list:
    #     sche.enter(3, 0, appium_start, kwargs=run_args)
    for run_args in app_args_list:
        if run_args['testapp']:
            logger.info(
                f'[{run_args["username"]}]\033[27;31;45m 开启测试模式！！！\033[0m')
        sche.enter(3, 1, emu_start, kwargs=run_args)
    for run_args in app_args_list:
        sche.enter(3, 2, adb_connect, kwargs=run_args)
    sche.run()
    time.sleep(10)
    for run_args in app_args_list:
        # begin_xuexi = multiprocessing.Process(
        #     target=begin_study, kwargs=run_args)
        begin_xuexi = threading.Thread(
            target=begin_study, kwargs=run_args)
        xuexi_process.append(begin_xuexi)
    random.choice(xuexi_process)
    for auto_xuexi in xuexi_process:
        auto_xuexi.start()
    for auto_xuexi in xuexi_process:
        auto_xuexi.join()
    end_time = datetime.datetime.now()
    winsound.PlaySound(r'Ending.wav', winsound.SND_ALIAS)
    logger.info(
        f'\033[7;41m 今日学习完成！！！\033[0m')
    logger.info(
        f'\033[7;41m 开始：{begin_time}  结束：{end_time}，总计耗时：{end_time - begin_time}\033[0m')
