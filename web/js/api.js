/**
 * api.js - HTTP 客户端封装
 */

const API_BASE = '/api/v1';

async function request(url, options = {}) {
    const resp = await fetch(API_BASE + url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || '请求失败');
    }
    // 检查是否为文件下载
    const contentType = resp.headers.get('content-type') || '';
    if (contentType.includes('application/vnd.openxmlformats')) {
        return resp; // 返回原始 response 用于 blob 下载
    }
    return resp.json();
}

const apiGet = (url, params) => {
    if (params) {
        const qs = new URLSearchParams(params).toString();
        url = qs ? `${url}?${qs}` : url;
    }
    return request(url);
};

const apiPost = (url, data) => request(url, { method: 'POST', body: JSON.stringify(data) });

const apiPut = (url, data) => request(url, { method: 'PUT', body: JSON.stringify(data) });

const apiDelete = (url) => request(url, { method: 'DELETE' });

/**
 * SSE 流式对话
 * @param {string} query 用户查询
 * @param {function} onMessage 收到文本回调
 * @param {function} onDone 完成回调
 * @param {function} onError 错误回调
 */
function streamChat(query, onMessage, onDone, onError) {
    const url = `${API_BASE}/chat/stream?q=${encodeURIComponent(query)}`;
    const evtSource = new EventSource(url);

    evtSource.addEventListener('message', (e) => {
        onMessage(e.data);
    });

    evtSource.addEventListener('done', () => {
        evtSource.close();
        onDone();
    });

    evtSource.addEventListener('error', (e) => {
        evtSource.close();
        // EventSource 的 error 事件不一定是服务端错误，检查是否正常关闭
        if (e.data) {
            onError(e.data);
        } else {
            onDone();
        }
    });

    return evtSource;
}

/**
 * 显示消息提示
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}
