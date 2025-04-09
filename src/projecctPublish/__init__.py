# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：__init__.py.py
@Time ：2024/11/6 14:26 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@__init__.py.py功能简介：

"""

# http://10.8.110.247:8060/api/AutoPackService/ADLogin
import requests
import urllib3
import random
import requests
import os

requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
]


def JDHostLogin(user, pwd):
    """
    索菲亚域用户登录身份验证
    :return:
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
    # if not interface_result.get('empId'):
    #     return False
    # else:
    #     print(interface_result)
    #     return True


def MmicroServiceLogin(host, login_params):
    """
    X计划用户登录身份验证
    :param host:
    :param login_params: {"rand": "4377", "user": "11031840", "password": "IVceVVVPVVVD"}
    :return:
    """
    headers = {'Accept': 'application/json, text/plain, */*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Content-Length': '86',
               'Content-Type': 'application/x-www-form-urlencoded',
               # 'Host': 'web.yp80.3dxt.com',
               'Origin': '{}'.format(host),
               'Referer': '{}/'.format(host),
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/75.0.3770.100 Safari/537.36'
               }
    data = {'version': '3.6',
            'platformCode': 'DIYHOME_WHT'}
    a = {'version': '3.6', 'platformCode': 'DIYHOME_WHT', 'rand': '4377', 'user': '11031840',
         'password': 'IVceVVVPVVVD'}
    for key, value in login_params.items():
        data[key] = value
    url = f'{host}/api/oauth/token'
    print(headers)
    print(data)
    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        if response.status_code == 200 and response.json()['access_token'] is not None:
            token = response.json()['token_type'] + ' ' + response.json()['access_token']
            # print('10j',token)
            return token
        elif response.status_code == 200 and response.json()['access_token'] is None:
            print("don't get cookie")
        else:
            print(response.status_code, '未知异常????', response.text)
    except Exception as ee:
        print(ee)


a = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate',
     'Accept-Language': 'zh-CN,zh;q=0.9', 'Connection': 'keep-alive', 'Content-Length': '86',
     'Content-Type': 'application/x-www-form-urlencoded',
     'Host': 'web.yp80.3dxt.com',
     'Origin': 'https://web.yp80.3dxt.com',
     'Referer': 'https://web.yp80.3dxt.com/',
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}


def service_platform_login(login_params):
    """
    服务平台用户登录身份验证
    :param login_params: {"account": "11031840", "password": ""}
    :return:
    """
    headers = {
        "User-Agent": random.choice(user_agent_list),
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        "X-FineUIMvc-Ajax": "true",
        "X-Requested-With": "XMLHttpRequest"
    }
    # fuwu_user = open_json()["fuwupingtai"]
    data = {
        "returnUrl": ""
    }
    for key, value in login_params.items():
        data[key] = value
    r = requests.post('http://10.10.18.107:8090/Account/Login', headers=headers, data=data, verify=False)
    return r.cookies


if __name__ == '__main__':
    pass
    # print(JDHostLogin(user="11031840", pwd="hubangguo199780"))
    # print(MmicroServiceLogin(host='web.yp80.3dxt.com', user='11031840', password='IVceVVVPVVVD', rand='4377'))
    # print(service_platform_login())
    # print(MmicroServiceLogin(host='web-dev.3dxt.com',)
    # login_params={"rand": "4377", "user": "11031840", "password": "IVceVVVPVVVD"}))
