# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：web
@File ：robot.py
@Time ：2023/11/30 9:15
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@robot功能简介：

"""
import requests
from urllib.parse import urlparse
import aiohttp
import hashlib
import base64
import asyncio
from typing import Optional, Dict, Any, Union

from src.config import self_host_serve, self_port_serve


class AsyncWeChatRobot:
    def __init__(self, robot_url: str):
        """
        异步企业微信机器人
        :param robot_url: 机器人webhook地址
        """
        self.robot_url = robot_url
        self.parse = urlparse(self.robot_url)
        self.robot_key = self.parse.query
        self.file_types = ["image", "voice", "video", "file"]
        self.upload_media_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?{self.robot_key}&type=file'
        self.session = None  # aiohttp客户端会话

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_media_id(self, file_path: str) -> Optional[str]:
        """
        异步获取文件media_id
        :param file_path: 文件路径
        :return: media_id或None
        """
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            form_data = aiohttp.FormData()
            form_data.add_field('file', file_data, filename=file_path.split('/')[-1])

            async with self.session.post(
                    self.upload_media_url,
                    data=form_data,
                    headers={'Content-Type': 'multipart/form-data'}
            ) as response:
                if response.status == 200:
                    json_res = await response.json()
                    return json_res.get('media_id')
                else:
                    print(f"上传文件失败，状态码：{response.status}")
                    return None
        except Exception as e:
            print(f"获取media_id异常：{str(e)}")
            return None

    async def post_text(
            self,
            content: str,
            mentioned_list: list = None,
            mentioned_mobile_list: list = None,
            content_type: bool = None
    ) -> Optional[Dict[str, Any]]:
        """
        异步发送文本/标记消息
        """
        msg_type = "markdown" if content_type else "text"
        payload = {
            "msgtype": msg_type,
            msg_type: {
                "content": content,
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or []
            }
        }

        try:
            async with self.session.post(self.robot_url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                print(f"发送消息失败，状态码：{response.status}")
                return None
        except Exception as e:
            print(f"发送消息异常：{str(e)}")
            return None

    async def post_news(
            self,
            title: str,
            description: str,
            jump_url: str,
            picurl: str
    ) -> Optional[Dict[str, Any]]:
        """
        异步发送图文消息
        """
        payload = {
            "msgtype": "news",
            "news": {
                "articles": [{
                    "title": title,
                    "description": description,
                    "url": jump_url,
                    "picurl": picurl
                }]
            }
        }

        try:
            async with self.session.post(self.robot_url, json=payload) as response:
                return await response.json() if response.status == 200 else None
        except Exception as e:
            print(f"发送图文消息异常：{str(e)}")
            return None

    async def post_file(
            self,
            file_type: str,
            file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        异步发送文件
        """
        if file_type not in self.file_types:
            print("文件类型错误：图片（image）、语音（voice）、视频（video），普通文件(file)")
            return None

        media_id = await self.get_media_id(file_path)
        if not media_id:
            return None

        payload = {
            "msgtype": "file",
            "file": {"media_id": media_id}
        }

        try:
            async with self.session.post(self.robot_url, json=payload) as response:
                return await response.json() if response.status == 200 else None
        except Exception as e:
            print(f"发送文件异常：{str(e)}")
            return None

    async def post_image(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        异步发送图片
        """
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
                base64_data = base64.b64encode(file_data).decode('utf-8')
                md5 = hashlib.md5(file_data).hexdigest()

            payload = {
                "msgtype": "image",
                "image": {
                    "base64": base64_data,
                    "md5": md5
                }
            }

            async with self.session.post(self.robot_url, json=payload) as response:
                return await response.json() if response.status == 200 else None
        except Exception as e:
            print(f"发送图片异常：{str(e)}")
            return None


async def async_message_notification(bot_key: str, content: Union[str, Dict]) -> None:
    """
    异步消息通知
    """
    wx_bot_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}'

    async with AsyncWeChatRobot(wx_bot_url) as robot:
        if isinstance(content, dict):
            formatted_content = setmarkdown_text(content)
            await robot.post_text(content=formatted_content, content_type=True)
        else:
            await robot.post_text(content=str(content))


class WeChatRobot(object):
    def __init__(self, robot_url):
        """

        :param url:
        """
        self.robot_url = robot_url
        self.parse = urlparse(self.robot_url)
        self.robot_key = self.parse.query
        self.headers = None
        self.file_types = ["image", "voice", "video", "file"]
        # 机器人文件中转
        self.upload_media_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?{self.robot_key}&type=file'

    def get_media_id(self, file):
        """
        # 请求id_url(将文件上传企业微信的临时平台),返回media_id，以便于后续发送
        :param file: 文件路径地址
        :return: media_id
        """
        upload_media_url = self.upload_media_url
        # id_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=xxx&type=file'
        response = requests.post(url=upload_media_url,
                                 headers={'Content-Type': 'multipart/form-data'},
                                 files={
                                     'file': open(file, 'rb')
                                 })
        json_res = response.json()
        # print(json_res)
        media_id = json_res['media_id']
        # print(media_id)
        return media_id

    def set_data(self):
        """

        :return:
        """
        pass


class WeChatAPI(WeChatRobot):
    def post_text(self, content, mentioned_list: list = None, mentioned_mobile_list: list = None, content_type=None):
        """
        :param content: 文本内容
        :param mentioned_list: 工号ID，"@all"
        :param content_type:
        :param mentioned_mobile_list: 手机号识别
        :return:
        """
        headers = {
            'Content-Type': "text/plain"
        }
        if content_type is None:
            data = {
                "msgtype": "text",  # 消息类型
                "text": {  # 固定抬头标识
                    "content": content,
                    # "广州今日天气：29度，大部分多云，降雨概率：60%",  # 文本类容
                    "mentioned_list": mentioned_list,  # ["11031840", "@all"],  # 工号
                    "mentioned_mobile_list": mentioned_mobile_list  # ["18282068745", "@all"]  # 手机号
                }
            }
        else:
            data = {
                "msgtype": "markdown",  # 消息类型
                "markdown": {  # 固定抬头标识
                    "content": content,
                    # "广州今日天气：29度，大部分多云，降雨概率：60%",  # 文本类容
                    # "mentioned_list": mentioned_list,  # ["11031840", "@all"],  # 工号
                    # "mentioned_mobile_list": mentioned_mobile_list  # ["18282068745", "@all"]  # 手机号
                }
            }
        try:
            result = requests.post(url=self.robot_url, headers=headers, json=data)
            return result
        except Exception as Error:
            print(Error)

    def post_news(self, title, description, jump_url, picurl):
        """

        :param title: 标题字段
        :param description: 描述字段(浅灰色)
        :param jump_url: 跳转链接
        :param picurl: 图片地址
        :return: result
        """
        headers = {'Content-Type': "text/plain"}
        data = {
            "msgtype": "news",  # 消息类型
            "news": {  # 固定抬头标识
                "articles": [
                    {
                        "title": title,  # "中秋节礼品领取",  # 标题字段
                        "description": description,  # "今年中秋节公司有豪礼相送",  # 描述字段(浅灰色)
                        "url": jump_url,  # "www.qq.com",  # 链接
                        "picurl": picurl,  # r"E:\Sfy_py\QQ图片20201201184940.jpg"
                        # 图片地址
                    }
                ]
            }
        }
        try:
            result = requests.post(url=self.robot_url, headers=headers, json=data)
            # print(result.text)
            return result
        except Exception as Error:
            print(Error)

    def post_file(self, file_type, file):
        """
        分别有图片（image）、语音（voice）、视频（video），普通文件(file)
        图片（image）：10MB，支持JPG,PNG格式
        语音（voice） ：2MB，播放长度不超过60s，仅支持AMR格式
        视频（video） ：10MB，支持MP4格式
        普通文件（file）：20MB
        :param file_type:文件类型
        :param file:文件地址
        :return:
        """
        if file_type in self.file_types:
            upload_media_url = self.upload_media_url + file_type
            # print(upload_media_url)
            data = {
                "msgtype": f"{file_type}",
                "file": {"media_id": self.get_media_id(file)}
            }
            try:
                result = requests.post(url=self.robot_url, json=data)
                # print(result.text)
                return result
            except Exception as Error:
                print(Error)
        else:
            print("文件类型错误：图片（image）、语音（voice）、视频（video），普通文件(file)")

    def post_image(self, file):
        with open(file, "rb") as f:
            base64_data = base64.b64encode(f.read())
            file = open(file, "rb")
            md = hashlib.md5()
            md.update(file.read())
            res1 = md.hexdigest()
        data = {
            "msgtype": "image",
            "image": {
                "base64": base64_data.decode('utf-8'),
                "md5": res1
            }
        }
        headers = {"Content-Type": "text/plain"}
        try:
            result = requests.post(url=self.robot_url, headers=headers, json=data)
            # print(result.text)
            return result

        except Exception as Error:
            print(Error)


def setmarkdown_text(content: dict = None):
    """
    content={'user': '系统管理', 'bot_key': '49c6002e-4044-4769-94de-ff98f1abea02',
    code_branch': 'test1', 'pack_type': {'产品包': '', '规则': '', '资源': ''}, 'environment': '80后台环境'}
    """
    set_text = ' '
    color_dict = {"info": "#999999", "erro": "#b73b3b"}
    title = "打包环境:" + content.get("environment")
    code_branch = content.get("code_branch", '')
    if code_branch:
        if code_branch != '':
            title += "\n分支:" + code_branch
    executor = f'任务执行人：{content.get("user")}'
    pack_type_content = content.get("pack_type")

    if pack_type_content:
        if isinstance(pack_type_content, dict):
            for _type, version in pack_type_content.items():
                print('setmarkdown_text', _type, version)

                try:
                    if len(version) == 1:
                        color = color_dict["info"]
                        type_version = ''
                    else:
                        type_version = str(version[0])
                        type_result = version[1]
                        if type_result or type_result not in ['False', 'false', '0']:
                            color = color_dict["info"]
                        else:
                            color = color_dict['erro']
                            type_version += '打包异常'
                except Exception as Error:
                    print(Error)
                    color = color_dict['erro']
                    type_version = ''
                set_text += f' \n <font color="#006666">{_type}： </font> <font face="楷体" color="{color}"> {str(type_version)} </font>  '

    markdown_text = str(
        f'<font color="blue">{title} </font> '
        '\n ``` '
        f'{set_text} '
        f'\n <font color="#006666">{executor}</font>'
        ' \n``` '
        f'\n[查看打包控制台](http://{self_host_serve}:{self_port_serve}/pack/pack_logs/)')
    # '\n ![打包截图](https://img0.baidu.com/it/u=4128765691,67812972&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=369)')
    return markdown_text


def message_notification(bot_key, content) -> None:
    wx_bot = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}'
    wechat_robot = WeChatAPI(wx_bot)

    wechat_robot.post_text(
        content=setmarkdown_text(content),
        content_type=True)


def img_notification(bot_key, jpg_path) -> None:
    wx_bot = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_key}'
    wechat_robot = WeChatAPI(wx_bot)
    wechat_robot.post_image(jpg_path)


async def _message_notification(bot_key, content):
    await async_message_notification(
        bot_key=bot_key,
        content=content
    )


if __name__ == '__main__':
    pass

    # wx_Bot = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=cde7d46e-3aca-4b42-95df-516052f6a34b'
    # wechat_robot = WeChatAPI(wx_Bot)
    # jpg_path = os.path.join(operating_path, 'img.png')
    # markdown_text = str(
    #     '<font color="info">【JC_20220415】 </font> '
    #     '\n ``` '
    #     '\n 构建：成功~  (o´ω`o)و '
    #     '\n <font color="red">耗时：？秒 </font> '
    #     '\n```'
    #     '\n[查看控制台](http://jenkins.3dxtyun.com/job/.net/job/CG_20231120AutoMergeToJC_20220415/537/console)'
    #     '\n ![打包截图](https://img0.baidu.com/it/u=4128765691,67812972&fm=253&fmt=auto&app=120&f=JPEG?w=500&h=369)')
    # html_content = markdown.markdown(markdown_text)
    # print(html_content)
    # print(markdown_text)
    # wechat_robot.post_text(
    #     content=markdown_text,
    #     mentioned_list=['@all'],
    #     mentioned_mobile_list=[],
    #     content_type=True)
    # wechat_robot.post_file('file', jpg_path)
    # wechat_robot.post_image(jpg_path)
    # wechat_robot.post_news('开发分支打包完成:',
    #                        "资源包:, 产品包:, 规则包:",
    #                        'https://qyapi.weixin.qq.com/',
    # jpg_path)
    # wechat_robot = WeChatAPI(wx_Bot)
    # wechat_robot.post_text(
    #     content=setmarkdown_text(title=f'消息测试',
    #                              content_text={'a计划': '123132', '规则包': '12313', '产品包': '123'},
    #                              content_text1=f'版本号:123'),
    #     content_type=True)
    # _message_notification(bot_key='21cf5d41-856a-497c-b07f-2cf677b5e4b7', message='测试11111111111111111')
    img_notification(bot_key='49c6002e-4044-4769-94de-ff98f1abea02', jpg_path=r'D:/packages\\temp\\img\\11319.png')
