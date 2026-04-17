/**
 * analysis.js - 数据分析 + ECharts 图表渲染
 */

let analysisCharts = []; // 跟踪已创建的 ECharts 实例

// ========== 初始化数据分析页 ==========
async function initAnalysisPage() {
    await loadAnalysisBuildingChips();
    await loadCbecsReports();
    initReportBuildingChips();
}

// ========== 分析 Tab 切换 ==========
function switchAnalysisTab(tab) {
    document.querySelectorAll('#page-analysis .tab-item').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });
    document.querySelectorAll('#page-analysis .tab-content').forEach(c => {
        c.classList.toggle('active', c.id === `tab-${tab}`);
    });
    if (tab === 'analysis-building') loadAnalysisBuildingChips();
    if (tab === 'analysis-cbecs') {
        loadCbecsReports();
        requestAnimationFrame(() => renderCbecsStaticCharts());
    }
    if (tab === 'analysis-report') initReportBuildingChips();
}

// ========== 建筑选择 Chips ==========
let selectedAnalysisBuildings = new Set();

async function loadAnalysisBuildingChips() {
    try {
        const data = await apiGet('/buildings');
        const buildings = data.buildings || {};
        const container = document.getElementById('analysisBuildingChips');
        container.innerHTML = '';
        Object.entries(buildings).forEach(([id, b]) => {
            const name = (b.basic_info || {}).name || id;
            const selected = selectedAnalysisBuildings.has(id);
            container.innerHTML += `
                <span class="building-chip ${selected ? 'selected' : ''}"
                      data-id="${id}" onclick="toggleAnalysisBuilding('${id}')">
                    ${escapeHTML(name)}
                </span>`;
        });
    } catch (e) { /* ignore */ }
}

function toggleAnalysisBuilding(id) {
    if (selectedAnalysisBuildings.has(id)) {
        selectedAnalysisBuildings.delete(id);
    } else {
        selectedAnalysisBuildings.add(id);
    }
    loadAnalysisBuildingChips();
}

