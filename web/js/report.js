/**
 * report.js - Word 报告生成下载
 */

let selectedReportBuildings = new Set();

// 初始化报告建筑选择
async function initReportBuildingChips() {
    try {
        const data = await apiGet('/buildings');
        const buildings = data.buildings || {};
        const container = document.getElementById('reportBuildingChips');
        container.innerHTML = '';
        Object.entries(buildings).forEach(([id, b]) => {
            const name = (b.basic_info || {}).name || id;
            const selected = selectedReportBuildings.has(id);
            container.innerHTML += `
                <span class="building-chip ${selected ? 'selected' : ''}"
                      data-id="${id}" onclick="toggleReportBuilding('${id}')">
                    ${escapeHTML(name)}
                </span>`;
        });
    } catch (e) { /* ignore */ }
}

function toggleReportBuilding(id) {
    if (selectedReportBuildings.has(id)) {
        selectedReportBuildings.delete(id);
    } else {
        selectedReportBuildings.add(id);
    }
    initReportBuildingChips();
}

// 生成报告
async function generateReport() {
    const title = document.getElementById('reportTitle').value.trim() || '建筑能耗分析报告';
    const author = document.getElementById('reportAuthor').value.trim() || '碳策通智能体分析服务';
    const btn = document.getElementById('generateReportBtn');
    const progress = document.getElementById('reportProgress');

    const requestBody = {
        title,
        author,
        building_ids: Array.from(selectedReportBuildings),
        include_overview: document.getElementById('rptOverview').checked,
        include_area_analysis: document.getElementById('rptArea').checked,
        include_type_analysis: document.getElementById('rptType').checked,
        include_energy_analysis: document.getElementById('rptEnergy').checked,
        include_eui_analysis: document.getElementById('rptEui').checked,
        include_recommendations: document.getElementById('rptRec').checked,
    };

    // 至少选一个内容
    if (!Object.values(requestBody).slice(2).some(v => v)) {
        showToast('请至少选择一项报告内容', 'warning');
        return;
    }

    try {
        btn.disabled = true;
        progress.classList.remove('hidden');

        const resp = await fetch('/api/v1/report/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody),
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            throw new Error(err.detail || '生成失败');
        }

        // 下载文件
        const blob = await resp.blob();
        const contentDisposition = resp.headers.get('content-disposition') || '';
        let filename = `${title}.docx`;
        const match = contentDisposition.match(/filename=([^;]+)/);
        if (match) filename = decodeURIComponent(match[1].replace(/"/g, ''));

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('报告生成成功，已开始下载', 'success');
    } catch (e) {
        showToast('报告生成失败: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        progress.classList.add('hidden');
    }
}

function escapeHTML(str) {
    if (typeof str !== 'string') str = String(str || '');
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
