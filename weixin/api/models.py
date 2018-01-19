# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/4
# -------------------------------------------------------------------------

import json
import time
from enum import Enum


class Jsonable(object):
    def to_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.to_json()


# ---------------------------------------------------------------------------
#   Media
# ---------------------------------------------------------------------------

class MediaType(Enum):
    """
    定义上传的多媒体类型
    """
    # 图片
    Image = "image"
    # 语音
    Voice = "voice"
    # 视频
    Video = "video"
    # 缩略图
    Thumb = "thumb"


# ---------------------------------------------------------------------------
#   AccessToken
# ---------------------------------------------------------------------------

class AccessToken(Jsonable):
    """
    第三方用户凭证
    """

    def __init__(self, token, expires, create_time=None):
        """
        建立第三方用户凭证对象
        :param token: 获取到的凭证
        :param expires: 凭证有效时间，单位为秒
        """
        Jsonable.__init__(self)
        self.token = token
        self.expires = expires
        self.create_time = create_time or int(time.time())

    def is_expired(self):
        """
        判断凭证是否过期，比过期时间提前60秒更新
        :return: 如果凭证过期，则返回True；否则返回False
        """
        return self.expires < (time.time() - self.create_time + 60)


# ---------------------------------------------------------------------------
#   订阅者及用户组
# ---------------------------------------------------------------------------

class Subscriber(Jsonable):
    """
    定义关注者对象
    :param Jsonable:
    :return:
    """

    def __init__(self, dic):
        Jsonable.__init__(self)
        self.openid = dic["openid"]
        self.subscribe = dic["subscribe"]
        self.nickname = dic.get("nickname", "")
        self.sex = dic.get("sex", -1)
        self.city = dic.get("city", "")
        self.country = dic.get("country", "")
        self.language = dic.get("language", "")
        self.headimgurl = dic.get("headimgurl", "")
        self.subscribe_time = dic.get("subscribe_time", 0)
        self.unionid = dic.get("unionid", "")
        self.remark = dic.get("remark", "")
        self.groupid = dic.get("groupid")
        tagids = dic.get("tagids", None)
        self.tagids = []
        if not(tagids is None):
            for tagid in tagids:
                self.tagids.append(tagid)


class SubscriberInfos(Jsonable):
    """
    关注者列表信息
    """

    def __init__(self, dic):
        print(dic)
        Jsonable.__init__(self)
        # 关注该公众账号的总用户数
        self.total = dic["total"]
        # 拉取的OPENID个数，最大值为10000
        self.count = dic["count"]
        # 列表数据，OPENID的列表
        self.openids = []
        data = dic["data"]
        for openid in data["openid"]:
            self.openids.append(openid)
        # 拉取列表的最后一个用户的OPENID
        self.next_openid = dic.get("next_openid", None)
        # 是否还有数据可以拉取
        self.has_next = False
        if self.count > 0 and not (self.next_openid is None):
            self.has_next = self.next_openid == self.openids[self.count - 1]


class Group(Jsonable):
    """
    定义粉丝组对象
    :param Jsonable:
    :return:
    """

    def __init__(self, id, name, count=0):
        Jsonable.__init__(self)
        # 分组标识
        self.id = id
        # 分组名称
        if isinstance(name, bytes):
            name = name.decode()
        self.name = name  # 转unicode字符?
        # 组内用户数量
        self.count = count


# ---------------------------------------------------------------------------
#   永久素材管理
# ---------------------------------------------------------------------------
class MaterialCount(Jsonable):
    """
    永久素材的总数，也会计算公众平台官网素材管理中的素材
    图片和图文消息素材（包括单图文和多图文）的总数上限为5000，其他素材的总数上限为1000
    """

    def __init__(self, voice_count, video_count, image_count):
        self.voice_count = voice_count
        self.video_count = video_count
        self.image_count = image_count


class MaterailItem(object):
    def __init__(self, dct):
        pass


class VideoItem(object):
    """

    """

    def __init__(self, dic):
        self.title = dic.get("title")
        self.description = dic.get("descripton")
        self.down_url = dic.get("down_url")


class ArticleItem(object):
    """

    """

    def __init__(self, dic):
        # 图文消息的标题
        self.title = dic["title"]
        # 图文消息的封面图片素材id（必须是永久mediaID）
        self.thumb_media_id = dic["thumb_media_id"]
        # 是否显示封面，0为false，即不显示，1为true，即显示
        self.show_cover_pic = dic["show_cover_pic"]
        # 作者
        self.author = dic["author"]
        # 图文消息的摘要，仅有单图文消息才有摘要，多图文此处为空
        self.digest = dic["digest"]
        # 图文消息的具体内容，支持HTML标签，必须少于2万字符，小于1M，且此处会去除JS
        self.content = dic["content"]
        # 图文页的URL
        self.url = dic.get("url")
        # 图文消息的原文地址，即点击“阅读原文”后的URL
        self.content_source_url = dic["content_source_url"]


class MaterialList(object):
    def __init__(self, total_count, item_count, items):
        self.total_count = total_count
        self.item_count = item_count
        self.items = items