// ========== 建筑数据分析 ==========
async function runBuildingAnalysis() {
    if (selectedAnalysisBuildings.size === 0) {
        showToast('请至少选择一栋建筑', 'warning');
        return;
    }

    try {
        const ids = Array.from(selectedAnalysisBuildings);
        const params = {};
        const allData = {};
        for (const id of ids) {
            const b = await apiGet(`/buildings/${id}`);
            allData[id] = b;
        }

        const container = document.getElementById('buildingAnalysisResult');
        const names = ids.map(id => (allData[id].basic_info || {}).name || id);
        const areas = ids.map(id => (allData[id].basic_info || {}).floor_area_sqm || 0);
        const employees = ids.map(id => (allData[id].basic_info || {}).num_employees || 0);
        const totalArea = areas.reduce((a, b) => a + b, 0);
        const totalEmployees = employees.reduce((a, b) => a + b, 0);
        const avgYear = ids.reduce((acc, id) => acc + ((allData[id].basic_info || {}).year_built || 2020), 0) / ids.length;

        let html = `
            <div class="metrics-grid">
                <div class="metric-card"><div class="metric-value">${ids.length}</div><div class="metric-label">选中建筑数</div></div>
                <div class="metric-card"><div class="metric-value">${totalArea.toLocaleString()}</div><div class="metric-label">总面积 (m²)</div></div>
                <div class="metric-card"><div class="metric-value">${totalEmployees.toLocaleString()}</div><div class="metric-label">总员工数</div></div>
                <div class="metric-card"><div class="metric-value">${avgYear.toFixed(0)}</div><div class="metric-label">平均建造年份</div></div>
            </div>

            <div class="chart-container">
                <div class="chart-title">📐 建筑面积分布</div>
                <div class="chart-placeholder" id="analysisAreaChart"></div>
            </div>

            <div class="chart-container">
                <div class="chart-title">🏢 建筑类型分布</div>
                <div class="chart-placeholder" id="analysisTypeChart"></div>
            </div>`;

        // 检查能耗数据
        let hasEnergy = false;
        const energyByBuilding = {};
        ids.forEach(id => {
            const monthly = (allData[id].energy_consumption || {}).monthly_data || {};
            if (Object.keys(monthly).length > 0) {
                hasEnergy = true;
                const name = (allData[id].basic_info || {}).name || id;
                energyByBuilding[name] = {
                    electricity: Object.values(monthly).reduce((s, m) => s + (m.electricity_kwh || 0), 0),
                    gas: Object.values(monthly).reduce((s, m) => s + (m.natural_gas_m3 || 0), 0),
                    water: Object.values(monthly).reduce((s, m) => s + (m.water_m3 || 0), 0),
                };
            }
        });

        if (hasEnergy) {
            html += `
                <div class="chart-container">
                    <div class="chart-title">⚡ 建筑能耗对比</div>
                    <div class="chart-placeholder" id="analysisEnergyChart"></div>
                </div>

                <div class="chart-container">
                    <div class="chart-title">📊 能耗强度对比 (EUI)</div>
                    <div class="chart-placeholder" id="analysisEuiChart"></div>
                </div>

                <div class="card">
                    <div class="card-title mb-md">能耗数据汇总表</div>
                    <div class="table-wrapper">
                        <table class="data-table">
                            <thead><tr><th>建筑名称</th><th>电力(kWh)</th><th>天然气(m³)</th><th>用水(m³)</th></tr></thead>
                            <tbody>${Object.entries(energyByBuilding).map(([name, d]) => `
                                <tr><td>${escapeHTML(name)}</td><td>${d.electricity.toLocaleString()}</td><td>${d.gas.toLocaleString()}</td><td>${d.water.toLocaleString()}</td></tr>
                            `).join('')}</tbody>
                        </table>
                    </div>
                </div>`;
        } else {
            html += `<div class="card text-center text-muted"><p>选中的建筑暂无能耗数据</p></div>`;
        }

        container.innerHTML = html;

        // 渲染图表（延迟确保 DOM 已更新）
        setTimeout(() => {
            // 面积图
            renderChart('analysisAreaChart', {
                title: { text: '建筑面积分布', left: 'center' },
                tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
                xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
                yAxis: { type: 'value', name: '面积 (m²)' },
                series: [{ name: '建筑面积', type: 'bar', data: areas, label: { show: true, position: 'top' } }]
            });

            // 类型饼图
            const typeCounts = {};
            ids.forEach(id => {
                const t = (allData[id].basic_info || {}).building_type || '未知';
                typeCounts[t] = (typeCounts[t] || 0) + 1;
            });
            renderChart('analysisTypeChart', {
                title: { text: '建筑类型分布', left: 'center' },
                tooltip: { trigger: 'item', formatter: '{b}: {c}栋 ({d}%)' },
                series: [{
                    name: '建筑类型', type: 'pie', radius: ['30%', '60%'],
                    data: Object.entries(typeCounts).map(([k, v]) => ({ value: v, name: k })),
                    label: { formatter: '{b}\n{c}栋' }
                }]
            });

            if (hasEnergy) {
                const eNames = Object.keys(energyByBuilding);
                // 能耗对比
                renderChart('analysisEnergyChart', {
                    title: { text: '建筑能耗对比', left: 'center' },
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['电力(kWh)', '天然气(m³)', '用水(m³)'], top: 'bottom' },
                    xAxis: { type: 'category', data: eNames },
                    yAxis: { type: 'value', name: '消耗量' },
                    series: [
                        { name: '电力(kWh)', type: 'bar', data: eNames.map(n => energyByBuilding[n].electricity), itemStyle: { color: '#f1c40f' } },
                        { name: '天然气(m³)', type: 'bar', data: eNames.map(n => energyByBuilding[n].gas), itemStyle: { color: '#e74c3c' } },
                        { name: '用水(m³)', type: 'bar', data: eNames.map(n => energyByBuilding[n].water), itemStyle: { color: '#3498db' } },
                    ]
                });

                // EUI
                const euiData = ids.map(id => {
                    const area = (allData[id].basic_info || {}).floor_area_sqm || 1;
                    const monthly = (allData[id].energy_consumption || {}).monthly_data || {};
                    const totalElec = Object.values(monthly).reduce((s, m) => s + (m.electricity_kwh || 0), 0);
                    const months = Math.max(Object.keys(monthly).length, 1);
                    return { name: (allData[id].basic_info || {}).name || id, eui: (totalElec / months * 12) / area };
                });
                renderChart('analysisEuiChart', {
                    title: { text: '能耗强度对比 (EUI)', left: 'center' },
                    tooltip: { trigger: 'axis' },
                    xAxis: { type: 'category', data: euiData.map(d => d.name) },
                    yAxis: { type: 'value', name: 'EUI (kWh/m²/年)' },
                    series: [{
                        name: 'EUI', type: 'bar',
                        data: euiData.map(d => ({
                            value: parseFloat(d.eui.toFixed(1)),
                            itemStyle: { color: d.eui < 100 ? '#27ae60' : d.eui < 200 ? '#f39c12' : '#e74c3c' }
                        })),
                        label: { show: true, position: 'top', formatter: '{c}' }
                    }]
                });
            }
        }, 100);

    } catch (e) {
        showToast('分析失败: ' + e.message, 'error');
    }
}

