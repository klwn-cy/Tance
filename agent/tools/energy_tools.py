"""
建筑能耗工具模块 - 提供建筑能耗诊断、节能策略、减碳评估等能力
"""
import json
import random
from langchain_core.tools import tool
from project.logger_handler import logger
from rag.rag_service import RagSummarizeService
from agent.services.building_service import building_service
from agent.services.analysis_report_service import analysis_report_service
from agent.tools.building_enums import (
    get_building_types, get_regions, get_wall_constructions,
    get_roof_constructions, get_roof_types, get_building_shapes,
    get_heating_types, get_cooling_types, get_water_heating_types
)

rag = RagSummarizeService()

# 模拟建筑能耗数据库
BUILDING_DATABASE = {
    "B001": {
        "name": "教学楼A栋",
        "type": "教育建筑",
        "area": 15000,  # 平方米
        "location": "北京",
        "year_built": 2010,
        "energy_data": {
            "2024-01": {"electricity": 85000, "gas": 12000, "water": 3200},
            "2024-02": {"electricity": 78000, "gas": 13500, "water": 2800},
            "2024-03": {"electricity": 72000, "gas": 8000, "water": 3100},
        }
    },
    "B002": {
        "name": "图书馆",
        "type": "公共建筑",
        "area": 8000,
        "location": "北京",
        "year_built": 2015,
        "energy_data": {
            "2024-01": {"electricity": 45000, "gas": 6000, "water": 1800},
            "2024-02": {"electricity": 42000, "gas": 6500, "water": 1600},
            "2024-03": {"electricity": 38000, "gas": 4500, "water": 1700},
        }
    },
    "B003": {
        "name": "实验楼",
        "type": "科研建筑",
        "area": 12000,
        "location": "北京",
        "year_built": 2018,
        "energy_data": {
            "2024-01": {"electricity": 120000, "gas": 8000, "water": 4500},
            "2024-02": {"electricity": 115000, "gas": 8500, "water": 4200},
            "2024-03": {"electricity": 98000, "gas": 6000, "water": 4300},
        }
    },
    "B004": {
        "name": "学生宿舍1号楼",
        "type": "居住建筑",
        "area": 6000,
        "location": "北京",
        "year_built": 2012,
        "energy_data": {
            "2024-01": {"electricity": 35000, "gas": 18000, "water": 2800},
            "2024-02": {"electricity": 32000, "gas": 19000, "water": 2600},
            "2024-03": {"electricity": 28000, "gas": 12000, "water": 2700},
        }
    },
    "B005": {
        "name": "体育馆",
        "type": "体育建筑",
        "area": 10000,
        "location": "北京",
        "year_built": 2016,
        "energy_data": {
            "2024-01": {"electricity": 28000, "gas": 5000, "water": 1500},
            "2024-02": {"electricity": 25000, "gas": 5500, "water": 1400},
            "2024-03": {"electricity": 22000, "gas": 3500, "water": 1450},
        }
    }
}

# 碳排放因子 (kgCO2/kWh 或 kgCO2/m³)
CARBON_FACTORS = {
    "electricity": 0.5839,  # 中国电网平均碳排放因子
    "gas": 2.16,           # 天然气碳排放因子
    "water": 0.91,         # 自来水碳排放因子
}

# 能源价格
ENERGY_PRICES = {
    "electricity": 0.85,   # 元/kWh
    "gas": 3.0,            # 元/m³
    "water": 5.0,          # 元/m³
}


@tool(description="从向量存储中检索建筑能耗、节能减排相关专业资料")
def rag_summarize(query: str) -> str:
    """从知识库检索专业资料"""
    return rag.rag_summarize(query)


