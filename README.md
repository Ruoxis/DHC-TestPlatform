# DHC-TestPlatform


### 必要依赖

```python
aiohttp==3.11.16
attrs==25.3.0
billiard==4.2.1
celery==5.3.0
Django==5.1.7
django-celery-beat==2.7.0
django-celery-results==2.5.1
django-db-connection-pool==1.2.5
django-redis==5.4.0
eventlet==0.39.1
numpy==2.2.4
openpyxl==3.1.5
pandas==2.2.3
pillow==11.1.0
PyMySQL==1.1.1
python-crontab==3.2.0
python-dateutil==2.9.0.post0
redis==5.2.1
requests==2.32.3
tqdm==4.67.1
urllib3==2.3.0
```
### 环境依赖
```python
1、python3.11
2、mysql服务器
3、redis服务器
```

### 指令集
```bash
celery启动指令
    1、celery -A TestProject worker -l info -P eventlet -c 1000 -Q default,pack,pack_io

django指令
    1、数据迁移文件生成指令: python manage.py makemigrations
    2、数据迁移指令: python manage.py migrate
    3、启动服务指令: python manage.py runserver 0.0.0.0:8527
    
python指令
    1、安装依赖: pip install -r requirements.txt
    
```

### 服务启动步骤
```bash
1、创建一个mysql数据库
2、修改TestProject-setting.py-DATABASES 配置的数据连接方式
3、修改TestProject-setting.py-CACHES 配置的redis连接方式
4、执行数据迁移指令: python manage.py makemigrations  , python manage.py migrate
5、启动redis
6、项目根目录启动celery: celery -A TestProject worker -l info -P eventlet -c 1000 -Q default,pack,pack_io
7、项目根目录启动django: python manage.py runserver 0.0.0.0:8527

```
### 其他
```bash
1、日志配置TestProject-setting.py-LOGGING 默认是不输出本地,如果需要放开则会输出到 logs文件目录
```