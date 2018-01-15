# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：处理消息的加解密
# 创建日期：2017-12-30
# 说明：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1434696670

# -------------------------------------------------------------------------
import base64
import time
import string
import hashlib
from weixin.utils import rand_str

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
except ImportError:
    raise RuntimeError("需要安装cryptography包")

from .exceptions import UnValidEncodingAESKey, AppIdValidationError, InvalidSignature


class AesCrypto(object):
    """

    """
    def __init__(self, aeskey):
        self.aeskey = aeskey


class PrpCrypt(object):
    """提供接收和推送给公众平台消息的加解密接口"""

    def __init__(self, key):
        pass

    def encrypt(self, text, appid):
        """

        :param text:
        :param appid:
        :return:
        """
        pass

    def decrypt(self, text, appid):
        """

        :param text:
        :param appid:
        :return:
        """
        return ''


def _get_signature(token, timestamp, nonce, *args):
    sign = [token, timestamp, nonce] + list(args)
    sign.sort()
    # 将参数拼接成字符串并且sha1算法加密
    sha1 = hashlib.sha1()
    map(sha1.update, sign)
    # 加密后的字节转换为文本
    return sha1.hexdigest()


class MessageCryptor(object):
    AES_TEXT_RESPONSE_TEMPLATE = r"<xml>" \
                                 r"<Encrypt><![CDATA[{encrypt}]]></Encrypt>" \
                                 r"<MsgSignature><![CDATA[{signature}]]></MsgSignature>" \
                                 r"<TimeStamp>{timestamp}</TimeStamp>" \
                                 r"<Nonce><![CDATA[{nonce}]]></Nonce>" \
                                 r"</xml>"

    def __init__(self, appid, token, encodingAESKey):
        key = base64.b64decode(encodingAESKey + "=")
        if len(key) != 32:
            raise UnValidEncodingAESKey(encodingAESKey)
        self.pc = PrpCrypt(key)
        self.token = token
        self.appid = appid

    def decrypt_msg(self, content, msg_signature, timestamp, nonce):
        """

        :param content:
        :param msg_signature:
        :param timestamp:
        :param nonce:
        :return:
        """
        signature = _get_signature(self.token, timestamp, nonce, content)
        if signature != msg_signature:
            raise InvalidSignature(msg_signature)
        return self.pc.decrypt(content)

    def encrypt_msg(self, content, nonce=None, timestamp=None):
        """

        :param content:
        :param nonce:
        :param timestamp:
        :return:
        """
        encrypt = self.pc.encrypt(content, self.appid)
        ts = timestamp or str(int(time.time()))
        nc = nonce or rand_str(10, string.digits)
        signature = _get_signature(self.token, ts, nonce, encrypt)
        return self.AES_TEXT_RESPONSE_TEMPLATE.format(
            encrypt=encrypt,
            signature=signature,
            timestamp=ts,
            nonce=nc
        )
