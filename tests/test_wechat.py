# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/6
# -------------------------------------------------------------------------
from unittest import TestCase

from weixin.wechat import SimpleWxService

WX_SETTINGS = {
    "ycx": {
        "appid": "wxff1ec8c09ae8c622",
        "token": "resplendsky",
        "secret": "a261f13b3f1067894616608fc08ef944",
        "encodingAESKey": "ATAQEUbhPfxqUEwI3KkemTuS1tRrhKyUH1yC1iuvT6J",
        "handlers": [
            'weixin.wechat.EchoHandler',
        ],
    },
    "ycx.test": {
        "appid": "wxff1ec8c09ae8c622",
        "token": "resplendsky",
        "secret": "a261f13b3f1067894616608fc08ef944",
        "encodingAESKey": "ATAQEUbhPfxqUEwI3KkemTuS1tRrhKyUH1yC1iuvT6J",
    },
}


class TestSimpleWxService(TestCase):
    def setUp(self):
        self.chat = SimpleWxService(WX_SETTINGS)

    def test_do_post(self):

        inputMsg = r"<xml>" \
                   r"<ToUserName><![CDATA[gh_153407c191e4]]></ToUserName>" \
                   r"<FromUserName><![CDATA[o-Qi-1Or0HmcnUyGqjXkhB4A6qqw]]></FromUserName>" \
                   r"<CreateTime>1515935965</CreateTime>" \
                   r"<MsgType><![CDATA[text]]></MsgType>" \
                   r"<Content><![CDATA[\xe5\xb9\xbf\xe5\x91\x8a\xe7\x94\xbb]]></Content>" \
                   r"<MsgId>6510895392933538073</MsgId>" \
                   r"</xml>"
        result1 = self.chat.do_post("ycx", inputMsg)
        self.assertIsNotNone(result1)
        # 检查没有配置消息处理器的情形
        result2 = self.chat.do_post("ycx.test", inputMsg)
        self.assertIsNotNone(result2)
