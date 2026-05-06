/**
 * carbon.js - 中国碳排放监测页面逻辑
 * 数据来源: Carbon Monitor (carbonmonitor.org) - 中国省级数据
 */

let carbonCharts = {};
let carbonMeta = null;
let _chinaGeoJson = null;

// 拖拽状态
let isDragging = false;
let dragStartX = 0;
let dragStartWidth = 0;

// 部门颜色映射
const SECTOR_COLORS = {
    "Power": "#e74c3c",
    "Industry": "#3498db",
    "Ground Transport": "#f39c12",
    "Residential": "#2ecc71",
    "Domestic Aviation": "#9b59b6",
    "International Aviation": "#1abc9c",
};

// 省份中文名映射
const PROVINCE_LABELS = {
    "Shanghai": "上海", "Beijing": "北京", "Tianjin": "天津", "Chongqing": "重庆",
    "Hebei": "河北", "Shanxi": "山西", "Inner Mongolia": "内蒙古", "Liaoning": "辽宁",
    "Jilin": "吉林", "Heilongjiang": "黑龙江", "Jiangsu": "江苏", "Zhejiang": "浙江",
    "Anhui": "安徽", "Fujian": "福建", "Jiangxi": "江西", "Shandong": "山东",
    "Henan": "河南", "Hubei": "湖北", "Hunan": "湖南", "Guangdong": "广东",
    "Guangxi": "广西", "Hainan": "海南", "Sichuan": "四川", "Guizhou": "贵州",
    "Yunnan": "云南", "Shaanxi": "陕西", "Gansu": "甘肃", "Qinghai": "青海",
    "Ningxia": "宁夏", "Xinjiang": "新疆", "Tibet": "西藏",
};

// 省份英文名 → GeoJSON 全称映射（用于 ECharts 中国地图）
const PROVINCE_GEO_NAMES = {
    "Beijing": "北京市", "Shanghai": "上海市", "Tianjin": "天津市",
    "Chongqing": "重庆市", "Hebei": "河北省", "Shanxi": "山西省",
    "Inner Mongolia": "内蒙古自治区", "Liaoning": "辽宁省", "Jilin": "吉林省",
    "Heilongjiang": "黑龙江省", "Jiangsu": "江苏省", "Zhejiang": "浙江省",
    "Anhui": "安徽省", "Fujian": "福建省", "Jiangxi": "江西省",
    "Shandong": "山东省", "Henan": "河南省", "Hubei": "湖北省",
    "Hunan": "湖南省", "Guangdong": "广东省", "Guangxi": "广西壮族自治区",
    "Hainan": "海南省", "Sichuan": "四川省", "Guizhou": "贵州省",
    "Yunnan": "云南省", "Shaanxi": "陕西省", "Gansu": "甘肃省",
    "Qinghai": "青海省", "Ningxia": "宁夏回族自治区", "Xinjiang": "新疆维吾尔自治区",
    "Tibet": "西藏自治区",
};

// ========== 初始化 ==========

async function initCarbonPage() {
    // 初始化拖拽调整宽度功能
    initSidebarResize();

    if (carbonMeta) {
        invalidateCarbonCharts();
        return;
    }

    showCarbonLoading(true);

    try {
        carbonMeta = await apiGet('/carbon/countries');
        if (!carbonMeta.success) {
            showToast('加载碳排放数据失败', 'error');
            return;
        }

        fillCarbonFilters();
        await loadCarbonDashboard();
    } catch (e) {
        showToast('加载碳排放数据失败: ' + e.message, 'error');
    } finally {
        showCarbonLoading(false);
    }
}

function fillCarbonFilters() {
    const sectorSelect = document.getElementById('carbonSectorFilter');
    if (sectorSelect && carbonMeta) {
        sectorSelect.innerHTML = '<option value="">全部部门</option>';
        (carbonMeta.sectors || []).forEach(s => {
            const label = (carbonMeta.sector_labels || {})[s] || s;
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = label;
            sectorSelect.appendChild(opt);
        });
    }

    const yearSelect = document.getElementById('carbonYearFilter');
    if (yearSelect && carbonMeta) {
        yearSelect.innerHTML = '<option value="">全部年份</option>';
        (carbonMeta.years || []).forEach(y => {
            const opt = document.createElement('option');
            opt.value = y;
            opt.textContent = y + '年';
            if (y === (carbonMeta.years || [])[0]) opt.selected = true;
            yearSelect.appendChild(opt);
        });
    }
}

// ========== 数据加载 ==========

async function loadCarbonDashboard() {
    const year = document.getElementById('carbonYearFilter')?.value || '';
    const sector = document.getElementById('carbonSectorFilter')?.value || '';
    showCarbonLoading(true);

    try {
        const [summaryData, trendData] = await Promise.all([
            apiGet(`/carbon/china/summary?year=${year}`),
            apiGet(`/carbon/china/trend?sector=${sector}&year=${year}&agg=month`),
        ]);

        renderCarbonSummary(summaryData);
        // 增加地图加载失败提示
        await loadChinaGeoJson().catch(() => {
            showToast('地图数据加载失败，仅展示图表数据', 'warning');
        });
        renderCarbonMap(summaryData);
        renderTrendChart(trendData);
        renderSectorChart(summaryData);
        renderProvinceRankChart(summaryData);
    } catch (e) {
        showToast('加载图表数据失败: ' + e.message, 'error');
    } finally {
        showCarbonLoading(false);
    }
}

