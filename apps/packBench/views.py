import json
import time
import uuid

from django.shortcuts import render
from django.http import JsonResponse
from src.mytest import logger
from . import conn
from .forms import PackOperationForm
from .models import VersionBranch, PackLog, PackType
from .tasks import pack_package
from django_celery_results.models import TaskResult
from ..userSettings.models import CustomUser, Robot
from .models import Environment
from django.views import View
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q


def evironment_info(id):
    info = Environment.objects.filter(id=id)
    print(info)


class PackOperationView(View):
    """
    打包操作视图
    """
    option_choice = [{"name": "upload_zongfu", "title": "是否上传服务平台"},
                     {"name": "sign_package", "title": "是否签名"}]
    branch_types = VersionBranch.Type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment = Environment.objects.all()
        self.pack_types = PackType.objects.all().exclude(name__icontains='内核').order_by('name')
        self.robot = Robot.objects.all()
        self.message_info = {"tack_id": None, 'pack_log': None, 'msgs': ''}

    def get_base_context(self):
        """返回基础上下文"""
        return {
            'environment': self.environment,
            "pack_types": self.pack_types,
            "robot": self.robot,
            "option_choice": self.option_choice,
            "branch_types": self.branch_types
        }

    def get(self, request):
        context = self.get_base_context()
        return render(request, 'packBench/pack_operations1.html', context=context)

    def post(self, request):
        form = PackOperationForm(request.POST)
        context = self.get_base_context()

        if not form.is_valid():
            self.message_info['msgs'] = '表单验证失败,请检查传参'
            context["message"] = self.message_info
            return render(request, 'packBench/pack_operations1.html', context=context)

        if not self.get_last_pack_log():
            self.message_info['msgs'] = '已有任务正在运行，请等待完成'
            context["message"] = self.message_info
            return render(request, 'packBench/pack_operations1.html', context=context)

        self.call_task(request, form)
        context["message"] = self.message_info
        return render(request, 'packBench/pack_operations1.html', context=context)

    def set_pack_types_data(self, request, pack_types, environment, upload_zongfu, sign_package, code_branch, bot_key,
                            is_regional):
        """
        任务调度数据初始化
        """
        types_data = {
            "user": request.user.first_name,
            "environment": {environment.id: environment.name,
                            "login": environment.env_login_params,
                            "back_url": environment.back_url,
                            "zf_url": environment.zongfu_url},
            "save_path": environment.save_path,
            "is_regional": is_regional,
            "bot_key": bot_key.robot_key if bot_key else None
        }
        try:
            pack_types_dict = {}
            for pack_type in pack_types:
                alt_name = str(pack_type.alternate_name)
                if alt_name == 'None':
                    pack_type_name = str(pack_type.name)
                else:
                    pack_type_name = str(pack_type.name) + '_' + alt_name
                type_data = {
                    "name": pack_type_name,
                    "id": pack_type.id,
                }

                if "产品" in pack_type.name or "内核" in pack_type.name:
                    type_data.update({
                        "code_branch": code_branch.branch if code_branch else None,
                        "sign_package": sign_package if sign_package else False
                    })
                    key = "product" if "产品" in pack_type.name else "kernel"
                elif "规则" in pack_type.name:
                    key = "rule"
                    types_data["get_rule_host"] = pack_type.get_url
                elif "资源" in pack_type.name:
                    key = "resource"
                else:
                    key = "unknown"

                if "产品" in pack_type.name:
                    type_data["upload_zongfu"] = upload_zongfu

                pack_types_dict[key] = type_data
            types_data["pack_types"] = pack_types_dict
            return types_data
        except Exception as e:
            self.message_info["msgs"] = f"打包数据初始化失败: {str(e)}"
            return None

    def get_last_pack_log(self):
        """
        获取上一条记录，用于决定是否继续执行打包
        """
        try:
            last_pack_log = PackLog.objects.latest('id')
            if last_pack_log.status in ["running", "waiting"]:
                return False
            return True
        except PackLog.DoesNotExist:
            return True
        except Exception as e:
            self.message_info["msgs"] = f"获取上一条记录失败: {str(e)}"
            return False

    def call_task(self, request, form):
        """
        调用任务
        """
        try:
            environment = form.cleaned_data['environment']
            pack_types = form.cleaned_data['pack_types']
            upload_zongfu = form.cleaned_data.get('upload_zongfu', False)
            sign_package = form.cleaned_data.get('sign_package', False)
            code_branch = form.cleaned_data.get('code_branch')
            is_regional = form.cleaned_data.get('is_regional', False)
            bot_key = form.cleaned_data.get('robot')

            set_data = self.set_pack_types_data(request, pack_types, environment, upload_zongfu, sign_package,
                                                code_branch, bot_key, is_regional)
            print(set_data)
            if not set_data:
                return

            self.task_scheduling_pack_package(
                request, set_data, sign_package,
                upload_zongfu, environment, code_branch
            )
        except Exception as e:
            self.message_info["msgs"] = f"任务调用失败: {str(e)}"

    def task_scheduling_pack_package(self, request, pack_data, sign_package, upload_zongfu, environment, code_branch):
        """
        实际任务调度内容
        """
        try:
            task_uuid = f"pack_{uuid.uuid4()}"
            pack_data['task_id'] = task_uuid

            with transaction.atomic():  # 事务控制
                pack_log = PackLog.objects.create(  # 初始化任务日志信息
                    executor=request.user,
                    task_id=task_uuid,
                    status=PackLog.STATUS.WAITING,
                    is_sign=sign_package,
                    is_push_upload_zongfu=upload_zongfu,
                    environment=environment,
                    branch=code_branch,
                )

                self.message_info["pack_log"] = pack_log.id
                pack_data['pack_log_id'] = str(pack_log.id)
                pack_data["is_notifies"] = True

                result = pack_package.apply_async(
                    kwargs=pack_data,
                    args=[1, 2, 3, 4],
                    task_id=task_uuid
                )

                if result:
                    self.message_info["tack_id"] = result
                else:
                    raise Exception("任务创建失败")

        except Exception as e:
            self.message_info["msgs"] = f"任务调度失败: {str(e)}"
            if 'pack_log' in locals():
                pack_log.status = PackLog.STATUS.FAILED
                pack_log.save()


