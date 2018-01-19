# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：通过自定义菜单接口实现的菜单项类型
# 创建日期：2017-12-30
# https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
# -------------------------------------------------------------------------

from weixin.api.models import Jsonable
import json


class WxMenu(Jsonable):
    """
    自定义菜单对象，
    能够帮助公众号丰富界面，让用户更好更快地理解公众号的功能
    """

    def __init__(self, dic):
        self.items = []
        for button in dic["menu"]["button"]:
            if "type" in button.keys():
                # 叶子菜单（包括一级或二级）
                menuclass = MENUITEM_TYPES[button["type"]]
                menuitme = menuclass(button)
                self.items.append(menuitme)
            else:
                # 一级菜单
                submenu = MenuItem(button)
                for subbutton in button["sub_button"]:
                    # 二级菜单
                    menuclass = MENUITEM_TYPES[subbutton["type"]]
                    menuitme = menuclass(subbutton)
                    submenu.add_submenuitem(menuitme)
                self.items.append(submenu)


MENUITEM_TYPES = {}


class MenuItemMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        return type.__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        print("Call MenuItemMetaClass.__init__")
        if '__type__' in attrs:
            MENUITEM_TYPES[attrs['__type__']] = cls
        type.__init__(cls, name, bases, attrs)


class MenuItem(Jsonable, metaclass=MenuItemMetaClass):
    __type__ = "submenu"

    def __init__(self, dic):
        Jsonable.__init__(self)
        # 菜单标题，不超过16个字节，子菜单不超过60个字节
        self.name = dic["name"]
        self.sub_button = []

    def add_submenuitem(self, sub_menuitem):
        self.sub_button.append(sub_menuitem)


class ClickMenuItem(MenuItem):
    """
    点击类型菜单。微信服务器会通过消息接口推送消息类型为event的结构给开发者
    ，并且带上按钮中开发者填写的key值，开发者可以通过自定义的key值与用户进行交互；
    """

    __type__ = "click"

    def __init__(self, dic):
        MenuItem.__init__(self, dic)
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = dic["key"]

    def __repr__(self):
        return repr(self.name, self.key, self.sub_button)


class ViewMenuItem(MenuItem):
    """
    网页类型菜单。用户点击view类型按钮后，微信客户端将会打开开发者在按钮中填写的网页URL，
    可与网页授权获取用户基本信息接口结合，获得用户基本信息。
    """

    __type__ = "view"

    def __init__(self, dic):
        MenuItem.__init__(self, dic)
        # 网页链接，用户点击菜单可打开链接，不超过1024字节
        self.url = dic["url"]

    def __repr__(self):
        return repr(self.name, self.url, self.sub_button)
