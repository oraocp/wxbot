# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/4
# -------------------------------------------------------------------------

import requests

from weixin.api.models import *
from weixin.exceptions import check_api_error
from weixin.logger import log
from weixin.utils import Lockable


# ---------------------------------------------------------------------------
#   Requestor
# ---------------------------------------------------------------------------


class Requestor(object):
    def get(self, url, params=None):
        raise NotImplementedError('Requestor的子类没有实现http_get方法')

    def download_file(self, url, params=None, writer=None, stream=False, **kwargs):
        raise NotImplementedError('Requestor的子类没有实现download_file方法')

    def post(self, url, params=None, data=None, **kwargs):
        raise NotImplementedError('Requestor的子类没有实现http_post方法')


class DefaultRequstor(Requestor):
    """
    默认的HTTP请求处理器
    """

    def get(self, url, params=None, **kwargs):
        r = requests.get(url, params=params, **kwargs)
        if isinstance(r, requests.Response):
            # 假定微信返回的结果都是json字符串
            r = r.json()
            check_api_error(r)
        return r

    def download_file(self, url, params=None, writer=None, stream=False, **kwargs):
        if writer is None:
            raise ValueError("在Stream模式下下载文件时，输出流对象不能为空.")
        r = requests.get(url, params=params, stream=stream, **kwargs)
        r.raise_for_status()
        if stream:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    writer.write(chunk)
        else:
            writer.write(r.content)

    def post(self, url, params=None, data=None, files=None, **kwargs):
        r = requests.post(url, params=params, data=data, files=files).json()
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
    # ~ 菜单相关

    def create_menus(self, menu_data):
        """
        创建微信公众号的菜单
        :param menu_data: 菜单数据为json格式
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}".format(self.token)
        r = self.requestor.post(url, data=menu_data)
        return r

    def get_menus(self):
        """
        获取微信公众号的菜单,数据格式为json
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token={0}".format(self.token)
        r = self.requestor.get(url)
        return r

    def remove_menus(self):
        """
        删除微信公众号的菜单
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={0}".format(self.token)
        r = self.requestor.get(url)
        return r

    # ---------------------------------------------------------------------------
    # ~ 临时素材文件相关， 媒体文件在微信后台保存时间为3天，即3天后media_id失效

    def upload_media(self, media_type, media_file):
        """
        上传临时素材文件
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
        :param media_id:  媒体标识
        :param writer:  输出流
        :param stream: 是否启用流模式，默认为True
        """
        url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token={0}&media_id={1}".format(self.token, media_id)
        self.requestor.download_file(url, None, writer, stream)

    # ---------------------------------------------------------------------------
    # ~ 永久素材相关

    def upload_material(self, media_type, media_file):
        """
        上传除视频外的其它类型永久素材
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

    def upload_material_video(self, title, introduction, media_file):
        """
        上传视频类型的永久素材
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
        :param media_id:  媒体标识
        :param writer:  输出流
        :param stream: 是否启用流模式，默认为True
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={0}&media_id={1}".format(self.token,
                                                                                                             media_id)
        self.requestor.download_file(url, None, writer, stream)

    def get_material_video(self, media_id):
        """
        获取视图素材
        :param media_id:
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={0}&media_id={1}".format(self.token,
                                                                                                             media_id)
        r = self.requestor.get(url)
        return r["title"], r["description"], r["down_url"]

    def remove_material(self, media_id):
        """
        删除永久素材,节省空间
        它可以删除公众号在公众平台官网素材管理模块中新建的图文消息、语音、视频等素材
        临时素材无法通过本接口删除
        :param media_id: 媒体标识
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/del_material?access_token={0}".format(self.token)
        data = {
            "media_id": media_id
        }
        r = self.requestor.post(url, data=data)
        return r

    def get_material_count(self):
        """
        获取永久素材的数量
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/get_materialcount?access_token={0}".format(self.token)
        r = self.requestor.get(url, None)
        return MaterialCount(r["voice_count"], r["video_count"], r["image_count"])

    def get_material_list(self, media_type, offset=0, count=10):
        """
        获取永久素材的列表,也包含公众号在公众平台官网素材管理模块中新建的图文消息、语音、视频等素材
        :return: 永久素材的列表
        """
        url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={0}".format(self.token)
        data = {
            "type": media_type.value,
            "offset": offset,
            "count": count
        }
        r = self.requestor.post(url, data=data)
        return r

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
    # ~ 粉丝相关

    def get_userinfo(self, openid, lang="zh_CN"):
        """
        获取粉丝基本信息
        :param open_id:
        :return:
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
        :param first_open_id: 第一个拉取的OPENID，不填默认从头开始拉取
        :return: 用户列表
        """
        url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token={0}".format(self.token)
        params = {}
        if first_open_id:
            params["next_openid"] = first_open_id
        r =  self.requestor.get(url, params)
        return SubscriberInfos(r)

    # ---------------------------------------------------------------------------
    # ~ 粉丝组相关

    def create_group(self, name):
        """
        创建粉丝组别
        一个公众账号，最多支持创建500个分组
        :param name: 组别名称（30个字符以内）
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/groups/create?access_token={0}".format(self.token)
        data = {"group": {"name": name}}
        r = self.requestor.post(url, data=data)
        return Group(r["id"], r["name"])

    def get_all_group(self):
        """
        获取公众号的所有粉丝组别
        :return:
        """
        groups = []
        url = "https://api.weixin.qq.com/cgi-bin/groups/get?access_token={0}".format(self.token)
        r = self.requestor.get(url)
        for g in r["groups"]:
            groups.append(Group(g["id"], g["name"], g["count"]))
        return groups

    def get_user_group(self, open_id):
        """
        获取粉丝所在的组信息
        :param open_id:  粉丝的标识
        :return: 组信息
        """
        url = "https://api.weixin.qq.com/cgi-bin/groups/getid?access_token={0}".format(self.token)
        data = {"openid": open_id}
        return self.requestor.get(url, data=data)

    def update_group(self, group_id, group_name):
        """
        更新粉丝组信息
        :param group_id:  组标识
        :param group_name: 组名称
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/groups/update?access_token={0}".format(self.token)
        data = '{"group": {"id":"%s","name":"%s"}' % (group_id, group_name.encode("utf-8"))
        return self.requestor.post(url, data=data)

    def remove_group(self, group_id):
        """
        删除粉丝组
        :param group_id:
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/groups/delete?access_token={0}".format(self.token)
        data = {
            "group": {
                "id": group_id
            }
        }
        return self.requestor.post(url, data=data)

    # ---------------------------------------------------------------------------
    # ~ 群发消息

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
