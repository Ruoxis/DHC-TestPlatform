// 1. 定义全局命名空间
window.MyApp = window.MyApp || {};

// 2. 将方法挂载到全局命名空间
MyApp.getCSRFToken = function () {
    const cookie = document.cookie.match(/csrftoken=([^;]+)/);
    return cookie ? cookie[1] : null;
};

MyApp.buildModalContent = function (data) {
    const formatResult = (result) => {
        try {
            return typeof result === 'string' ? result : JSON.stringify(result, null, 2);
        } catch {
            return "结果格式无法解析";
        }
    };

    const statusClass = {
        'SUCCESS': 'bg-success',
        'FAILURE': 'bg-danger',
        'PENDING': 'bg-secondary',
        'STARTED': 'bg-info',
        'RETRY': 'bg-warning'
    }[data.status] || 'bg-primary';
    console.log(data)
    console.log(data.task_args)
    const task_args = data.task_args ? data.task_args.join(', ') : '无';
    return `
        <div class="mb-2"><strong>基础信息:</strong></div>
        <div class="mb-2">
            <strong>任务ID:</strong> <span>${data.task_id}</span>
            <strong>任务名称:</strong> <span>${data.task_name}</span>
            <strong>状态:</strong> <span class="badge ${statusClass}">${data.status}</span>
            <strong>传参数据:</strong>
            <span style="word-break: break-all; display: inline-block;">${task_args}</span>
            <strong>完成时间:</strong> <spanp>${data.date_done || '未完成'}</spanp>
        </div>
        <div class="mb-2"><strong>结果返回数据:</strong></div>
        <pre class="bg-light p-3 rounded">${formatResult(data.result)}</pre>
        ${data.traceback ? `
        <div class="mt-2"><strong>错误追踪:</strong></div>
        <pre class="bg-danger text-white p-3 rounded">${data.traceback}</pre>
        ` : ''}
    `;
};

MyApp.showError = function (message) {
    const alert = $(`
        <div class="alert alert-danger alert-dismissible fade show position-fixed bottom-0 end-0 m-3">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    $('body').append(alert);
    setTimeout(() => alert.alert('close'), 5000);
};

// 3. 初始化（如果需要）
$(document).ready(function () {
    console.log('PackBench JS initialized');
});

// // 统一管理AJAX请求
// MyApp.loadCodeBranches = function (packTypes, branchType, codeBranchSelect, loadCodeBranchesUrl) {
//     $.ajax({
//         url: loadCodeBranchesUrl,
//         method: 'GET',
//         data: {'pack_types': packTypes.join(','), 'branchType': branchType},
//         beforeSend: function () {
//             codeBranchSelect.innerHTML = '<option value="">加载中...</option>';
//         },
//         success: function (data) {
//             codeBranchSelect.innerHTML = data;
//             // 如果返回数据为空，显示提示
//             if (codeBranchSelect.options.length <= 1) {
//                 const option = document.createElement('option');
//                 option.value = '';
//                 option.textContent = '无可用分支';
//                 option.disabled = true;
//                 option.selected = true;
//                 codeBranchSelect.appendChild(option);
//             }
//         },
//         error: function () {
//             codeBranchSelect.innerHTML = '<option value="" disabled selected>加载失败，请重试</option>';
//         }
//     });
// }