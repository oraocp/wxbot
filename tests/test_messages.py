# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：测试wenxin.messages中的定义的微信消息解析
# 创建日期：2018/1/3
# -------------------------------------------------------------------------
from unittest import TestCase

from weixin.messages import *
from weixin.utils import msgtodict,parse_message


class TestMessages(TestCase):
    def test_textmessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[text]]></MsgType>" \
                  r"<Content><![CDATA[这是测试数据]]></Content>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"
        print(xmldata)
        dic = msgtodict(xmldata)
        text_message = parse_message(dic)
        self.assertTrue(isinstance(text_message, TextInputMessage), "类型不是文本消息")
        self.assertEqual(text_message.content, "这是测试数据")

    def test_imagemesage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[image]]></MsgType>" \
                  r"<PicUrl><![CDATA[这是测试URL]]></PicUrl>" \
                  r"<MediaId><![CDATA[media_id]]></MediaId>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        image_message = parse_message(dic)
        self.assertTrue(isinstance(image_message, ImageInputMessage), "类型不是图片消息")
        self.assertEqual(image_message.picUrl, "这是测试URL")
        self.assertEqual(image_message.mediaId, "media_id")

    def test_voicemessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[voice]]></MsgType>" \
                  r"<MediaId><![CDATA[media_id]]></MediaId>" \
                  r"<Format><![CDATA[Format]]></Format>" \
                  r"<Recognition><![CDATA[腾讯微信团队]]></Recognition>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        voice_message = parse_message(dic)
        self.assertTrue(isinstance(voice_message, VoiceInputMessage), "类型不是语音消息")
        self.assertEqual(voice_message.mediaId, "media_id")
        self.assertEqual(voice_message.format, "Format")
        self.assertEqual(voice_message.recognition, "腾讯微信团队")

    def test_videomessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[video]]></MsgType>" \
                  r"<MediaId><![CDATA[media_id]]></MediaId>" \
                  r"<ThumbMediaId><![CDATA[thumb_media_id]]></ThumbMediaId>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        video_message = parse_message(dic)
        self.assertTrue(isinstance(video_message, VideoInputMessage), "类型不是视频消息")
        self.assertEqual(video_message.mediaId, "media_id")
        self.assertEqual(video_message.thumbMediaId, "thumb_media_id")

    def test_shortvideomessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[shortvideo]]></MsgType>" \
                  r"<MediaId><![CDATA[short_media_id]]></MediaId>" \
                  r"<ThumbMediaId><![CDATA[short_thumb_media_id]]></ThumbMediaId>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        shortvideo_message = parse_message(dic)
        self.assertTrue(isinstance(shortvideo_message, ShortVideoInputMessage), "类型不是视频消息")
        self.assertEqual(shortvideo_message.mediaId, "short_media_id")
        self.assertEqual(shortvideo_message.thumbMediaId, "short_thumb_media_id")

    def test_locationmessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[location]]></MsgType>" \
                  r"<Location_X>23.134521</Location_X>" \
                  r"<Location_Y>113.358803</Location_Y>" \
                  r"<Scale>20</Scale>" \
                  r"<Label><![CDATA[位置信息]]></Label>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        location_message = parse_message(dic)
        self.assertTrue(isinstance(location_message, LocationInputMessage), "类型不是语音消息")
        self.assertEqual(location_message.location_x, "23.134521")
        self.assertEqual(location_message.location_y, "113.358803")
        self.assertEqual(location_message.scale, "20")
        self.assertEqual(location_message.label, "位置信息")

    def test_linkmessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[link]]></MsgType>" \
                  r"<Title><![CDATA[Title]]></Title>" \
                  r"<Description><![CDATA[公众平台官网链接]]></Description>" \
                  r"<Url><![CDATA[这是测试URL]]></Url>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        link_message = parse_message(dic)
        self.assertTrue(isinstance(link_message, LinkInputMessage), "类型不是语音消息")
        self.assertEqual(link_message.title, "Title")
        self.assertEqual(link_message.description, "公众平台官网链接")
        self.assertEqual(link_message.url, "这是测试URL")

    def test_unkownmessage(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[toUser]]></ToUserName>" \
                  r"<FromUserName><![CDATA[fromUser]]></FromUserName>" \
                  r"<CreateTime>1348831860</CreateTime>" \
                  r"<MsgType><![CDATA[WrongType]]></MsgType>" \
                  r"<Title><![CDATA[Title]]></Title>" \
                  r"<Description><![CDATA[公众平台官网链接]]></Description>" \
                  r"<Url><![CDATA[这是测试URL]]></Url>" \
                  r"<MsgId>1234567890123456</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        unkown_message = parse_message(dic)
        self.assertTrue(isinstance(unkown_message, UnknownMessage), "类型不是未知消息")
