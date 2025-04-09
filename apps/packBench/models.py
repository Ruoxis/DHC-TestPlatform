from django.db import models

from apps.userSettings.models import CustomUser, Project, Robot
from django.utils.translation import gettext_lazy as _


class Environment(models.Model):
    """
    环境管理
    """
    name = models.CharField(max_length=100, verbose_name=_("环境名称"), unique=True)
    back_url = models.URLField(max_length=100, verbose_name=_("环境后台地址"), blank=True, null=True)
    zongfu_url = models.URLField(max_length=100, verbose_name=_("综服地址"), blank=True, null=True)
    env_login_params = models.JSONField(verbose_name=_("打包账号参数"), default=dict, blank=True, null=True)
    save_path = models.CharField(max_length=200, verbose_name=_("存放路径名"), blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 如果 save_path 为空，则将其设置为 name 字段的值
        if not self.save_path:
            self.save_path = self.name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("环境")
        verbose_name_plural = _("环境管理")


#
# class ProjectEnvironment(models.Model):
#     """
#     项目环境管理
#     """
#     environment = models.ForeignKey('Environment', on_delete=models.DO_NOTHING, verbose_name="项目环境")
#     project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, verbose_name="项目信息")
#     robot = models.ForeignKey(Robot, on_delete=models.DO_NOTHING, verbose_name="机器人信息")
#
#     class Meta:
#         verbose_name = "包类型"
#         verbose_name_plural = "打包类型管理"


class PackType(models.Model):
    """
    打包类型管理
    """
    name = models.CharField(max_length=100, verbose_name=_("包类型"))
    get_url = models.URLField(max_length=200, verbose_name=_("获取包路径url"), blank=True, null=True)
    alternate_name = models.CharField(max_length=50, verbose_name=_("副名"), default=None, blank=True, null=True)
    upload_url = models.CharField(max_length=100, verbose_name=_("后台上传拼接url"), blank=True, null=True)
    params = models.JSONField(verbose_name=_("参数管理"), default=dict, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("包类型")
        verbose_name_plural = _("打包类型管理")
        ordering = ['name']  # 按新增时间降序排列


class CodePath(models.Model):
    """
    代码仓库管理
    """
    # 根据打包类型管理一对多(一个包类型可能有多个管理地址)
    pack_type = models.ForeignKey(PackType, on_delete=models.CASCADE, verbose_name=_("包类型"))
    name = models.CharField(max_length=100, verbose_name=_("仓库名称"), unique=True)
    git_url = models.URLField(max_length=200, verbose_name=_("git仓库地址"), blank=True, null=True)
    code_login_params = models.JSONField(verbose_name=_("打包账号参数"), default=dict, blank=True, null=True)
    folder_path = models.CharField(max_length=200, verbose_name=_("本地存放路径"), blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("新增时间"))

    def __str__(self):
        return f"{self.pack_type.name} - {self.name}"

    class Meta:
        unique_together = ('pack_type', 'name')  # 确保同一包类型下仓库名称唯一
        verbose_name = _("代码仓库")
        verbose_name_plural = _("代码仓库管理")


class VersionBranch(models.Model):
    """
    版本分支管理
    """

    # 根据代码仓库管理一对多(一个仓库可能有多个分支)
    # pack_type = models.ForeignKey(PackType, on_delete=models.CASCADE, verbose_name="包类型")
    class Type(models.TextChoices):
        TEST = 'test', '测试'
        RELEASE = 'release', '发布'
        DEVELOP = 'develop', '开发'
        MASTER = 'master', '主干'
        OTHER = 'other', '其他'

    code_path = models.ForeignKey(CodePath, on_delete=models.CASCADE, verbose_name=_("仓库名称"))
    branch = models.CharField(max_length=100, verbose_name=_("git分支"), blank=True, null=True)
    description = models.TextField(verbose_name=_("分支描述"), blank=True, null=True)
    branch_type = models.CharField(max_length=100, verbose_name=_("分支类型"), choices=Type, default=Type.TEST)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_("新增时间"))

    def __str__(self):
        return f"{self.code_path.name}({self.branch})"

    class Meta:
        verbose_name = _("版本分支")
        verbose_name_plural = _("版本分支管理")
        unique_together = ('code_path', 'branch')  # 确保同一仓库下分支名称唯一
        ordering = ['-add_time']  # 按新增时间降序排列


class PackLog(models.Model):
    """
    打包执行记录
    """

    class STATUS(models.TextChoices):
        SUCCESS = 'success', '成功'
        FAILED = 'failed', '失败'
        RUNNING = 'running', '进行中'
        WAITING = 'waiting', '等待中'
        CANCELED = 'canceled', '已取消'

    # 执行人，关联到系统中的用户
    executor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_("执行人"))

    start_time = models.DateTimeField(verbose_name=_("开始时间"), auto_now_add=True, db_index=True)

    task_id = models.CharField(max_length=150, verbose_name=_("任务ID"), blank=True, null=True)

    end_time = models.DateTimeField(verbose_name=_("结束时间"), auto_now=True, blank=True, null=True)

    resource_version = models.CharField(max_length=100, verbose_name=_("资源版本"), blank=True, null=True)

    rule_version = models.CharField(max_length=100, verbose_name=_("规则版本"), blank=True, null=True)

    product_version = models.CharField(max_length=100, verbose_name=_("产品版本"), blank=True, null=True)

    is_sign = models.BooleanField(verbose_name=_("是否签名"), default=False)
    is_push_upload_zongfu = models.BooleanField(verbose_name=_("是否推送综服"), default=False)

    status = models.CharField(max_length=100, verbose_name=_("状态"), choices=STATUS, default=STATUS.WAITING,
                              blank=True,
                              null=True, db_index=True)

    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, verbose_name=_("打包环境"))
    branch = models.ForeignKey(VersionBranch, on_delete=models.CASCADE, verbose_name=_("代码分支"), blank=True,
                               null=True)

    def __str__(self):
        env_name = self.environment.name if self.environment else "未知环境"
        return f"{self.executor} - {env_name} - {self.task_id} - {self.start_time}"

    class Meta:
        verbose_name = _("打包记录")
        verbose_name_plural = _("打包记录")
        ordering = ['-start_time']


a = {"1": "A计划",
     "2": "向导式"}
