from __future__ import absolute_import, unicode_literals
import pymysql

from .celery import celery_app

pymysql.install_as_MySQLdb()

# 使得django启动时加载celery的app
__all__ = ('celery_app',)
