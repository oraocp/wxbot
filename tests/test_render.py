# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/6
# -------------------------------------------------------------------------

from unittest import TestCase

from weixin.render import Renderer
from weixin.utils import msgtodict


class TestResonse(TestCase):


    def test_render_test(self):

        resp = Renderer(self.account.appid)
        response_xml = resp.render_text("openid", "回复微信服务器的内容：content")
        dic = msgtodict(response_xml)
        self.assertEqual(dic["ToUserName"], "openid")
        self.assertEqual(dic["FromUserName"], "appid")
        self.assertEqual(dic["MsgType"], "text")
        self.assertEqual(dic["Content"], "回复微信服务器的内容：content")
