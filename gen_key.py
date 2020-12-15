#!/usr/bin/env python
# -*- coding:utf-8 -*-from Crypto import Random
"""
@project: AutoXue
@file: autoxue.py
@author: alonik
@contact: https://github.com/my-autoxuexi/myAutoXuexi
@time: 2020-10-16(星期五) 09:03
@Copyright © 2019. All rights reserved.
"""
from Crypto import Random
from Crypto.PublicKey import RSA
from configparser import ConfigParser
 
# 伪随机数生成器
random_generator = Random.new().read
# rsa算法生成实例
rsa = RSA.generate(1024, random_generator)
 
# master的秘钥对的生成
private_pem = rsa.exportKey()
 
#--------------------------------------------生成公私钥对文件-----------------------------------------------------------
with open('private.pem', 'wb') as f:
    f.write(private_pem)
 
public_pem = rsa.publickey().exportKey()
with open('public.pem', 'wb') as f:
    f.write(public_pem)
 
#---------------------------------------------------
# ghost的秘钥对的生成
private_pem = rsa.exportKey()
with open('ghost-private.pem', 'wb') as f:
    f.write(private_pem)
 
public_pem = rsa.publickey().exportKey()
with open('ghost-public.pem', 'wb') as f:
    f.write(public_pem)
 
'''
#-----------------------------------生成的公私钥文件类似于如下形式-------------------------------------------------------
# 私钥

-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQC6mwuOxuqYi6mugLGr3OuiHwm/hF4kQX1zd5VhGwxYf4H5+pkO
CES2UjOyLP9Xh6w+DJtRwTGE2xwDd3wMfW2wkHijM/uHkM9Jt+oRGIjy4IiXo+7t
ue/NWBkDiQm1qte0YDKlmkFREwvZ5X2KaCsSx+dyKH4QsovxQ3/RxftdmQIDAQAB
AoGAPA5SNe1G6zlnrsW0aL99Bnw+wuhy8/Av082Uwd/WpVTEHBPO1nlKw/LIuHtK
4nzDrmSYSEOJEF0EMwltXwevGSm1wq2FBhX4T+kz3XUpWfv9O0dlHeNtgxeD1QXL
kOxqU4F2WpdALgvi/rlPDd0aIagoXLi8MXkUH7hQlrJpQUECQQC6rygx3jDQA9Iw
kPUXlokEuLod+Kgoa700S5qpJi7vft675+tMG5SZtr+HQeqGHty0fqc8MIcy1fJm
ZYUrogN9AkEA/+RrrOoTYQbR3ENslTsNsiqQa2aZW5XAv9pEyGJBWu/4HUEEa6G3
FY0Y3ACZR0Xaraya8XAgOo61pWm83GBlTQJBAKH2812Ikzr2BbdDHJExdoEVL8xu
/p3LE6U6bt2QFiqNHPtT9C3cw+k0xyi3RJzGS9+A/uDWjYXKXvr92zMG5hUCQFXR
alccTZF9swX2ysSlgGtfIP4T85ymdXUiI208noR79C8DbhMWsgsVPeASh1VC1Rrn
xzLvkq9wyvSFqKQT5AUCQAxMO7KI1rwIm+ISuDEcwxRJXkdFypD74kOSYRxTqMun
Zdu4ku4t6mVeq5kBv1/S2dtF3TiqMRlxmLmV/fx7KHM=
-----END RSA PRIVATE KEY-----
 
#公钥
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC6mwuOxuqYi6mugLGr3OuiHwm/
hF4kQX1zd5VhGwxYf4H5+pkOCES2UjOyLP9Xh6w+DJtRwTGE2xwDd3wMfW2wkHij
M/uHkM9Jt+oRGIjy4IiXo+7tue/NWBkDiQm1qte0YDKlmkFREwvZ5X2KaCsSx+dy
KH4QsovxQ3/RxftdmQIDAQAB
-----END PUBLIC KEY-----
'''
