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

    def post(self, url, params=None, data=None, **kwargs):
        raise NotImplementedError('Requestor的子类没有实现http_post方法')


class DefaultRequstor(Requestor):
    """
    默认的HTTP请求处理器
    """

    def get(self, url, params=None, **kwargs):
        r = requests.get(url, params=params, **kwargs)
        if isinstance(r, requests.Response):
            # 如果是
            r = r.json()
            check_api_error(r)
        return r

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
    # ~ 媒体文件相关

    def upload_media(self, media_type, media_file):
        """
        上传媒体文件
        :param media_type: 媒体类型
        :param media_file:
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token={0}&type={1}".format(self.token, media_type)
        r = self.requestor.post(url,
                                files={"media_file", media_file}
                                )
        return r

    def download_media(self, media_id):
        """
        下载媒体文件
        :param media_id:
        :return:
        """
        url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token={0}&media_id={1}".format(self.token, media_id)
        f = self.requestor.get(url)
        return f

    # ---------------------------------------------------------------------------
    # ~ 图文素材相关

    # ---------------------------------------------------------------------------
    # ~ 粉丝相关



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
