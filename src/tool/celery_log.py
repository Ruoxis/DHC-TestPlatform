# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：celery_log.py
@Time ：2025/4/3 11:07 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@celery_log.py功能简介：

"""

from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def setup_logging():
    """配置项目日志"""
    LOG_DIR = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)

    # 主日志格式
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )

    # 文件日志（按天切割）
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_DIR / 'celery_tasks.log',
        when='midnight',  # 每天切割
        backupCount=7,  # 保留7天
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # 应用配置
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler]
    )

    # Celery特定日志配置
    logging.getLogger('celery').setLevel(logging.INFO)


# 在文件开头调用
# setup_logging()
# logger = logging.getLogger(__name__)
if __name__ == '__main__':
    pass
