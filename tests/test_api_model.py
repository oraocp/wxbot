# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/9
# -------------------------------------------------------------------------

from unittest import TestCase

from weixin.api.models import *


class TestApiModel(TestCase):
    def test_access_tokens(self):
        ac = AccessToken("token", 20112)
        print("ac=", ac)
