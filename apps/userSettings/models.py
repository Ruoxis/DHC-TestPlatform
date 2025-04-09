# Create your models here.
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.navigation.models import Permission


# Create your models here.
class CustomUser(AbstractUser):
    """
    自定义用户表
    """

    class Type(models.TextChoices):
        DEVELOPER = 'developer', '开发'
        TESTER = 'tester', '测试'
        PROJECT_MANAGER = 'project_manager', '项目经理'
        ADMIN = 'admin', '管理员'
        GUEST = 'guest', '游客'

    phone_number = models.CharField(verbose_name=_('电话号码'), max_length=15, blank=True, null=True, unique=True)
    profile_picture = models.ImageField(verbose_name=_('用户头像'), upload_to='profile_pics/{username}/', blank=True,
                                        null=True)
    paw = models.CharField(verbose_name=_('密码'), max_length=100, blank=True, null=True)
    user_type = models.CharField(verbose_name=_('职能'), max_length=40, choices=Type.choices, default=Type.GUEST)
    role = models.OneToOneField('Role', verbose_name=_('角色'), on_delete=models.CASCADE, null=True, blank=True)
    last_login = models.DateTimeField(verbose_name=_('最后登录时间'), blank=True, null=True, auto_now=True)
    objects = UserManager()

    def __str__(self):
        return f"{self.first_name}({self.username})({self.get_user_type_display()})"

    # @property
    # def backend(self):
    # return 'django.contrib.auth.backends.ModelBackend'

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        verbose_name = "用户表"
        verbose_name_plural = "用户管理"
        pass


class Role(models.Model):
    """
    角色表
    """
    title = models.CharField(verbose_name=_('角色名称'), max_length=50, unique=True)
    status = models.BooleanField(verbose_name=_('状态'), default=True)

    def __str__(self):
        return self.title


class RolePermission(models.Model):
    """
    角色与权限表 {角色与权限表多对多}
    """
    role = models.ForeignKey(Role, verbose_name=_('角色'), on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, verbose_name=_('权限'), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.role.title} - {self.permission.title}"

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = "角色与权限"
        verbose_name_plural = "角色与权限管理"


class Robot(models.Model):
    """
    企业微信机器人配置
    """
    name = models.CharField(verbose_name=_('机器人名称'), max_length=50, unique=True)
    description = models.TextField(verbose_name=_('机器人描述'), blank=True, null=True)
    robot_key = models.CharField(verbose_name=_('机器人key'), max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}-{self.description}"

    class Meta:
        verbose_name = "机器人"
        verbose_name_plural = "机器人配置"


class Project(models.Model):
    """
    项目基础信息
    """

    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', '待启动'
        FINISHED = 'finished', '已结束'
        IN_PROGRESS = 'in_progress', '进行中'
        PAUSED = 'paused', '暂停'

    name = models.CharField(verbose_name=_('项目名称'), max_length=50, unique=True)
    status = models.CharField(verbose_name=_('状态'), default=Status.NOT_STARTED, max_length=40, choices=Status.choices)
    description = models.TextField(verbose_name=_('项目描述'), blank=True, null=True)
    create_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('更新时间'), auto_now=True)
    principal = models.ForeignKey(CustomUser, verbose_name=_('项目负责人'), on_delete=models.DO_NOTHING, null=True,
                                  blank=True)
    robot = models.ForeignKey(Robot, verbose_name=_('机器人'), on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

    class Meta:
        verbose_name = "项目信息"
        verbose_name_plural = "项目配置"



