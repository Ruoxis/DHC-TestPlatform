# Register your models here.
from django.shortcuts import render, redirect
# views.py
from django.contrib.auth.views import LoginView
from src.externalApi.unit_api import JDHostLogin
from .forms import CustomLoginForm, CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import authenticate


class CustomLoginView(LoginView):
    form_class = CustomLoginForm  # 使用自定义表单
    template_name = 'userSettings/login.html'  # 登录模板
    redirect_authenticated_user = True  # 如果用户已登录，重定向到 LOGIN_REDIRECT_URL


class LoginView(LoginView):
    template_name = 'userSettings/login.html'  # 登录模板
    form_class = CustomLoginForm  # 使用自定义表单
    redirect_authenticated_user = True  # 如果用户已登录，重定向到 LOGIN_REDIRECT_URL


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "用户名和密码不能为空")
            return render(request, 'userSettings/login_for_api.html')

        # 调用JDHostLogin进行外部认证
        print(password, username)
        result = JDHostLogin(username, password)
        # 如果认证成功，返回用户信息并保存到数据库
        if result.get("empId"):  # 根据接口返回的字段判断成功与否
            # 在数据库中查找用户，如果没有则创建新用户

            user, created = CustomUser.objects.get_or_create(username=username)
            user.username = username
            user.password = password
            user.paw = password
            user.first_name = result.get("empName", "")
            user.email = f"{username}@sfygroup.com"
            user.save()
            # 登录用户
            user.backend = 'apps.userSettings.backends.PhoneNumberBackend'
            login(request, user)
            messages.success(request, "登录成功")
            return redirect('pack:pack_log_list')  # 登录成功后跳转到主页

        else:
            messages.error(request, "登录失败，用户名或密码错误")

    return render(request, 'userSettings/login_for_api.html')  # 显示登录页面


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # 保存用户

            CustomLoginView(form.username, form.password1)
            login(request, user)
            return redirect('index')  # 重定向到仪表盘页面
    else:
        form = CustomUserCreationForm()
        print(form)
    return render(request, 'userSettings/register.html', {'form': form})
