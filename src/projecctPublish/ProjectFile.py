# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：AutomatedPackagingService
@File ：FileProject.py
@Time ：2023/11/22 10:55
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@FileProject功能简介：

"""
import os
import zipfile


def get_local_file_lates_version(dir_path):
    """
    获取本地文件夹最新版本号
    :param dir_path: 需要分享的文件路径地址
    :return: 最后修改的文件路径
    """

    # 获取指定目录下的所有文件名和最后修改时间
    file_list = file_list = [(os.path.join(dir_path, f), os.path.getmtime(os.path.join(dir_path, f))) for f in
                             os.listdir(dir_path)]
    # 按照最后修改时间对文件列表进行排序
    sorted_file_list = sorted(file_list, key=lambda x: x[1], reverse=True)
    # 返回最新文件的文件名
    return sorted_file_list[0][0]


def make_zip_archive_with_ignore(source_folder, destination_zip, ignore_list):
    """
    压缩文件夹
    :param source_folder: 文件夹目录
    :param destination_zip: 输出名字
    :param ignore_list: 需要排除的文件
    :return:
    """

    with zipfile.ZipFile(destination_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if all(ignore_item not in os.path.join(root, file) for ignore_item in ignore_list):
                    zipf.write(file_path, os.path.relpath(file_path, source_folder))

                    # zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), source_folder))
        zipf.close()
        return True

def unzip_replace_zip(source_zip, destination_folder):
    """
    解压压缩包
    :param source_zip: 压缩包路径
    :param destination_folder: 解压到地址
    :return:
    """
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # 解压缩压缩包到目标文件夹
        with zipfile.ZipFile(source_zip, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':

    pass
    # t = MmicroServiceLogin(host='web.yp80.3dxt.com', user='11031840', password='IVceVVVPVVVD', rand='4377')
    # project_updata_headers = {'Host': 'web.yp80.3dxt.com',
    #                           'Connection': 'keep-alive',
    #                           'Origin': 'http://web.yp80.3dxt.com',
    #                           'Content-Type': 'application/json;charset=UTF-8',
    #                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    #                           'Referer': 'http://web.yp80.3dxt.com/nirvana/series/resupgrade/list',
    #                           'Accept': 'application/json;charset=UTF-8',
    #                           'Authorization': t}

    # r = requests.get(
    #     'https://web.yp80.3dxt.com/api/nirvana/idc-packages-group/relative/page?keyword=&pageNo=1&pageSize=10&resUpgradeId=7664',
    #     headers=project_updata_headers, verify=False)
    # print(r.json())
    # 使用示例
    # source_zip_path = 'release7560.zip'  # 源压缩包路径
    # destination_folder_path = r'E:\Ruo\sfy_test\AutomatedPackagingService\packages\PublishBranch'  # 目标文件夹路径
