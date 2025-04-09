from django.db import models


# Create your models here.
class Permission(models.Model):
    # 权限表，用于控制url是否可访问
    pass
    path_name = models.CharField(verbose_name='路径名称', max_length=100, unique=True)
    url = models.URLField(verbose_name='url', max_length=200, unique=True)
    parent = models.ForeignKey('self', verbose_name='父级菜单', on_delete=models.CASCADE, null=True, blank=True)
    is_menu = models.BooleanField(verbose_name='是否为菜单', default=False)
    title = models.CharField(verbose_name='标题', max_length=100, unique=True)
    icon = models.ImageField(verbose_name='图标', upload_to='icon/', blank=True, null=True)
    status = models.BooleanField(verbose_name='状态', default=True)
