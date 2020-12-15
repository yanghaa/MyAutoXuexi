#!/usr/bin/env python
# -*- coding:utf-8 -*-import base64
"""
@project: AutoXue
@file: jiami.py
@author: alonik
@contact: https://github.com/my-autoxuexi/myAutoXuexi
@time: 2020-10-16(星期五) 09:03
@Copyright © 2019. All rights reserved.
"""
import base64
import re
from configparser import ConfigParser

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


# master的秘钥对的生成 
# --------------------------------------------生成公私钥对文件-----------------------------------------------------------
# private_pem = rsa.exportKey()
# with open('master-private.pem', 'wb') as f:
#     f.write(private_pem)

# public_pem = rsa.publickey().exportKey()
# with open('master-public.pem', 'wb') as f:
#     f.write(public_pem)

# ---------------------------------------------------
# ghost的秘钥对的生成
def gen_keypair():
    # 伪随机数生成器
    random_generator = Random.new().read
    # rsa算法生成实例
    rsa = RSA.generate(1024, random_generator)
    private_pem = rsa.exportKey()
    with open('ghost-private.pem', 'wb') as f:
        f.write(private_pem)

    public_pem = rsa.publickey().exportKey()
    with open('ghost-public.pem', 'wb') as f:
        f.write(public_pem)


# 加密
def encrypt(text):
    with open('d:\\rsa\\public.pem', "r") as f:
        key = f.read()
        rsakey = RSA.importKey(key)  # 导入读取到的公钥
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
        # 通过生成的对象加密message明文，注意，在python3中加密的数据必须是bytes类型的数据，不能是str类型的数据
        cipher_text = base64.b64encode(cipher.encrypt(text.encode(encoding="utf-8")))
        # print(cipher_text)
        return cipher_text.decode('utf8')


# 解密
def decrypt(text):
    with open('d:\\rsa\\private.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)  # 导入读取到的私钥
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
        # 将密文解密成明文，返回的是一个bytes类型数据，需要自己转换成str
        cipher_text = cipher.decrypt(base64.b64decode(text), "ERROR")
        # print(cipher_text)
        return cipher_text.decode('utf8')


# 结果：
# b'meBtYXP35VNjtWXsONDluweXdG98tMHjb5GxBLFJ0GJzo+96wSrHe8SDhNJweDJP6/OdeIQ8jP1HKCK+aC9HA12YMSUUqcixsY5s8QUyTs+fkMjGrlC6I7hPLO4DGQbFXEY0jiqP9ycgmAi5FCsDMcm0oEm8/fVzv7vl9QarSN4='  # 加密后的密文
# b'hello ghost, this is a plian text'  # 解密后的明文


# gen_keypair()

usernamelist = []
passwordlist = []
app_argslist = []

userscfg = ConfigParser()
userscfg.read(r'config\\users.ini', encoding='utf-8')

# 获得密文
for i in range(len(userscfg.items("users"))//2):
    usernamelist.append(encrypt(
        userscfg.get('users', f'username{i+1}')))
    print(f'username{1+i}={usernamelist[i]}')
    passwordlist.append(encrypt(
        userscfg.get('users', f'password{i+1}')))
    print(f'password{1+i}={passwordlist[i]}')

# 解密以后加入用户名和密码列表
for i in range(len(userscfg.items("users")) // 2):
    usernamelist.append(decrypt(
        userscfg.get('users', f'username{i + 1}')))
    print(f'User{i}帐号的用户名加密文本是：username{1 + i}={usernamelist[i]}')
    passwordlist.append(decrypt(
        userscfg.get('users', f'password{i + 1}')))
    print(f'User{i}帐号的密码加密文本是：password{1 + i}={passwordlist[i]}')