@tool(description="获取建筑能耗历史数据。参数building_id为建筑ID（如B001），time_range为时间范围（如2024-01）")
def get_building_energy_data(building_id: str, time_range: str = "all") -> str:
    """获取建筑能耗数据（从建筑管理数据实时获取）"""
    # 从建筑管理服务获取实时数据
    building = building_service.get_building(building_id)

    if not building:
        # 返回所有建筑列表
        buildings = building_service.list_buildings()
        if buildings:
            available_ids = ', '.join(buildings.keys())
            return f"未找到建筑ID {building_id}。可用建筑ID: {available_ids}"
        else:
            return f"未找到建筑ID {building_id}。当前没有建筑数据。"

    basic = building.get("basic_info", {})
    energy_consumption = building.get("energy_consumption", {})
    monthly_data = energy_consumption.get("monthly_data", {})

    if not monthly_data:
        return f"""建筑名称：{basic.get('name', building_id)}
建筑类型：{basic.get('building_type', '未知')}
建筑面积：{basic.get('floor_area_sqm', 0)} 平方米
所在地区：{basic.get('region', '未知')}
建造年份：{basic.get('year_built', '未知')}

暂无能耗数据，请在建筑管理页面添加能耗数据。"""

    if time_range != "all":
        if time_range in monthly_data:
            monthly_data = {time_range: monthly_data[time_range]}
        else:
            available = list(monthly_data.keys())
            return f"未找到时间范围 {time_range}。可用时间: {', '.join(available)}"

    result = f"""建筑名称：{basic.get('name', building_id)}
建筑类型：{basic.get('building_type', '未知')}
建筑面积：{basic.get('floor_area_sqm', 0)} 平方米
所在地区：{basic.get('region', '未知')}
建造年份：{basic.get('year_built', '未知')}

能耗数据：
"""
    total_elec = 0
    total_gas = 0
    total_water = 0

    for month, data in monthly_data.items():
        elec = data.get("electricity_kwh", 0)
        gas = data.get("natural_gas_m3", 0)
        water = data.get("water_m3", 0)
        total_elec += elec
        total_gas += gas
        total_water += water

        result += f"""
{month}:
  - 电力: {elec:,} kWh
  - 天然气: {gas:,} m³
  - 用水: {water:,} m³"""

    # 计算能耗强度
    area = basic.get("floor_area_sqm", 1)
    months = len(monthly_data)
    eui = total_elec / (area * months / 12) if months > 0 and area > 0 else 0

    result += f"""

汇总统计（{months}个月）：
  - 总用电量: {total_elec:,} kWh
  - 总用气量: {total_gas:,} m³
  - 总用水量: {total_water:,} m³
  - 月均用电强度(EUI): {eui:.2f} kWh/m²/年"""

    return result


@tool(description="计算减碳量和经济效益。参数energy_saved为节能量(kWh)，energy_type为能源类型（electricity/gas/water）")
def calculate_carbon_reduction(energy_saved: float, energy_type: str = "electricity") -> str:
    """计算减碳量和经济效益"""
    if energy_type not in CARBON_FACTORS:
        return f"不支持的能源类型: {energy_type}。支持类型: electricity, gas, water"

    carbon_factor = CARBON_FACTORS[energy_type]
    price = ENERGY_PRICES[energy_type]

    carbon_reduction = energy_saved * carbon_factor
    cost_saved = energy_saved * price

    # 等效指标
    if energy_type == "electricity":
        tree_equivalent = carbon_reduction / 18.3  # 一棵树年吸收CO2约18.3kg
        car_equivalent = carbon_reduction / 0.15 / 1000  # 汽车每公里排放约0.15kg CO2
    else:
        tree_equivalent = carbon_reduction / 18.3
        car_equivalent = carbon_reduction / 0.15 / 1000

    result = f"""减碳效益计算结果：

基本信息：
  - 节约能源类型: {energy_type}
  - 节约能源量: {energy_saved:,.2f} {'kWh' if energy_type == 'electricity' else 'm³'}

减碳效益：
  - 减碳量: {carbon_reduction:,.2f} kg CO2
  - 相当于种植: {tree_equivalent:.1f} 棵树一年吸收的CO2
  - 相当于减少: {car_equivalent:.1f} 公里汽车行驶排放

经济效益：
  - 节约费用: {cost_saved:,.2f} 元
  - 年化节约（按12月计）: {cost_saved * 12:,.2f} 元

参考数据：
  - 电网碳排放因子: {carbon_factor} kg CO2/kWh
  - 能源单价: {price} 元/{'kWh' if energy_type == 'electricity' else 'm³'}"""

    return result


