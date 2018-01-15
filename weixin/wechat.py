# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2017-12-30
# -------------------------------------------------------------------------
from enum import Enum

from weixin.api.client import WxClient
from weixin.crypto import MessageCryptor
from weixin.logger import log, set_logger
from weixin.messages import TextInputMessage
from weixin.render import render_text
from weixin.utils import check_signature, msgtodict, Lockable, Activator, parse_message


# ---------------------------------------------------------------------------
#   Handler
# ---------------------------------------------------------------------------


class Handler(Lockable):
    """
    消息处理器
    """

    def __init__(self):
        Lockable.__init__(self)

    def handle(self, record):
        self.acquire_lock()
        try:
            return self.reply(record)
        finally:
            self.release_lock()

    def reply(self, record):
        raise NotImplementedError('Hanlder的子类没有实现reply方法')


class EchoHandler(Handler):
    """
    简单的消息回应处理器
    """

    def reply(self, record):
        msg = record.msg
        retval = ""
        if msg and isinstance(msg, TextInputMessage):
            retval = render_text(msg.fromUserName, msg.toUserName,
                                                 "收到来自%s的消息。\\n内容为'%s'" % (msg.fromUserName, msg.content))
        return retval


class _Handlerer(Lockable):
    """
    Handler的管理
    """

    def __init__(self):
        self.handler_list = []
        self.default_handler = None

    def add_handler(self, handler):
        self.acquire()
        try:
            self.handler_list.append(handler)
        finally:
            self.release()

    def remove_handler(self, handler):
        self.acquire()
        try:
            if handler in self.handlerList:
                self.handler_list.append(handler)
        finally:
            self.release()

    def handle(self, record):
        if len(self.handler_list) == 0:
            log.warning("公众号{0}没有配置消息处理器，使用默认的EchoHandler".format(record.appid))
            if self.default_handler is None:
                self.default_handler = EchoHandler()
            return self.default_handler.handle(record)
        else:
            log.debug("进入消息处理过程，处理器为:"+str(type(self.handler_list[0])))
            for h in self.handler_list:
                if hasattr(h, 'handle'):
                    result = h.handle(record)
                else:
                    result = h(record)  # 调用函数
                if not (result is None) and len(result) > 0:
                    return result
            return ""


# ---------------------------------------------------------------------------
#   MsgRecord
# ---------------------------------------------------------------------------


class MsgRecord(object):
    """
    消息处理的中间对象
    """

    def __init__(self, appid, kind, msg, client):
        self.appid = appid
        self.kind = kind
        self.msg = msg
        self.client = client

    def __str__(self):
        return "{0}:{1}".format(self.appid, self.msg)


# ---------------------------------------------------------------------------
#   WxAccount
# ---------------------------------------------------------------------------

class ACCOUNTKIND(Enum):
    """
    公众号类别
    """
    SUBSCRIPTION = 10
    SERVICE = 20
    ENTERPRISE = 30


WX_AUTHORIZE_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"


