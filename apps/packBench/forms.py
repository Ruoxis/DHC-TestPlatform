# !/usr/bin/env python
"""
@Project ：TestProject
@File ：forms.py
@Time ：2025/3/20 9:49 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@forms.py功能简介：

"""
from django import forms
from .models import Environment, PackType, VersionBranch, CodePath, PackLog, Robot
from django.forms import inlineformset_factory


class PackOperationForm(forms.Form):
    environment = forms.ModelChoiceField(queryset=Environment.objects.all(), label="打包环境")
    pack_types = forms.ModelMultipleChoiceField(
        queryset=PackType.objects.all().exclude(name__icontains='内核'),
        label="打包类型",
        widget=forms.CheckboxSelectMultiple
    )
    upload_zongfu = forms.BooleanField(required=False, label="是否上传综服")
    sign_package = forms.BooleanField(required=False, label="是否签名")
    is_regiona = forms.BooleanField(required=False, label="是否区域发布")

    code_branch = forms.ModelChoiceField(
        queryset=VersionBranch.objects.none(),
        label="代码分支",
        required=False
    )
    robot = forms.ModelChoiceField(
        queryset=Robot.objects.all(),
        label="信息通知机器人",
        required=False,
        # disabled=Robot.objects.all().count() == 0
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置代码分支的queryset
        if 'pack_types' in self.data:
            try:
                pack_type_ids = self.data.getlist('pack_types')
                self.fields['code_branch'].queryset = VersionBranch.objects.filter(
                    code_path__pack_type__id__in=pack_type_ids
                )
            except (ValueError, TypeError):
                pass


class PackLogFrom(forms.ModelForm):
    class Meta:
        model = PackLog
        fields = '__all__'


if __name__ == '__main__':
    pass