class LoadCodeBranches(View):
    """
    加载分支信息
    """

    def get(self, request):
        pack_type_ids = request.GET.get('pack_types', '').split(',')
        branch_type = request.GET.get('branch_type', None)
        print(pack_type_ids, branch_type)
        branches = VersionBranch.objects.filter(code_path__pack_type__id__in=pack_type_ids)
        if branch_type:
            branches = branches.filter(branch_type=branch_type)

        return render(request, 'packBench/branch_options.html', {
            'branches': branches
        })

    def post(self, request):
        pass


class GetTaskResult(View):
    """
    获取celery任务结果
    """

    DEFAULT_PAGE_SIZE = 15
    STATUS_CHOICES = ['SUCCESS', 'FAILURE', 'PENDING', 'STARTED']
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def _get_task_data(self, task):
        """提取任务数据的公共方法"""
        return {
            'task_id': task.task_id,
            'status': task.status,
            'result': task.result,
            'date_done': task.date_done.strftime(self.DATE_FORMAT) if task.date_done else '',
            'traceback': task.traceback or ''
        }

    def _get_full_task_data(self, task):
        """获取完整任务数据的公共方法"""
        data = self._get_task_data(task)
        data.update({
            'task_args': [task.task_args, task.task_kwargs],
            'task_name': task.task_name or '',
            'worke': task.worker,
        })
        return data

    def _validate_page_params(self, page_number, size):
        """验证分页参数"""
        try:
            page_number = int(page_number)
            size = int(size)
            return max(page_number, 1), max(size, 1)
        except (ValueError, TypeError):
            return 1, self.DEFAULT_PAGE_SIZE

    def get(self, request):
        """
        处理GET请求
        返回任务结果列表，支持搜索、过滤和分页
        """
        search = request.GET.get('search', '').strip()
        status = request.GET.get('status', '').strip()
        page_number, size = self._validate_page_params(
            request.GET.get('page', 1),
            request.GET.get('siz', self.DEFAULT_PAGE_SIZE)
        )

        # 构建查询
        tasks = TaskResult.objects.all().order_by('-date_created')

        # 应用过滤条件
        filters = Q()
        if search:
            filters &= Q(task_id__icontains=search)
        if status in self.STATUS_CHOICES:
            filters &= Q(status=status)

        tasks = tasks.filter(filters)

        # 分页处理
        paginator = Paginator(tasks, size)
        page_obj = paginator.get_page(page_number)

        # AJAX请求返回JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            tasks_data = [self._get_task_data(task) for task in page_obj]
            return JsonResponse({
                'tasks': tasks_data,
                'has_next': page_obj.has_next(),
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number
            })

        # 普通请求返回完整页面
        return render(request, 'packBench/result_table.html', {
            'page_obj': page_obj,
            'status_choices': self.STATUS_CHOICES,
            'current_status': status,
            'current_search': search
        })

    def post(self, request):
        """
        处理POST请求
        根据task_id返回单个任务的详细信息
        """
        task_id = request.POST.get('task_id', '').strip()
        if not task_id:
            return JsonResponse({'error': '任务ID不能为空'}, status=400)

        try:
            task_result = TaskResult.objects.get(task_id=task_id)
            return JsonResponse(self._get_full_task_data(task_result))
        except TaskResult.DoesNotExist:
            return JsonResponse({'error': '没有找到指定的任务'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)


class PackLogListView(ListView):
    """
    # 打包记录列表视图

    """
    model = PackLog
    template_name = 'packBench/pack_log_list.html'  # 模板文件
    context_object_name = 'pack_logs'  # 模板中使用的上下文变量名
    paginate_by = 15  # 每页显示15条记录
    ordering = ['-start_time']  # 按开始时间倒序排列
    default_title = '打包记录列表'

    def get_context_data(self, **kwargs):
        # 添加上下文数据，例如跳转链接
        context = super().get_context_data(**kwargs)
        context['title'] = self.default_title  # 使用类变量
        # context['pack_operation_url'] = reverse_lazy('pack:pack_operation')  # 打包操作页面的URL
        return context


a = {'pack_types': {
    'product': {'name': '产品包', 'id': 1, 'code_branch': 'test1', 'sign_package': True, 'upload_zongfu': True},
    'rule': {'name': '规则', 'id': 6}, 'resource': {'name': '资源', 'id': 3}}}
