/**
 * dashboard.js - 驾驶舱首页逻辑
 */

let dashboardTimer = null;

// 初始化驾驶舱
function initDashboard() {
    updateDashboardClock();
    if (dashboardTimer) clearInterval(dashboardTimer);
    dashboardTimer = setInterval(updateDashboardClock, 1000);
    loadDashboardStats();
}

// 更新时钟
function updateDashboardClock() {
    const el = document.getElementById('dashboardClock');
    if (!el) return;
    const now = new Date();
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    const h = String(now.getHours()).padStart(2, '0');
    const min = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    el.textContent = `${y}/${m}/${d} ${days[now.getDay()]} ${h}:${min}:${s}`;
}

// 加载驾驶舱统计数据
async function loadDashboardStats() {
    try {
        const data = await apiGet('/buildings');
        const buildings = data.buildings || {};
        const ids = Object.keys(buildings);
        const count = ids.length;

        // 汇总面积
        let totalArea = 0;
        // 汇总能耗（逐月累加 electricity_kwh）
        let totalElecKwh = 0;
        let totalGasM3 = 0;
        // 统计有能耗数据的建筑数（用于计算达标率）
        let buildingWithEUI = 0;
        let compliantCount = 0;

        ids.forEach(bid => {
            const b = buildings[bid];
            const basic = b.basic_info || {};
            const ec = b.energy_consumption || {};
            const monthly = ec.monthly_data || {};

            totalArea += basic.floor_area_sqm || 0;

            let yearlyElec = 0;
            let yearlyGas = 0;
            Object.values(monthly).forEach(m => {
                yearlyElec += m.electricity_kwh || 0;
                yearlyGas += m.natural_gas_m3 || 0;
            });
            totalElecKwh += yearlyElec;
            totalGasM3 += yearlyGas;

            // 计算单栋 EUI 判断节能达标（参考 GB 55015-2021，办公建筑限值 85 kWh/m²）
            if (basic.floor_area_sqm > 0 && yearlyElec > 0) {
                buildingWithEUI++;
                const eui = yearlyElec / basic.floor_area_sqm;
                // 不同类型限值不同，简化处理：取 100 kWh/m² 为通用限值
                if (eui <= 100) compliantCount++;
            }
        });

        // 平均 EUI
        const avgEUI = totalArea > 0 ? (totalElecKwh / totalArea).toFixed(1) : '--';

        // 碳排放估算：电力 0.5810 tCO₂/MWh，天然气 2.1622 tCO₂/千m³
        const carbonElec = (totalElecKwh / 1000) * 0.5810;
        const carbonGas = (totalGasM3 / 1000) * 2.1622;
        const totalCarbon = carbonElec + carbonGas;

        // 节能达标率
        const savingRate = buildingWithEUI > 0
            ? Math.round((compliantCount / buildingWithEUI) * 100)
            : '--';

        // 渲染
        document.getElementById('dashBuildingCount').textContent = count;
        document.getElementById('dashTotalArea').textContent = totalArea > 0
            ? (totalArea / 10000).toFixed(1) : '0';
        document.getElementById('dashTotalEnergy').textContent = totalElecKwh > 0
            ? (totalElecKwh / 10000).toFixed(1) : '0';
        document.getElementById('dashTotalCarbon').textContent = totalCarbon > 0
            ? totalCarbon.toFixed(0) : '0';
        document.getElementById('dashAvgEUI').textContent = avgEUI;
        document.getElementById('dashSavingRate').textContent = savingRate;
    } catch (e) {
        console.warn('加载驾驶舱数据失败:', e);
        document.getElementById('dashBuildingCount').textContent = '0';
        document.getElementById('dashTotalArea').textContent = '0';
        document.getElementById('dashTotalEnergy').textContent = '0';
        document.getElementById('dashTotalCarbon').textContent = '0';
        document.getElementById('dashAvgEUI').textContent = '--';
        document.getElementById('dashSavingRate').textContent = '--';
    }
}
