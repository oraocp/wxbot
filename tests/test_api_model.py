# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/9
# -------------------------------------------------------------------------

from unittest import TestCase

from weixin.api.models import *
from weixin.api.menu import *


class TestApiModel(TestCase):
    def test_access_tokens(self):
        ac = AccessToken("token", 20112)
        print("ac=", ac)

    def test_enum(self):
        # 测试枚举类型
        for media_type in MediaType:
            print(media_type, ":", media_type.value)
        print('')
        # 直接将值赋给枚举类型
        print(MediaType('image'))

    def test_menu(self):
        dic = {'menu': {'button': [{'name': '一键投保',
                                    'sub_button': [{'type': 'click', 'name': '购买车险', 'key': 'GMCX', 'sub_button': []},
                                                   {'type': 'view', 'name': '在线支付', 'url': 'http://cxm.test1.cn/livebot/OAuth2/main?state=http://test1.95590.cn/ccicws/CCICWXProject/onlinePayment.html', 'sub_button': []},
                                                   {'type': 'view', 'name': '查询支付', 'url': 'http://test1.95590.cn/livebot/OAuth2/main?state=http://test1.95590.cn/ccicws/CCICWXProject/dispatch.html?dynid=SB0446', 'sub_button': []},
                                                   {'type': 'view', 'name': '我的订单', 'url': 'http://test1.95590.cn/livebot/OAuth2/main?state=http://test1.95590.cn/ccicws/CCICWXProject/proposalList.html', 'sub_button': []}]},
                                    {'type': 'view', 'name': '一键报案', 'url': 'http://test1.95590.cn/livebot/OAuth2/main?state=http://test1.95590.cn/ccicws/CCICWXProject/policyList.html', 'sub_button': []},
                                   {'name': '尊享服务',
                                    'sub_button': [{'type': 'click', 'name': '我的客服', 'key': 'RGKF', 'sub_button': []},
                                                   {'type': 'view', 'name': '增值服务', 'url': 'http://test1.95590.cn/livebot/OAuth2/main?state=http://test1.95590.cn/ccicws/CCICWXProject/dispatch.html?dynid=SB2007', 'sub_button': []},
                                                   {'type': 'click', 'name': '我的保单', 'key': 'WDBD', 'sub_button': []},
                                                   {'type': 'click', 'name': '我的理赔', 'key': 'WDLP', 'sub_button': []}]}]}}
        menu = WxMenu(dic)
        dic2 = json.loads(menu.to_json())
        print(dic2)

    def test_subscripter(self):
        dic = {'subscribe': 1, 'openid': 'o6a4U0grN2cwJKSu_2tFQN6THWrw', 'nickname': '张少坡', " \
               r"'sex': 1, 'language': 'zh_CN', 'city': '浦东新区', 'province': '上海', 'country': '中国', " \
               r"'headimgurl': 'http://wx.qlogo.cn/mmopen/v6WjItCGdtzyGHI4EzNLH9oW3uNLtd1hyBaICNW8lqA8hxmlib8EfeCTFaFhiaQlgZEKtx9cDicQaZhkDaWKO660phwdSicicyf0J/132'," \
               r" 'subscribe_time': 1515740901, 'remark': '', 'groupid': 0, 'tagid_list': []}
        subsripter = Subscriber(dic)
        self.assertEqual('o6a4U0grN2cwJKSu_2tFQN6THWrw', subsripter.openid)
        print(subsripter)
