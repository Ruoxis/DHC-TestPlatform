# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：pack_c.py
@Time ：2025/3/21 9:25 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@pack_c.py功能简介：

"""
from concurrent.futures import ThreadPoolExecutor

from billiard.exceptions import SoftTimeLimitExceeded
from django_celery_results.models import TaskResult

from apps.packBench.models import PackType, Environment
from apps.packBench.views import evironment_info

"""
    {"environment": {"2": "工厂后台"},
    "pack_types": {"1": "产品包", "4": "规则", "5": "综服"},
    "upload_zongfu": true,
    "sign_package": true,
    "code_branch": {"3": "test1"}}
    :param args:
    :param kwargs:
    :return:
"""


def pack_resource_tack(*args, **kwargs):
    """
    :param environment_id
    :param pack_type_id
    :param args:
    :param kwargs:
    :return:
    """
    pass


def pack_rule_tack(*args, **kwargs):
    pass


def pack_product_tack(*args, **kwargs):
    pass


def tack4(*args, **kwargs):
    pass


def tack5(*args, **kwargs):
    pass


# def a():
#     pool = ThreadPoolExecutor(max_workers=10)
#     task_list = [{"task_fun": tack1, 'data': {}},
#                  {"task_fun": tack2, 'data': {}},
#                  {"task_fun": tack3, 'data': {}},
#                  {"task_fun": tack4, 'data': {}},
#                  {"task_fun": tack5, 'data': {}}]
#     for i in task_list:
#         pool.submit(i['task_fun'], **i['data'])
#     pool.shutdown()


if __name__ == '__main__':
    pass
    import redis

    # r = redis.Redis(host='127.0.0.1', port=6379, db=0, encoding='utf-8')
    # v = r.get('pack_task')
    # print(v.decode('utf-8'))
    evironment_info(2)


def r(bot_key, cookie_name):
    wx_Bot = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}'
    wechat_robot = WeChatAPI(wx_Bot)
    wechat_robot.post_text(
        content=setmarkdown_text(title_=f'预发布分支打包完成：',
                                 content_text={'a计划': '123132', '规则包': '12313', '产品包': '123'},
                                 content_text1=f'版本号:123', executor=cookie_name),
        content_type=True)
