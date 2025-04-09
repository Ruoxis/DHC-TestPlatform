# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：celery.py
@Time ：2025/3/21 15:15 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@celery.py功能简介：

"""
import os
from celery import Celery
from kombu import Queue, Exchange
from django.conf import settings
import logging.config  # 需要这行导入

# 设置系统环境变量，安装django，必须设置，否则在启动celery时会报错
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestProject.settings')
celery_app = Celery('TestProject')
# 读取django的配置文件
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
# 发现每个app下的task.py
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# -------------------任务队列路由配置------------------------------ #
# 声明 Exchange
default_exchange = Exchange('default_exchange', type='direct')
pack_exchange = Exchange('pack_exchange', type='direct')

# 需要先声明队列和绑定
celery_app.conf.task_queues = (
    Queue(name='default',
          exchange=default_exchange,
          routing_key='asia.default',
          exclusive=False,  # 允许多消费者
          durable=True,  # 队列持久化
          ),
    Queue(name='pack',
          exchange=pack_exchange,
          routing_key='asia.pack',
          exclusive=False,  # 允许多消费者
          durable=True,  # 队列持久化
          ),
    Queue(name='pack_io',
          exchange=pack_exchange,
          routing_key='asia.pack_io',
          exclusive=False,  # 允许多消费者
          durable=True,  # 队列持久化
          )
)
# 默认路由配置
celery_app.conf.task_default_exchange = 'default_exchange'
celery_app.conf.task_default_routing_key = 'asia.default'

# -----------------其他设置-------------------------------- #
celery_app.conf.task_create_missing_queues = True  # 允许自动创建队列
celery_app.conf.task_default_queue = 'default'  # 设置默认队列

# -----------------日志设置-------------------------------- #
# logging.config.dictConfig(settings.LOGGING)
# 延迟日志配置（关键修改）


if __name__ == '__main__':
    pass

    """
    Celery的依赖库：
    mysqlclient
    redis
    celery
    django-celery-beat
    django_celery_results
    eventlet  # 并发池类型，windows下运行celery4以后的版本，还需额外安装eventlet库
    
    model
    django_celery_beat_clockedschedule  # 以指定时间执行任务，例如：2024-05-22 09:22:10
    django_celery_beat_crontabschedule  # 以crontab格式时间执行任务，某月某天星期几某时某分
    django_celery_beat_intervalschedule  # 以间隔时间执行任务，例如：每5秒、每2小时
    django_celery_beat_periodictask  # 存储要执行的任务。
    django_celery_beat_periodictasks  # 索引和跟踪任务更改状态
    django_celery_beat_solarschedule  # 以天文时间执行任务，例如：日出、日落
    django_celery_results_chordcounter  # 存储Celery的chord任务的状态
    django_celery_results_groupresult  # 存储Celery的group任务的结果
    django_celery_results_taskresult  # 存储Celery任务的执行结果
    
    celery -A TestProject worker -l info -P eventlet
    """
