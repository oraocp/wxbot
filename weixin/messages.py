# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：定义服务器从微信接收到的消息对象
# 创建日期：2018/1/3
# -------------------------------------------------------------------------

# 微信提供的消息类型
MESSAGE_TYPES = {}


def register_message(msg_type):
    def register(cls):
        MESSAGE_TYPES[msg_type] = cls
        return cls

    return register


# ---------------------------------------------------------------------------
#   Handler
# ---------------------------------------------------------------------------

class BaseMessage(object):
    """
    微信发送XML消息的基本类型
    """

    def __init__(self, dic):
        # 开发者微信号
        self.toUserName = dic['ToUserName']
        # 发送方账号(一个OpenId)
        self.fromUserName = dic['FromUserName']
        # 消息创建时间（整型）
        self.createTime = dic['CreateTime']
        # 消息类型
        self.msgType = dic['MsgType']


# ---------------------------------------------------------------------------
#   InputMessage
# ---------------------------------------------------------------------------

class InputMessage(BaseMessage):
    """
   微信发送消息的基本类型
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 消息id, 64位整型
        self.msgId = dic['MsgId']


@register_message('text')
class TextInputMessage(InputMessage):
    """
    微信发送的文本消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 文本消息内容
        self.content = dic['Content']


@register_message('image')
class ImageInputMessage(InputMessage):
    """
    微信图片消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 图片链接
        self.picUrl = dic['PicUrl']
        # 图片消息媒体id,可以调用多媒体文件下载接口摘取数据
        self.mediaId = dic['MediaId']


@register_message('voice')
class VoiceInputMessage(InputMessage):
    """
    微信语音消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 语音消息媒体id,可以调用多媒体文件下载接口摘取数据
        self.mediaId = dic['MediaId']
        # 语音格式，如amr, speex等
        self.format = dic['Format']
        # 语音识别结果，UTF8编码
        self.recognition = dic.get('Recognition', '')


@register_message('video')
class VideoInputMessage(InputMessage):
    """
    微信视频消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 视频消息媒体id,可以调用多媒体文件下载接口摘取数据
        self.mediaId = dic['MediaId']
        # 视频消息缩略图的媒体id,可以调用多媒体文件下载接口摘取数据
        self.thumbMediaId = dic['ThumbMediaId']


@register_message('shortvideo')
class ShortVideoInputMessage(VideoInputMessage):
    """
    微信小视频信息
    """

    def __init__(self, dic):
        super().__init__(dic)


@register_message('location')
class LocationInputMessage(InputMessage):
    """
    微信地理位置消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 地理位置维度X
        self.location_x = dic['Location_X']
        # 地理位置维度Y
        self.location_y = dic['Location_Y']
        # 地理缩放大小
        self.scale = dic.get('Scale', '1')
        # 地理位置信息
        self.label = dic['Label']

    def location(self):
        return self.location_x, self.location_y


@register_message('link')
class LinkInputMessage(InputMessage):
    """
    微信链接消息
    """

    def __init__(self, dic):
        super().__init__(dic)
        # 消息标题
        self.title = dic['Title']
        # 消息描述
        self.description = dic['Description']
        # 消息链接
        self.url = dic['Url']


class UnknownMessage(object):
    """
    未知的消息类型
    """

    def __init__(self, dic):
        self.dic = dic
        self.msgType = "Unkown"
