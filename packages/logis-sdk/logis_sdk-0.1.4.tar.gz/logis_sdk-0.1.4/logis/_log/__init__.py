FORMAT_COLORED_MORE = "[%(asctime)s] %(log_color)s%(levelname)-8s%(reset)s %(module)s:%(funcName)s:%(lineno)d - %(blue)s%(message)s"

FORMAT_MORE = (
    "[%(asctime)s] %(levelname)-8s %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)

import logging

import colorlog


def add_color_log_handler(logger: logging.Logger):
    """
    为logger添加 coloredlog 处理器
    """
    raise NotImplementedError()
