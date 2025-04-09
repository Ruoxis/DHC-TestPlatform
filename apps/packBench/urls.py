"""
URL configuration for TestPlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from apps.packBench import views

urlpatterns = [
                  # path('pack_operations/', views.get_data, name='pack_operations'),
                  path('pack_operation/', views.PackOperationView.as_view(), name='pack_operation'),
                  path('ajax/load_code_branches/', views.LoadCodeBranches.as_view(), name='load_code_branches'),
                  path('pack_logs/', views.PackLogListView.as_view(), name='pack_log_list'),
                  # path('test/', views.pack_package_v, name='test'),
                  # path('get_task_result/', views.get_task_result, name='get_task_result'),
                  path('results/', views.GetTaskResult.as_view(), name='task-results')

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = 'userSettings'

# celery -A TestProject beat -l info  # 启动beat任务调度器
# celery -A TestProject worker -P eventlet -l info  # 启动worker消费异步任务
