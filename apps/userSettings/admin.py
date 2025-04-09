from django.contrib import admin

# Create your views here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, RolePermission


# 自定义用户管理类
class CustomUserAdmin(UserAdmin):
    # 在用户列表页面显示的字段
    list_display = ('username', 'email', 'phone_number', 'user_type', 'role', 'last_login')
    # 可以通过哪些字段来搜索用户
    search_fields = ('username', 'email', 'phone_number', 'user_type', 'role',)

    # 在编辑用户页面显示的字段
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')}),
        ('权限',
         {'fields': ('user_type', 'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('date_joined',)}),
    )
    # 在添加用户页面显示的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'phone_number', 'user_type', 'role'),
        }),
    )


# 角色管理类
class RoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status')
    search_fields = ('title',)
    list_filter = ('status',)


# 角色权限管理类
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    search_fields = ('role__title', 'permission__title')
    list_filter = ('role', 'permission')


# 注册角色权限模型
admin.site.register(RolePermission, RolePermissionAdmin)
# 注册角色模型
admin.site.register(Role, RoleAdmin)
# 注册自定义用户模型
admin.site.register(CustomUser, CustomUserAdmin)
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Robot, Project


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    # 列表页配置
    list_display = ('name', 'robot_key', 'description_short')
    list_display_links = ('name',)
    search_fields = ('name', 'robot_key')
    ordering = ('name',)

    # 字段分组显示
    fieldsets = (
        (None, {
            'fields': ('name', 'robot_key')
        }),
        (_('添加信息描述'), {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    def description_short(self, obj):
        """描述字段的缩短显示"""
        return obj.description[:50] + '...' if obj.description else ''

    description_short.short_description = _('描述摘要')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # 列表页配置
    list_display = ('name', 'status', 'status_display', 'principal_name', 'robot_name', 'create_time')
    list_filter = ('status', 'create_time')
    search_fields = ('name', 'principal__username', 'robot__name')
    date_hierarchy = 'create_time'
    list_editable = ('status',)  # 现在 status 在 list_display 中存在
    list_per_page = 20

    # 表单页配置
    fieldsets = (
        (_('基础信息'), {
            'fields': ('name', 'status',)
        }),
        (_('添加信息描述'), {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        (_('Relationships'), {
            'fields': ('principal', 'robot')
        }),
        (_('Timestamps'), {
            'fields': ('create_time', 'update_time'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('create_time', 'update_time')
    autocomplete_fields = ['principal', 'robot']

    # 自定义方法字段
    def status_display(self, obj):
        """获取状态的可读名称"""
        return obj.get_status_display()

    status_display.short_description = _('状态')

    def principal_name(self, obj):
        return obj.principal.username if obj.principal else ''

    principal_name.short_description = _('负责人')

    def robot_name(self, obj):
        return obj.robot.name if obj.robot else ''

    robot_name.short_description = _('机器人')

    # 保存逻辑
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时自动设置创建用户
            obj.creator = request.user
        super().save_model(request, obj, form, change)
