/**
 * chat.js - 浮动对话窗口逻辑 + SSE 流式渲染
 */

let chatMessages = []; // 当前会话消息 [{role, content}]
let isStreaming = false;
let currentEventSource = null;
let chatWidgetFirstOpen = true;

// 加载聊天历史
async function loadChatHistory() {
    try {
        const data = await apiGet('/chat/history');
        chatMessages = data.messages || [];
        renderChatMessages();
    } catch (e) {
        console.warn('加载历史失败:', e);
    }
}

// 保存聊天历史
async function saveChatHistory() {
    try {
        await apiPost('/chat/history', chatMessages);
        showToast('聊天记录已保存', 'success');
    } catch (e) {
        showToast('保存失败: ' + e.message, 'error');
    }
}

// 清空聊天
async function clearChat() {
    if (!confirm('确定清空所有聊天记录？')) return;
    chatMessages = [];
    try {
        await apiDelete('/chat/history');
    } catch (e) { /* ignore */ }
    renderChatMessages();
    showToast('聊天记录已清空', 'success');
}

// 渲染聊天消息
function renderChatMessages() {
    const container = document.getElementById('chatMessages');
    if (chatMessages.length === 0) {
        container.innerHTML = `
            <div class="welcome-message">
                <div class="icon">🌿</div>
                <h2>欢迎使用碳策Agent</h2>
                <p>我是建筑节能减排智能助手，可以帮您分析建筑能耗、提供节能建议、查询分析报告。请输入您的问题开始对话。</p>
            </div>`;
        return;
    }
    container.innerHTML = chatMessages.map(msg => createMessageHTML(msg.role, msg.content)).join('');
    scrollToBottom();
}

// 创建消息 HTML
function createMessageHTML(role, content) {
    const avatar = role === 'user' ? '👤' : '🤖';
    const escaped = escapeHTML(content);
    const formatted = formatMessage(escaped);
    return `
        <div class="message ${role}">
            <div class="message-avatar">${avatar}</div>
            <div class="message-bubble">${formatted}</div>
        </div>`;
}

// 格式化消息（简单 Markdown）
function formatMessage(text) {
    return text
        // 标题
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        // 粗体
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // 行内代码
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // 列表
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
        // 换行
        .replace(/\n/g, '<br>');
}

// HTML 转义
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// 滚动到底部
function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

// 发送消息
function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text || isStreaming) return;

    // 移除欢迎消息
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // 添加用户消息
    chatMessages.push({ role: 'user', content: text });
    const container = document.getElementById('chatMessages');
    container.insertAdjacentHTML('beforeend', createMessageHTML('user', text));
    input.value = '';
    autoResizeInput();
    scrollToBottom();

    // 创建助手消息占位
    const assistantDiv = document.createElement('div');
    assistantDiv.className = 'message assistant';
    assistantDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble typing-cursor"></div>`;
    container.appendChild(assistantDiv);
    scrollToBottom();

    // 开始流式接收
    isStreaming = true;
    updateSendButton();
    let fullResponse = '';

    currentEventSource = streamChat(
        text,
        // onMessage
        (chunk) => {
            fullResponse += chunk;
            const bubble = assistantDiv.querySelector('.message-bubble');
            bubble.innerHTML = formatMessage(escapeHTML(fullResponse));
            bubble.classList.add('typing-cursor');
            scrollToBottom();
        },
        // onDone
        () => {
            isStreaming = false;
            currentEventSource = null;
            chatMessages.push({ role: 'assistant', content: fullResponse });
            const bubble = assistantDiv.querySelector('.message-bubble');
            bubble.classList.remove('typing-cursor');
            updateSendButton();
        },
        // onError
        (err) => {
            isStreaming = false;
            currentEventSource = null;
            const bubble = assistantDiv.querySelector('.message-bubble');
            bubble.classList.remove('typing-cursor');
            bubble.innerHTML = `<span style="color:#e74c3c">❌ 请求失败: ${escapeHTML(err)}</span>`;
            updateSendButton();
        }
    );
}

// 快捷查询
function quickQuery(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}

// 更新发送按钮状态
function updateSendButton() {
    const btn = document.getElementById('sendBtn');
    const input = document.getElementById('chatInput');
    btn.disabled = isStreaming;
    input.disabled = isStreaming;
}

// 输入框自动调整高度
function autoResizeInput() {
    const input = document.getElementById('chatInput');
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
}

// ========== 浮动窗口逻辑 ==========

// 展开/关闭聊天窗口
function toggleChatWidget() {
    const widget = document.getElementById('chatWidget');
    const fab = document.getElementById('chatFab');
    if (widget.classList.contains('hidden')) {
        widget.classList.remove('hidden');
        widget.classList.remove('minimized');
        fab.style.display = 'none';
        // 首次展开时加载历史
        if (chatWidgetFirstOpen) {
            chatWidgetFirstOpen = false;
            loadChatHistory();
        }
        scrollToBottom();
    } else {
        widget.classList.add('hidden');
        fab.style.display = 'flex';
    }
}

// 最小化/还原聊天窗口
function minimizeChatWidget() {
    const widget = document.getElementById('chatWidget');
    if (widget.classList.contains('minimized')) {
        widget.classList.remove('minimized');
    } else {
        widget.classList.add('minimized');
    }
}

// ========== 拖动逻辑 ==========

document.addEventListener('DOMContentLoaded', () => {
    const widget = document.getElementById('chatWidget');
    const header = document.getElementById('chatWidgetHeader');
    const input = document.getElementById('chatInput');

    // 输入框自动调整高度
    if (input) {
        input.addEventListener('input', autoResizeInput);
    }

    // 拖动相关
    let isDragging = false;
    let dragOffset = { x: 0, y: 0 };

    header.addEventListener('mousedown', (e) => {
        // 忽略按钮点击
        if (e.target.closest('#chatWidgetControls')) return;
        isDragging = true;
        const rect = widget.getBoundingClientRect();
        dragOffset = { x: e.clientX - rect.left, y: e.clientY - rect.top };
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const x = Math.max(0, Math.min(e.clientX - dragOffset.x, window.innerWidth - widget.offsetWidth));
        const y = Math.max(0, Math.min(e.clientY - dragOffset.y, window.innerHeight - widget.offsetHeight));
        widget.style.left = x + 'px';
        widget.style.top = y + 'px';
        widget.style.right = 'auto';
        widget.style.bottom = 'auto';
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });
});
