# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：封装微信提供的API，方便系统调用
# 创建日期：2018/1/4
# 微信API官方文档地址为： https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1445241432
# -------------------------------------------------------------------------

import requests

from weixin.api.models import *
from weixin.exceptions import check_api_error, WxApiException
from weixin.logger import log
from weixin.utils import Lockable, deprecated
from weixin.api.menu import WxMenu


# ---------------------------------------------------------------------------
#   Requestor
# ---------------------------------------------------------------------------


class Requestor(object):
    def get(self, url, params=None):
        raise NotImplementedError('Requestor的子类没有实现http_get方法')

    def download_file(self, url, params=None, writer=None, stream=False, **kwargs):
        raise NotImplementedError('Requestor的子类没有实现download_file方法')

    def download_file(self, url, writer=None, stream=False, data=None, **kwargs):
        raise NotImplementedError('Requestor的子类没有实现http_post方法')


class DefaultRequstor(Requestor):
    """
    默认的HTTP请求处理器
    """

    def get(self, url, params=None, encoding='utf-8', **kwargs):
        r = requests.get(url, params=params, **kwargs)
        r.encoding = encoding
        # 假定微信返回的结果都是json字符串
        r = r.json()
        check_api_error(r)
        return r

    def download_file(self, url, writer, stream=False, data=None, **kwargs):
        if writer is None:
            raise ValueError("在Stream模式下下载文件时，输出流对象不能为空.")
        if data is None:
            r = requests.get(url, stream=stream, **kwargs)
        else:
            r = requests.post(url, data=data, **kwargs)
        # 修正bug-1， 即微信返回失败记录，如"{errcode;40017,errmsg:'media_id is not valid hint", 系统不返回失败
        # 导致会将错误文本当作记录写入到下载素材文件流中
        if "Content-Type" in r.headers.keys() and r.headers["Content-Type"] == 'text/plain':
            check_api_error(r.json())
        if stream:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    writer.write(chunk)
        else:
            writer.write(r.content)

    def post(self, url, params=None, data=None, files=None, headers=None, encoding='utf-8', **kwargs):
        r = requests.post(url, params=params, data=data, files=files, headers=headers, **kwargs)
        r.encoding = encoding
        # 假定微信返回的结果都是json字符串
        r = r.json()
        check_api_error(r)
        return r


# ---------------------------------------------------------------------------
#   WxClient
# ---------------------------------------------------------------------------

