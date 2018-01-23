# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：测试微信API的用法
# 创建日期：2018/1/3
# -------------------------------------------------------------------------

from unittest import TestCase

from weixin.api.client import WxClient
from weixin.api.models import *
from weixin.api.menu import *


class WxClientClass(TestCase):
    def setUp(self):
        self.client = WxClient(
            # appid="wxff1ec8c09ae8c622",
            # secret="a261f13b3f1067894616608fc08ef944"
            appid="wx879cbaef5d53c126",
            secret="4f2b9aa36e9bffc2b595c4285c1c85f8"
        )
        # set_logger()

    def test_get_ip_list(self):
        """
        测试获取微信服务器列表API
        """
        ip_list = self.client.get_ip_list()
        self.assertIsNotNone(ip_list)
        self.assertTrue(len(ip_list) > 0)

    def test_grant_token(self):
        """
        测试微信Token令牌授权API
        """
        token1 = self.client.grant_token()
        token2 = self.client.grant_token()
        self.assertNotEqual(token1.token, token2.token, "两次调用产生的凭证Token是一样的，应该不一样")

    def test_menu(self):
        """
        测试微信自定义菜单API
        """

        # 1.取现有自定义菜单
        menu = self.client.get_menus()
        print(menu.to_json())
        self.assertTrue( len(menu.items) >= 0)

        # 2.删除所有菜单
        self.client.remove_menus()
        menu2 = self.client.get_menus()
        print(menu2)
        self.assertTrue(len(menu2.items) == 0)

        # 3.创建菜单

        menu_data = r'{"button":[{"name":"一键投保","sub_button":[{"type":"click","name":"购买车险","key":"GMCX",' \
                    r'"sub_button":[]},{"type":"view","name":"在线支付",' \
                    r'"url":"http:\/\/test1.95590.cn\/livebot\/OAuth2\/main?state=http:\/\/test1.95590.cn\/ccicws' \
                    r'\/CCICWXProject\/onlinePayment.html","sub_button":[]},{"type":"view","name":"查询支付",' \
                    r'"url":"http:\/\/test1.95590.cn\/livebot\/OAuth2\/main?state=http:\/\/test1.95590.cn\/ccicws' \
                    r'\/CCICWXProject\/dispatch.html?dynid=SB0446","sub_button":[]},{"type":"view","name":"我的订单",' \
                    r'"url":"http:\/\/test1.95590.cn\/livebot\/OAuth2\/main?state=http:\/\/test1.95590.cn\/ccicws' \
                    r'\/CCICWXProject\/proposalList.html","sub_button":[]}]},{"type":"view","name":"一键报案",' \
                    r'"url":"http:\/\/test1.95590.cn\/livebot\/OAuth2\/main?state=http:\/\/test1.95590.cn\/ccicws' \
                    r'\/CCICWXProject\/policyList.html","sub_button":[]},{"name":"尊享服务","sub_button":[{' \
                    r'"type":"click","name":"我的客服","key":"RGKF","sub_button":[]},{"type":"view","name":"增值服务",' \
                    r'"url":"http:\/\/test1.95590.cn\/livebot\/OAuth2\/main?state=http:\/\/test1.95590.cn\/ccicws' \
                    r'\/CCICWXProject\/dispatch.html?dynid=SB2007","sub_button":[]},{"type":"click","name":"我的保单",' \
                    r'"key":"WDBD","sub_button":[]},{"type":"click","name":"我的理赔","key":"WDLP","sub_button":[]}]}]} '
        dic = json.loads(menu_data)
        menu3 = WxMenu(dic)
        # menu3.items[0].add_submenuitem(ViewMenuItem({"name": "百度一下", "url": "http://m.baidu.com/"}))
        self.client.create_menus(menu3.to_json().encode('utf-8'))

        # 4. 重新取现有自定义菜单
        menu4 = self.client.get_menus()
        self.assertIsNotNone(menu4)
        # 测试菜单模型的串行化
        dic = json.loads(menu4.to_json())
        menu5 = WxMenu(dic)
        self.assertEqual(len(menu4.items), len(menu5.items))
        for i in range(0, len(menu4.items)):
            self.assertEqual(menu4.items[i].name, menu5.items[i].name)

    def test_media(self):
        """
        测试临时素材API
        """
        # 1 上传素材
        with open("loadinglit.gif", "rb") as f:
            media_id = self.client.upload_media(MediaType.Image, f)
        # 2. 下载素材
        with open('temp1.gif', 'wb') as cf1:
            # 默认使用流模式下载
            self.client.download_media(media_id, cf1)
        with open('temp2.gif', 'wb') as cf2:
            # 使用加载内存方式下载
            self.client.download_media(media_id, cf2, False)

    def test_material(self):
        """
        测试永久素材API
        :return:
        """
        # 1. 上传永久素材图片
        # open("ad1.jpg", encoding="utf-8") 出现  'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
        # 错误原因是因为文件不是 UTF8 编码的（例如，可能是 GBK 编码的），而系统默认采用 UTF8 解码
        # 解决方法是指定文件打开的模式为字节方式'rb'
        with open("ad1.jpg", mode="rb") as f:
            media_id = self.client.upload_material(MediaType.Image, f)
        # 2. 下载永久素材图片
        with open("temp3.jpg", mode="wb") as w:
            self.client.download_material(media_id, w)
        # 3. 获取永久素材列表
        mc = self.client.get_material_count()
        self.assertTrue(mc.image_count >= 0)
        print("material_count:", mc)
        # 4. 获取永久素材图片

        # 5. 移除新上传的图片
        self.client.remove_material(media_id)



    def _test_material_viedo(self):
        # 测试上传视频永久素材
        with open("fu.mp4", mode="rb") as f:
            media_id = self.client.upload_material_video("春节福来到", "随着灯笼摆动，喜气四处飘散，福满人间.", f)
        mc = self.client.get_material_count()
        self.assertTrue(mc.video_count > 0)
        print("material_count:", mc)
        # 删除数据时会报：47001, 'data format error hint
        self.client.remove_material(media_id)

    def test_user_tags(self):
        """
        测试用户标签
        """
        # 1 创建组
        nt = self.client.create_tag("明日之星")
        print(nt)
        # 2.获取所有的组
        tags = self.client.get_all_tags()
        for t in tags:
            print(t)
        # 3.删除新创建的组
        self.client.remove_tag(nt.id)

    def test_users(self):
        # 获取所有的用户
        userinfos = self.client.get_userlist()
        print(userinfos)
        # 获取单个用户信息
        if userinfos.count > 0:
            openid = userinfos.openids[0]
            print(self.client.get_userinfo(openid))
