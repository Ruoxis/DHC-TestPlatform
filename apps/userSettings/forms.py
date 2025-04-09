# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：forms.py
@Time ：2025/3/19 11:08 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@forms.py功能简介：

"""
# forms.py

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser
from django import forms


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="用户名或手机号")  # 允许用户使用用户名或手机号登录

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': '请输入用户名或手机号'})
        self.fields['password'].widget.attrs.update({'placeholder': '请输入密码'})


# forms.py


# forms.py
class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label='手机号',  # 设置中文标签
        help_text='请输入手机号'
    )
    profile_picture = forms.ImageField(
        required=False,
        label='用户头像',  # 设置中文标签
        help_text='上传头像（可选）'
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.Type.choices,
        required=True,
        label='职能',  # 设置中文标签
        help_text='选择职能'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'profile_picture', 'user_type', 'password1', 'password2')


if __name__ == '__main__':
    pass
