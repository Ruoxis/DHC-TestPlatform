# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：__init__.py.py
@Time ：2025/3/21 9:25 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@__init__.py.py功能简介：

"""
import requests
import urllib.parse


def get_git_info(gitlab_url, project_name, access_token):
    # URL 编码项目名称
    encoded_project_name = urllib.parse.quote(project_name)

    # 构建 API 请求 URL
    api_url = f"http://gitlab.3dxtyun.com/api/v4/projects?acsess_token={access_token}&search={encoded_project_name}"
    print(api_url)
    # 请求头，包含 Personal Access Token
    headers = {
        "PRIVATE-TOKEN": access_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.485.400 QQBrowser/13.6.6321.400"
    }

    # response = requests.get(url, headers=headers)
    # 发送 GET 请求获取分支信息
    response = requests.get(api_url, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        print(response.text)
        branches = response.json()  # 解析 JSON 响应
        for i in branches:
            print(i)
    else:
        print(f"Failed to fetch branches: {response.status_code}, {response.text}")


if __name__ == '__main__':
    pass

    # # 使用 Git 仓库 URL 获取远程分支列表，包含用户名和密码
    # git_url = "http://gitlab.3dxtyun.com/diyhome-csharp/ypcode.git"  # 替换为实际仓库 URL
    # username = "bangguo.hu@3dxt.com"
    # password = "Sfy89757"  # 如果用 Token，使用 Token 替代密码

    # 设置 GitLab 项目 URL 和个人访问令牌
    gitlab_url = "http://gitlab.3dxtyun.com"  # GitLab 服务器地址
    project_name = "diyhome-csharp/ypcode"  # 项目名，格式为 'namespace/repository'
    access_token = "MjxeyCzJrBWz5rZJvBqu"  # 你的 Personal Access Token
    get_git_info(gitlab_url, project_name, access_token)
    # http://gitlab.3dxtyun.com/diyhome-csharp/ypcode/refs
    # import requests
    'http://gitlab.3dxtyun.com/api/v4/projects'
    'http://gitlab.3dxtyun.com/api/v4/projects/84/repository/branches'
'curl --header "PRIVATE-TOKEN: MjxeyCzJrBWz5rZJvBqu" "http://gitlab.3dxtyun.com/api/v4/projects/84/repository/branches"'
