# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：unit.py
@Time ：2025/3/22 9:07 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@unit.py功能简介：

"""
import requests


def JDHostLogin(user, pwd):
    """
    索菲亚域用户登录身份验证
    :return: 返回接口返回的数据
    """
    url = "http://10.8.110.247:8060/api/AutoPackService/ADLogin"

    payload = {
        "userAccount": user,
        "pwd": pwd
    }
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
    }
    response = requests.get(url, headers=headers, data=payload, verify=False)
    interface_result = response.json()
    return interface_result


if __name__ == '__main__':
    pass