@tool(description="生成节能策略建议。参数building_type为建筑类型，energy_issue为能耗问题描述")
def generate_energy_strategy(building_type: str, energy_issue: str = "") -> str:
    """生成节能策略建议"""
    strategies = {
        "教育建筑": {
            "照明节能": [
                "更换LED灯具，预计节能30-50%",
                "安装智能照明控制系统，根据自然光自动调节",
                "教室安装人体感应开关，无人自动关灯"
            ],
            "空调系统": [
                "夏季温度设置不低于26°C，冬季不高于20°C",
                "安装变频空调，根据负荷自动调节",
                "定期清洗空调滤网，提高效率10-15%"
            ],
            "用电管理": [
                "课后自动断电系统",
                "寒暑假调低供暖温度",
                "建立能耗监测平台，实时监控"
            ]
        },
        "公共建筑": {
            "照明节能": [
                "大厅、走廊采用智能感应照明",
                "自然采光区域安装光感控制",
                "地下车库安装雷达感应灯"
            ],
            "空调系统": [
                "安装新风热回收系统",
                "采用变风量空调系统(VAV)",
                "安装建筑能耗监测系统"
            ],
            "用电管理": [
                "安装智能电表，分项计量",
                "制定节能运行管理制度",
                "设备定期维护保养"
            ]
        },
        "科研建筑": {
            "设备管理": [
                "实验室设备待机管理",
                "通风柜安装变频控制",
                "实验区温湿度分区控制"
            ],
            "空调系统": [
                "实验室独立空调系统",
                "安装排风热回收装置",
                "精密空调效率优化"
            ],
            "特殊节能": [
                "实验室废气处理系统优化",
                "纯水系统节能改造",
                "高压气瓶集中供气系统"
            ]
        },
        "居住建筑": {
            "照明节能": [
                "公共区域LED改造",
                "楼道声控开关",
                "地下室感应照明"
            ],
            "供暖系统": [
                "安装温控阀",
                "管道保温改造",
                "换热站自动化控制"
            ],
            "用水管理": [
                "安装节水器具",
                "中水回用系统",
                "热水系统保温改造"
            ]
        },
        "体育建筑": {
            "照明节能": [
                "比赛场馆智能照明系统",
                "训练馆LED照明改造",
                "自然采光利用"
            ],
            "空调系统": [
                "观众席分区空调",
                "场馆间歇运行模式",
                "新风节能控制"
            ],
            "用水管理": [
                "游泳池水循环利用",
                "淋浴节水装置",
                "雨水收集利用"
            ]
        }
    }

    # 获取对应建筑类型的策略
    type_strategies = strategies.get(building_type, strategies.get("公共建筑", {}))

    result = f"""【{building_type}节能策略建议】

"""
    for category, items in type_strategies.items():
        result += f"一、{category}\n"
        for i, item in enumerate(items, 1):
            result += f"  {i}. {item}\n"
        result += "\n"

    if energy_issue:
        result += f"""针对问题的专项建议：
{energy_issue}

建议优先排查：
  1. 检查是否存在设备故障或运行异常
  2. 分析能耗数据，找出异常时段
  3. 实地巡查，发现浪费点
  4. 制定针对性整改措施
"""

    result += """
实施建议：
  - 短期措施（0-6月）：低投入、见效快的措施优先
  - 中期措施（6-24月）：适度投资、效果显著的改造
  - 长期措施（24月以上）：重大改造、战略意义的项目"""

    return result


@tool(description="基于数字孪生模型进行能耗仿真预测。参数building_params为建筑参数JSON字符串，scenario为场景类型")
def simulate_building_energy(building_params: str, scenario: str = "baseline") -> str:
    """基于数字孪生模型进行能耗仿真"""
    try:
        params = json.loads(building_params) if building_params.startswith("{") else {"area": float(building_params)}
    except:
        params = {"area": 10000}

    area = params.get("area", 10000)
    building_type = params.get("type", "公共建筑")
    location = params.get("location", "北京")
    year_built = params.get("year_built", 2015)

    # 基于建筑特征的仿真模型
    base_eui = {
        "教育建筑": 45,
        "公共建筑": 55,
        "科研建筑": 85,
        "居住建筑": 25,
        "体育建筑": 35
    }.get(building_type, 50)

    # 场景调整系数
    scenario_factors = {
        "baseline": 1.0,
        "energy_saving": 0.75,
        "high_efficiency": 0.60,
        "passive_house": 0.45
    }

    factor = scenario_factors.get(scenario, 1.0)

    # 计算仿真结果
    annual_eui = base_eui * factor
    annual_electricity = area * annual_eui

    # 分月仿真（考虑季节因素）
    monthly_factors = [1.15, 1.10, 0.95, 0.85, 0.90, 1.05, 1.20, 1.20, 1.00, 0.90, 0.95, 1.10]

    result = f"""【数字孪生能耗仿真结果】

建筑参数：
  - 类型: {building_type}
  - 面积: {area:,} m²
  - 位置: {location}
  - 建造年份: {year_built}

仿真场景: {scenario}

年度能耗预测：
  - 年度EUI: {annual_eui:.1f} kWh/m²/年
  - 年度总用电量: {annual_electricity:,.0f} kWh
  - 年度电费预估: {annual_electricity * 0.85:,.0f} 元

月度能耗仿真：
"""

    for i, mf in enumerate(monthly_factors, 1):
        month_elec = annual_electricity / 12 * mf
        result += f"  {i:2d}月: {month_elec:,.0f} kWh\n"

    # 减碳效益
    baseline_elec = area * base_eui
    saved_elec = baseline_elec - annual_electricity
    carbon_saved = saved_elec * 0.5839

    result += f"""
对比基准场景：
  - 节电量: {saved_elec:,.0f} kWh/年
  - 减碳量: {carbon_saved:,.0f} kg CO2/年
  - 节约费用: {saved_elec * 0.85:,.0f} 元/年

建议：
  - 此仿真结果基于典型建筑能耗模型
  - 实际能耗受使用行为、设备效率等因素影响
  - 建议结合实际监测数据进行校准"""

    return result


