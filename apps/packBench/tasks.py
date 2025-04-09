# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
@Project ：TestProject
@File ：tasks.py
@Time ：2025/3/21 11:24 
@Author ：11031840
@Motto: 理解しあうのはとても大事なことです。理解とは误解の総体に过ぎないと言う人もいますし
@tasks.py功能简介：

"""
import json
import time
from celery.utils import uuid
from datetime import timedelta, datetime
from celery import shared_task, current_task, chord, group
from django.db.backends.mysql.base import version

from src.projecctPublish.productProject import PublishProductProject
from src.projecctPublish.resourceProject import PublishResourceProject
from src.projecctPublish.rulePackage import PublishRuleProject
# from src.projecctPublish.productProject import PublishProductProject
from src.workers.classTasks import MessageNotificationTask
from celery.exceptions import SoftTimeLimitExceeded


@shared_task(bind=True, base=MessageNotificationTask)
def pack_product_package(self, *args, **kwargs):
    """产品包打包任务"""
    self._notifies = False
    self._is_parent_task = False
    kwargs = kwargs.get("kwargs")
    self.logger.info(f"pack_product_package:{kwargs}")
    parent_task = kwargs.get("parent_task")
    self._parent_task_id = parent_task
    is_regional = kwargs.get('is_regional', False)
    back_login = kwargs.get('back_login')
    zf_login = kwargs.get('zf_login')
    back_url = kwargs.get("back_url")
    zf_url = kwargs.get("zf_url")
    bot_key = kwargs.get("bot_key")
    save_path = kwargs.get("save_path")
    # 实际业务逻辑

    try:
        # 实际业务逻辑
        self.logger.info(f"Processing product package with {kwargs}")
        product_obj = PublishProductProject(host=back_url,
                                            regional_publishing=is_regional,
                                            back_login=back_login,
                                            zf_host=zf_url,
                                            zf_login=zf_login,
                                            branch_name=kwargs.get('param').get('code_branch'),
                                            is_upload_zongfu=kwargs.get('param').get('upload_zongfu'),
                                            is_sign_package=kwargs.get('param').get('sign_package'),
                                            wx_bot_key=bot_key,
                                            save_path=save_path
                                            )
        obj_result = product_obj.upload_product_publishing()
        result = {
            "result": True, "version": product_obj.product_version,
            "error": None,
            "type_code": 'product_version',
            "type": f"{kwargs.get('param').get('name')}",
            "img": product_obj.product_version_img_path
        }
        if obj_result is True:
            return {"status": "success", "result_data": result}
        else:
            result["result"] = False
            return {"status": "failure", "result_data": result}
    except SoftTimeLimitExceeded:
        self.logger.warning("Product package task timeout")
        raise
    except Exception as e:
        self.logger.error(f"Product task error: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, base=MessageNotificationTask)
def pack_rule_package(self, *args, **kwargs):
    """规则包打包任务"""
    try:
        self._notifies = False
        self._is_parent_task = False
        kwargs = kwargs.get("kwargs")
        self.logger.info(f"pack_rule_package:{kwargs}")
        parent_task = kwargs.get("parent_task")
        self._parent_task_id = parent_task
        is_regional = kwargs.get('is_regional', False)
        back_login = kwargs.get('back_login')
        back_url = kwargs.get("back_url")
        get_rule_host = kwargs.get("get_rule_host")
        save_path = kwargs.get("save_path")
        bot_key = kwargs.get("bot_key")
        self.logger.info(f"Processing rule package with {kwargs}")

        rule_obj = PublishRuleProject(
            host=back_url, back_login=back_login, regional_publishing=is_regional,
            get_rule_host=get_rule_host, save_path=save_path, wx_bot_key=bot_key)

        obj_result = rule_obj.upload_rule_publishing()
        result = {
            "result": True, "version": rule_obj.rule_version,
            "type_code": 'rule_version',
            "error": None,
            "type": f"{kwargs.get('param').get('name')}"
        }
        if obj_result is True:
            return {"status": "success", "result_data": result}
        else:
            result["result"] = False
            return {"status": "failure", "result_data": result}

    except SoftTimeLimitExceeded:
        self.logger.warning("Product rule task timeout")
        raise
    except Exception as e:
        self.logger.error(f"rule task error: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, base=MessageNotificationTask)
def pack_resource_package(self, *args, **kwargs):
    """资源包打包任务"""
    try:
        self.logger.info(f"Processing resource package with {kwargs}")
        self._notifies = False
        self._is_parent_task = False
        kwargs = kwargs["kwargs"]
        is_regional = kwargs.get('is_regional', False)
        back_login = kwargs.get('back_login')
        back_url = kwargs.get("back_url")
        parent_task = kwargs["parent_task"]
        self._parent_task_id = parent_task
        branch_name = kwargs.get('param').get('name')
        resource_obj = PublishResourceProject(host=back_url,
                                              regional_publishing=is_regional,
                                              back_login=back_login,
                                              branch_name=branch_name)
        print("正在执行资源包打包任务")
        obj_result = resource_obj.upload_resource_publishing()
        result = {
            "result": True, "version": resource_obj.resource_name,
            "type_code": 'resource_version',
            "error": None, "type": f"{branch_name}"
        }
        if obj_result is True:
            return {"status": "success", "result_data": result}  # 修正类型字段
        else:
            result["result"] = False
            return {"status": "failure", "result_data": result}

    except SoftTimeLimitExceeded:
        self.logger.warning("Resource task timeout")  # 修正日志消息
        raise
    except Exception as e:
        self.logger.error(f"resource task error: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, base=MessageNotificationTask)
def process_results(self, results, **kwargs):
    """结果聚合处理器"""
    try:
        self._notifies = True
        self._is_parent_task = False
        parent_task = kwargs["task_id"]
        self._parent_task_id = parent_task
        success = all(r.get('status') == 'success' for r in results if isinstance(r, dict))
        result = {
            "summary": "completed" if success else "partial_failure",
            "detail": results,
            "timestamp": str(self.request.eta),
            "parent_task": parent_task
        }
        return result
    except Exception as e:
        self.logger.error(f"process_results task error: {e}")


@shared_task(bind=True, base=MessageNotificationTask)
def error_handler(self, task_id, parent_task):
    """统一错误处理"""
    try:
        self._notifies = True  # 先禁用通知
        self._is_parent_task = False
        self._parent_task_id = parent_task
        from celery.result import AsyncResult
        task = AsyncResult(task_id)
        result = {
            "error_task": task_id,
            "status": task.status,
            "error": str(task.result),
            "parent_task": parent_task
        }
        return result
    except Exception as e:
        self.logger.error(f"error_handler task error: {e}")


@shared_task(bind=True, base=MessageNotificationTask)
def pack_package(self, *args, **kwargs):
    """主编排任务"""

    pack_types = kwargs.get('pack_types', {})
    if not isinstance(pack_types, dict):
        raise ValueError("pack_types must be a dict")

    self.logger.info(f"pack_package入参：{kwargs}")
    parent_task = kwargs.get("task_id")
    is_regional = kwargs.get("is_regional", False)
    get_rule_host = kwargs.get("get_rule_host", None)
    self._notifies = True
    self._parent_task_id = parent_task
    self._is_parent_task = True
    login_params = dict(kwargs.get("environment").get("login", {}))
    back_login = login_params.get("back", None)
    zf_login = login_params.get("zf", None)
    bot_key = kwargs.get("bot_key")
    save_path = kwargs.get("save_path")
    back_url = kwargs.get("environment").get("back_url")

    now = datetime.now()
    task_signatures = []

    try:
        if "product" in pack_types:
            product_uuid = f"product_{uuid()}"
            payload = {
                "task_id": product_uuid,
                "param": pack_types["product"],
                "parent_task": parent_task,
                "back_url": back_url,
                "zf_url": kwargs.get("environment").get("zf_url"),
                "back_login": back_login,
                "zf_login": zf_login,
                "is_regional": is_regional,
                "bot_key": bot_key,
                "save_path": save_path
            }
            task_signatures.append(
                pack_product_package.s(kwargs=payload).set(
                    task_id=product_uuid,
                    queue='pack_io',
                    priority=9,  # 最高优先级
                    expires=now + timedelta(minutes=30),
                    headers={'pack_type': 'product'}
                ))

        if "rule" in pack_types:
            rule_uuid = f"rule_{uuid()}"
            payload = {
                "task_id": rule_uuid,
                "param": pack_types["rule"],
                "parent_task": parent_task,
                "back_login": back_login,
                "back_url": back_url,
                "is_regional": is_regional,
                "save_path": save_path,
                "get_rule_host": get_rule_host,
                "bot_key": bot_key,
            }
            task_signatures.append(
                pack_rule_package.s(kwargs=payload).set(
                    task_id=rule_uuid,
                    queue='pack_io',
                    priority=6,
                    expires=now + timedelta(minutes=10),
                    headers={'pack_type': 'rule'}
                ))

        if "resource" in pack_types:
            resource_uuid = f"resource_{uuid()}"
            payload = {
                "task_id": resource_uuid,
                "param": pack_types["resource"],
                "parent_task": parent_task,
                "back_login": back_login,
                "back_url": back_url,
                "is_regional": is_regional
            }
            task_signatures.append(
                pack_resource_package.s(kwargs=payload).set(
                    task_id=resource_uuid,
                    queue='pack',
                    priority=3,  # 最低优先级
                    expires=now + timedelta(minutes=10),
                    headers={'pack_type': 'resource'}
                ))

        if not task_signatures:
            return {"status": "skipped"}
        workflow = group(task_signatures) | process_results.s(**kwargs)
        self.logger.info(f"任务链结构: {workflow}")
        result = workflow.apply_async()
        # workflow = chord(
        #     header=group(task_signatures),
        #     body=process_results.s(parent_task=parent_task).on_error(error_handler.s(parent_task=parent_task))
        # )
        # result = workflow.apply_async()

        return {
            "orchestration_id": self.request.id,
            "child_tasks": [t.options["task_id"] for t in task_signatures],
            "result_id": result.id,
            "parent_task": parent_task
        }

    except Exception as e:
        self.logger.exception(f"Orchestration failed: {e}")
        raise self.retry(exc=e, countdown=60)


if __name__ == '__main__':
    pass
