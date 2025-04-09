# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：publishProject.py
@Time ：2024/11/6 14:29 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@publishProject.py功能简介：
# 通用发布封装
"""
from src.config import auto_project_apifox
from src.projecctPublish import MmicroServiceLogin, requests, random, user_agent_list
from requests_toolbelt import MultipartEncoder
import os


class PublishProject:
    token = None
    project_updata_headers = None
    service_state = ['已打包', '测试发布', '区域发布', '全国发布']

    def __init__(self, host, back_login):
        self.host = host
        self.back_login = back_login
        self.set_token_headers()

    def set_token_headers(self):
        """80后台登录，设置token和请求头"""
        self.token = MmicroServiceLogin(self.host, self.back_login)
        host = self.host.split('//')[1]
        self.project_updata_headers = {
            'Host': host,
            'Connection': 'keep-alive',
            'Origin': self.host.replace('https', 'http'),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Referer': 'http://' + host + '/nirvana/series/resupgrade/list',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': self.token}

    @staticmethod
    def get_product_update_log(branchName="JC_20220415", versionId="3a35135ff26c4cf5b59422150118e592"):
        """
        获取产品包更新日子图片 # http://10.8.110.247:8060/api/AutoPackService/DownloadCommitPicture
        :param versionId:
        :param branchName:
        :return:
        """
        # 设置资源包路径的逻辑

        # url = "http://10.8.110.247:8060/api/AutoPackService/DownloadCommitPicture"

        payload = {"branchName": branchName,
                   "versionId": versionId}

        response = requests.get(auto_project_apifox.get('DownloadCommitPicture'),
                                headers=auto_project_apifox.get('headers'), data=payload)

        print(response.json())

    def upload(self, url, upload_path):
        """
        上传包去服务器
        """
        file_name, file_extension = os.path.splitext(os.path.basename(upload_path))
        m = MultipartEncoder(
            fields={'cid': (None, '5'),
                    'brand': (None, '4'),
                    'appVersion': (None, '10'),
                    'name': (None, '{}'.format(os.path.basename(file_name))),
                    'logs': (None, '{}'.format(os.path.basename(file_name))),
                    'clientVersion': (None, '544'),
                    'clientName': (None, 'V3.16.3.T001'),
                    'clientPatchVersion': (None, '0'),
                    'clientPatchName': (None, '不限制'),
                    'dataVersion': (None, '12972'),
                    'dataVersionName': (None, '12972(12972)'),
                    'zipfile': ('aa.zip', open(upload_path, 'rb'), 'application/x-zip-compressed')})

        try:
            response = requests.post(url=url,
                                     data=m, headers={'Authorization': self.token,
                                                      'Content-Type': m.content_type,
                                                      'User-Agent': random.choice(user_agent_list)}, verify=False)
            response_text = response.json()
            print(response_text)
            # print(response.status_code)
            if response_text['code'] == 200:
                return response.status_code
            else:
                return False
        except Exception as error:
            print(error)


if __name__ == '__main__':
    pass