@tool(description="获取所有建筑列表和基本信息，无参数")
def list_all_buildings() -> str:
    """获取所有建筑列表（从建筑管理数据实时获取）"""
    # 从建筑管理服务获取实时数据
    buildings = building_service.list_buildings()

    if not buildings:
        return "【建筑列表】\n\n暂无建筑数据，请先在建筑管理页面添加建筑。"

    result = f"【建筑列表】共 {len(buildings)} 个建筑\n\n"

    for bid, building in buildings.items():
        basic = building.get("basic_info", {})
        energy_systems = building.get("energy_systems", {})

        result += f"""建筑ID: {bid}
  名称: {basic.get('name', '未命名')}
  类型: {basic.get('building_type', '未知')}
  地区: {basic.get('region', '未知')}
  面积: {basic.get('floor_area_sqm', 0):,.0f} m²
  楼层: {basic.get('num_floors', 0)} 层
  建造年份: {basic.get('year_built', '未知')}
  员工人数: {basic.get('num_employees', 0)}
  供暖类型: {energy_systems.get('heating', {}).get('primary_type', '未知')}
  制冷类型: {energy_systems.get('cooling', {}).get('primary_type', '未知')}

"""
    return result


# ==================== 建筑管理工具（基于buildings_v2.json） ====================

@tool(description="创建新建筑。参数name为建筑名称，building_type为建筑类型，region为地区，floor_area_sqm为建筑面积（平方米）。可选参数：num_floors（楼层数，默认1），year_built（建造年份），num_employees（员工人数）")
def create_building(
    name: str,
    building_type: str,
    region: str,
    floor_area_sqm: float,
    num_floors: int = 1,
    year_built: int = None,
    num_employees: int = 0
) -> str:
    """创建新建筑"""
    # 验证建筑类型
    valid_types = get_building_types()
    if building_type not in valid_types:
        return f"无效的建筑类型: {building_type}。有效类型: {', '.join(valid_types)}"

    # 验证地区
    valid_regions = get_regions()
    if region not in valid_regions:
        return f"无效的地区: {region}。有效地区: {', '.join(valid_regions)}"

    try:
        result = building_service.create_building(
            name=name,
            building_type=building_type,
            region=region,
            floor_area_sqm=floor_area_sqm,
            num_floors=num_floors,
            year_built=year_built,
            num_employees=num_employees
        )
        building_id = result["building_id"]
        return f"""建筑创建成功！

建筑ID: {building_id}
建筑名称: {name}
建筑类型: {building_type}
所在地区: {region}
建筑面积: {floor_area_sqm:,.0f} 平方米
楼层数: {num_floors}
建造年份: {year_built or '未指定'}
员工人数: {num_employees}

您可以使用建筑ID {building_id} 来查询、更新或管理此建筑的信息。
"""
    except Exception as e:
        logger.error(f"创建建筑失败: {e}")
        return f"创建建筑失败: {str(e)}"


@tool(description="获取建筑详细信息。参数building_id为建筑ID（如B001）")
def get_building_info(building_id: str) -> str:
    """获取建筑详细信息"""
    return building_service.get_building_summary(building_id)