// ========== 中国地图 ==========

async function loadChinaGeoJson() {
    if (_chinaGeoJson) return;
    try {
        // 替换为本地map文件夹的GeoJSON路径（根据实际目录结构调整）
        const resp = await fetch('/map/china_full.json'); 
        _chinaGeoJson = await resp.json();
        echarts.registerMap('china', _chinaGeoJson);
        console.log('本地中国地图GeoJSON加载成功');
    } catch (e) {
        console.error('加载本地中国地图 GeoJSON 失败:', e);
        // 降级方案：加载在线CDN（可选保留）
        try {
            const fallbackResp = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json');
            _chinaGeoJson = await fallbackResp.json();
            echarts.registerMap('china', _chinaGeoJson);
            console.log('降级加载在线GeoJSON成功');
        } catch (fallbackE) {
            console.error('在线降级加载也失败:', fallbackE);
        }
    }
}

async function renderCarbonMap(summaryData) {
    const container = document.getElementById('carbonMapChart');
    if (!container || !summaryData.success) return;

    await loadChinaGeoJson();
    if (!_chinaGeoJson) return;

    if (carbonCharts.map) carbonCharts.map.dispose();
    carbonCharts.map = echarts.init(container);

    const provinces = summaryData.provinces || {};

    // 将英文名映射为 GeoJSON 中的全称
    const mapData = Object.entries(provinces)
        .map(([en, value]) => ({
            name: PROVINCE_GEO_NAMES[en] || en,
            value: Math.round(value * 100) / 100,
        }))
        .filter(d => d.value > 0);

    const values = mapData.map(d => d.value);
    const maxVal = Math.max(...values, 1);

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: function (params) {
                if (params.value == null || isNaN(params.value)) return params.name + '<br/>暂无数据';
                return `<b>${params.name}</b><br/>碳排放量: <b>${params.value.toFixed(2)}</b> MtCO₂`;
            },
        },
        visualMap: {
            min: 0,
            max: maxVal,
            left: 'left',
            top: 'bottom',
            text: ['高', '低'],
            calculable: true,
            inRange: {
                color: ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
            },
            textStyle: { fontSize: 11 },
        },
        series: [{
            type: 'map',
            map: 'china',
            data: mapData,
            roam: true,
            label: {
                show: true,
                fontSize: 9,
                color: '#333',
            },
            emphasis: {
                label: { show: true, fontSize: 12, fontWeight: 'bold' },
                itemStyle: { areaColor: '#ff4500' },
            },
            itemStyle: {
                borderColor: '#fff',
                borderWidth: 0.8,
            },
        }],
    };

    carbonCharts.map.setOption(option);
}

// ========== 汇总卡片 ==========

function renderCarbonSummary(data) {
    if (!data.success) return;

    const provinces = data.provinces || {};
    const sectors = data.sectors || {};

    const total = data.total || 0;
    const topProvince = Object.entries(provinces).sort((a, b) => b[1] - a[1])[0];
    const topSector = Object.entries(sectors).sort((a, b) => b[1] - a[1])[0];

    document.getElementById('carbonTotalValue').textContent = (total / 1000).toFixed(1);
    document.getElementById('carbonTopProvince').textContent =
        topProvince ? (PROVINCE_LABELS[topProvince[0]] || topProvince[0]) : '--';
    document.getElementById('carbonTopSector').textContent =
        topSector ? ((carbonMeta?.sector_labels || {})[topSector[0]] || topSector[0]) : '--';
    document.getElementById('carbonProvinceCount').textContent = data.province_count || '--';
}

// ========== 趋势图 ==========

function renderTrendChart(trendData) {
    const container = document.getElementById('carbonTrendChart');
    if (!container || !trendData.success) return;

    if (carbonCharts.trend) carbonCharts.trend.dispose();
    carbonCharts.trend = echarts.init(container);

    const data = trendData.data || [];
    if (data.length === 0) return;

    const dates = data.map(d => d.date);
    const values = data.map(d => d.value);

    const option = {
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const p = params[0];
                return `<b>${p.axisValue}</b><br/>排放量: <b>${p.value.toFixed(2)}</b> MtCO₂/天`;
            },
        },
        grid: { top: 30, right: 15, bottom: 50, left: 55 },
        xAxis: {
            type: 'category',
            data: dates,
            axisLabel: { fontSize: 9, rotate: 45, interval: 2 },
        },
        yAxis: {
            type: 'value',
            name: 'MtCO₂',
            nameTextStyle: { fontSize: 10 },
            axisLabel: { fontSize: 9 },
        },
        series: [{
            type: 'line',
            data: values,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, color: '#e74c3c' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(231,76,60,0.25)' },
                    { offset: 1, color: 'rgba(231,76,60,0.02)' },
                ]),
            },
        }],
    };

    carbonCharts.trend.setOption(option);
}

