# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：测试微信API的用法
# 创建日期：2018/1/3
# -------------------------------------------------------------------------

from unittest import TestCase

from weixin.api.client import WxClient
from weixin.logger import set_logger


class WxClientClass(TestCase):
    def setUp(self):
        self.client = WxClient(
            # appid="wxff1ec8c09ae8c622",
            # secret="a261f13b3f1067894616608fc08ef944"
            appid="wx879cbaef5d53c126",
            secret="4f2b9aa36e9bffc2b595c4285c1c85f8"
        )
        set_logger()

    def test_get_ip_list(self):
        ip_list = self.client.get_ip_list()
        print(ip_list)

    def test_grant_token(self):
        token1 = self.client.grant_token()
        token2 = self.client.grant_token()
        self.assertNotEqual(token1.token, token2.token, "两次调用产生的凭证Token是一样的，应该不一样")

    def test_get_menu(self):
        menu_data = self.client.get_menus()
        print(menu_data)