@tool(description="查询建筑列表，支持筛选。可选参数：building_type（建筑类型），region（地区），min_area（最小面积），max_area（最大面积）")
def query_buildings(
    building_type: str = None,
    region: str = None,
    min_area: float = None,
    max_area: float = None
) -> str:
    """查询建筑列表（支持筛选）"""
    buildings = building_service.list_buildings(
        building_type=building_type,
        region=region,
        min_area=min_area,
        max_area=max_area
    )

    if not buildings:
        return "未找到符合条件的建筑。"

    result = f"【建筑查询结果】共找到 {len(buildings)} 个建筑\n\n"

    for bid, building in buildings.items():
        basic = building.get("basic_info", {})
        result += f"""建筑ID: {bid}
  名称: {basic.get('name', '未命名')}
  类型: {basic.get('building_type', '未知')}
  地区: {basic.get('region', '未知')}
  面积: {basic.get('floor_area_sqm', 0):,.0f} m²
  楼层: {basic.get('num_floors', 0)} 层
  建造年份: {basic.get('year_built', '未知')}

"""
    return result


@tool(description="更新建筑信息。参数building_id为建筑ID，其他参数为要更新的字段：name（名称），building_type（类型），region（地区），floor_area_sqm（面积），num_floors（楼层数），num_employees（员工人数），heating_type（供暖类型），cooling_type（制冷类型）")
def update_building_info(building_id: str, **kwargs) -> str:
    """更新建筑信息"""
    # 过滤None值
    update_data = {k: v for k, v in kwargs.items() if v is not None}

    if not update_data:
        return "未提供要更新的字段。"

    result = building_service.update_building(building_id, **update_data)

    if result is None:
        return f"建筑不存在: {building_id}"

    return f"""建筑更新成功！

建筑ID: {building_id}
更新字段: {', '.join(update_data.keys())}

更新后的信息:
{building_service.get_building_summary(building_id)}
"""


@tool(description="删除建筑。参数building_id为要删除的建筑ID")
def delete_building(building_id: str) -> str:
    """删除建筑"""
    # 先获取建筑信息用于确认
    building = building_service.get_building(building_id)
    if not building:
        return f"建筑不存在: {building_id}"

    building_name = building.get("basic_info", {}).get("name", "未命名")

    success = building_service.delete_building(building_id)

    if success:
        return f"建筑删除成功！\n\n已删除: {building_id} - {building_name}"
    else:
        return f"删除建筑失败: {building_id}"


@tool(description="添加建筑月度能耗数据。参数building_id为建筑ID，month为月份（格式YYYY-MM如2024-03），electricity_kwh为电力消耗（kWh），natural_gas_m3为天然气消耗（m³），water_m3为用水量（m³）")
def add_energy_data(
    building_id: str,
    month: str,
    electricity_kwh: float = 0,
    natural_gas_m3: float = 0,
    water_m3: float = 0
) -> str:
    """添加建筑月度能耗数据"""
    # 验证月份格式
    if len(month) != 7 or month[4] != '-':
        return "月份格式错误，请使用YYYY-MM格式（如2024-03）"

    building = building_service.get_building(building_id)
    if not building:
        return f"建筑不存在: {building_id}"

    success = building_service.add_monthly_energy_data(
        building_id=building_id,
        month=month,
        electricity_kwh=electricity_kwh,
        natural_gas_m3=natural_gas_m3,
        water_m3=water_m3
    )

    if success:
        return f"""能耗数据添加成功！

建筑ID: {building_id}
建筑名称: {building.get('basic_info', {}).get('name', '未命名')}
月份: {month}

能耗数据:
  - 电力: {electricity_kwh:,.0f} kWh
  - 天然气: {natural_gas_m3:,.0f} m³
  - 用水: {water_m3:,.0f} m³
"""
    else:
        return f"添加能耗数据失败: {building_id}"


@tool(description="获取建筑类型列表，无参数")
def get_building_type_list() -> str:
    """获取所有可用的建筑类型"""
    types = get_building_types()
    return "【可用建筑类型】\n\n" + "\n".join(f"  - {t}" for t in types)


@tool(description="获取地区列表，无参数")
def get_region_list() -> str:
    """获取所有可用的地区"""
    regions = get_regions()
    return "【可用地区】\n\n" + "\n".join(f"  - {r}" for r in regions)


# ==================== 分析报告查询工具 ====================

@tool(description="列出所有可用的CBECS 2012分析报告，无参数")
def list_analysis_reports() -> str:
    """列出所有分析报告"""
    return analysis_report_service.list_reports()


@tool(description="获取指定分析报告的详细内容。参数report_id为报告编号（如R001、R002等）")
def get_analysis_report(report_id: str) -> str:
    """获取指定报告的详细内容"""
    return analysis_report_service.get_report(report_id)


@tool(description="按关键词搜索分析报告。参数keyword为搜索关键词（如供暖、照明、节能等）")
def search_reports(keyword: str) -> str:
    """按关键词搜索报告"""
    return analysis_report_service.search_reports(keyword)