// ========== 部门分布图 ==========

function renderSectorChart(summaryData) {
    const container = document.getElementById('carbonSectorChart');
    if (!container || !summaryData.success) return;

    if (carbonCharts.sector) carbonCharts.sector.dispose();
    carbonCharts.sector = echarts.init(container);

    const sectors = summaryData.sectors || {};

    const pieData = Object.entries(sectors)
        .sort((a, b) => b[1] - a[1])
        .map(([sector, value]) => ({
            name: (carbonMeta?.sector_labels || {})[sector] || sector,
            value: Math.round(value * 100) / 100,
            itemStyle: { color: SECTOR_COLORS[sector] || '#999' },
        }));

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} MtCO₂ ({d}%)',
        },
        legend: {
            orient: 'horizontal',
            bottom: 5,
            textStyle: { fontSize: 10 },
            itemWidth: 12,
            itemHeight: 12,
        },
        series: [{
            type: 'pie',
            radius: ['35%', '60%'],
            center: ['50%', '45%'],
            avoidLabelOverlap: true,
            label: { show: false },
            emphasis: {
                label: { show: true, fontSize: 12, fontWeight: 'bold' },
            },
            data: pieData,
        }],
    };

    carbonCharts.sector.setOption(option);
}

// ========== 省份排名图 ==========

function renderProvinceRankChart(summaryData) {
    const container = document.getElementById('carbonProvinceRankChart');
    if (!container || !summaryData.success) return;

    if (carbonCharts.rank) carbonCharts.rank.dispose();
    carbonCharts.rank = echarts.init(container);

    const provinces = summaryData.provinces || {};

    const sorted = Object.entries(provinces)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const names = sorted.map(([p]) => PROVINCE_LABELS[p] || p);
    const values = sorted.map(([, v]) => Math.round(v * 100) / 100);

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function (params) {
                const p = params[0];
                return `${p.name}: <b>${p.value.toFixed(2)}</b> MtCO₂`;
            },
        },
        grid: { top: 10, right: 30, bottom: 10, left: 80 },
        xAxis: {
            type: 'value',
            axisLabel: { fontSize: 10 },
        },
        yAxis: {
            type: 'category',
            data: names.reverse(),
            axisLabel: { fontSize: 11 },
        },
        series: [{
            type: 'bar',
            data: values.reverse().map((v) => ({
                value: v,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                        { offset: 0, color: 'rgba(46,139,87,0.3)' },
                        { offset: 1, color: 'rgba(46,139,87,0.9)' },
                    ]),
                    borderRadius: [0, 4, 4, 0],
                },
            })),
            barMaxWidth: 20,
        }],
    };

    carbonCharts.rank.setOption(option);
}

// ========== 工具函数 ==========

function showCarbonLoading(show) {
    const el = document.getElementById('carbonLoading');
    if (el) el.classList.toggle('hidden', !show);
}

function invalidateCarbonCharts() {
    Object.values(carbonCharts).forEach(chart => {
        if (chart && !chart.isDisposed()) chart.resize();
    });
}

function disposeCarbonCharts() {
    Object.values(carbonCharts).forEach(chart => {
        if (chart && !chart.isDisposed()) chart.dispose();
    });
    carbonCharts = {};
}

async function refreshCarbonData() {
    carbonMeta = null;
    carbonCharts = {};
    await initCarbonPage();
}

async function onCarbonFilterChange() {
    await loadCarbonDashboard();
}

window.addEventListener('resize', function () {
    Object.values(carbonCharts).forEach(chart => {
        if (chart && !chart.isDisposed()) chart.resize();
    });
});

// ========== 左侧边栏拖拽调整宽度 ==========

// 初始化拖拽功能（在initCarbonPage中调用）
function initSidebarResize() {
    const sidebar = document.getElementById('carbonSidebarLeft');
    const handle = document.getElementById('sidebarResizeHandle');

    if (!sidebar || !handle) {
        console.warn('侧边栏拖拽元素未找到');
        return;
    }

    handle.addEventListener('mousedown', function(e) {
        isDragging = true;
        dragStartX = e.clientX;
        dragStartWidth = sidebar.offsetWidth;

        handle.classList.add('dragging');
        document.body.style.cursor = 'ew-resize';
        document.body.style.userSelect = 'none';

        e.preventDefault();
        e.stopPropagation();
    }, { passive: false });

    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;

        const deltaX = e.clientX - dragStartX;
        const newWidth = dragStartWidth + deltaX;

        // 限制宽度范围
        const minWidth = 180;
        const maxWidth = 400;
        const clampedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

        sidebar.style.width = clampedWidth + 'px';
    });

    document.addEventListener('mouseup', function(e) {
        if (!isDragging) return;

        isDragging = false;
        handle.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';

        // 调整图表尺寸
        setTimeout(() => {
            if (carbonCharts.trend && !carbonCharts.trend.isDisposed()) {
                carbonCharts.trend.resize();
            }
        }, 100);
    });
}
