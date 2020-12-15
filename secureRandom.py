#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: secureRandom.py
@author: wongsyrone
@Copyright © 2019. All rights reserved.
'''
import base64
import secrets

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

# 从 secrets 模块获取 SystemRandom 实例
_inst = secrets.SystemRandom()


class SecureRandom:
    seed = _inst.seed
    random = _inst.random
    uniform = _inst.uniform
    triangular = _inst.triangular
    randint = _inst.randint
    choice = _inst.choice
    randrange = _inst.randrange
    sample = _inst.sample
    shuffle = _inst.shuffle
    normalvariate = _inst.normalvariate
    lognormvariate = _inst.lognormvariate
    expovariate = _inst.expovariate
    vonmisesvariate = _inst.vonmisesvariate
    gammavariate = _inst.gammavariate
    gauss = _inst.gauss
    betavariate = _inst.betavariate
    paretovariate = _inst.paretovariate
    weibullvariate = _inst.weibullvariate
    getstate = _inst.getstate
    setstate = _inst.setstate
    getrandbits = _inst.getrandbits


def notice():
    raise NotImplementedError(
        'The library does not support execution. Please import to another py file')


def encrypt(text, pubkey_path):
    with open(pubkey_path, "r") as f:
        key = f.read()
        rsakey = RSA.importKey(key)  # 导入读取到的公钥
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
        # 通过生成的对象加密message明文，注意，在python3中加密的数据必须是bytes类型的数据，不能是str类型的数据
        cipher_text = base64.b64encode(
            cipher.encrypt(text.encode(encoding="utf-8")))
        # print(cipher_text)
        return cipher_text.decode('utf8')


# 解密
def decrypt(text, prikey_path):
    with open(prikey_path) as f:
        key = f.read()
        rsakey = RSA.importKey(key)  # 导入读取到的私钥
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
        # 将密文解密成明文，返回的是一个bytes类型数据，需要自己转换成str
        cipher_text = cipher.decrypt(base64.b64decode(text), "ERROR")
        # print(cipher_text)
        return cipher_text.decode('utf8')


if __name__ == '__main__':
    notice()
