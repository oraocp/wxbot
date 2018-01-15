# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：wxbot的全局视图
# 创建日期：2018/1/13
# -------------------------------------------------------------------------

import django
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from weixin.logger import log
from weixin.wechat import SimpleWxService
from .settings import WX_SETTINGS


def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
        return request.META['HTTP_X_FORWARDED_FOR']
    else:
        return request.META['REMOTE_ADDR']


@csrf_exempt
def welcome_to_django(request):
    """
    输出django欢迎语，以及django版本
    :param request:
    :return:
    """
    return HttpResponse("欢迎来到djano的编程世界，当前版本为：%s." % (django.__version__))


wx_service = SimpleWxService(WX_SETTINGS)


@csrf_exempt
def wx_process(request, id):
    """
    处理来自微信服务器的请求。
    :param request: HTTP请求
    :param id: 公众号标识
    :return: 应答的微信消息或者为空
    """
    try:
        if request.method == "POST":
            rec = request.body
            # 请求消息为字节的，使用utf-8编码格式先转为字符串
            if isinstance(rec, bytes):
                rec = rec.decode()
            log.info("收到来自%s的公众号(标识为:%s)的请求消息:%s" % (get_ip(request), id, rec))

            result = wx_service.do_post(id, rec, request.GET)
            log.info("响应公众号(标识为:%s)的服务器请求，回复为:%s", (id, result))
            return HttpResponse(result)
        elif request.method == "GET":
            try:
                # 公众号响应字符串
                echostr = request.GET.get('echostr')
                # 微信加密签名
                signature = request.GET.get('signature')
                # 时间戳
                timestamp = request.GET.get('timestamp')
                # 随机字符串
                nonce = request.GET.get('nonce')
            except ValueError:
                return HttpResponse("wxbot")

            log.info("收到来自'{0}'的公众号(标识为:{1})的服务验证请求，参数为:echostr={2},signature={3},timestamp={4},nonce={5}".
                     format(get_ip(request), id, echostr, signature, timestamp, nonce))
            return HttpResponse(wx_service.do_get(id, echostr, signature, timestamp, nonce))
        else:
            return HttpResponseNotAllowed(['GET', 'POST'])
    except Exception as e:
        log.error(e)

