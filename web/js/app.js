/**
 * app.js - 页面路由与初始化
 */

let enumsCache = null;

// 页面切换
function switchPage(page) {
    // 离开分析页时清理 ECharts 实例
    if (typeof disposeCharts === 'function') disposeCharts();
    // 离开碳排放页时清理图表
    if (typeof disposeCarbonCharts === 'function') disposeCarbonCharts();
    // 更新导航
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.page === page);
    });
    // 更新页面
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });
    // 更新 hash
    window.location.hash = page;
    // 页面初始化回调
    if (page === 'dashboard') initDashboard();
    if (page === 'building') initBuildingPage();
    if (page === 'analysis') initAnalysisPage();
    if (page === 'carbon') initCarbonPage();
}

// 监听 hash 变化
window.addEventListener('hashchange', () => {
    const hash = window.location.hash.slice(1) || 'building';
    if (['dashboard', 'building', 'analysis', 'carbon'].includes(hash)) {
        switchPage(hash);
    }
});

// 获取枚举数据
async function loadEnums() {
    if (enumsCache) return enumsCache;
    enumsCache = await apiGet('/enums/all');
    return enumsCache;
}

// 填充 select 下拉
function fillSelect(selectId, options, placeholder) {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    sel.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
    options.forEach(opt => {
        const val = typeof opt === 'object' ? opt.value : opt;
        const label = typeof opt === 'object' ? opt.label : opt;
        sel.innerHTML += `<option value="${val}">${label}</option>`;
    });
}

// 初始化
async function init() {
    // 加载枚举
    try {
        const enums = await loadEnums();
        // 预填充所有下拉框
        fillSelect('filterType', enums.building_types, '所有类型');
        fillSelect('filterRegion', enums.regions, '所有地区');
        fillSelect('addType', enums.building_types);
        fillSelect('addRegion', enums.regions);
        fillSelect('addWall', enums.wall_constructions);
        fillSelect('addRoof', enums.roof_constructions);
        fillSelect('addRoofType', enums.roof_types);
        fillSelect('addShape', enums.building_shapes);
        fillSelect('addHeating', enums.heating_types);
        fillSelect('addCooling', enums.cooling_types);
        fillSelect('addWater', enums.water_heating_types);
        // 编辑表单下拉
        fillSelect('editType', enums.building_types);
        fillSelect('editRegion', enums.regions);
        fillSelect('editWall', enums.wall_constructions);
        fillSelect('editRoof', enums.roof_constructions);
        fillSelect('editRoofType', enums.roof_types);
        fillSelect('editShape', enums.building_shapes);
        fillSelect('editHeating', enums.heating_types);
        fillSelect('editCooling', enums.cooling_types);
        fillSelect('editWater', enums.water_heating_types);
    } catch (e) {
        console.warn('加载枚举失败:', e);
    }

    // 根据 hash 初始化页面（必须调用 switchPage 以触发各页面的 init 函数）
    const hash = window.location.hash.slice(1) || 'dashboard';
    switchPage(hash);

    // 自动加载聊天历史
    loadChatHistory();
}

document.addEventListener('DOMContentLoaded', init);
