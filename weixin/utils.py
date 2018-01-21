# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2017-12-30
# -------------------------------------------------------------------------

import hashlib

try:
    import threading
except ImportError:  # pragma: no cover
    threading = None
from random import choice
from weixin.messages import MESSAGE_TYPES, UnknownMessage
from weixin.events import EVENT_TYPES, SubscribeScanEvent, SubscribeEvent, SUBSCRIBE_QRSCENE

try:
    import xml.etree.cElementTree as Et
except ImportError:
    import xml.etree.ElementTree as Et


def check_signature(token, timestamp, nonce, signature):
    """
    验证微信服务器签名是否符合微信规则
    :param token: 公众号令牌
    :param timestamp: 时间戳
    :param nonce: 随机字符串
    :param signature: 微信加密签名
    :return: 如果签名验证成功，则返回True；否则返回False
    """
    lst = [token, timestamp, nonce]
    # 将token, timestamp, nonce三个参数按升序进行排序
    lst.sort()
    # 将三个参数拼接成字符串并且sha1算法加密
    sign = "".join(lst)
    # Python3中sha1中在哈希前需要先将字符串转码
    sha1 = hashlib.sha1(sign.encode('utf-8'))
    # 加密后的字节转换为文本
    hashcode = sha1.hexdigest()

    # 将字节与服务器提供的微信加密签名进行比较。如两者相等，则校验通过
    return hashcode == signature


def msgtodict(msg_xml):
    """
    解析微信消息的XML文本，获取消息数据
    :param msg_xml: 消息XML文本
    :return: 消息数据字典
    """
    props = {}
    # 消息XML没有根节点
    tree = Et.fromstring(msg_xml)
    for child in tree:
        props[child.tag] = child.text
    return props


def rand_str(length, dictionary):
    """
    生成指定长度的随机字符串
    :param length:  字符串长度
    :param dictionary: 字符字典
    :return: 随机字符串
    """
    return ''.join(choice(dictionary) for _ in range(length))


class Activator:
    @staticmethod
    def new_instance(class_name, *args, **kwargs):
        """
        动态创建类的实例
        :param class_name: 类的全名
        :param args: 类构建器所需要的无名参数列表
        :param kwargs: 类构造器所需要的有名参数字典
        :return: 类的实例
        <p>
        http://blog.csdn.net/kongxx/article/details/65626418
        [Example]
        class_name = "weixin.message.TextInputMessage"
        dic = {"ToUserName": "2323-232323", "FromUserName": "abdc-dsddss", "MsgId": "M-232322",
               "MsgType": "text", "CreateTime": "232323", "Content": "微信发送的消息"}
        msg = Activator.new_instance(class_name, dic)
        </p>
        """
        (modulename, clsname) = class_name.rsplit('.', 1)
        modulemeta = __import__(modulename, globals(), locals(), [clsname])
        clsmeta = getattr(modulemeta, clsname)
        return clsmeta(*args, **kwargs)


class deprecated(object):
    """
    打印函数已废弃的警告

    >>> @deprecated()
    ... def f():
    ...    pass
    >>> f()
    ... f is deprectead.
    """

    def _wrapper(self, *args, **kwargs):
        self.count += 1
        if self.count == 1:
            print(self.func.__name__, 'is deprecated.')
        return self.func(*args, **kwargs)

    def __call__(self, func):
        self.func = func
        self.count = 0
        return self._wrapper


class Lockable(object):
    def __init__(self):
        if threading:
            self.lock = threading.RLock()
        else:  # pragma: no cover
            self.lock = None

    def acquire_lock(self):
        """
        Acquire the module-level lock for serializing access to shared data.

        This should be released with _releaseLock().
        """
        if self.lock:
            self.lock.acquire()

    def release_lock(self):
        """
        Release the module-level lock acquired by calling _acquireLock().
        """
        if self.lock:
            self.lock.release()


def parse_message(dic):
    """
    将接收到的数据解析为具体的消息类型实例
    :param dic: 接收到的数据
    :return: 消息类型实例
    """
    message_type = dic['MsgType'].lower()
    if message_type == 'event':
        return parse_event(dic)
    message_class = MESSAGE_TYPES.get(message_type, UnknownMessage)
    return message_class(dic)


def parse_event(dic):
    # assert (dic['MsgType'].lower() == 'event')
    event = dic["Event"].lower()
    if event == "subscribe":
        eventkey = dic.get("EventKey", "")
        if eventkey.startswith(SUBSCRIBE_QRSCENE):
            return SubscribeScanEvent(dic)
        return SubscribeEvent(dic)
    event_type = dic['MsgType'].lower()
    event_class = EVENT_TYPES.get(event_type, UnknownMessage)
    return event_class(dic)