class WxClient(Lockable):
    """
    调用微信提供的API
    """

    def __init__(self, appid, secret, requestor=None, access_token=None):
        """

        :param appid: 第三方用户唯一凭证
        :param secret: 第三方用户唯一凭证密钥，即appsecret
        :param requestor: HTTP请求处理器
        """
        Lockable.__init__(self)
        self.appid = appid
        self.secret = secret
        self.requestor = requestor or DefaultRequstor()
        self.access_token = access_token

    @property
    def token(self):
        # Token存在于本机内存中，如果多机部署会存在问题？
        self.check_token()
        return self.access_token.token

    # ---------------------------------------------------------------------------
    # ~ 凭证相关

    def grant_token(self):
        """
        获得用户凭证，凭证是用来验证发送给服务器的消息是否来自微信后台
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}" \
            .format(self.appid, self.secret)
        r = self.requestor.get(url)
        log.debug("微信API返回结果为:{0}".format(r))
        return AccessToken(r["access_token"], r["expires_in"])

    def check_token(self):
        try:
            self.acquire_lock()
            if (self.access_token is None) or (self.access_token.is_expired()):
                self.access_token = self.grant_token()
        finally:
            self.release_lock()

    # ---------------------------------------------------------------------------
    # ~ 自定义菜单相关

    def create_menus(self, menu):
        """
        创建微信公众号的自定义菜单
        自定义菜单能够帮助公众号丰富界面，让用户更好更快地理解公众号的功能
        :param menu: WxMenu类型或者Json格式字符串
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}".format(self.token)
        # 如果是WxMenu类型，需将其转换为Json格式字符串
        if isinstance(menu, WxMenu):
            data = menu.to_json().encode('utf-8')
        else:
            data = menu
        r = self.requestor.post(url, data=data)
        return r

    def get_menus(self):
        """
        使用接口创建自定义菜单后，开发者还可使用接口查询自定义菜单的结构
        请注意，在设置了个性化菜单后，使用本自定义菜单查询接口可以获取默认菜单和全部个性化菜单信息
        参见:https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141014
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token={0}".format(self.token)
        try:
            r = self.requestor.get(url)
        except WxApiException as e:
            if e.errcode == 46003:
                # 对于菜单不存在的异常，返回空菜单对象
                return WxMenu(None)
            raise e
        return WxMenu(r)

    def remove_menus(self):
        """
        使用接口创建自定义菜单后，开发者还可使用接口删除当前使用的自定义菜单
        请注意，在个性化菜单时，调用此接口会删除默认菜单及全部个性化菜单
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141015
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={0}".format(self.token)
        try:
            r = self.requestor.get(url)
        except WxApiException as e:
            if e.errcode == 46003:
                # 对于菜单不存在的异常，返回空菜单对象
                return WxMenu(None)
            raise e
        return r

    # ---------------------------------------------------------------------------
    # ~ 临时素材文件相关， 媒体文件在微信后台保存时间为3天，即3天后media_id失效

    def upload_media(self, media_type, media_file):
        """
        上传临时素材文件
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738726
        :param media_type: 媒体类型
        :param media_file: 输入文件流
        :return: 返回微信提供的媒体标识Id
        """
        url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token={0}&type={1}".format(self.token,
                                                                                                media_type.value)
        r = self.requestor.post(url,
                                files={"media_file": media_file}
                                )
        return r["media_id"]

    def download_media(self, media_id, writer, stream=True):
        """
        下载临时素材文件
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738727
        :param media_id:  媒体标识
        :param writer:  输出流
        :param stream: 是否启用流模式，默认为True
        """
        url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token={0}&media_id={1}".format(self.token, media_id)
        self.requestor.download_file(url, writer, stream)

    # ---------------------------------------------------------------------------
    # ~ 永久素材相关

    def upload_material(self, media_type, media_file):
        """
        上传除视频外的其它类型永久素材
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738729
        :param media_type: 媒体文件类型，分别有图片（image）、语音（voice）、和缩略图（thumb）
        :param media_file: 媒体文件
        :return: 返回的即为新增的图文消息素材的media_id; 当上传类型为图片时，返回tuple结构的(media_id,url)
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={0}&type={1}". \
            format(self.token, media_type.value)
        r = self.requestor.post(url,
                                files={"media": media_file}
                                )
        if media_type == MediaType.Image:
            # 新增图片素材时会返回新增的图片素材的图片URL
            return r["media_id"], r["url"]
        return r["media_id"]

    def upload_video(self, title, introduction, media_file):
        """
        上传视频类型的永久素材
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738729
        :param title: 视频素材的标题
        :param introduction: 视频素材的描述
        :param media_file: 媒体文件
        :return: 新增的永久素材的media_id
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={0}&type={1}".format(self.token,
                                                                                                         MediaType.Video.value)
        params = {
            "description": '{"title":"%s", "introduction": "%s"}' % (title, introduction)
        }
        r = self.requestor.post(url,
                                params=params,
                                files={"media": media_file}
                                )
        return r["media_id"]

    def download_material(self, media_id, writer, stream=True):
        """
        下载其他类型的永久素材消息，则响应的直接为素材的内容，开发者可以自行保存为文件
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738730
        :param media_id:  媒体标识
        :param writer:  输出流
        :param stream: 是否启用流模式，默认为True
        """
        # 处理新增图片素材返回值的问题
        if isinstance(media_id, tuple):
            mid = media_id[0]
        else:
            mid = media_id
        url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={0}&media_id={1}".format(self.token,
                                                                                                             mid)
        data = '{"media_id":"%s"}' % mid
        self.requestor.download_file(url, writer, stream, data=data)

    def remove_material(self, media_id):
        """
        删除永久素材,节省空间
        它可以删除公众号在公众平台官网素材管理模块中新建的图文消息、语音、视频等素材
        临时素材无法通过本接口删除
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738731
        :param media_id: 媒体标识
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/del_material?access_token={0}".format(self.token)
        if isinstance(media_id, tuple):
            mid = media_id[0]
        else:
            mid = media_id
        data = '{"media_id":"%s"}' % mid
        r = self.requestor.post(url, data=data)
        return r

    def get_material_count(self):
        """
        获取永久素材的数量
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738733
        :return: MaterialCount对象
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/get_materialcount?access_token={0}".format(self.token)
        r = self.requestor.get(url, None)
        return MaterialCount(r["voice_count"], r["video_count"], r["image_count"])

    def get_material_list(self, media_type, offset=0, count=10):
        """
        获取永久素材的列表,也包含公众号在公众平台官网素材管理模块中新建的图文消息、语音、视频等素材
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1444738734
        :return: 永久素材的列表
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={0}".format(self.token)
        data = '{"type":"%s","offset":%d,"count":%d}' % (media_type.value, offset, count)
        r = self.requestor.post(url, data=data)
        return MaterialList(media_type, r)

    def get_video_info(self, media_id):
        """
        获取了永久视图素材信息
        :param media_id: 媒体标识
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={0}".format(self.token)
        data = '{"media_id":"%s"}' % media_id
        r = self.requestor.post(url, data=data)
        return VideoInfo(r)

    # ---------------------------------------------------------------------------
    # ~ 图文信息相关

    def upload_news(self, articles):
        """
        上传图文类型永久素材
        :param articles: 要上传的图文数组
        :return: 媒体标识
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/add_news?access_token={0}". \
            format(self.token)
        jsondata = articles.tojson()
        r = self.requestor.post(url,
                                data=jsondata
                                )
        return r["media_id"]

    # ---------------------------------------------------------------------------
    # ~ 微信用户相关

    def get_userinfo(self, openid, lang="zh_CN"):
        """
        获取微信用户基本信息
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140839
        :param openid: 普通用户的标识，对当前公众号唯一
        :param lang: 返回国家地区语言版本，zh_CN 简体，zh_TW 繁体，en 英语
        :return: Subscriber对象
        """
        url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}".format(self.token)
        params = {
            "openid": openid,
            "lang": lang
        }
        r = self.requestor.get(url, params)
        return Subscriber(r)

    def get_userlist(self, first_open_id=None):
        """
        批量获取公众号对应的用户列表
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140840
        :param first_open_id: 第一个拉取的OPENID，不填默认从头开始拉取
        :return: 用户列表SubscriberInfos对象
        """
        url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token={0}".format(self.token)
        params = {}
        if first_open_id:
            params["next_openid"] = first_open_id
        r = self.requestor.get(url, params)
        return SubscriberInfos(r)

    def remark_user(self, openid, remark):
        """
        设置用户备注名
        参见：https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140838
        :param openid:
        :param remark:
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token={0}".format(self.token)
        data = '{"openid":"%s", "":"%s"}' % (openid, remark)
        r = self.requestor.post(url, data=data)
        return r

    # ---------------------------------------------------------------------------
    # ~ 微信用户标签相关
    # ~ https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421140837
    # ~ 注：2016,微信已用标签管理取代以前的分组管理，公众号的运营者可以给一个用户打上更多的标签，而不再是之前的单一的分组 ，

    def create_tag(self, name):
        """
        创建新的公众号用户标签
        一个公众账号，最多支持创建100个标签
        :param name: 标签名称（30个字符以内）
        :return: 标签对象
        """
        url = "https://api.weixin.qq.com/cgi-bin/tags/create?access_token={0}".format(self.token)
        data = '{"tag":{"name":"%s"}}' % name
        r = self.requestor.post(url, data=data)
        return Tag(r["id"], r["name"])

    def get_all_tags(self):
        """
        获取公众号下所有的用户标签
        :return: 公众号下所有的用户标签
        """
        tags = []
        url = "https://api.weixin.qq.com/cgi-bin/tags/get?access_token={0}".format(self.token)
        r = self.requestor.get(url)
        for g in r["tags"]:
            tags.append(g)
        return tags

    def update_tag(self, tag_id, new_name):
        """
        编辑公众号下的用户标签
        :param tag_id: 标签标识
        :param new_name: 标签的新名称
        :return: 标签对象
        """
        url = "https://api.weixin.qq.com/cgi-bin/tags/update?access_token={0}".format(self.token)
        data = '{"tag":{"id":%d,"name":"%s"}}' % (tag_id, new_name)
        self.requestor.post(url, data=data)

    def remove_tag(self, tag_id):
        """
        删除用户标签
        请注意，当某个标签下的粉丝超过10w时，后台不可直接删除标签
        :param tag_id: 标签标识
        """
        url = "https://api.weixin.qq.com/cgi-bin/tags/delete?access_token={0}".format(self.token)
        data = '{"tag":{"id":%d}}' % tag_id
        self.requestor.post(url, data=data)

    def get_users_in_tag(self, tag_id, next_openid=""):
        """
        获取标签下粉丝列表
        :param tag_id: 标签标识
        :param next_openid:
        :return: TagUsers对象
        """
        url = "https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token={0}".format(self.token)
        data = '{"tag":%d, "next_openid":"%s"}' % (tag_id, next_openid)
        r = self.requestor.post(url, data=data)
        return r["count"]

    def tag_users(self, tag_id, openids):
        """
        批量为用户打标签
        标签功能目前支持公众号为用户打上最多20个标签
        :param tag_id:
        :param openids:
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token={0}".format(self.token)
        data = '{"tagid":%d, "openid_list":%s}' % (tag_id, json.dumps(openids))
        r = self.requestor.post(url, data=data)
        return r["count"]

    def cancel_tag_users(self, tag_id, openids):
        """
        批量为用户取消标签

        :param tag_id: 标签标识
        :param openids: 要取消的用户的openids
        """
        url = "https://api.weixin.qq.com/cgi-bin/tags/members/batchuntagging?access_token={0}".format(self.token)
        data = '{"tagid":%d,"openid_list":%s}' % (tag_id, json.dumps(openids))
        r = self.requestor.post(url, data)
        return r

    def get_tags_in_user(self, openid):
        """
        获取用户身上的标签列表
        :param openid:
        :return:
        """
        pass

    # ---------------------------------------------------------------------------
    # ~ 群发消息
    # https: // mp.weixin.qq.com / wiki?t = resource / res_main & id = mp1481187827_i0l21

    def send_message(self):
        pass

    def send_voice(self):
        pass

    def send_image(self):
        pass

    def send_vide(self):
        pass

    def remove_message(self):
        pass

    def message_status(self, msg_id):
        """
        查询群发消息发送状态【订阅号与服务号认证后均可用】
        :param msg_id: 要查询的消息标识
        :return: MessageStatus 消息状态
        """
        url = "https://api.weixin.qq.com/cgi-bin/message/mass/get?access_token={0}".format(self.token)
        data = '{"msg_id":"%s"}' % msg_id
        r = self.requestor.post(url, data)
        return MessageStatus(r["msg_status"])

    # ---------------------------------------------------------------------------
    # ~ 杂类

    def get_ip_list(self):
        """
        获取微信服务器IP地址。
        :return: 微信服务器IP地址列表
        """
        url = "https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token={0}".format(self.token)
        r = self.requestor.get(url)
        return r
