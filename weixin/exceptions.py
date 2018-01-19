# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：定义框架中生成的异常
# 创建日期：2018/1/3
# -------------------------------------------------------------------------


class WxExcepion(Exception):
    """"""
    pass


class UnValidEncodingAESKey(WxExcepion):
    """"""
    pass


class AppIdValidationError(WxExcepion):
    """"""
    pass


class InvalidSignature(WxExcepion):
    """"""
    pass


class ApiException(WxExcepion):
    """"""
    pass


class AccountNotFound(WxExcepion):
    """"""
    pass


class AccountDisabled(WxExcepion):
    """"""
    pass


def check_api_error(result):
    if result and isinstance(result, dict):
        if "errcode" in result.keys() and result["errcode"] != 0:
            raise WxApiException(result["errcode"], result.get("errmsg", ""))


class WxApiException(WxExcepion):
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg
