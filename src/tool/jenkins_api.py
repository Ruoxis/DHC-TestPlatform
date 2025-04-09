# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：AutoTestingProject1
@File ：jenkins_api.py
@Time ：2025/3/6 10:12 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@jenkins_api.py功能简介：

"""
import os
import time
from tqdm import tqdm
import requests
from requests_toolbelt import MultipartEncoder


def get_jenkins_crumb(jenkins_service_url, jenkins_user, jenkins_api_token):
    """
    获取Jenkins的CSRF Crumb
    :param jenkins_service_url: Jenkins服务URL
    :param jenkins_user: Jenkins用户名
    :param jenkins_api_token: Jenkins API Token
    :return: Crumb
    """
    try:
        crumb_url = f"{jenkins_service_url}/crumbIssuer/api/json"
        response = requests.get(crumb_url, auth=(jenkins_user, jenkins_api_token))

        if response.status_code == 200:
            crumb = response.json()
            return crumb['crumb']
        else:
            print(f"获取Crumb失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取Crumb时发生错误: {e}")


def get_jenkins_build_number(build_item_number, jenkins_service_url, jenkins_user, jenkins_api_token, wait_time=60):
    """
    获取Jenkins构建号
    :return: Jenkins构建号
    """
    build_number = None
    item_url = f'{jenkins_service_url}/queue/item/{build_item_number}/api/json'
    # job_api_json = f'{jenkins_service_url}/job/{job_name}/api/json'
    start_time = time.time()
    while time.time() - start_time < wait_time:
        response = requests.get(item_url, auth=(jenkins_user, jenkins_api_token))
        try:
            job_info = response.json()
        except Exception as err:
            print(f"返回的数据非json格式,错误信息: {err}")
            break
        if response.status_code == 200:
            build_executable = job_info.get('executable')
            if build_executable:
                build_number = build_executable.get('number')
            elif job_info.get('_class') == 'hudson.model.Queue$WaitingItem':
                print("等待构建任务执行")
            else:
                print(f"获取构建任务信息失败，状态码: {response.status_code}")

        else:
            print(f"获取最新构建任务号失败，状态码: {response.status_code}")
        if build_number:
            print(f"获取最新构建任务号成功，任务号: {build_number}")
            break
        time.sleep(3)

    return build_number


# 上传文件并触发构建
def jenkins_trigger_build(jenkins_service_url, job_name, jenkins_user, jenkins_api_token, params=None, multipart=None,
                          boundary=None):
    """
    触发Jenkins构建
    :param jenkins_service_url: Jenkins服务URL
    :param jenkins_user: Jenkins用户名
    :param jenkins_api_token: Jenkins API Token
    :param params: Jenkins构建参数
    :param multipart: 上传文件时，需要提供multipart对象
    :param boundary: 上传文件时，需要提供boundary
    :return: 构建队列号
    """
    # 获取Jenkins任务的Crumb（用于CSRF保护）
    crumb = get_jenkins_crumb(jenkins_service_url, jenkins_user, jenkins_api_token)
    headers = {
        'Jenkins-Crumb': crumb,
    }
    if not crumb:
        print("没有获取到jenkins的crumb信息")
        return None
    try:
        # 构建触发构建的URL
        build_url = f"{jenkins_service_url}/job/{job_name}/buildWithParameters"
        if multipart:
            if not boundary:
                boundary = "----WebKitFormBoundaryGsNavqGpFS0VRly0"

            headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'  # 自动设置multipart边界
            # 发送POST请求，上传文件并触发构建
            response = requests.post(build_url, headers=headers, data=multipart,
                                     auth=(jenkins_user, jenkins_api_token))

        else:
            print("非文件上传构建")
            response = requests.post(build_url, headers=headers, params=params,
                                     auth=(jenkins_user, jenkins_api_token))

        print("正在执行编译,请等候...    url: ", build_url)
        if response.status_code == 201:
            print("文件上传并且构建已成功触发！")
            # 提取构建号（从返回的URL中获取构建号）
            print(response.headers)
            print('--' * 30)
            print(response.text)
            build_item_number = response.headers.get('Location').split('/')[-2]
            print("本次构建的队列号为: ", build_item_number)
            start_time = time.time()
            while time.time() - start_time < 60:
                build_number = get_jenkins_build_number(build_item_number=build_item_number,
                                                        jenkins_service_url=jenkins_service_url,
                                                        jenkins_user=jenkins_user,
                                                        jenkins_api_token=jenkins_api_token)
                if build_number:
                    print("本次构建的build号为: ", build_number)
                    return build_number
                time.sleep(5)
            return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as err:
        print(f"触发构建过程发生错误: {err}")
        return None


def get_build_status(jenkins_service_url, jenkins_user, jenkins_api_token, job_name, build_number):
    """
    获取构建状态
    :param jenkins_service_url: Jenkins服务URL
    :param jenkins_user: Jenkins用户名
    :param jenkins_api_token: Jenkins API Token
    :param job_name: Jenkins任务名称
    :param build_number: Jenkins构建号
    :return: 构建状态
    """
    try:
        build_status_url = f"{jenkins_service_url}/job/{job_name}/{build_number}/api/json"
        response = requests.get(build_status_url, auth=(jenkins_user, jenkins_api_token))

        if response.status_code == 200:
            build_data = response.json()
            return build_data['result']  # 获取构建结果（SUCCESS, FAILURE等）
        else:
            print(f"获取构建状态失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取构建状态时发生错误: {e}")


def download_build_artifact(jenkins_service_url, jenkins_user, jenkins_api_token, job_name, build_number,
                            artifact_name):
    """
    下载构建产物
    :param jenkins_service_url: Jenkins服务URL
    :param jenkins_user: Jenkins用户名
    :param jenkins_api_token: Jenkins API Token
    :param job_name: Jenkins任务名称
    :param build_number: Jenkins构建号
    :param artifact_name: 构建产物的文件名
    :return: None
    """
    file_name = os.path.basename(artifact_name)
    name, ext = os.path.splitext(file_name)
    try:
        artifact_url = f"{jenkins_service_url}/job/{job_name}/{build_number}/artifact/source/{file_name}"
        print(artifact_url)
        response = requests.get(artifact_url, auth=(jenkins_user, jenkins_api_token))

        if response.status_code == 200:
            print(f"开始下载构建产物: {artifact_name}")
            total_size = int(response.headers.get('content-length', 0))
            # 使用 tqdm 创建进度条
            with open(artifact_name, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=artifact_name) as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:  # 过滤掉空的 chunk
                            f.write(chunk)
                        pbar.update(len(chunk))  # 更新进度条
            print(f"构建产物已下载完成: {artifact_name}")
            return artifact_name
        else:
            print(f"下载构建产物失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"下载构建产物时发生错误: {e}")


def upload_file_and_trigger_build_download(jenkins_service_url, job_name, sing_file_path, jenkins_user,
                                           jenkins_api_token, file_path,
                                           timeout=900,
                                           poll_interval=30):
    """
    上传文件并触发构建，等待构建完成，然后下载构建产物
    :param jenkins_service_url: Jenkins服务URL
    :param job_name: Jenkins任务名称
    :param sing_file_path: 上传文件路径
    :param jenkins_user: Jenkins用户名
    :param jenkins_api_token: Jenkins API Token
    :param file_path: 文件路径
    :param timeout: 超时时间（秒）默认15分钟，实际时间应该在16~17分钟
    :param poll_interval: 检查构建状态的间隔时间（秒）
    :return: 构建号
    """
    print("文件上传构建")
    file_name = os.path.basename(file_path)
    boundary = "----WebKitFormBoundaryGsNavqGpFS0VRly0"

    fields = {
        'SIGN_FILE': (file_name, open(file_path, 'rb')),
        'name': file_name
    }
    m = MultipartEncoder(fields=fields, boundary=boundary)

    build_number = jenkins_trigger_build(jenkins_service_url=jenkins_service_url,
                                         job_name=job_name,
                                         jenkins_user=jenkins_user,
                                         jenkins_api_token=jenkins_api_token,
                                         multipart=m,
                                         boundary=boundary)
    if build_number:
        # 等待构建完成
        print(f"等待job {build_number} 任务完成构建...")
        wait_time = 0
        build_status = None
        while build_status not in ['SUCCESS', 'FAILURE', 'null'] and wait_time < timeout:
            print(f"Jenkins {build_number} 构建执行中，等待构建结束...")
            build_status = get_build_status(jenkins_service_url=jenkins_service_url,
                                            jenkins_user=jenkins_user,
                                            jenkins_api_token=jenkins_api_token,
                                            job_name=job_name,
                                            build_number=build_number)
            if build_status == 'SUCCESS':
                print(f"Jenkins {build_number} 构建完成...")
                name, ext = os.path.splitext(file_name)
                # 下载构建产物
                download_build_file_name = os.path.join(os.path.dirname(sing_file_path),
                                                        f'sign_{build_number}-{name}{ext}')
                return download_build_artifact(jenkins_service_url=jenkins_service_url,
                                               jenkins_user=jenkins_user,
                                               jenkins_api_token=jenkins_api_token,
                                               job_name=job_name,
                                               build_number=build_number,
                                               artifact_name=download_build_file_name)
            elif build_status == 'FAILURE':
                print(f"构建 {build_number} 失败！")
                return None
            time.sleep(poll_interval)  # 每隔一定时间检查一次构建状态
            wait_time += poll_interval
        if wait_time >= timeout:
            print(f"超时 {timeout} 秒，构建 {build_number} 未完成。")
            return None
    else:
        print(f"触发构建失败！")
        return None


def file_sing(service_url="http://10.8.111.253/", job_name="diyhome_code_sign", user="11031840",
              api_token="11b09928ce115c86242d51fafb001d8407",
              sing_file_path=r"E:\tempResult\release11035.zip"):
    try:
        return upload_file_and_trigger_build_download(service_url, job_name, sing_file_path, user, api_token,
                                                      sing_file_path,
                                                      timeout=900,
                                                      poll_interval=30)  # 900秒超时，30秒轮询一次
    except Exception as e:
        print(f"文件签名失败: {e}")


if __name__ == "__main__":
    pass
    # Jenkins服务器的URL、用户凭证以及job信息11c857ecfbcddca57b7bb32216a4a413df
    # code_sign_token :http://10.8.111.253/ : 11b09928ce115c86242d51fafb001d8407
    # service_url = "http://10.8.111.253/"
    # user = "11031840"
    # api_token = "11b09928ce115c86242d51fafb001d8407"  # Jenkins api token *** 用户信息中的Security添加
    # # job_name = "diyhome_code_sign"
    # sing_file_path = r"E:\tempResult\release11035.zip"  # 需要上传的文件路径
    # upload_file_and_trigger_build_download(service_url, user, job_name,api_token, sing_file_path, timeout=900,
    #                                        poll_interval=30)  # 900秒超时，30秒轮询一次
    print(file_sing())