class WxAccount(_Handlerer):
    """
    定义微信公众号对象
    """

    # ----------------------------------------------------------------------
    # Constructor

    def __init__(self, id, appid, token, secret, encoding_aes_key="",
                 enable=True, kind=ACCOUNTKIND.SUBSCRIPTION, handler_list=None):
        _Handlerer.__init__(self)
        self.id = id
        # 服务器配置令牌
        self.token = token
        # 公众号开发者ID
        self.appid = appid
        # 公众号开发者密码
        self.secret = secret
        # 消息加解密方式
        self.encoding_aes_key = encoding_aes_key
        # 公众号为生效状态
        self.enable = enable
        # 公众号类别
        self.kind = kind

        self.handler_list = handler_list

        # 公众号API调用
        self.client = WxClient(appid, secret)
        # 消息加解密器
        self.crypto = MessageCryptor(self.appid, self.token, self.encoding_aes_key)

    # ----------------------------------------------------------------------
    # Methods

    def check_valid(self, echostr, signature, timestamp, nonce):
        """
        接收微信服务器发送的Get请求并进行服务器有效性验证。
        :param params: 请求参数
        :return: 如果验证通过，返回公众号响应字符串；否则返回空字符
        """

        log.debug("接收到微信服务器验证公众号'{0}'请求，参数为:echostr={1},signature={2},timestamp={3},nonce={4}".
                  format(self.id, echostr, signature, timestamp, nonce))

        if check_signature(self.token, timestamp, nonce, signature):
            log.debug("微信服务器验证公众号'{0}'校验成功".format(self.id))
            return echostr
        else:
            log.error("微信服务器验证公众号'{0}'校验失败，参数为:echostr={1},signature={2},timestamp={3},nonce={4}".
                      format(self.id, echostr, signature, timestamp, nonce))
            # 如果校验失败或服务器无法在5秒内回复，则返回空字符串或Success
            # 否则微信后台会发起三次重试
            # 三次重试后，依旧没有及时回复任何内容，系统自动在粉丝会话界面出现错误提示“该公众号暂时无法提供服务，请稍后再试
            return ""

    def response_message(self, params, msgdata):
        """
        处理微信服务器以POST方式发送的消息并作出响应
        :param params: 消息请求参数
        :param msgdata: 消息请求数据,格式为XML
        :return: 返回响应信息或空字符串
        """
        log.debug("接收到微信服务器公众号'{0}'请求:{1}".format(id, msgdata))
        # 消息是否已加密，默认为未加密
        b_encrypt = False
        log.debug("准备进入消息转字典的过程...")
        msg_dict = msgtodict(msgdata)
        log.debug("解析后的消息类型为:"+msg_dict["MsgType"])
        if "Encrypt" in msg_dict.keys():
            # 消息已加密
            b_encrypt = True
            timestamp = params.get("timestamp")
            nonce = params.get("nonce")
            msg_signature = params.get("msg_signature")
            body = msg_dict["Encrypt"]

            decrypt_content = self.crypto.decrypt_msg(body, msg_signature, timestamp, nonce)
            log.info("服务器请求已加密，加密后请求为:{0}".format(decrypt_content))
            msg_dict = msgtodict(decrypt_content)

        # 解析获取输入的消息对象
        input_message = parse_message(msg_dict)
        rv = MsgRecord(self.appid, self.kind, input_message, self.client)

        result = self.handle(rv) or ""
        # 如果是加密模式，则响应信息也需加密返回
        if b_encrypt:
            result = self.crypto.encrypt_msg(result)
        log.debug("响应微信服务器请求，回复为:{0}".format(result))
        return result

    def oauth_url(self, url):
        """

        :param url:
        :return:
        """
        return WX_AUTHORIZE_URL + "?appid={0}&redirect_uri={1}".format(self.appid, url)


# ---------------------------------------------------------------------------
#   BaseWXService
# ---------------------------------------------------------------------------

class BaseWXService(object):
    """
    定义基本的微信服务对象，用于响应Web服务器的请求
    """

    def get_account(self, id):
        raise NotImplementedError("WeChat的子类没有实现get_account方法")

    # ----------------------------------------------------------------------
    # 微信服务器验证

    def do_get(self, id, echostr, signature, timestamp, nonce):
        """
        接收微信服务器发送的Get请求并进行验证
        :param id: 公众号标识
        :param echostr: 公众号响应字符串
        :param signature: 微信加密签名
        :param timestamp: 时间戳
        :param nonce: 随机字符串
        :return: 如果验证成功，则返回； 验证失败，返回空字符串
        """

        account = self.get_account(id)
        return account.check_valid(echostr, signature, timestamp, nonce)

    def do_post(self, id, msgdata, params=None):
        """
        处理微信服务器以POST方式发送的消息并作出响应
        :param msgdata: 消息请求数据
        :param params:  消息请求参数
        :return: 回传服务器的消息文本
        """

        account = self.get_account(id)
        return account.response_message(params, msgdata)


# ---------------------------------------------------------------------------
#   SimpleWxService
# ---------------------------------------------------------------------------

class SimpleWxService(BaseWXService):
    """
    提供简单的微信服务，用于响应Web服务器的请求
    通过配置文件来设置微信公众号，公众号需要通过配置文件来修改
    """

    def __init__(self, settings):
        BaseWXService.__init__(self)
        self.accounts = {}
        set_logger()
        if settings is None or not isinstance(settings, dict): return
        for key in settings.keys():
            val = settings[key]
            if val and isinstance(val, dict) and "appid" in val.keys():
                # 设置消息管理器
                handlers = []
                if "handlers" in val.keys():
                    clslist = []
                    for cls in val["handlers"]:
                        if cls in clslist:
                            log.warn("公众号{0}消息处理器'{1}'重复设置")
                            continue
                        try:
                            h = Activator.new_instance(cls.strip())
                            if isinstance(h, Handler):
                                handlers.append(h)
                            else:
                                log.error("公众号{0}消息处理器'{1}'不是MessageHandler类型，实例化异常。")
                        except Exception as e:
                            log.error("公众号{0}消息处理器'{1}'实例化失败，原因为:{2}".format(key, cls, e))
                        clslist.append(cls)
                account = WxAccount(
                    id=key,
                    appid=val["appid"],
                    token=val["token"],
                    secret=val["secret"],
                    encoding_aes_key=val.get("encodingAESKey", ""),
                    handler_list=handlers,
                )
                self.accounts[key] = account

    def get_account(self, id):
        if id in self.accounts.keys():
            return self.accounts[id]
        return None
