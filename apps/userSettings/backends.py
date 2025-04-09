# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：backends.py
@Time ：2025/3/19 11:08 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@backends.py功能简介：

"""
# backends.py
from django.contrib.auth.backends import BaseBackend
from .models import CustomUser


class PhoneNumberBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 尝试通过手机号查找用户
            print("尝试通过手机号查找用户")
            user = CustomUser.objects.get(phone_number=username)
        except CustomUser.DoesNotExist:
            try:
                # 尝试通过用户名查找用户
                print("尝试通过用户名查找用户")
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                return None

        # 检查密码是否正确
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


if __name__ == '__main__':
    pass