// ========== CBECS 基准分析 ==========
async function loadCbecsReports() {
    try {
        const data = await apiGet('/reports');
        const reports = data.reports || [];
        const container = document.getElementById('cbecsReportList');
        if (reports.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>暂无分析报告</p></div>';
            return;
        }
        container.innerHTML = reports.map(r => `
            <div class="report-item" onclick="viewCbecsReport('${r.report_id}')">
                <div class="report-item-info">
                    <h4>${escapeHTML(r.title)}</h4>
                    <p>${escapeHTML((r.summary || '').slice(0, 80))}${(r.summary || '').length > 80 ? '...' : ''}</p>
                </div>
                <span class="badge badge-info">${r.report_id}</span>
            </div>
        `).join('');
    } catch (e) {
        console.warn('加载报告列表失败:', e);
    }
}

async function viewCbecsReport(id) {
    try {
        const data = await apiGet(`/reports/${id}/summary`);
        const detail = document.getElementById('cbecsReportDetail');
        detail.classList.remove('hidden');
        detail.innerHTML = `<div class="report-detail">${formatCbecsSummary(data.summary)}</div>`;
    } catch (e) {
        showToast('加载报告失败: ' + e.message, 'error');
    }
}

function formatCbecsSummary(text) {
    return escapeHTML(text)
        .replace(/^#{1,3}\s+(.+)$/gm, '<h3>$1</h3>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/\n/g, '<br>');
}

// CBECS 静态图表
function renderCbecsStaticCharts() {
    // 建筑类型EUI
    renderChart('cbecsEuiChart', {
            title: { text: '不同建筑类型能耗强度对比', left: 'center' },
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
            xAxis: {
                type: 'category',
                data: ['餐饮服务', '医疗保健', '食品销售', '住宿服务', '教育建筑', '办公建筑', '零售建筑', '仓储建筑'],
                axisLabel: { rotate: 30 }
            },
            yAxis: { type: 'value', name: 'EUI (kBtu/sqft)' },
            series: [{ name: '能耗强度', type: 'bar', data: [325, 250, 200, 125, 80, 87, 65, 30], label: { show: true, position: 'top' } }]
        });

        // 供暖能源
        renderChart('cbecsHeatingChart', {
            title: { text: '供暖能源占比', left: 'center' },
            tooltip: { trigger: 'item' },
            series: [{
                name: '供暖能源', type: 'pie', radius: ['40%', '70%'],
                data: [
                    { value: 45, name: '天然气炉具' },
                    { value: 25, name: '锅炉系统' },
                    { value: 15, name: '热泵系统' },
                    { value: 10, name: '区域供热' },
                    { value: 5, name: '电阻加热' }
                ]
            }]
        });

        // 区域能耗
        renderChart('cbecsRegionalChart', {
            title: { text: '各区域能耗强度对比', left: 'center' },
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'category', data: ['东北部', '中西部', '南部', '西部'] },
            yAxis: { type: 'value', name: 'EUI (kBtu/sqft)' },
            series: [{ name: 'EUI', type: 'bar', data: [115, 107, 95, 85], label: { show: true, position: 'top' } }]
        });
}

// ========== ECharts 渲染工具 ==========
function renderChart(domId, option) {
    const dom = document.getElementById(domId);
    if (!dom) return;

    // 销毁已有实例（避免隐藏容器初始化后尺寸为 0 的问题）
    const existing = echarts.getInstanceByDom(dom);
    if (existing) existing.dispose();

    const chart = echarts.init(dom);
    chart.setOption(option);
    analysisCharts.push(chart);

    // 确保图表填满容器
    requestAnimationFrame(() => chart.resize());

    const resizeHandler = () => chart.resize();
    window.addEventListener('resize', resizeHandler);
    return chart;
}

// 清理所有 ECharts 实例（供 app.js switchPage 调用）
function disposeCharts() {
    analysisCharts.forEach(c => c.dispose());
    analysisCharts = [];
}

function escapeHTML(str) {
    if (typeof str !== 'string') str = String(str || '');
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
