# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import abc
import base64
import hashlib
import hmac
import json
import random
import time
import pyDes

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5


class TripleDes(object):
    """ 3DES 加解密 """

    def __init__(self, data, de3key):
        self.__data = data
        self.__des3key = de3key

    def encrypt(self):
        data = bytes(self.__data, encoding="utf8")
        key = bytes(self.__des3key[0:8], encoding="utf8")
        return base64.b64encode(
            pyDes.triple_des(self.__des3key, pyDes.CBC, key, pad=None, padmode=pyDes.PAD_PKCS5).encrypt(data))

    def decrypt(self):
        data = bytes(self.__data, encoding="utf8")
        key = bytes(self.__des3key[0:8], encoding="utf8")
        return pyDes.triple_des(self.__des3key, pyDes.CBC, key, pad=None, padmode=pyDes.PAD_PKCS5) \
            .decrypt(base64.b64decode(data))


class Signer(abc.ABC):
    """ 签名 """

    @abc.abstractmethod
    def sign_type(self):
        return NotImplemented

    @abc.abstractmethod
    def sign(self, data, mess, timestamp):
        return NotImplemented

    @abc.abstractmethod
    def verify_sign(self, data, mess, timestamp, signature):
        return NotImplemented


class HmacSigner(Signer):
    """ Hmac 签名 """

    def __init__(self, app_key):
        self.__app_key = app_key

    def sign_type(self):
        return "sha256"

    def sign(self, data, mess, timestamp):
        sign_pairs = "data=%s&mess=%s&timestamp=%d&key=%s" % (
            str(data, encoding="utf-8"), mess, timestamp, self.__app_key)
        app_key = bytes(self.__app_key, encoding="utf8")
        sign_pairs = bytes(sign_pairs, encoding="utf8")
        return hmac.new(app_key, msg=sign_pairs, digestmod=hashlib.sha256).hexdigest()

    def verify_sign(self, data, mess, timestamp, signature):
        sign_pairs = "data=%s&mess=%s&timestamp=%d&key=%s" % (data, mess, timestamp, self.__app_key)
        app_key = bytes(self.__app_key, encoding="utf8")
        sign_pairs = bytes(sign_pairs, encoding="utf8")
        return hmac.new(app_key, msg=sign_pairs, digestmod=hashlib.sha256).hexdigest() == signature


class RSASigner(Signer):
    """ RSA 签名 """

    def __init__(self, app_key, public_key, private_key):
        self.__public_key = RSA.importKey(public_key)
        if private_key is not None:
            self.__private_key = RSA.importKey(private_key)
        self.__app_key = app_key

    def sign_type(self):
        return "rsa"

    def sign(self, data, mess, timestamp):
        sign_pairs = "data=%s&mess=%s&timestamp=%d&key=%s" % (
            str(data, encoding="utf-8"), mess, timestamp, self.__app_key)
        signer = Signature_pkcs1_v1_5.new(self.__private_key)
        digest = SHA256.new()
        digest.update(sign_pairs.encode("utf8"))
        sign = signer.sign(digest)
        return base64.b64encode(sign)

    def verify_sign(self, data, mess, timestamp, signature):
        sign_pairs = "data=%s&mess=%s&timestamp=%d&key=%s" % (data, mess, timestamp, self.__app_key)
        signature = base64.b64decode(signature)
        cipher = Signature_pkcs1_v1_5.new(self.__public_key)
        digest = SHA256.new()
        digest.update(sign_pairs.encode("utf8"))
        return cipher.verify(digest, signature)


class ReqMessage(object):
    """
    ReqMessage 请求消息体
    """

    def __init__(self, encrypt, data, des3key):
        """
        :param encrypt: 加密算法
        :type data: {} 请求信息
        :param data: 请求信息
        """
        self.__encrypt = encrypt
        self.__data = None
        self.__des3key = des3key
        if data is not None:
            self.__data = json.dumps(data, ensure_ascii=False)

    def pack(self):
        if self.__data is None:
            return None
        timestamp = int(time.time())
        mess = "".join(random.sample("1234567890abcdefghijklmnopqrstuvwxy", 10))
        encrypt_data = TripleDes(self.__data, self.__des3key).encrypt()
        return {
            "data": encrypt_data,
            "mess": mess,
            "timestamp": timestamp,
            "sign": self.__encrypt.sign(encrypt_data, mess, timestamp),
            "sign_type": self.__encrypt.sign_type()
        }


class RespMessage(object):
    """
    RespMessage 返回信息
    """

    def __init__(self, des3key, content, req_data, req_param, headers):
        self.__des3key = des3key
        self.__content = content
        dic = json.loads(content)
        self.__req_param = req_param
        self.__req_data = req_data
        self.__code = dic.get("code", None)
        self.__message = dic.get("message", None)
        self.__data = dic.get("data")
        self.__request_id = headers["request-id"]

    def decrypt(self):
        if self.__data is None:
            return self

        if self.__des3key is not None and self.__req_param is not None \
                and self.__req_param.get("data_type", "") == "encryption":
            self.__data = json.loads(TripleDes(self.__data, self.__des3key).decrypt())
        return self

    @property
    def code(self):
        return self.__code

    @property
    def message(self):
        return self.__message

    @property
    def data(self):
        return self.__data

    @property
    def content(self):
        return self.__content

    @property
    def request_id(self):
        return self.__request_id


def notify_decoder(public_key, app_key, des3key, data, mess, timestamp, signature, sign_type):
    try:
        timestamp = int(timestamp)
    except ValueError:
        return False, ""

    res_data, verify_result = "", False
    if sign_type == "sha256":
        if HmacSigner(app_key).verify_sign(data, mess, timestamp, signature):
            res_data = TripleDes(data, des3key).decrypt().decode()
            verify_result = True
    else:
        if RSASigner(app_key, public_key, None).verify_sign(data, mess, timestamp, signature):
            res_data = TripleDes(data, des3key).decrypt().decode()
            verify_result = True
    return verify_result, res_data
