# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestPlatform
@File ：utils.py
@Time ：2025/3/13 8:36 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@utils.py功能简介：

"""


def apps_jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'id': user.id
    }


if __name__ == '__main__':
    pass
