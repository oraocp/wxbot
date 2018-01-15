# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# 文件目的：
# 创建日期：2018/1/7
# -------------------------------------------------------------------------

import logging
from logging.handlers import RotatingFileHandler

log = logging.getLogger("weixin")


def set_logger(logging_config=None):
    """
    根据日志配置参数设置模块日志记录器
    :param logging_config: 日志配置参数
    """
    if logging_config is None:
        # 设置默认的日志信息
        log.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d-%H:%M:%S")
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        log.addHandler(console)
    else:
        # 设置日志级别
        if "level" in logging_config:
            level = logging_config["level"]
            # todo
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.DEBUG)
        # 设置格式
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d-%H:%M:%S")
        # 设置输出
        if "handler" in logging_config:
            handler = logging["handler"]
            if "console" in handler and dict["console"] == 'True':
                console = logging.StreamHandler()
                console.setFormatter(fmt)
                log.addHandler(console)
            if "rotating-file" in handler:
                rthandler = handler["rotating-file"]
                filepath = rthandler["file"]
                max_bytes = 10 * 1024 * 1024
                if "maxBytes" in rthandler:
                    max_bytes = rthandler["maxBytes"]
                backup_count = 5
                if "backupCount" in rthandler:
                    backup_count = rthandler["backupCount"]
                rt_file = RotatingFileHandler(filepath, maxBytes=max_bytes, backupCount=backup_count)
                rt_file.setFormatter(fmt)
                log.addHandler(rt_file)
