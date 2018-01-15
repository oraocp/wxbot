# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：测试wenxin.utils中的方法
# 创建日期：2018/1/4
# -------------------------------------------------------------------------
import string
from unittest import TestCase
from xml.etree.ElementTree import ParseError

from weixin.utils import *
from hashlib import sha1

class TestUtils(TestCase):

    def get_signature(token, timestamp, nonce ):
        sign = [token, timestamp, nonce]
        sign.sort()
        sign = sign
        return sha1(sign).hexdigest()

    def test_check_signature(self):
        signature = "e6281974b61927e31886dea53108664cf130f045"
        timestamp = "1515914909"
        nonce = "691998230"
        self.assertTrue(check_signature("resplendsky", timestamp, nonce, signature))

    def test_msgtodict(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[公众号]]></ToUserName>" \
                  r"<FromUserName><![CDATA[粉丝号]]></FromUserName>" \
                  r"<CreateTime>1460537339</CreateTime>" \
                  r"<MsgType><![CDATA[text]]></MsgType>" \
                  r"<Content><![CDATA[欢迎开启公众号开发者模式]]></Content>" \
                  r"<MsgId>6272960105994287618</MsgId>" \
                  r"</xml>"

        dic = msgtodict(xmldata)
        self.assertEqual(dic["ToUserName"], '公众号')

    def test_msgtodict2(self):
        xmldata = r"<xml>" \
                  r"<ToUserName><![CDATA[公众号]]></ToUserName>" \
                  r"<FromUserName><![CDATA[粉丝号]]></FromUserName>" \
                  r"<CreateTime>1460537339</CreateTime>" \
                  r"<Article><ID>1212</ID><AUTHOR>JACK</AUTHOR></Article>" \
                  r"<MsgType><![CDATA[text]]></MsgType>" \
                  r"<Content><![CDATA[欢迎开启公众号开发者模式]]></Content>" \
                  r"<MsgId>6272960105994287618</MsgId>" \
                  r"</xml>"
        dic = msgtodict(xmldata)
        # 不支持包含子节点的元素
        self.assertIsNone(dic["Article"])
        self.assertEqual(dic["ToUserName"], '公众号')
        self.assertEqual(dic["CreateTime"], '1460537339')

    def test_msgtodict3(self):
        wrong_xmldata = r"<xml>" \
                        r"<ToUserName><![CDATA[公众号]]></ToUserName>" \
                        r"<FromUserName><![CDATA[粉丝号]]></FromUserNameWrong>" \
                        r"<CreateTime>1460537339</CreateTime>" \
                        r"<MsgType><![CDATA[text]]></MsgType>" \
                        r"<Content><![CDATA[欢迎开启公众号开发者模式]]></Content>" \
                        r"<MsgId>6272960105994287618</MsgId>" \
                        r"</xml>"
        # 测试异常
        self.assertRaises(ParseError, msgtodict, wrong_xmldata)
        # 测试异常的常规写法
        try:
            # 传入XML格式出错
            msgtodict(wrong_xmldata)
            self.fail("解析错误XML文件，未抛出异常")
        except ParseError as e:
            print('解析错误XML文件捕捉到的异常信息为:', e)

    def test_rand_str(self):
        print(rand_str(10, string.digits))
        print(rand_str(10, string.digits + string.ascii_letters))

    def test_newinstance(self):
        class_name = "weixin.messages.TextInputMessage"
        dic = {"ToUserName": "2323-232323", "FromUserName": "abdc-dsddss", "MsgId": "M-232322",
               "MsgType": "text", "CreateTime": "232323", "Content": "微信发送的消息"}
        msg = Activator.new_instance(class_name, dic)
        # msg = TextInputMessage(dic)
        self.assertEqual(msg.toUserName, "2323-232323")
        self.assertEqual(msg.content, "微信发送的消息")
