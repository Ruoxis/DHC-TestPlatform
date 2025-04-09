from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Environment, PackType, CodePath, VersionBranch


# Environment 模型的后台管理
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'back_url', 'zongfu_url')  # 显示的列
    search_fields = ('name',)  # 搜索框支持的字段
    list_filter = ('name',)  # 过滤器，可以根据环境名称进行过滤
    ordering = ('name',)  # 排序规则，可以按环境名称排序


# PackType 模型的后台管理
class PackTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'alternate_name', 'get_url')  # 显示的列
    search_fields = ('name',)  # 搜索框支持的字段
    list_filter = ('name',)  # 过滤器，可以根据包类型名称进行过滤
    ordering = ('name',)  # 排序规则，可以按包类型名称排序


# CodePath 模型的后台管理
class CodePathAdmin(admin.ModelAdmin):
    list_display = ('pack_type', 'name', 'git_url', 'add_time')  # 显示的列
    search_fields = ('name', 'git_url')  # 搜索框支持的字段
    list_filter = ('pack_type',)  # 过滤器，可以根据包类型进行过滤
    ordering = ('-add_time',)  # 排序规则，可以按新增时间降序排列


# VersionBranch 模型的后台管理
class VersionBranchAdmin(admin.ModelAdmin):
    list_display = ('code_path', 'branch', 'add_time')  # 显示的列
    search_fields = ('branch', 'code_path__name')  # 搜索框支持的字段
    list_filter = ('code_path',)  # 过滤器，可以根据包类型和仓库名称进行过滤
    ordering = ('-add_time',)  # 排序规则，可以按新增时间降序排列


# 注册模型到后台
admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(PackType, PackTypeAdmin)
admin.site.register(CodePath, CodePathAdmin)
admin.site.register(VersionBranch, VersionBranchAdmin)

# admin.site.register(TaskResult)  # 注册celery任务结果模型
# admin.site.register(PeriodicTask)  # 注册celery定时任务模型
# admin.site.register(IntervalSchedule)  # 注册celery间隔任务模型
# admin.site.register(CrontabSchedule)  # 注册celery定时任务模型
