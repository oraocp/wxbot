>pip3 install django
>django-admin startproject wxbot
>cd wxbot
>python3 manage.py migrate
>python3 manage.py runserver 80


# ----------------------------------------------------------------------------
# ~ 以下事件， 仅支持微信iPhone5.4.1以上版本，和Android5.4以上版本的微信用户

class ScancodeMenuItem(MenuItem):
    """
    扫码推事件菜单。用户点击按钮后，微信客户端将调起扫一扫工具，
    完成扫码操作后显示扫描结果（如果是URL，将进入URL），且会将扫码的结果传给开发者，开发者可以下发消息
    """

    def __init__(self, name, key):
        MenuItem.__init__(self, name, "scancode_push")
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = key


class ScancodeWaitmsgMenuItem(MenuItem):
    """
    扫码推事件的菜单，弹出“消息接收中”提示框.
    用户点击按钮后，微信客户端将调起扫一扫工具，完成扫码操作后，将扫码的结果传给开发者，同时收起扫一扫工具，然后弹出“消息接收中”提示框，随后可能会收到开发者下发的消息。
    """

    def __init__(self, name, key):
        MenuItem.__init__(self, name, "scancode_waitmsg")
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = key


class PicSysPhotoMenuItem(MenuItem):
    """
    弹出系统拍照发图的菜单。
    用户点击按钮后，微信客户端将调起系统相机，
    完成拍照操作后，会将拍摄的相片发送给开发者，并推送事件给开发者，同时收起系统相机，随后可能会收到开发者下发的消息。
    """

    def __init__(self, name, key):
        MenuItem.__init__(self, name, "sys_photo")
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = key


class PicPhotoOrAlbumMenuItem(MenuItem):
    """
    弹出拍照或者相册发图的菜单。
    用户点击按钮后，微信客户端将弹出选择器供用户选择“拍照”或者“从手机相册选择”。
    用户选择后即走其他两种流程。
    """

    def __init__(self, name, key):
        MenuItem.__init__(self, name, "pic_photo_or_album")
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = key


class PicWeixinMenuItem(MenuItem):
    """
    弹出微信相册图器的菜单。
    用户点击按钮后，微信客户端将调起微信相册，
    完成选择操作后，将选择的相片发送给开发者的服务器，并推送事件给开发者，同时收起相册，随后可能会收到开发者下发的消息
    """

    def __init__(self, name, key):
        MenuItem.__init__(self, name, "pic_weixin")
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = key


class LocationSelectMenuItem(MenuItem):
    """
    弹出地理位置选择器的菜单。
    用户点击按钮后，微信客户端将调起地理位置选择工具，完成选择操作后，将选择的地理位置发送给开发者的服务器，
    同时收起位置选择工具，随后可能会收到开发者下发的消息
    """

    def __init__(self, name, key):
        MenuItem.__init__(self, name, "location_select")
        # 菜单KEY值，用于消息接口推送，不超过128字节
        self.key = key


class MiniPrgoramMenuItem(MenuItem):
    """
    小程序类型菜单。
    """

    def __init__(self, name, url, appid, pagepath):
        MenuItem.__init__(self, name, "miniprogram")
        # 不支持小程序的老版本客户端将打开本url
        self.url = url
        # 小程序的appid（仅认证公众号可配置）
        self.appid = appid
        # 小程序的页面路径
        self.pagepath = pagepath


# ----------------------------------------------------------------------------
# ~ 以下事件，是专门给第三方平台旗下未微信认证（具体而言，是资质认证未通过）的订阅号准备的事件类型，
# ~ 它们是没有事件推送的，能力相对受限，其他类型的公众号不必使用

class MediaIdMenuItem(MenuItem):
    """
    下发消息（除文本消息）菜单。
    用户点击media_id类型按钮后，微信服务器会将开发者填写的永久素材id对应的素材下发给用户，
    永久素材类型可以是图片、音频、视频、图文消息。
    请注意：永久素材id必须是在“素材管理/新增永久素材”接口上传后获得的合法id
    """

    def __init__(self, name, media_id):
        MenuItem.__init__(self, name, "media_id")
        #
        self.media_id = media_id


class ViewLimitedMenuItem(MenuItem):
    """
    跳转图文消息菜单。
    用户点击view_limited类型按钮后，微信客户端将打开开发者在按钮中填写的永久素材id对应的图文消息URL，
    永久素材类型只支持图文消息。请注意：永久素材id必须是在“素材管理/新增永久素材”接口上传后获得的合法id。
    """

    def __init__(self, name, media_id):
        MenuItem.__init__(self, name, "view_limited")
        #
        self.media_id = media_id
