# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：输出回复微信服务器的消息文本
# 创建日期：2018/1/2
# 说明：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140543
# -------------------------------------------------------------------------

import time


def _create_time(timestamp):
    return timestamp or str(int(time.time()))


_TEXT_XML = r"<xml>" \
            r"<ToUserName><![CDATA[{0}]]></ToUserName>" \
            r"<FromUserName><![CDATA[{1}]]></FromUserName>" \
            r"<CreateTime>{2}</CreateTime>" \
            r"<MsgType><![CDATA[text]]></MsgType>" \
            r"<Content><![CDATA[{3}]]></Content>" \
            r"</xml>"


def render_text(openid, userid, content, timestamp=None):
    """
    回复文本消息
    """
    return _TEXT_XML.format(
        openid, userid, _create_time(timestamp), content
    )


_IMAGE_XML = r"<xml>" \
             r"<ToUserName><![CDATA[{0}]]></ToUserName>" \
             r"<FromUserName><![CDATA[{1}]]></FromUserName>" \
             r"<CreateTime>{2}</CreateTime>" \
             r"<MsgType><![CDATA[image]]></MsgType>" \
             r"<Image><MediaId><![CDATA[{3}]]></MediaId></Image>" \
             r"</xml>"

_VOICE_XML = r"<xml>" \
             r"<ToUserName><![CDATA[{0}]]></ToUserName>" \
             r"<FromUserName><![CDATA[{1}]]></FromUserName>" \
             r"<CreateTime>{2}</CreateTime>" \
             r"<MsgType><![CDATA[voice]]></MsgType>" \
             r"<Image><MediaId><![CDATA[{3}]]></MediaId></Image>" \
             r"</xml>"

_VIDEO_XML = r"<xml>" \
             r"<ToUserName><![CDATA[{0}]]></ToUserName>" \
             r"<FromUserName><![CDATA[{1}]]></FromUserName>" \
             r"<CreateTime>{2}</CreateTime>" \
             r"<MsgType><![CDATA[video]]></MsgType>" \
             r"<Video>" \
             r"<MediaId><![CDATA[{3}]]></MediaId>" \
             r"<Title><![CDATA[{4}]]></Title>" \
             r"<Description><![CDATA[{5}]]></Description>" \
             r"</Video>" \
             r"</xml>"

_MUSIC_XML = r"<xml>" \
             r"<ToUserName><![CDATA[{0}]]></ToUserName>" \
             r"<FromUserName><![CDATA[{1}]]></FromUserName>" \
             r"<CreateTime>{2}</CreateTime>" \
             r"<MsgType><![CDATA[music]]></MsgType>" \
             r"<Music>" \
             r"<Title><![CDATA[{3}]]></Title>" \
             r"<Description><![CDATA[{4}]]></Description>" \
             r"<MusicUrl><![CDATA[{5}]]></MusicUrl>" \
             r"<HQMusicUrl><![CDATA[{6}]]></HQMusicUrl>" \
             r"<ThumbMediaId><![CDATA[{7}]]></ThumbMediaId>" \
             r"</Music>" \
             r"</xml>"

_NEWS_XML = r"<xml>" \
            r"<ToUserName><![CDATA[{0}]]></ToUserName>" \
            r"<FromUserName><![CDATA[{1}]]></FromUserName>" \
            r"<CreateTime>{2}</CreateTime>" \
            r"<MsgType><![CDATA[news]]></MsgType>" \
            r"<ArticleCount>{3}</ArticleCount>" \
            r"<Articles>" \
            r"{4}" \
            r"</Articles>" \
            r"</xml>"

_ARTICLE_XML = r"<item>" \
               r"<Title><![CDATA[{3}]]></Title>" \
               r"<Description><![CDATA[{4}]]></Description>" \
               r"<PicUrl><![CDATA[{5}]]></PicUrl>" \
               r"</item>"


class Article(object):
    """
    表示图文消息
    """

    def __init__(self, title, desc, picurl):
        self.title = title
        self.desc = desc
        self.picurl


class Renderer(object):
    """
    输出回复微信服务器的消息文本
    """

    def __init__(self, appid):
        # 开发者微信号
        self.fromUserName = appid

    def render_text(self, openid, content, timestamp=None):
        """
        回复文本消息
        :param openid: 接收方帐号
        :param content: 回复的消息内容（换行：在content中能够换行，微信客户端就支持换行显示）
        :param timestamp: 消息创建时间 （整型）
        :return: 微信格式的XML文本
        """
        return render_text(self.fromUserName, openid, content, timestamp)

    def render_image(self, openid, mediaId, timestamp=None):
        """
        回复图片消息
        :param openid: 接收方帐号
        :param mediaId:通过素材管理中的接口上传多媒体文件，得到的id
        :param timestamp:消息创建时间 （整型）
        :return:微信格式的XML文本
        """
        return _IMAGE_XML.format(
            openid, self.fromUserName, _create_time(timestamp), mediaId
        )

    def render_voice(self, openid, mediaId, timestamp=None):
        """
        回复消息
        :param openid: 接收方帐号
        :param mediaId:通过素材管理中的接口上传多媒体文件，得到的id
        :param timestamp:消息创建时间 （整型）
        :return:微信格式的XML文本
        """
        return _VOICE_XML.format(
            openid, self.fromUserName, mediaId, _create_time(timestamp)
        )

    def render_video(self, openid, title, desc, mediaId, timestamp=None):
        """
        回复图片消息
        :param openid: 接收方帐号
        :param title:
        :param desc:
        :param mediaId:通过素材管理中的接口上传多媒体文件，得到的id
        :param timestamp: 消息创建时间 （整型）
        :return: 微信格式的XML文本
        """
        return _VIDEO_XML.format(
            openid, self.fromUserName, mediaId, _create_time(timestamp), title, desc
        )

    def render_music(self, openid, title, desc, mediaId, musicurl, hqmusicurl, timestamp=None):
        """

        :param openid:
        :param title:
        :param desc:
        :param mediaId:
        :param musicurl:
        :param hqmusicurl:
        :param timestamp:
        :return: 微信格式的XML文本
        """
        return _MUSIC_XML.format(
            openid, self.fromUserName, mediaId, _create_time(timestamp), title, desc
        )

    def render_news(self, openid, articles, timestamp=None):
        """

        :param openid:
        :param articles:
        :param timestamp:
        :return: 微信格式的XML文本
        """
        pass
