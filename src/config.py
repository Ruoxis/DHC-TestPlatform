# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：config.py
@Time ：2025/4/7 10:32 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@config.py功能简介：

"""
import os
import socket
# 获取当前文件所在目录
root_directory = os.path.dirname(os.path.abspath(__file__))
roots_doc = os.path.dirname(root_directory)  # 项目根目录
self_hostname = socket.gethostname()  # 获取主机名
self_host_serve = socket.gethostbyname(self_hostname)  # 获取主机IP地址
self_port_serve = '8527'  # 设置服务端口

# ***************************************************
# 产品包制作依赖（用于制作产品包的，景强大佬维护）
auto_project_apifox = {
    'headers': {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
    },
    'MarkProductPackage': 'http://10.8.110.247:8060/api/AutoPackService/MarkProductPackage',  # 制作产品包的接口
    'GetProductPackageEnvironments': 'http://10.8.110.247:8060/api/service/GetProductPackageEnvironments',  # 获取产品包分支信息
    'GetEnvironmentStatus': 'http://10.8.110.247:8060/api/AutoPackService/GetEnvironmentStatus',  # 获取环境状态是否有报错
    'DownloadProductPackage': 'http://10.8.110.247:8060/api/AutoPackService/DownloadProductPackage',  # 下载产品包
    'DownloadCommitPicture': 'http://10.8.110.247:8060/api/AutoPackService/DownloadCommitPicture',
    'v4_environments': 'V4_integration'
}
database = {
    "3.0": "diyhome3packages",
    "4.0": "diyhome_new_4_packages"
}

packages_dir = 'D:/packages'  # 产品包存放路径
os.makedirs(packages_dir, exist_ok=True)

if __name__ == '__main__':
    pass
