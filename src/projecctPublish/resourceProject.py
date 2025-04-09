# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：resourceProject.py
@Time ：2024/11/6 14:28 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@resourceProject.py功能简介：

"""
from src.projecctPublish.publishProject import PublishProject
from requests_toolbelt import MultipartEncoder
import requests
import time

requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数


class PublishResourceProject(PublishProject):
    """
    资源包处理类
    """

    def __init__(self, host=None,
                 regional_publishing=None,
                 back_login=None,
                 branch_name=None):
        """
        :param host: 请求地址
        :param regional_publishing: 是否是区域发布
        :param back_login: 后台登录信息
        :param branch_name: 分支名称
        """
        # 调用父类构造函数
        super().__init__(host, back_login)

        if "向导" in branch_name:  # 资源包类型，暂时是‘A计划'&’向导式‘
            self.resource_type = '向导式'
        else:
            self.resource_type = 'A计划'
        self.regional_publishing = regional_publishing
        self.resource_version = None
        self.resource_name = None

    def get_resupgrade_version(self):
        """
        资源包状态查询
        :return:
        """
        try:
            response = requests.get(
                f'{self.host}/api/nirvana/resupgrade/page?keyword=&pageNo=1&pageSize=10',
                headers={'Authorization': self.token}, verify=False)
            resupgrade_version_data = response.json()['data']['rows']
            for i in resupgrade_version_data:
                if i['brandName'] == "A计划" and self.resource_type == 'A计划':
                    aplan_data = i
                    return aplan_data, resupgrade_version_data[0]['verCode']
                elif i['brandName'] == "向导式" and self.resource_type == '向导式':
                    return i, resupgrade_version_data[0]['verCode']
        except Exception as ee:
            print(ee)

    def upload_resource(self):
        # 资源包打包的逻辑
        result_data = self.get_resupgrade_version()
        _name = result_data[1]
        _ver = result_data[0]['ver']
        self.resource_version = int(_ver.split('.')[-1]) + 1
        self.resource_name = int(_name) + 1
        print("当前版本号:", self.resource_name, 'ver版本号:', _ver)
        m = MultipartEncoder(
            fields={'cid': (None, '5'),
                    'brand': (None, '4'),
                    'appVersion': (None, '10'),
                    'packModel': (None, '2'),
                    'name': (None, '{}'.format(self.resource_name)),
                    'volume': (None, '200'),
                    'logs': (None, '{}'.format(self.resource_name)),
                    'ver': (None, 'aplan.p.10.0.{}'.format(self.resource_version)),
                    'startTime': (None, '2022-05-07 14:22:02'),
                    'endTime: ': (None, ''),
                    'verCode': (None, '{}'.format(self.resource_name)),
                    'packType': (None, 'a')})
        # 'zipfile': ('aa.zip', open(Path, 'rb'), 'application/x-zip-compressed')})
        try:
            response = requests.post(f"{self.host}/api/nirvana/resupgrade", data=m,
                                     headers={'Authorization': self.token,
                                              'Content-Type': m.content_type}, verify=False)
            print(response.json())
            "1={'data': None, 'code': 401, 'msg': '非法的资源包版本号，必须为aplan.p.10.0.3744'}"
            return True
        except Exception as ee:
            print(ee)
            return False

    def publish_resource_project(self):
        # 循环持续发布
        def project_updata_result(data_):
            """
            更新状态
            :param data_:
            :return:
            """
            try:
                response = requests.post(f'{self.host}/api/nirvana/resupgrade/change', data=data_,
                                         headers=self.project_updata_headers, verify=False)
                return response.json()
            except Exception as e:
                print(e)

        loop_counter = 0
        while True:
            result_data = self.get_resupgrade_version()
            result_id = result_data[0]['id']  # 当前资源包id号
            cdn_status_name = result_data[0]['statusName']  # 当前资源包状态
            if cdn_status_name not in ['已打包', '测试发布', '区域发布', '全国发布']:
                time.sleep(20)
            else:
                if cdn_status_name == '已打包':
                    # 判断是否已经上传完毕,上传完毕就进行预发布
                    data = {'id': result_id,
                            'flag': 'test',
                            'boundary': '------WebKitFormBoundaryJ4Az9bLC84MdQ7QJ'}
                    r_json = project_updata_result(data)
                    print("测试发布:", r_json)
                    time.sleep(5)
                    result_data = self.get_resupgrade_version()
                    result_id = result_data[0]['id']  # 当前资源包id号
                    cdn_status_name = result_data[0]['statusName']  # 当前资源包状态
                if cdn_status_name == '测试发布':
                    # 区域预发布设置
                    data = {"id": result_id,
                            'flag': 'prepare',
                            'boundary': '------WebKitFormBoundaryJ4Az9bLC84MdQ7QJ'}
                    r_json = project_updata_result(data)
                    print("区域发布:", r_json)
                    time.sleep(5)
                    if self.regional_publishing:
                        pass
                        break
                    result_data = self.get_resupgrade_version()
                    result_id = result_data[0]['id']  # 当前资源包id号
                    cdn_status_name = result_data[0]['statusName']  # 当前资源包状态
                if cdn_status_name == '区域发布':
                    # 全国发布设置
                    data = {"id": result_id,
                            'flag': 'rel',
                            'boundary': '------WebKitFormBoundaryJ4Az9bLC84MdQ7QJ'}
                    r_json = project_updata_result(data)
                    print("全国发布:", r_json)
                    time.sleep(5)
                    result_data = self.get_resupgrade_version()
                    cdn_status_name = result_data[0]['statusName']  # 当前资源包状态
                if cdn_status_name == '全国发布':
                    print('当前资源包已经全国发布')
                    return True
            loop_counter += 1
            if loop_counter > 20:
                return False

    def upload_resource_publishing(self):
        # 设置资源包路径的逻辑
        try:
            if self.upload_resource():
                self.publish_resource_project()
                return True
        except Exception as e:
            print(f"upload_resource_publishing_error:{e}")
            return False


if __name__ == '__main__':
    pass
    """
    import asyncio
     # 资源包打包
    async def publish_resource_project_a_plan(table_id, resource_type='A计划'):
        try:
            Resource_obj = PublishResourceProject(regional_publishing=False, host=service_domain,
                                                  user='11031840', password='IVceVVVPVVVD', rand='4377',
                                                  resource_type=resource_type)

            # 确保 upload_resource_publishing() 是协程并返回布尔值
            if await Resource_obj.upload_resource_publishing() is True:
                version = Resource_obj.get_resupgrade_version()[1]  # 确保 get_resupgrade_version() 返回的是可索引对象
                return version
            else:
                print("上传资源失败")
                return None

        except Exception as e:
            print(f"错误: {e}")
            return None


    asyncio.run(publish_resource_project_a_plan(table_id='612a8c7e5b8d5e0c5c6d7e8f'))
    """
    a = {
        "event": "OnCreate", "clazz": "AAADH000",
        "pos": {"x": 1472.2728729248047, "y": 798.40254783630371, "z": 497.63858318328857},
        "nor": {"x": -1, "y": 0, "z": 0},
        "product": {"name": "斜直装饰框", "code": "ZKEDBM", "uuid": "17411613790307000", "nodes": [
            {"uuid": "17411613790307000", "pid": "17411588260071001", "name": "斜直装饰框",
             "pm": [{"key": "CLASS", "text": "BGROUP", "value": "BGROUP"},
                    {"key": "CODE", "text": "ZKEDBM", "value": "ZKEDBM"},
                    {"key": "CORE_BRAND", "text": "P03", "value": 0}, {"key": "ContentInfo",
                                                                       "text": "{\"code\":\"ZKEDBM \",\"category\":\"组件,海纳百穿,通用收纳\",\"name\":\"斜直装饰框\",\"tags\":\"\"} ",
                                                                       "value": "{\"code\":\"ZKEDBM \",\"category\":\"组件,海纳百穿,通用收纳\",\"name\":\"斜直装饰框\",\"tags\":\"\"} "},
                    {"key": "D", "text": "300", "value": 300}, {"key": "DGCLX", "text": "2", "value": 2},
                    {"key": "H", "text": "300", "value": 300}, {"key": "ROLE", "text": "", "value": ""},
                    {"key": "RecordId", "text": "0", "value": 0}, {"key": "STYLE", "text": "", "value": ""},
                    {"key": "UserPermission", "text": "0", "value": "0"},
                    {"key": "UserPermissionStr", "text": "DIYHOMEMD", "value": "DIYHOMEMD"},
                    {"key": "VERSION", "text": "", "value": 0}, {"key": "W", "text": "300", "value": 300},
                    {"key": "YCBHD", "text": "18", "value": 18}, {"key": "ZCBHD", "text": "18", "value": 18},
                    {"key": "createIdcVersion", "text": "11037", "value": "11037"},
                    {"key": "createTime", "text": "20250305155619", "value": "20250305155619"},
                    {"key": "map", "text": "", "value": ""}, {"key": "mdir", "text": "", "value": ""}],
             "type": "utGroup"}, {"uuid": "17411613790307001", "pid": "17411613790307000", "name": "上下斜切左侧板",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "AAAAG", "value": "AAAAG"},
                                         {"key": "D", "text": "D", "value": 300},
                                         {"key": "H", "text": "H", "value": 300},
                                         {"key": "PATH", "text": "/PM/products//AAAAG.xml",
                                          "value": "/PM/products//AAAAG.xml"},
                                         {"key": "ROLE", "text": "", "value": ""},
                                         {"key": "RecordId", "text": "0", "value": 0},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "18", "value": 18},
                                         {"key": "map", "text": "", "value": ""},
                                         {"key": "mdir", "text": "", "value": ""},
                                         {"key": "px", "text": "0", "value": 0},
                                         {"key": "py", "text": "0", "value": 0},
                                         {"key": "pz", "text": "0", "value": 0}], "type": "utGroup"},
            {"uuid": "17411613790310000", "pid": "17411613790307000", "name": "上下斜切右侧板",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "AAABG", "value": "AAABG"}, {"key": "D", "text": "D", "value": 300},
                    {"key": "H", "text": "H", "value": 300},
                    {"key": "PATH", "text": "/PM/products//AAABG.xml", "value": "/PM/products//AAABG.xml"},
                    {"key": "ROLE", "text": "", "value": ""},
                    {"key": "RecordId", "text": "16378053810597000", "value": 16378053550669824},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "18", "value": 18}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir", "text": "", "value": ""}, {"key": "px", "text": "W-18", "value": 282},
                    {"key": "py", "text": "0", "value": 0}, {"key": "pz", "text": "0", "value": 0}],
             "type": "utGroup"}, {"uuid": "17411613790312000", "pid": "17411613790307000", "name": "斜切上固层",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "BACAA", "value": "BACAA"},
                                         {"key": "D", "text": "D", "value": 300},
                                         {"key": "H", "text": "18", "value": 18},
                                         {"key": "PATH", "text": "/PM/products//BACAA.xml",
                                          "value": "/PM/products//BACAA.xml"},
                                         {"key": "ROLE", "text": "", "value": ""},
                                         {"key": "RecordId", "text": "0", "value": 0},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "W", "value": 300},
                                         {"key": "YQ", "text": "1", "value": 1},
                                         {"key": "ZQ", "text": "1", "value": 1},
                                         {"key": "ZYSZ", "text": "0", "value": 0},
                                         {"key": "eAng", "text": "45", "value": 45},
                                         {"key": "map", "text": "map", "value": ""},
                                         {"key": "mdir", "text": "", "value": ""},
                                         {"key": "px", "text": "0", "value": 0},
                                         {"key": "py", "text": "0", "value": 0},
                                         {"key": "pz", "text": "H-18", "value": 282},
                                         {"key": "sAng", "text": "-45", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790315000", "pid": "17411613790307000", "name": "斜切下固层",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "BCCAA", "value": "BCCAA"}, {"key": "D", "text": "D", "value": 300},
                    {"key": "H", "text": "18", "value": 18},
                    {"key": "PATH", "text": "/PM/products//BCCAA.xml", "value": "/PM/products//BCCAA.xml"},
                    {"key": "ROLE", "text": "", "value": ""},
                    {"key": "RecordId", "text": "16378102660488000", "value": 16378102942793728},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 300}, {"key": "YQ", "text": "1", "value": 1},
                    {"key": "ZQ", "text": "1", "value": 1}, {"key": "ZYSZ", "text": "0", "value": 0},
                    {"key": "eAng", "text": "45", "value": 45}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir", "text": "", "value": ""}, {"key": "px", "text": "0", "value": 0},
                    {"key": "py", "text": "0", "value": 0}, {"key": "pz", "text": "0", "value": 0},
                    {"key": "sAng", "text": "-45", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790318000", "pid": "17411613790307000", "name": "斜直装饰框透明背板",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "11111", "value": "11111"}, {"key": "D", "text": "18", "value": 18},
                    {"key": "H", "text": "H-36", "value": 264},
                    {"key": "PATH", "text": "/pm/products/11111.xml", "value": "/pm/products/11111.xml"},
                    {"key": "ROLE", "text": "", "value": ""}, {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W-ZCBHD-YCBHD", "value": 264}, {"key": "map", "text": "", "value": ""},
                    {"key": "mdir", "text": "", "value": ""}, {"key": "px", "text": "18", "value": 18},
                    {"key": "py", "text": "", "value": 0}, {"key": "pz", "text": "18", "value": 18}],
             "type": "utGroup"}, {"uuid": "17411613790307002", "pid": "17411613790307001", "name": "斜切斜角",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "KAFAB", "value": "KAFAB"},
                                         {"key": "D", "text": "13", "value": 13},
                                         {"key": "H", "text": "18", "value": 18},
                                         {"key": "PATH", "text": "/pm/products/KAFAB.xml",
                                          "value": "/pm/products/KAFAB.xml"},
                                         {"key": "ROLE", "text": "样条", "value": "样条"},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "H", "value": 300},
                                         {"key": "eAng", "text": "45", "value": 45},
                                         {"key": "map", "text": "map", "value": ""},
                                         {"key": "px", "text": "", "value": 0},
                                         {"key": "py", "text": "-D+13", "value": -287},
                                         {"key": "pz", "text": "H", "value": 300},
                                         {"key": "ra", "text": "90", "value": 90},
                                         {"key": "rx", "text": "0.0", "value": 0},
                                         {"key": "ry", "text": "1.0", "value": 1},
                                         {"key": "rz", "text": "0.0", "value": 0},
                                         {"key": "sAng", "text": "-45", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790309000", "pid": "17411613790307001", "name": "斜切侧板基础板",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "KAEAB", "value": "KAEAB"}, {"key": "D", "text": "W", "value": 18},
                    {"key": "H", "text": "H", "value": 300},
                    {"key": "PATH", "text": "/pm/products/KAEAB.xml", "value": "/pm/products/KAEAB.xml"},
                    {"key": "ROLE", "text": "shape", "value": "shape"},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "SXQ", "text": "1", "value": 1},
                    {"key": "VERSION", "text": "", "value": ""}, {"key": "W", "text": "D-13", "value": 287},
                    {"key": "XXQ", "text": "1", "value": 1}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir1", "text": "1", "value": 1}, {"key": "px", "text": "", "value": 0},
                    {"key": "py", "text": "-D+13", "value": -287}, {"key": "pz", "text": "", "value": 0},
                    {"key": "ra", "text": "90", "value": 90}, {"key": "rx", "text": "0.0", "value": 0},
                    {"key": "ry", "text": "0.0", "value": 0}, {"key": "rz", "text": "1.0", "value": 1}],
             "type": "utGroup"}, {"uuid": "17411613790310001", "pid": "17411613790310000", "name": "斜切斜角",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "KAFAB", "value": "KAFAB"},
                                         {"key": "D", "text": "13", "value": 13},
                                         {"key": "H", "text": "18", "value": 18},
                                         {"key": "PATH", "text": "/pm/products/KAFAB.xml",
                                          "value": "/pm/products/KAFAB.xml"},
                                         {"key": "ROLE", "text": "样条", "value": "样条"},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "H", "value": 300},
                                         {"key": "eAng", "text": "45", "value": 45},
                                         {"key": "map", "text": "map", "value": ""},
                                         {"key": "px", "text": "W", "value": 18},
                                         {"key": "py", "text": "-D+13", "value": -287},
                                         {"key": "pz", "text": "0", "value": 0},
                                         {"key": "ra", "text": "270", "value": 270},
                                         {"key": "rx", "text": "0.0", "value": 0},
                                         {"key": "ry", "text": "1.0", "value": 1},
                                         {"key": "rz", "text": "0.0", "value": 0},
                                         {"key": "sAng", "text": "-45", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790311000", "pid": "17411613790310000", "name": "斜切侧板基础板",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "KAEAB", "value": "KAEAB"}, {"key": "D", "text": "W", "value": 18},
                    {"key": "H", "text": "H", "value": 300},
                    {"key": "PATH", "text": "/pm/products/KAEAB.xml", "value": "/pm/products/KAEAB.xml"},
                    {"key": "ROLE", "text": "shape", "value": "shape"},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "SXQ", "text": "1", "value": 1},
                    {"key": "VERSION", "text": "", "value": ""}, {"key": "W", "text": "D-13", "value": 287},
                    {"key": "XXQ", "text": "1", "value": 1}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir1", "text": "1", "value": 1}, {"key": "px", "text": "W", "value": 18},
                    {"key": "py", "text": "0", "value": 0}, {"key": "pz", "text": "", "value": 0},
                    {"key": "ra", "text": "270", "value": 270}, {"key": "rx", "text": "0.0", "value": 0},
                    {"key": "ry", "text": "0.0", "value": 0}, {"key": "rz", "text": "1.0", "value": 1}],
             "type": "utGroup"}, {"uuid": "17411613790312001", "pid": "17411613790312000", "name": "斜切上固层【底层】",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "BACAI", "value": "BACAI"},
                                         {"key": "D", "text": "D", "value": 300},
                                         {"key": "H", "text": "18", "value": 18},
                                         {"key": "PATH", "text": "/pm/products/BACAI.xml",
                                          "value": "/pm/products/BACAI.xml"}, {"key": "ROLE", "text": "", "value": ""},
                                         {"key": "RecordId", "text": "16400524310461000", "value": 16400524819562496},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "W", "value": 300},
                                         {"key": "YQ", "text": "YQ", "value": 1},
                                         {"key": "ZQ", "text": "ZQ", "value": 1},
                                         {"key": "ZYSZ", "text": "0", "value": 0},
                                         {"key": "eAng", "text": "eAng", "value": 45},
                                         {"key": "map", "text": "map", "value": ""},
                                         {"key": "mdir", "text": "", "value": ""},
                                         {"key": "px", "text": "", "value": 0}, {"key": "py", "text": "", "value": 0},
                                         {"key": "pz", "text": "", "value": 0},
                                         {"key": "sAng", "text": "sAng", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790315001", "pid": "17411613790315000", "name": "斜切下固层【底层】",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "BCCAC", "value": "BCCAC"}, {"key": "D", "text": "D", "value": 300},
                    {"key": "H", "text": "H", "value": 18},
                    {"key": "PATH", "text": "/pm/products/BCCAC.xml", "value": "/pm/products/BCCAC.xml"},
                    {"key": "ROLE", "text": "", "value": ""},
                    {"key": "RecordId", "text": "16378102660488000", "value": 16378102942793728},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 300}, {"key": "YQ", "text": "YQ", "value": 1},
                    {"key": "ZQ", "text": "ZQ", "value": 1}, {"key": "ZYSZ", "text": "0", "value": 0},
                    {"key": "eAng", "text": "eAng", "value": 45}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir", "text": "", "value": ""}, {"key": "px", "text": "", "value": 0},
                    {"key": "py", "text": "", "value": 0}, {"key": "pz", "text": "", "value": 0},
                    {"key": "sAng", "text": "sAng", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790318001", "pid": "17411613790318000", "name": "透明的虚拟背板3",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "1111A", "value": "1111A"}, {"key": "CORE_TEXT", "text": "1", "value": 1},
                    {"key": "D", "text": "0.02", "value": 0.019999999552965164},
                    {"key": "H", "text": "H", "value": 264},
                    {"key": "PATH", "text": "\\PM\\products\\1111A.xml", "value": "\\PM\\products\\1111A.xml"},
                    {"key": "ROLE", "text": "", "value": ""}, {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 264}, {"key": "map", "text": "W_WHILE", "value": "W_WHILE"},
                    {"key": "mdir", "text": "", "value": ""}], "type": "utGroup"},
            {"uuid": "17411613790347000", "pid": "17411613790318000", "name": "透明的虚拟背板3",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "1111A", "value": "1111A"}, {"key": "CORE_TEXT", "text": "1", "value": 1},
                    {"key": "D", "text": "0.02", "value": 0.019999999552965164},
                    {"key": "H", "text": "H", "value": 264},
                    {"key": "PATH", "text": "\\PM\\products\\1111A.xml", "value": "\\PM\\products\\1111A.xml"},
                    {"key": "ROLE", "text": "", "value": ""}, {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 264}, {"key": "map", "text": "W_WHILE", "value": "W_WHILE"},
                    {"key": "mdir", "text": "", "value": ""}, {"key": "px", "text": "W", "value": 264},
                    {"key": "py", "text": "0.05", "value": 0.05000000074505806}, {"key": "pz", "text": "", "value": 0},
                    {"key": "ra", "text": "180", "value": 180}, {"key": "rx", "text": "0.0", "value": 0},
                    {"key": "ry", "text": "0.0", "value": 0}, {"key": "rz", "text": "1.0", "value": 1}],
             "type": "utGroup"},
            {"uuid": "17411613790313000", "pid": "17411613790312001", "name": "斜切上固层【左右切】",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "BACAN", "value": "BACAN"}, {"key": "D", "text": "D", "value": 300},
                    {"key": "H", "text": "18", "value": 18},
                    {"key": "PATH", "text": "/PM/products//BACAN.xml", "value": "/PM/products//BACAN.xml"},
                    {"key": "ROLE", "text": "", "value": ""},
                    {"key": "RecordId", "text": "16400524310461000", "value": 16400524819562496},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 300}, {"key": "YQ", "text": "YQ", "value": 1},
                    {"key": "ZQ", "text": "ZQ", "value": 1}, {"key": "ZYSZ", "text": "0", "value": 0},
                    {"key": "eAng", "text": "eAng", "value": 45}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir", "text": "", "value": ""}, {"key": "px", "text": "", "value": 0},
                    {"key": "py", "text": "", "value": 0}, {"key": "pz", "text": "", "value": 0},
                    {"key": "sAng", "text": "sAng", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790316000", "pid": "17411613790315001", "name": "斜切下固层【左右切】",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "BCCAF", "value": "BCCAF"}, {"key": "D", "text": "D", "value": 300},
                    {"key": "H", "text": "H", "value": 18},
                    {"key": "PATH", "text": "/PM/products//BCCAF.xml", "value": "/PM/products//BCCAF.xml"},
                    {"key": "ROLE", "text": "", "value": ""},
                    {"key": "RecordId", "text": "16378102660488000", "value": 16378102942793728},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "SJDJBS", "text": "XQZSGSA", "value": "XQZSGSA"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 300}, {"key": "YQ", "text": "YQ", "value": 1},
                    {"key": "ZQ", "text": "ZQ", "value": 1}, {"key": "eAng", "text": "eAng", "value": 45},
                    {"key": "map", "text": "map", "value": ""}, {"key": "mdir", "text": "", "value": ""},
                    {"key": "px", "text": "", "value": 0}, {"key": "py", "text": "", "value": 0},
                    {"key": "pz", "text": "", "value": 0}, {"key": "sAng", "text": "sAng", "value": -45}],
             "type": "utGroup"}, {"uuid": "17411613790319000", "pid": "17411613790318001", "name": "文字竖放",
                                  "pm": [{"key": "CLASS", "text": "", "value": ""},
                                         {"key": "CODE", "text": "wenzi", "value": "wenzi"},
                                         {"key": "D", "text": "D", "value": 0.019999999552965164},
                                         {"key": "H", "text": "H", "value": 264},
                                         {"key": "PATH", "text": "/PM/base/board/wenzi.xml",
                                          "value": "/PM/base/board/wenzi.xml"},
                                         {"key": "ROLE", "text": "板件", "value": "板件"},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "W", "value": 264},
                                         {"key": "map", "text": "map", "value": "W_WHILE"},
                                         {"key": "mdir", "text": "0", "value": 0},
                                         {"key": "px", "text": "", "value": 0}, {"key": "py", "text": "", "value": 0},
                                         {"key": "pz", "text": "", "value": 0}], "type": "utGroup"},
            {"uuid": "17411613790348000", "pid": "17411613790347000", "name": "文字竖放",
             "pm": [{"key": "CLASS", "text": "", "value": ""}, {"key": "CODE", "text": "wenzi", "value": "wenzi"},
                    {"key": "D", "text": "D", "value": 0.019999999552965164}, {"key": "H", "text": "H", "value": 264},
                    {"key": "PATH", "text": "/PM/base/board/wenzi.xml", "value": "/PM/base/board/wenzi.xml"},
                    {"key": "ROLE", "text": "板件", "value": "板件"},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 264}, {"key": "map", "text": "map", "value": "W_WHILE"},
                    {"key": "mdir", "text": "0", "value": 0}, {"key": "px", "text": "", "value": 0},
                    {"key": "py", "text": "", "value": 0}, {"key": "pz", "text": "", "value": 0}], "type": "utGroup"},
            {"uuid": "17411613790313001", "pid": "17411613790313000", "name": "斜切层板基础板",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "KAFAC", "value": "KAFAC"}, {"key": "D", "text": "18", "value": 18},
                    {"key": "H", "text": "D-13", "value": 287},
                    {"key": "PATH", "text": "/pm/products/KAFAC.xml", "value": "/pm/products/KAFAC.xml"},
                    {"key": "ROLE", "text": "shape", "value": "shape"},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 300}, {"key": "YQ", "text": "YQ", "value": 1},
                    {"key": "ZQ", "text": "ZQ", "value": 1}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir1", "text": "0", "value": 0}, {"key": "px", "text": "", "value": 0},
                    {"key": "py", "text": "", "value": 0}, {"key": "pz", "text": "H", "value": 18},
                    {"key": "ra", "text": "90", "value": 90}, {"key": "rx", "text": "1.0", "value": 1},
                    {"key": "ry", "text": "0.0", "value": 0}, {"key": "rz", "text": "0.0", "value": 0}],
             "type": "utGroup"}, {"uuid": "17411613790314000", "pid": "17411613790313000", "name": "斜切斜角",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "KAFAB", "value": "KAFAB"},
                                         {"key": "D", "text": "13", "value": 13},
                                         {"key": "H", "text": "18", "value": 18},
                                         {"key": "PATH", "text": "/pm/products/KAFAB.xml",
                                          "value": "/pm/products/KAFAB.xml"},
                                         {"key": "ROLE", "text": "样条", "value": "样条"},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "W+(eAng==45?0:5)+(sAng==-45?0:5)", "value": 300},
                                         {"key": "eAng", "text": "eAng", "value": 45},
                                         {"key": "map", "text": "map", "value": ""},
                                         {"key": "px", "text": "W+(sAng==-45?0:5)", "value": 300},
                                         {"key": "py", "text": "-D+13", "value": -287},
                                         {"key": "pz", "text": "H", "value": 18},
                                         {"key": "ra", "text": "180", "value": 180},
                                         {"key": "rx", "text": "0.0", "value": 0},
                                         {"key": "ry", "text": "1.0", "value": 1},
                                         {"key": "rz", "text": "0.0", "value": 0},
                                         {"key": "sAng", "text": "sAng", "value": -45}], "type": "utGroup"},
            {"uuid": "17411613790316001", "pid": "17411613790316000", "name": "斜切层板基础板",
             "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                    {"key": "CODE", "text": "KAFAC", "value": "KAFAC"}, {"key": "D", "text": "18", "value": 18},
                    {"key": "H", "text": "D-13", "value": 287},
                    {"key": "PATH", "text": "/pm/products/KAFAC.xml", "value": "/pm/products/KAFAC.xml"},
                    {"key": "ROLE", "text": "shape", "value": "shape"},
                    {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                    {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                    {"key": "STYLE", "text": "", "value": ""}, {"key": "VERSION", "text": "", "value": ""},
                    {"key": "W", "text": "W", "value": 300}, {"key": "YQ", "text": "YQ", "value": 1},
                    {"key": "ZQ", "text": "ZQ", "value": 1}, {"key": "map", "text": "map", "value": ""},
                    {"key": "mdir1", "text": "0", "value": 0}, {"key": "px", "text": "", "value": 0},
                    {"key": "py", "text": "-D+13", "value": -287}, {"key": "pz", "text": "0", "value": 0},
                    {"key": "ra", "text": "270", "value": 270}, {"key": "rx", "text": "1.0", "value": 1},
                    {"key": "ry", "text": "0.0", "value": 0}, {"key": "rz", "text": "0.0", "value": 0}],
             "type": "utGroup"}, {"uuid": "17411613790317000", "pid": "17411613790316000", "name": "斜切斜角",
                                  "pm": [{"key": "CLASS", "text": "CGROUP", "value": "CGROUP"},
                                         {"key": "CODE", "text": "KAFAB", "value": "KAFAB"},
                                         {"key": "D", "text": "13", "value": 13},
                                         {"key": "H", "text": "18", "value": 18},
                                         {"key": "PATH", "text": "/pm/products/KAFAB.xml",
                                          "value": "/pm/products/KAFAB.xml"},
                                         {"key": "ROLE", "text": "样条", "value": "样条"},
                                         {"key": "SHOWORHIDE", "text": "SHOW", "value": "SHOW"},
                                         {"key": "SHOWORHIDE_NAVI", "text": "SHOW", "value": "SHOW"},
                                         {"key": "STYLE", "text": "", "value": ""},
                                         {"key": "VERSION", "text": "", "value": ""},
                                         {"key": "W", "text": "W+(eAng==45?0:5)+(sAng==-45?0:5)", "value": 300},
                                         {"key": "eAng", "text": "eAng", "value": 45},
                                         {"key": "map", "text": "map", "value": ""},
                                         {"key": "px", "text": "sAng==-45?0:-5", "value": 0},
                                         {"key": "py", "text": "-D+13", "value": -287},
                                         {"key": "pz", "text": "0", "value": 0},
                                         {"key": "ra", "text": "180", "value": 180},
                                         {"key": "sAng", "text": "sAng", "value": -45}], "type": "utGroup"}]},
        "parent": {"clazz": "Wall", "target": "17411589240293001", "root": "17411589240293001",
                   "pos": {"x": 0, "y": 0, "z": 0}, "nor": {"x": 0, "y": 0, "z": 1}},
        "right": {"target": "17411589240293000", "distance": 838.89019775390625, "root": "", "clazz": "Wall"},
        "front": {"target": "17411589240294000", "distance": 3400, "root": "", "clazz": "Wall"},
        "left": {"target": "17411589240293002", "distance": 2661.109619140625, "root": "", "clazz": "Wall"},
        "back": {"target": "17411589240293001", "distance": 100.00002288818359, "root": "", "clazz": "Wall"},
        "up": {"target": "2000", "distance": 2302.361572265625, "root": "2000", "clazz": "Ceil"},
        "down": {"target": "3000", "distance": 497.63858032226562, "root": "3000", "clazz": "Floor"}}
