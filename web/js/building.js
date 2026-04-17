/**
 * building.js - 建筑 CRUD 逻辑
 */

let buildingListCache = {};

// ========== 初始化建筑管理页 ==========
async function initBuildingPage() {
    await loadBuildingList();
    await refreshEditSelect();
    await refreshEnergySelect();
}

// ========== 建筑 Tab 切换 ==========
function switchBuildingTab(tab) {
    document.querySelectorAll('#page-building .tab-item').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });
    document.querySelectorAll('#page-building .tab-content').forEach(c => {
        c.classList.toggle('active', c.id === `tab-${tab}`);
    });
    if (tab === 'building-list') loadBuildingList();
}

// ========== 建筑列表 ==========
async function loadBuildingList() {
    try {
        const type = document.getElementById('filterType')?.value || '';
        const region = document.getElementById('filterRegion')?.value || '';
        const params = {};
        if (type) params.building_type = type;
        if (region) params.region = region;

        const data = await apiGet('/buildings', params);
        buildingListCache = data.buildings || {};
        renderBuildingList(buildingListCache);
    } catch (e) {
        showToast('加载建筑列表失败: ' + e.message, 'error');
    }
}

function renderBuildingList(buildings) {
    const container = document.getElementById('buildingListContainer');
    if (!buildings || Object.keys(buildings).length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">🏛️</div>
                <p>暂无建筑数据，请先添加建筑。</p>
            </div>`;
        return;
    }

    container.innerHTML = Object.entries(buildings).map(([id, b]) => {
        const info = b.basic_info || {};
        const systems = b.energy_systems || {};
        const name = info.name || '未命名';
        const type = info.building_type || '未知';
        const region = info.region || '未知';
        const area = info.floor_area_sqm ? `${info.floor_area_sqm.toLocaleString()} m²` : '-';
        const year = info.year_built || '-';
        return `
            <div class="building-card" id="card-${id}">
                <div class="building-card-header" onclick="toggleBuildingCard('${id}')">
                    <div class="building-card-title">
                        <span class="expand-icon">▶</span>
                        <span>${escapeHTML(name)}</span>
                        <span class="id">${id}</span>
                    </div>
                    <div class="building-card-meta">
                        <span class="badge badge-primary">${escapeHTML(type)}</span>
                        <span class="badge badge-info">${escapeHTML(region)}</span>
                        <span class="badge badge-success">${area}</span>
                    </div>
                </div>
                <div class="building-card-body">
                    <div class="building-info-grid">
                        <div class="building-info-item"><span class="label">楼层/地下：</span><span class="value">${info.num_floors || 0}F / ${info.num_basements || 0}B</span></div>
                        <div class="building-info-item"><span class="label">建造年份：</span><span class="value">${year}</span></div>
                        <div class="building-info-item"><span class="label">员工人数：</span><span class="value">${(info.num_employees || 0).toLocaleString()}</span></div>
                        <div class="building-info-item"><span class="label">周运营时长：</span><span class="value">${info.weekly_operating_hours || 0}h</span></div>
                        <div class="building-info-item"><span class="label">墙体：</span><span class="value">${(b.building_structure || {}).wall_construction || '-'}</span></div>
                        <div class="building-info-item"><span class="label">供暖：</span><span class="value">${(systems.heating || {}).primary_type || '-'}</span></div>
                        <div class="building-info-item"><span class="label">制冷：</span><span class="value">${(systems.cooling || {}).primary_type || '-'}</span></div>
                        <div class="building-info-item"><span class="label">热水：</span><span class="value">${(systems.water_heating || {}).primary_type || '-'}</span></div>
                    </div>
                    <div class="building-card-actions">
                        <button class="btn btn-sm btn-outline" onclick="editBuildingById('${id}')">✏️ 编辑</button>
                        <button class="btn btn-sm btn-outline" onclick="viewEnergyById('${id}')">⚡ 能耗</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteBuildingDirect('${id}')">🗑️ 删除</button>
                    </div>
                </div>
            </div>`;
    }).join('');
}

function toggleBuildingCard(id) {
    const card = document.getElementById(`card-${id}`);
    if (card) card.classList.toggle('expanded');
}

function resetBuildingFilters() {
    document.getElementById('filterType').value = '';
    document.getElementById('filterRegion').value = '';
    loadBuildingList();
}

// ========== 添加建筑 ==========
async function addBuilding() {
    const name = document.getElementById('addName').value.trim();
    if (!name) {
        showToast('请输入建筑名称', 'warning');
        return;
    }
    const data = {
        name,
        building_type: document.getElementById('addType').value,
        region: document.getElementById('addRegion').value,
        floor_area_sqm: parseFloat(document.getElementById('addArea').value) || 1000,
        num_floors: parseInt(document.getElementById('addFloors').value) || 1,
        num_basements: parseInt(document.getElementById('addBasements').value) || 0,
        year_built: parseInt(document.getElementById('addYear').value) || null,
        num_employees: parseInt(document.getElementById('addEmployees').value) || 0,
        weekly_operating_hours: parseInt(document.getElementById('addHours').value) || 40,
        wall_construction: document.getElementById('addWall').value,
        roof_construction: document.getElementById('addRoof').value,
        roof_type: document.getElementById('addRoofType').value,
        building_shape: document.getElementById('addShape').value,
        glass_percentage: parseFloat(document.getElementById('addGlass').value) || 30,
        floor_to_ceiling_height_m: parseFloat(document.getElementById('addCeiling').value) || 3.0,
        heating_type: document.getElementById('addHeating').value,
        cooling_type: document.getElementById('addCooling').value,
        water_heating_type: document.getElementById('addWater').value,
        uses_electricity: document.getElementById('addElec').checked,
        uses_natural_gas: document.getElementById('addGas').checked,
    };

    try {
        const result = await apiPost('/buildings', data);
        showToast(`建筑 ${result.building_id} 创建成功`, 'success');
        document.getElementById('addName').value = '';
        loadBuildingList();
        refreshEditSelect();
        refreshEnergySelect();
    } catch (e) {
        showToast('创建失败: ' + e.message, 'error');
    }
}

// ========== 编辑建筑 ==========
async function refreshEditSelect() {
    try {
        const data = await apiGet('/buildings');
        const buildings = data.buildings || {};
        const sel = document.getElementById('editBuildingSelect');
        sel.innerHTML = '<option value="">-- 选择要编辑的建筑 --</option>';
        Object.entries(buildings).forEach(([id, b]) => {
            sel.innerHTML += `<option value="${id}">${id} - ${escapeHTML((b.basic_info || {}).name || '未命名')}</option>`;
        });
    } catch (e) { /* ignore */ }
}

async function loadBuildingForEdit() {
    const id = document.getElementById('editBuildingSelect').value;
    if (!id) {
        document.getElementById('editFormContainer').classList.add('hidden');
        return;
    }
    try {
        const b = await apiGet(`/buildings/${id}`);
        const info = b.basic_info || {};
        const structure = b.building_structure || {};
        const systems = b.energy_systems || {};
        const consumption = b.energy_consumption || {};

        document.getElementById('editName').value = info.name || '';
        document.getElementById('editType').value = info.building_type || '';
        document.getElementById('editRegion').value = info.region || '';
        document.getElementById('editArea').value = info.floor_area_sqm || '';
        document.getElementById('editFloors').value = info.num_floors || '';
        document.getElementById('editBasements').value = info.num_basements || '';
        document.getElementById('editYear').value = info.year_built || '';
        document.getElementById('editEmployees').value = info.num_employees || '';
        document.getElementById('editHours').value = info.weekly_operating_hours || '';
        document.getElementById('editWall').value = structure.wall_construction || '';
        document.getElementById('editRoof').value = structure.roof_construction || '';
        document.getElementById('editRoofType').value = structure.roof_type || '';
        document.getElementById('editShape').value = structure.building_shape || '';
        document.getElementById('editGlass').value = structure.glass_percentage || '';
        document.getElementById('editCeiling').value = structure.floor_to_ceiling_height_m || '';
        document.getElementById('editHeating').value = (systems.heating || {}).primary_type || '';
        document.getElementById('editCooling').value = (systems.cooling || {}).primary_type || '';
        document.getElementById('editWater').value = (systems.water_heating || {}).primary_type || '';
        document.getElementById('editElec').checked = consumption.uses_electricity !== false;
        document.getElementById('editGas').checked = consumption.uses_natural_gas !== false;

        document.getElementById('editFormContainer').classList.remove('hidden');
    } catch (e) {
        showToast('加载建筑详情失败: ' + e.message, 'error');
    }
}

async function updateBuilding() {
    const id = document.getElementById('editBuildingSelect').value;
    if (!id) return;

    const data = {
        name: document.getElementById('editName').value,
        building_type: document.getElementById('editType').value,
        region: document.getElementById('editRegion').value,
        floor_area_sqm: parseFloat(document.getElementById('editArea').value) || undefined,
        num_floors: parseInt(document.getElementById('editFloors').value) || undefined,
        num_basements: parseInt(document.getElementById('editBasements').value) || undefined,
        year_built: parseInt(document.getElementById('editYear').value) || undefined,
        num_employees: parseInt(document.getElementById('editEmployees').value) || undefined,
        weekly_operating_hours: parseInt(document.getElementById('editHours').value) || undefined,
        wall_construction: document.getElementById('editWall').value,
        roof_construction: document.getElementById('editRoof').value,
        roof_type: document.getElementById('editRoofType').value,
        building_shape: document.getElementById('editShape').value,
        glass_percentage: parseFloat(document.getElementById('editGlass').value) || undefined,
        floor_to_ceiling_height_m: parseFloat(document.getElementById('editCeiling').value) || undefined,
        heating_type: document.getElementById('editHeating').value,
        cooling_type: document.getElementById('editCooling').value,
        water_heating_type: document.getElementById('editWater').value,
        uses_electricity: document.getElementById('editElec').checked,
        uses_natural_gas: document.getElementById('editGas').checked,
    };

    try {
        await apiPut(`/buildings/${id}`, data);
        showToast('建筑信息已更新', 'success');
        loadBuildingList();
        refreshEditSelect();
    } catch (e) {
        showToast('更新失败: ' + e.message, 'error');
    }
}

// ========== 删除建筑 ==========
function deleteBuildingConfirm() {
    const id = document.getElementById('editBuildingSelect').value;
    if (!id) return;
    deleteBuildingDirect(id);
}

async function deleteBuildingDirect(id) {
    if (!confirm(`确定删除建筑 ${id}？此操作不可撤销。`)) return;
    try {
        await apiDelete(`/buildings/${id}`);
        showToast(`建筑 ${id} 已删除`, 'success');
        loadBuildingList();
        refreshEditSelect();
        refreshEnergySelect();
    } catch (e) {
        showToast('删除失败: ' + e.message, 'error');
    }
}

// 快捷跳转
function editBuildingById(id) {
    switchBuildingTab('building-edit');
    document.getElementById('editBuildingSelect').value = id;
    loadBuildingForEdit();
}

function viewEnergyById(id) {
    switchBuildingTab('building-energy');
    document.getElementById('energyBuildingSelect').value = id;
    loadEnergyData();
}

// ========== 能耗数据 ==========
async function refreshEnergySelect() {
    try {
        const data = await apiGet('/buildings');
        const buildings = data.buildings || {};
        const sel = document.getElementById('energyBuildingSelect');
        sel.innerHTML = '<option value="">-- 选择建筑 --</option>';
        Object.entries(buildings).forEach(([id, b]) => {
            sel.innerHTML += `<option value="${id}">${id} - ${escapeHTML((b.basic_info || {}).name || '未命名')}</option>`;
        });
    } catch (e) { /* ignore */ }
}

async function loadEnergyData() {
    const id = document.getElementById('energyBuildingSelect').value;
    const container = document.getElementById('energyDataContainer');
    if (!id) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">⚡</div>
                <p>请选择建筑以查看或录入能耗数据</p>
            </div>`;
        return;
    }

    try {
        const data = await apiGet(`/buildings/${id}/energy`);
        const energyData = data.energy_data || {};

        if (Object.keys(energyData).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">⚡</div>
                    <p>该建筑暂无能耗数据，请添加月度能耗数据。</p>
                </div>
                ${energyInputForm(id)}`;
            return;
        }

        // 按月份排序
        const months = Object.keys(energyData).sort();
        const tableRows = months.map(m => {
            const d = energyData[m];
            return `<tr>
                <td>${m}</td>
                <td>${(d.electricity_kwh || 0).toLocaleString()}</td>
                <td>${(d.natural_gas_m3 || 0).toLocaleString()}</td>
                <td>${(d.water_m3 || 0).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteEnergyMonth('${id}','${m}')">删除</button>
                </td>
            </tr>`;
        }).join('');

        // 合计
        const totals = months.reduce((acc, m) => {
            const d = energyData[m];
            acc.elec += d.electricity_kwh || 0;
            acc.gas += d.natural_gas_m3 || 0;
            acc.water += d.water_m3 || 0;
            return acc;
        }, { elec: 0, gas: 0, water: 0 });

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="card-title">⚡ 能耗数据 - ${id}</div>
                    <span class="badge badge-info">共 ${months.length} 条记录</span>
                </div>
                <div class="table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>月份</th>
                                <th>电力 (kWh)</th>
                                <th>天然气 (m³)</th>
                                <th>用水 (m³)</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                            <tr style="font-weight:600;background:var(--color-primary-bg)">
                                <td>合计</td>
                                <td>${totals.elec.toLocaleString()}</td>
                                <td>${totals.gas.toLocaleString()}</td>
                                <td>${totals.water.toLocaleString()}</td>
                                <td></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            ${energyInputForm(id)}`;
    } catch (e) {
        showToast('加载能耗数据失败: ' + e.message, 'error');
    }
}

function energyInputForm(buildingId) {
    const now = new Date();
    const defaultMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    return `
        <div class="card mt-md">
            <div class="card-title mb-md">➕ 添加月度能耗数据</div>
            <div class="energy-input-grid">
                <div class="form-group">
                    <label class="form-label">月份 (YYYY-MM)</label>
                    <input class="form-input" id="energyMonth" type="month" value="${defaultMonth}">
                </div>
                <div class="form-group">
                    <label class="form-label">电力 (kWh)</label>
                    <input class="form-input" id="energyElec" type="number" min="0" value="0">
                </div>
                <div class="form-group">
                    <label class="form-label">天然气 (m³)</label>
                    <input class="form-input" id="energyGas" type="number" min="0" value="0">
                </div>
                <div class="form-group">
                    <label class="form-label">用水 (m³)</label>
                    <input class="form-input" id="energyWater" type="number" min="0" value="0">
                </div>
            </div>
            <button class="btn btn-primary" onclick="addEnergyData('${buildingId}')">➕ 添加</button>
        </div>`;
}

async function addEnergyData(buildingId) {
    const month = document.getElementById('energyMonth').value;
    if (!month) {
        showToast('请选择月份', 'warning');
        return;
    }
    const data = {
        month,
        electricity_kwh: parseFloat(document.getElementById('energyElec').value) || 0,
        natural_gas_m3: parseFloat(document.getElementById('energyGas').value) || 0,
        water_m3: parseFloat(document.getElementById('energyWater').value) || 0,
    };
    try {
        await apiPost(`/buildings/${buildingId}/energy`, data);
        showToast('能耗数据添加成功', 'success');
        loadEnergyData();
    } catch (e) {
        showToast('添加失败: ' + e.message, 'error');
    }
}

async function deleteEnergyMonth(buildingId, month) {
    if (!confirm(`确定删除 ${month} 的能耗数据？`)) return;
    // 后端暂无单独删除月度数据的API，通过覆盖为0模拟
    try {
        await apiPost(`/buildings/${buildingId}/energy`, { month, electricity_kwh: 0, natural_gas_m3: 0, water_m3: 0 });
        showToast('能耗数据已清零', 'success');
        loadEnergyData();
    } catch (e) {
        showToast('操作失败: ' + e.message, 'error');
    }
}

// HTML 转义复用（与 chat.js 一致，但保持独立以避免依赖）
function escapeHTML(str) {
    if (typeof str !== 'string') return str;
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
