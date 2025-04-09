# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：rulePackage.py
@Time ：2024/11/6 14:27 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@rulePackage.py功能简介：

"""

from src.projecctPublish.publishProject import PublishProject, requests
from requests.exceptions import RequestException
from src.tool.robot import WeChatAPI
from src.config import packages_dir
from six.moves import urllib
import time
import os

requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数


class PublishRuleProject(PublishProject):
    """
    规则包处理类
    """

    def __init__(self, host=None, back_login=None, regional_publishing=None,
                 get_rule_host=None, rule_type=None, save_path=None, wx_bot_key=None
                 ):
        """
        调用父类构造函数
        :param host: 微服务后台地址
        :param back_login: 微服务后台登录信息
        :param regional_publishing: 是否是区域发布
        :param get_rule_host: 获取规则包地址
        :param rule_type: 规则包类型
        :param save_path: 规则包保存路径
        """
        super().__init__(host, back_login)
        self.rule_type = rule_type
        self.regional_publishing = regional_publishing
        self.save_path = os.path.join(packages_dir, f'RuleProject/{save_path}')
        self.get_rule_host = get_rule_host
        self.rule_version = None
        self.wechat_robot = WeChatAPI(wx_bot_key)
        # 检查使用到的目录是否存在
        for dir_path in [self.save_path]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def get_rule_version(self):
        """
        获取微服务后台规则包状态版本信息
        :return:
        """

        def request_with_retry(url, headers, retries=3, delay=1):
            # 尝试请求多次，直到成功或达到最大重试次数
            for i in range(retries):
                try:
                    response = requests.get(url, headers=headers, verify=False)
                    response.raise_for_status()  # 如果响应状态码不是 200，抛出异常
                    return response.json()['data']['rows']
                except (RequestException, ValueError):
                    # 处理异常
                    print(f"Failed to request {url}. Retrying ({i + 1}/{retries})...")
                    time.sleep(delay)
            raise RequestException(f"All retries failed for {url}.")

        return request_with_retry(
            url=f'{self.host}/api/nirvana/urule-packages/page?keyword=&pageNo=1&pageSize=10',
            headers={'Authorization': self.token})

    def get_rule_package(self):
        """
        下载规则包到本地
        :return:
        """

        def download_rule(package_save_path):
            response = requests.get(url=f'{self.get_rule_host}/rulePackage?_=1730337743380', verify=False)
            download_rule_url = urllib.parse.urljoin(f'{self.get_rule_host}/downlaod/', response.json()['data'])
            download_rule_path = urllib.request.urlretrieve(url=download_rule_url, filename=package_save_path,
                                                            reporthook=None)
            return download_rule_path[0]

        rule_version = self.get_rule_version()[0]["version"]
        self.rule_version = int(rule_version) + 1
        if self.regional_publishing:
            # 发布环境规则包打包
            package_save_path = os.path.join(self.save_path, f'release{self.rule_version}.zip')
        else:
            # 开发环境规则包打包
            package_save_path = os.path.join(self.save_path, f'{self.rule_version}.zip')
        try:
            print("package_save_path：", package_save_path, f'{self.get_rule_host}/rulePackage?_=1730337743380')
            # 打包好的规则包下载到本地
            for i in range(0, 3):
                rule_package = download_rule(package_save_path)
                if rule_package:
                    return rule_package
                else:
                    time.sleep(120)

        except Exception as error:
            print(error)

    def upload_rule(self, path):
        """
        上传规则包的接口
        :param path:
        :return:
        """
        state_code = self.upload(f"{self.host}/api/nirvana/urule-packages", path)
        if state_code == 200:
            return True
        else:
            return False

    def publish_rule_project(self):
        # 循环持续发布
        def project_updata_result(data_):
            """
            更新状态
            :param data_:
            :return:
            """
            try:
                response = requests.post(
                    f'{self.host}/api/nirvana/urule-packages/change', data=data_,
                    headers=self.project_updata_headers, verify=False)
                return response.json()
            except Exception as e:
                print(e)

        loop_counter = 0
        while True:
            result_data = self.get_rule_version()
            result_id = result_data[0]['id']  # 当前规则包id号
            cdn_status_name = result_data[0]['statusName']  # 当前规则包状态
            if cdn_status_name not in ['已经上传CDN', '已打包', '测试发布', '区域发布', '全国发布']:
                time.sleep(20)
            else:
                if cdn_status_name == '已经上传CDN':
                    # 判断是否已经上传完毕,上传完毕就进行预发布
                    data = {'id': result_id,
                            'flag': 'test',
                            'boundary': '------WebKitFormBoundaryJ4Az9bLC84MdQ7QJ'}
                    r_json = project_updata_result(data)
                    print("测试发布:", r_json)
                    time.sleep(5)
                    result_data = self.get_rule_version()
                    result_id = result_data[0]['id']  # 当前规则包id号
                    cdn_status_name = result_data[0]['statusName']  # 当前规则包状态
                if cdn_status_name == '测试发布':
                    # 区域预发布设置
                    data = {"id": result_id,
                            'flag': 'prepare',
                            'boundary': '------WebKitFormBoundaryJ4Az9bLC84MdQ7QJ'}
                    r_json = project_updata_result(data)
                    print("区域发布:", r_json)
                    time.sleep(5)
                    result_data = self.get_rule_version()
                    result_id = result_data[0]['id']  # 当前规则包id号
                    cdn_status_name = result_data[0]['statusName']  # 当前规则包状态
                    if self.regional_publishing:
                        # 发布分组设置
                        packages_group_headers = self.project_updata_headers
                        packages_group_headers['Content-Type'] = 'application/json;charset=UTF-8'
                        r = requests.post(f'{self.host}/api/nirvana/urule-packages-group', json={
                            "resUpgradeId": result_id,
                            "groups": [
                                {
                                    "groupCode": "test",
                                    "groupName": "发布分组"
                                }
                            ]
                        }, verify=False, headers=packages_group_headers)
                        if r.status_code == 200:
                            return True
                    elif result_data[1]['statusName'] == '区域发布':
                        # 开发分组设置
                        packages_group_headers = self.project_updata_headers
                        packages_group_headers['Content-Type'] = 'application/json;charset=UTF-8'
                        r = requests.post(f'{self.host}/api/nirvana/urule-packages-group', json={
                            "resUpgradeId": result_id,
                            "groups": [
                                {
                                    "groupCode": "KFFZ",
                                    "groupName": "开发分组"
                                }
                            ]
                        }, verify=False, headers=packages_group_headers)
                        if r.status_code == 200:
                            return True
                if cdn_status_name == '区域发布':
                    # 全国发布设置
                    data = {"id": result_id,
                            'flag': 'rel',
                            'boundary': '------WebKitFormBoundaryJ4Az9bLC84MdQ7QJ'}
                    r_json = project_updata_result(data)
                    print("全国发布:", r_json)
                    time.sleep(5)
                    result_data = self.get_rule_version()
                    cdn_status_name = result_data[0]['statusName']  # 当前规则包状态
                if cdn_status_name == '全国发布':
                    print('当前资源包已经全国发布')
                    return True
            loop_counter += 1
            if loop_counter > 20:
                return False

    def upload_rule_publishing(self):
        # 设置规则包路径的逻辑
        try:
            rule_package = self.get_rule_package()
            if rule_package:
                if self.upload_rule(rule_package):
                    if self.publish_rule_project():
                        return True
            else:
                return False

        except Exception as e:
            print(f"upload_rule_publishing_error: {e}")
            return False


if __name__ == '__main__':
    pass
    """

    import asyncio
    async def publish_rule_project(table_id):
        print("规则", table_id)
        try:
            Rule_obj = PublishRuleProject(regional_publishing=False, host=service_domain,
                                          user='11031840', password='IVceVVVPVVVD', rand='4377')
            if await Rule_obj.upload_rule_publishing() is True:
                version = Rule_obj.get_rule_version()[0]["version"]
                return version
            else:
                print("规则包打包失败")
                return None

        except Exception as e:
            print(f"错误: {e}")
            return None


    asyncio.run(publish_rule_project(table_id='612a8c7e5b8d5e0c5c6d7e8f'))
    """
