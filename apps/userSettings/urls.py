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
from apps.userSettings import views

urlpatterns = [
                  # path('create_environment/', views.create_pack_environment, name='create_pack_environment'),
                  # path('view_environment/<int:environment_id>/', views.view_pack_environment,
                  #      name='view_pack_environment'),
                  # path('update_environment/<int:environment_id>/', views.update_pack_environment,
                  #      name='update_pack_environment'),
                  # path('update_record/<int:record_id>/', views.update_pack_record, name='update_pack_record'),
                  #
                  # path('create_record/', views.create_pack_record, name='create_pack_record'),
                  # path('view_record/<int:record_id>/', views.view_pack_record, name='view_pack_record'),
                  # path('update_record/<int:record_id>/', views.update_pack_record, name='update_pack_record'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = 'userSettings'
