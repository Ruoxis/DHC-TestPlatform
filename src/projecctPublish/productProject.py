# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：productProject.py
@Time ：2024/11/6 14:27 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@productProject.py功能简介：
产品包
"""
from src.projecctPublish.ProjectFile import unzip_replace_zip, make_zip_archive_with_ignore
from src.projecctPublish import requests, random, user_agent_list, service_platform_login
from src.projecctPublish.publishProject import PublishProject
from src.config import auto_project_apifox, packages_dir
from requests_toolbelt import MultipartEncoder

from src.tool.jenkins_api import file_sing
from src.tool.robot import WeChatAPI
from six.moves import urllib
import time
import os


class PublishProductProject(PublishProject):
    """
    产品包处理类
    """

    def __init__(self, host=None,
                 regional_publishing=None,
                 back_login=None, branch_name=None,
                 zf_host=None, zf_login=None,
                 is_upload_zongfu=None, is_sign_package=None,
                 product_type=None,
                 wx_bot_key=None, save_path=None):
        """
        :param host: 请求地址
        :param back_login: 后台登录
        :param branch_name: 分支名称
        :param product_type: 产品包类型
        :param regional_publishing: 是否是区域发布
        :param zf_host: 综服地址
        :param zf_login: 综服登录
        :param is_upload_zongfu: 是否上传综服
        :param is_sign_package: 是否签名
        :param save_path: 保存路径
        """
        # 调用父类构造函数
        super().__init__(host, back_login)
        self.branchName = branch_name
        self.product_version_img_path = None
        self.product_type = product_type
        self.regional_publishing = regional_publishing
        self.zf_host = zf_host
        self.zf_login = zf_login
        self.is_upload_zongfu = is_upload_zongfu
        self.is_sign_package = is_sign_package
        self.save_path_dir = packages_dir
        self.wechat_robot = WeChatAPI(wx_bot_key)
        self.product_version = None
        self.temp_dir = os.path.join(self.save_path_dir, 'temp')
        self.uat_dir = os.path.join(self.save_path_dir, r'release\uat_release')
        self.pre_dir = os.path.join(self.save_path_dir, r'release\pre_release')
        self.save_path = os.path.join(self.save_path_dir, rf'ProductProject\{save_path}')
        self.img_dir = os.path.join(self.temp_dir, 'img')

        # 检查使用到的目录是否存在
        for dir_path in [self.temp_dir, self.uat_dir, self.pre_dir, self.save_path, self.img_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def get_product_package_environments(self, is_v4=False):
        """
        获取开发分支 & 发布分支的版本名称以便于后续打包使用
        :return:
        """
        response = requests.get(auto_project_apifox.get('GetProductPackageEnvironments'),
                                headers=auto_project_apifox.get('headers')
                                )
        if is_v4:
            # 存在多个集成测试环境,待景强优化
            return auto_project_apifox.get('v4_environments')
        elif self.regional_publishing:
            return next(item['branchName'] for item in response.json() if item['envName'] == '预发布环境')
        else:
            return next(item['branchName'] for item in response.json() if item['envName'] == '集成测试环境')

    def get_environment_status(self):
        """
        获取打包环境是否存在报错信息
        :param branchName:
        :return:
        """
        # url = "http://10.8.110.247:8060/api/AutoPackService/GetEnvironmentStatus"
        #
        payload = {"branchName": self.branchName}
        try:
            response = requests.get(auto_project_apifox.get('GetEnvironmentStatus'),
                                    headers=auto_project_apifox.get('headers'), data=payload)
            # print('sdasdsad', response.json())
            if not response.json()['errorPhone']:
                return True, ''
            else:
                # print(response.json()['isError'])
                return False, response.json()['errorPhone']
        except Exception as e:
            print(e)
            return False, None

    def mark_product_package(self):
        """
        制作产品包
        :return:
        """
        # url = "http://10.8.110.247:8060/api/AutoPackService/MarkProductPackage"

        payload = {"branchName": self.branchName}
        try:
            response = requests.get(auto_project_apifox.get('MarkProductPackage'),
                                    headers=auto_project_apifox.get('headers'), data=payload)
            return response.json()['version']
        except Exception as e:
            print(e)
            return False

    def upload_service_platform(self, product_package_path):
        """
         上传包去综合服务平台
        :param product_package_path:
        :return:
        """
        filename, extension = os.path.splitext(os.path.basename(product_package_path))
        print(filename, extension)
        cookies = service_platform_login(self.zf_login)
        boundary = "------WebKitFormBoundaryd2sbD3y2BPmcGnzc"
        fields = {
            "hfId": '0',
            "hfFileName": '',
            "hfFilePath": "",
            "hfFileMd5": "",
            "ckbStatus": "true",
            "txtVersionNo": str(filename),  # 备注名
            "ckbEffection": "false",
            "dpEffectiveTime": "",
            "txtaRemark": "",
            "__RequestVerificationToken": "hT1qSRNxEOwnsAQp7x7gF6Od7BjlVa_QujhCstNSoiW__lAHBiMNvMTUKLVcii3soIOA63mBArAoJ2RtGe8bNPVurkdvKpPUYq9xUGJyxgw1",
            "X-FineUIMvc-Ajax": "true",
            "fuZipFile": (
                '{}'.format(os.path.join(filename, extension)), open(product_package_path, 'rb'),
                'application/x-zip-compressed'),
            # 'formValues'
        }
        m = MultipartEncoder(fields=fields, boundary=boundary)

        headers = {"Content-Type": "multipart/form-data; boundary={}".format(boundary),
                   "User-Agent": random.choice(user_agent_list)}
        try:
            r = requests.post(f'{self.zf_host}/Version/Version/Save', headers=headers, cookies=cookies,
                              data=m)
            print(r)
        except Exception as e:
            print(e)
        else:
            if "添加数据成功" in r.text:
                return True
            else:
                return False

    def download_product_package(self):
        """
        # 获取分支名，然后获取分支打包状态，再进行打包下载
        :return:
        """
        if self.branchName is None:
            self.branchName = self.get_product_package_environments()
        environment_status = self.get_environment_status()
        if environment_status[0]:
            version_id = self.mark_product_package()
            product_version = self.get_product_version()[0]["version"]
            self.product_version = int(product_version) + 1
            print(product_version)
            if self.regional_publishing:
                # 发布包命名
                package_save_path = os.path.join(self.temp_dir, f'release{self.product_version}.zip')
            else:
                package_save_path = os.path.join(self.temp_dir, f'{self.product_version}.zip')
            download_url = f"{auto_project_apifox.get('DownloadProductPackage')}?branchName={self.branchName}&versionId={version_id}"
            try:
                # url处理下载 返回文件保存路径
                product_download_path = urllib.request.urlretrieve(url=download_url, filename=package_save_path,
                                                                   reporthook=None)
                self.product_version_img_path = self.save_image_from_api(version_id=version_id)
                return product_download_path[0]
            except Exception as error:
                print(error)
                return False

        else:
            self.wechat_robot.post_text(content=f"{self.branchName}分支打包编译出现错误，请及时处理！",
                                        mentioned_list=[],
                                        mentioned_mobile_list=[environment_status[1]])
            return False

    def get_product_version(self):
        """
        获取微服务产品包的版本号等信息
        :return:
        """
        try:
            response = requests.get(
                f'{self.host}/api/nirvana/idc-packages/page?keyword=&pageNo=1&pageSize=10',
                headers={'Authorization': self.token}, verify=False)
            product_version_data = response.json()['data']['rows']
            return product_version_data
        except Exception as ee:
            print(ee)

    def save_image_from_api(self, version_id):
        url = f"{auto_project_apifox.get('DownloadCommitPicture')}?branchName={self.branchName}&versionId={version_id}"
        response = requests.get(url, stream=True)
        img_path = os.path.join(self.img_dir, rf'{self.product_version}.png')
        if response.status_code == 200:
            with open(img_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
            return img_path
        else:
            print("请求失败")

    def upload_product(self, path):
        """
        上传包至服务器
        :param path:
        :return:
        """
        print('dasdad', path)
        state_code = self.upload(f"{self.host}/api/nirvana/idc-packages", path)
        if state_code == 200:
            return True
        else:
            return False

    def publish_product_project(self):
        """
        发布产品包
        :return:
        """

        # 循环持续发布
        def project_updata_result(data_):
            """
            更新状态
            :param data_:
            :return:
            """
            try:
                response = requests.post(
                    f'{self.host}/api/nirvana/idc-packages/change', data=data_,
                    headers=self.project_updata_headers, verify=False)
                print(response.text)
                return response.json()
            except Exception as e:
                print(e)

        loop_counter = 0
        while True:
            result_data = self.get_product_version()
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
                    result_data = self.get_product_version()
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
                    result_data = self.get_product_version()
                    result_id = result_data[0]['id']  # 当前规则包id号
                    cdn_status_name = result_data[0]['statusName']  # 当前规则包状态
                    if self.regional_publishing:
                        # 发布分组设置
                        packages_group_headers = self.project_updata_headers
                        packages_group_headers['Content-Type'] = 'application/json;charset=UTF-8'
                        r = requests.post(f'{self.host}/api/nirvana/idc-packages-group', json={
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
                        r = requests.post(f'{self.host}/api/nirvana/idc-packages-group', json={
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
                    result_data = self.get_product_version()
                    cdn_status_name = result_data[0]['statusName']  # 当前规则包状态
                if cdn_status_name == '全国发布':
                    print('当前资源包已经全国发布')
                    return True
            loop_counter += 1
            if loop_counter > 20:
                return False

    def product_project_zip(self, source_zip_path, destination_folder_path):
        if unzip_replace_zip(source_zip_path, destination_folder_path):
            # 解压压缩包
            zip_file_path = os.path.join(self.save_path, os.path.basename(source_zip_path))
            make_zip_archive_with_ignore(destination_folder_path, zip_file_path,
                                         ['System.Data.SQLite.Linq.dll', 'setting.ini'])
            # print(zip_file_path)
            return zip_file_path

    def upload_product_publishing(self):
        try:
            product_download_path = self.download_product_package()
            if product_download_path is False:
                return False
            else:
                if self.regional_publishing:
                    zip_file_path = self.product_project_zip(product_download_path, self.pre_dir)
                else:
                    zip_file_path = self.product_project_zip(product_download_path, self.uat_dir)
                if self.is_sign_package:
                    _sing_file = file_sing(sing_file_path=zip_file_path)
                    if _sing_file:
                        zip_file_path = _sing_file
                    else:
                        return False
                if self.upload_product(zip_file_path):
                    if self.publish_product_project():
                        if self.regional_publishing:
                            pass
                        else:
                            self.upload_service_platform(zip_file_path)
                        return True
        except Exception as e:
            print(f"upload_product_publishing_error: {e}")
            return False


if __name__ == '__main__':
    pass

    """
    import asyncio
    async def publish_product_project(table_id):
        print("测试分支产品包", table_id)
        # try:
        Product_obj = PublishProductProject(regional_publishing=False, host=service_domain,
                                            user='11031840', password='IVceVVVPVVVD', rand='4377')
        if await Product_obj.upload_product_publishing() is True:
            version = Product_obj.get_product_version()[0]["version"]
            return Product_obj.branchName, version, Product_obj.product_version_img_path
        else:
            print("产品包打包失败")
            return None

        # except Exception as e:
        #     print(f"错误: {e}")
        #     return None


    asyncio.run(publish_product_project(table_id='612a8c7e5b8d5e0c5c6d7e8f'))
    """
