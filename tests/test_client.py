# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：测试微信API的用法
# 创建日期：2018/1/3
# -------------------------------------------------------------------------

from unittest import TestCase

from weixin.api.client import WxClient
from weixin.logger import set_logger
from weixin.api.models import *


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
        self.assertIsNotNone(ip_list)
        self.assertTrue(len(ip_list) > 0)

    def test_grant_token(self):
        token1 = self.client.grant_token()
        token2 = self.client.grant_token()
        self.assertNotEqual(token1.token, token2.token, "两次调用产生的凭证Token是一样的，应该不一样")

    def test_get_menu(self):
        menu_data = self.client.get_menus()
        self.assertIsNotNone(menu_data)
        print(menu_data)

    def _test_media(self):
        # 测试临时素材
        with open("loadinglit.gif", "rb") as f:
            media_id = self.client.upload_media(MediaType.Image, f)
        with open('temp1.gif', 'wb') as cf1:
            # 默认使用流模式下载
            self.client.download_media(media_id, cf1)
        with open('temp2.gif', 'wb') as cf2:
            self.client.download_media(media_id, cf2, False)

    def _test_material(self):
        # 测试上传一般永久素材
        # open("ad1.jpg", encoding="utf-8") 出现  'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
        # 错误原因是因为文件不是 UTF8 编码的（例如，可能是 GBK 编码的），而系统默认采用 UTF8 解码
        # 解决方法是指定文件打开的模式为字节方式'rb'
        with open("ad1.jpg", mode="rb") as f:
            media_id = self.client.upload_material(MediaType.Image, f)
        mc = self.client.get_material_count()
        self.assertTrue(mc.image_count > 0)
        print("material_count:", mc)
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

    def test_fans_group(self):
        # 获取所有的组
        self.client.remove_group(100)
        groups = self.client.get_all_group()
        for group in groups:
            print(group)
            # 创建组
            # g = self.client.create_group("钻石王老五")
            # print(g)

            # if group:
            # print(self.client.update_group(100, "群众2"))
            # print(self.client.update_group(100, gname))

    def test_fans(self):
        # 获取所有的用户
        userinfos = self.client.get_userlist()
        print(userinfos)
        # 获取单个用户信息
        if userinfos.count > 0:
            openid = userinfos.openids[0]
            print(self.client.get_userinfo(openid))
