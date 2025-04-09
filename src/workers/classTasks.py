# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：classTasks.py
@Time ：2025/3/31 8:55 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@classTasks.py功能简介：

"""
import asyncio

from billiard.exceptions import SoftTimeLimitExceeded
from django_celery_results.models import TaskResult
from apps.packBench.models import PackLog
from src.tool.robot import message_notification, _message_notification, img_notification
from celery import Task
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
import json
import logging
from datetime import datetime


class MessageNotificationTask(Task):
    """
    增强版任务基类，提供：
    1. 全生命周期状态追踪
    2. 原子化任务记录更新
    3. 结构化日志
    4. 异常自动捕获
    """
    # 任务超时配置
    time_limit = 1800  # 硬超时（秒）
    soft_time_limit = time_limit * 0.8  # 软超时（秒）

    # 重试策略
    autoretry_for = (Exception,)
    max_retries = 0
    retry_backoff = True
    retry_jitter = True
    default_retry_delay = time_limit * 0.5

    def __init__(self):
        self._task_data = None
        self._notifies = False
        self._parent_task_id = None
        self._is_parent_task = True
        self.logger = logging.getLogger('task')  # 使用配置中的'task' logger

    def _get_task_kwargs(self, task_id, args, kwargs):
        """安全提取任务参数"""

        try:
            if not kwargs.get('is_notifies'):
                self._notifies = False
            self._task_data = {
                'task_id': task_id,
                'kwargs': kwargs,
                'args': args,
                'start_time': datetime.now()
            }
        except (IndexError, TypeError, ValueError) as e:
            self.logger.warning(f"参数解析失败: {e}")

    def before_start(self, task_id, args, kwargs):
        """任务开始前初始化（Worker端）"""
        try:
            with transaction.atomic():
                self._get_task_kwargs(task_id, args, kwargs)
                meta = {'retries': self.request.retries}
                TaskResult.objects.create(
                    task_id=task_id,
                    status='STARTED',
                    task_name=self.name,
                    task_args=json.dumps(args, cls=DjangoJSONEncoder, ensure_ascii=False),
                    task_kwargs=json.dumps(kwargs, cls=DjangoJSONEncoder, ensure_ascii=False),
                    meta=json.dumps(meta, cls=DjangoJSONEncoder, ensure_ascii=False),
                    worker=self.request.hostname
                )
            if "pack_" in task_id:
                self._parent_task_id = task_id
                self.update_pack_log(event_type="started")
                self._send_notification('started', kwargs)

        except Exception as e:
            self.logger.exception(f"before_start 失败: {e}")
            raise

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """最终状态处理（无论成功失败都会执行）"""
        if not hasattr(self, '_notification_sent'):
            if status == 'SUCCESS':
                self.on_success(retval, task_id, args, kwargs)
            else:
                self.on_failure(retval, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """任务成功回调"""
        try:
            with transaction.atomic():
                self._get_task_kwargs(task_id, args, kwargs)
                task_result = TaskResult.objects.filter(task_id=task_id).first()
                meta = json.loads(task_result.meta)
                meta['retries'] = self.request.retries
                task_result.task_name = str(self.name)  # 任务名称
                task_result.task_args = json.dumps(args, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.task_kwargs = json.dumps(kwargs, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.meta = json.dumps(meta, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.status = 'SUCCESS'
                task_result.result = json.dumps(retval, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.date_done = datetime.now()
                task_result.worker = self.request.hostname
                task_result.save()
            if retval.get('pack_types') or retval.get('detail'):
                self.logger.info(
                    f"on_success 消息推送测试: {retval}")
                # 发送通知（示例）
                versions = self._send_notification('success', kwargs, retval)

                self.update_pack_log(event_type="success", versions=versions)

        except Exception as e:
            self.logger.exception(f"on_success 更新失败: {e}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败回调"""
        try:
            with transaction.atomic():
                self._get_task_kwargs(task_id, args, kwargs)
                task_result = TaskResult.objects.filter(task_id=task_id).first()
                meta = json.loads(task_result.meta)
                meta['retries'] = self.request.retries
                meta['error'] = str(exc)
                meta['retry_count'] = self.request.retries
                task_result.task_name = str(self.name)  # 任务名称
                task_result.task_args = json.dumps(args, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.task_kwargs = json.dumps(kwargs, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.status = 'FAILURE'
                task_result.traceback = str(einfo)
                task_result.meta = json.dumps(meta, cls=DjangoJSONEncoder, ensure_ascii=False)
                task_result.worker = self.request.hostname
                task_result.save()

            self._send_notification('failure', kwargs, error=exc)
            self.update_pack_log(event_type="failure")
        except Exception as e:
            self.logger.exception(f"on_failure 更新失败: {e}")

    def _send_notification(self, event_type, task_kwargs, result=None, error=None):
        """发送消息通知（根据实际需求实现）"""
        pack_log = PackLog.objects.get(task_id=self._parent_task_id)
        img_path = None
        versions = {}
        if pack_log:
            try:
                if pack_log.status in [PackLog.STATUS.RUNNING, PackLog.STATUS.RUNNING]:
                    bot_key = task_kwargs.get('bot_key')
                    user = task_kwargs.get('user')
                    print(f"jinru 消息发送{bot_key}，{task_kwargs}")
                    if not bot_key:
                        return
                    message = {
                        'event': event_type,
                        'task': self.name,
                        'user': user,
                        'task_id': self.request.id,
                        "environment": list(task_kwargs.get('environment').values())[0]
                    }
                    pack_type_list = {}
                    if event_type == 'started':
                        for pack_type, value in task_kwargs.get('pack_types').items():
                            if isinstance(value, dict):
                                if pack_type == 'product':
                                    message["code_branch"] = value.get('code_branch')
                                pack_type_list[value.get('name')] = ''
                        message["pack_type"] = pack_type_list

                    elif event_type == 'success':
                        # message['data'] = result
                        print(f"result-result,{result}")
                        for detail in result["detail"]:
                            result_data = detail.get("result_data")
                            pack_type_list[result_data.get('type')] = [result_data.get('version'),
                                                                       result_data.get('result')]
                            if "产品" in result_data.get('type'):
                                try:
                                    message["code_branch"] = task_kwargs.get('pack_types')['product'].get('code_branch')
                                    img_path = result_data.get('img')
                                except KeyError:
                                    print(KeyError)
                            if result_data.get("result"):
                                versions[result_data.get('type_code')] = result_data.get('version')
                            else:
                                versions[result_data.get('type_code')] = '任务异常'
                        message["pack_type"] = pack_type_list
                    elif event_type == 'failure':
                        message["pack_type"] = {'error': str(error)}
                    # 实际调用通知API（示例）
                    self.logger.info(
                        f"通知触发来源: {self.name} | "
                        f"事件类型: {event_type} | "
                        f"任务ID: {self.request.id}|"
                        f"message:{message}"
                    )
                    message_notification(bot_key, message)
                    if img_path:
                        img_notification(bot_key, img_path)
                    self.logger.info(f"通知发送: {message}")
                return versions
            except Exception as e:
                self.logger.exception(f"_send_notification 消息发送失败: {e}")

    def __call__(self, *args, **kwargs):
        """任务执行入口（增强异常捕获）"""
        try:
            self.logger.info(f"任务开始执行: {self.name}[{self.request.id}]")
            return super().__call__(*args, **kwargs)
        except SoftTimeLimitExceeded:
            self.logger.warning(f"任务超时: {self.name}[{self.request.id}]")
            raise
        except Exception as e:
            self.logger.exception(f"任务异常: {self.name}[{self.request.id}]")
            raise self.retry(exc=e)

    def update_pack_log(self, event_type, versions=None):
        """更新任务日志"""
        pack_log = PackLog.objects.get(task_id=self._parent_task_id)
        if event_type == 'success':
            pack_log.status = PackLog.STATUS.SUCCESS
        elif event_type == 'failure':
            pack_log.status = PackLog.STATUS.FAILED
        elif event_type == 'started':
            pack_log.status = PackLog.STATUS.RUNNING
        if versions:
            for key, v in versions.items():
                if hasattr(pack_log, key):  # 安全检查
                    setattr(pack_log, key, v)

        pack_log.save()


if __name__ == '__main__':
    pass
