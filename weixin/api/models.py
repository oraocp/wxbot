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
    Image = "image",
    # 语音
    Voice = "voice",
    # 视频
    Video = "video",
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
#   Subscriber & Group
# ---------------------------------------------------------------------------

def Subscriber(Jsonable):
    """

    :param Jsonable:
    :return:
    """

    def __init__(self, dct):
        self.openid = dct["openid"]
        self.subscribe = dct[""]
        self.nickname = dict.get("nickname", "")
        self.sex = dct.get("sex", -1)
        self.city = dct.get("city", "")
        self.country = dct.get("country", "")
        self.language = dict.get("language", "")
        self.headimgurl = dict.get("headimgurl", "")
        self.subscribe_time = dict.get("subscribe_time", 0)
        self.unionid = dict.get("unionid", "")
        self.remark = dct.get("remark", "")
        self.groupid = dct.get("groupid")
        self.tagids = []


def Group(Jsonable):
    """

    :param Jsonable:
    :return:
    """

    def __init__(self, dict):
        # 分组标识
        self.id = dict["id"]
        # 分组名称
        self.name = dict["name"]
        # 组内用户数量
        self.count = 0
