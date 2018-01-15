# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：定义微信服务器以事件推送形式通知的事件
# 创建日期：2018/1/3
# -------------------------------------------------------------------------

from weixin.messages import BaseMessage

EVENT_TYPES = {}
SUBSCRIBE_QRSCENE = "qrscene_"


def register_event(event_type):
    def register(cls):
        if event_type in EVENT_TYPES.keys():
            raise ValueError("重复的事件类型:" + event_type)
            EVENT_TYPES[event_type] = cls
        return cls

    return register


class EventMessage(BaseMessage):
    """
    定义微信服务器推送的基本事件消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 事件类型
        self.event = dic["Event"]


class EventKeyMessage(EventMessage):
    """
    定义微信服务器推送的明细事件消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 事件Key值
        self.eventKey = dic["EventKey"]


class EventTicketMessage(EventKeyMessage):
    """
    定义微信服务器推送的二维码事件信息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 事件Key值
        self.ticket = dic["Ticket"]


# ----------------------------------------------------------------------
# 关注、取消关注事件

@register_event("subscribe")
class SubscribeEvent(EventMessage):
    """
    用户关注公众号时的事件推送
    """
    pass


@register_event("unsubscribe")
class UnSubscribeEvent(EventMessage):
    """
    用户取消关注公众号时的事件推送
    """
    pass


# ----------------------------------------------------------------------
# 扫描带参数二维码事件

@register_event("scan")
class ScanEvent(EventTicketMessage):
    """

    """
    pass


@register_event("subscribe.qrscene")
class SubscribeScanEvent(EventTicketMessage):
    """
    用户未关注时，通过扫描带场景值关注公众号时的事件推送
    """

    def __init__(self, dic):
        super().__init__(dic)
        self.qrvalue = self.eventKey[len(SUBSCRIBE_QRSCENE):]


# ----------------------------------------------------------------------
# 地理位置事件相关

@register_event("location")
class LocationEvent(EventMessage):
    """

    """

    def __init__(self, dic):
        super().__init__(dic)
        # 地理位置纬度
        self.latitude = dic["Latitude"]
        # 地理位置经度
        self.longitude = dic["Longitude"]
        # 地理位置精度
        self.precision = dic["Precision"]


# ----------------------------------------------------------------------
# 自定义菜单事件相关

@register_event("click")
class ClickEvent(EventKeyMessage):
    """
    点击菜单拉取消息时的事件推送
    """
    pass


@register_event("view")
class ViewEvent(EventKeyMessage):
    """
    点击菜单跳转链接时的事件推送
    """
    pass


@register_event("scancode_push")
class ScancodePushEvent(EventKeyMessage):
    """
    点击扫码二维码事件的菜单时，系统通知的事件
    """
    pass


@register_event("scancode_waitmsg")
class ScancodeWaitmsgEvent(EventKeyMessage):
    """
    点击扫码二维码事件并带弹框的菜单时，系统通知的事件
    """
    pass


@register_event("pic_weixin")
class PicSysphotoEvent(EventKeyMessage):
    """
    点击弹出系统拍照发图的菜单时，系统通知的事件
    """
    pass


@register_event("pic_photo_or_album")
class PicPhtoOrAlbumEvent(EventKeyMessage):
    """
    点击弹出拍照或者相册发图的菜单时，系统通知的事件。
    """
    pass


@register_event("location_select")
class LocationSelectEvent(EventKeyMessage):
    """
    点击弹出地理位置选择器的菜单时，系统通知的事件
    """
    pass
