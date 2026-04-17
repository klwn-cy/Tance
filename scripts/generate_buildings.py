"""
生成50个建筑数据 - 用于碳策Agent演示
"""
import json
import random
from datetime import datetime
from pathlib import Path

# 枚举定义
BUILDING_TYPES = [
    "教育建筑", "公共建筑", "科研建筑", "居住建筑", "体育建筑",
    "办公建筑", "医疗建筑", "商业建筑", "酒店建筑", "仓储建筑",
    "工业建筑", "其他建筑"
]

REGIONS = [
    "北方地区", "南方地区", "华东地区", "华中地区",
    "西南地区", "西北地区", "东北地区"
]

WALL_CONSTRUCTIONS = ["混凝土", "砖墙", "钢结构", "木结构", "玻璃幕墙", "复合结构"]
ROOF_CONSTRUCTIONS = ["混凝土平顶", "金属屋面", "瓦片屋顶", "绿色屋顶", "玻璃顶"]
ROOF_TYPES = ["平顶", "坡顶", "穹顶", "锯齿形"]
BUILDING_SHAPES = ["矩形", "L形", "U形", "圆形", "不规则形状"]
HEATING_TYPES = ["集中供暖", "天然气锅炉", "电采暖", "热泵", "区域供热", "无供暖"]
COOLING_TYPES = ["中央空调", "分体空调", "VRV多联机", "冷水机组", "蒸发冷却", "无制冷"]
WATER_HEATING_TYPES = ["天然气热水器", "电热水器", "太阳能热水器", "热泵热水器", "集中热水系统", "无集中热水"]

# 建筑名称模板
BUILDING_NAME_TEMPLATES = {
    "教育建筑": ["教学楼{}栋", "综合教学楼{}", "实验教学楼{}", "学生活动中心", "研究生楼{}栋", "教师培训中心"],
    "公共建筑": ["市民服务中心{}号", "政务大厅{}", "会议中心", "展览馆{}号馆", "博物馆分馆", "档案馆{}楼"],
    "科研建筑": ["研发中心{}号楼", "创新实验室{}", "科技孵化器{}栋", "研究院大楼", "实验基地{}区", "检测中心"],
    "居住建筑": ["住宅小区{}号楼", "公寓楼{}栋", "宿舍楼{}号", "人才公寓{}", "保障房{}栋", "社区住宅{}单元"],
    "体育建筑": ["体育馆{}号馆", "游泳馆{}", "健身中心{}", "运动场配套楼", "羽毛球馆", "篮球馆{}"],
    "办公建筑": ["写字楼{}大厦", "商务中心{}楼", "企业总部大楼", "科技园{}号楼", "创意产业园{}栋", "行政办公楼{}"],
    "医疗建筑": ["医院住院楼{}栋", "门诊大楼{}号", "社区卫生中心{}", "康复中心{}楼", "疾控中心大楼", "体检中心{}"],
    "商业建筑": ["购物中心{}区", "百货大楼{}号", "商业综合体{}栋", "超市大楼", "商场{}层", "商业街{}号楼"],
    "酒店建筑": ["酒店{}号楼", "宾馆大楼{}", "会议酒店{}", "度假酒店{}栋", "商务酒店{}", "快捷酒店{}号"],
    "仓储建筑": ["仓库{}号库", "物流中心{}栋", "配送中心{}楼", "冷链仓库{}号", "货运站{}", "储备库{}"],
    "工业建筑": ["厂房{}号车间", "生产车间{}栋", "加工中心{}", "制造厂{}楼", "装配车间{}号", "工业厂房{}"],
    "其他建筑": ["综合楼{}栋", "多功能厅{}", "配套设施{}号", "服务站{}楼", "管理中心{}", "辅助建筑{}"]
}

# 不同建筑类型的典型面积范围(平方米)
AREA_RANGES = {
    "教育建筑": (3000, 25000),
    "公共建筑": (2000, 15000),
    "科研建筑": (5000, 20000),
    "居住建筑": (2000, 12000),
    "体育建筑": (5000, 30000),
    "办公建筑": (3000, 50000),
    "医疗建筑": (5000, 30000),
    "商业建筑": (5000, 100000),
    "酒店建筑": (3000, 25000),
    "仓储建筑": (1000, 20000),
    "工业建筑": (2000, 50000),
    "其他建筑": (500, 5000)
}

# 不同建筑类型的典型楼层数范围
FLOOR_RANGES = {
    "教育建筑": (3, 8),
    "公共建筑": (2, 6),
    "科研建筑": (3, 10),
    "居住建筑": (4, 20),
    "体育建筑": (1, 3),
    "办公建筑": (5, 30),
    "医疗建筑": (3, 15),
    "商业建筑": (2, 8),
    "酒店建筑": (3, 20),
    "仓储建筑": (1, 3),
    "工业建筑": (1, 5),
    "其他建筑": (1, 3)
}

# 不同建筑类型的员工密度(人/1000平米)
EMPLOYEE_DENSITY = {
    "教育建筑": (50, 150),
    "公共建筑": (20, 80),
    "科研建筑": (15, 50),
    "居住建筑": (100, 300),  # 居住人数
    "体育建筑": (5, 20),
    "办公建筑": (30, 100),
    "医疗建筑": (20, 60),
    "商业建筑": (10, 50),
    "酒店建筑": (5, 30),
    "仓储建筑": (2, 15),
    "工业建筑": (5, 50),
    "其他建筑": (5, 30)
}

# 基于建筑面积计算典型月度能耗
def calculate_energy_data(area_sqm, building_type, region, month):
    """基于建筑特征计算能耗数据"""
    base_eui = {
        "教育建筑": 150,
        "公共建筑": 180,
        "科研建筑": 200,
        "居住建筑": 120,
        "体育建筑": 100,
        "办公建筑": 160,
        "医疗建筑": 250,
        "商业建筑": 220,
        "酒店建筑": 200,
        "仓储建筑": 50,
        "工业建筑": 180,
        "其他建筑": 100
    }

    # 地区系数
    region_factor = {
        "北方地区": 1.3,
        "南方地区": 0.9,
        "华东地区": 1.0,
        "华中地区": 1.05,
        "西南地区": 0.85,
        "西北地区": 1.4,
        "东北地区": 1.5
    }

    # 季节系数(月份)
    month_season_factor = {
        1: 1.4,   # 冬季
        2: 1.35,
        3: 1.1,   # 春季
        4: 0.9,
        5: 0.85,
        6: 1.1,   # 夏季
        7: 1.25,
        8: 1.2,
        9: 0.95,  # 秋季
        10: 0.85,
        11: 1.05,
        12: 1.3
    }

    eui = base_eui.get(building_type, 150) * region_factor.get(region, 1.0)

    # 电力消耗(kWh/月) - 基于EUI和面积
    electricity = area_sqm * eui / 12 * month_season_factor.get(month, 1.0)
    electricity = electricity * random.uniform(0.85, 1.15)  # 添加随机波动

    # 天然气消耗(m³/月) - 北方地区供暖季较高
    if region in ["北方地区", "西北地区", "东北地区"] and month in [1, 2, 3, 11, 12]:
        gas = area_sqm * random.uniform(0.5, 1.2)  # 供暖季用气量大
    else:
        gas = area_sqm * random.uniform(0.05, 0.2)

    # 用水量(m³/月) - 与员工/居住人数相关
    water = area_sqm * random.uniform(0.02, 0.08)

    return {
        "electricity_kwh": round(electricity),
        "natural_gas_m3": round(gas),
        "water_m3": round(water)
    }


def generate_building(building_id, building_type):
    """生成单个建筑数据"""
    # 选择建筑名称
    templates = BUILDING_NAME_TEMPLATES.get(building_type, ["建筑{}栋"])
    name_template = random.choice(templates)
    if "{}" in name_template:
        name = name_template.format(building_id.replace("B", ""))
    else:
        name = f"{name_template}{building_id.replace('B', '')}"

    # 基本参数
    area_range = AREA_RANGES.get(building_type, (1000, 10000))
    floor_range = FLOOR_RANGES.get(building_type, (1, 5))
    employee_range = EMPLOYEE_DENSITY.get(building_type, (10, 50))

    area = random.randint(area_range[0], area_range[1])
    floors = random.randint(floor_range[0], floor_range[1])
    employees = int(area * random.randint(employee_range[0], employee_range[1]) / 1000)
    year_built = random.randint(1990, 2023)
    region = random.choice(REGIONS)

    # 根据地区选择供暖制冷类型
    if region in ["北方地区", "西北地区", "东北地区"]:
        heating = random.choice(["集中供暖", "天然气锅炉", "区域供热", "热泵"])
        cooling = random.choice(["中央空调", "分体空调", "VRV多联机"])
    elif region in ["南方地区", "华东地区", "华中地区", "西南地区"]:
        heating = random.choice(["无供暖", "热泵", "电采暖", "天然气锅炉"])
        cooling = random.choice(["中央空调", "分体空调", "VRV多联机", "冷水机组"])
    else:
        heating = random.choice(HEATING_TYPES)
        cooling = random.choice(COOLING_TYPES)

    # 根据建筑类型选择结构特征
    if building_type in ["办公建筑", "商业建筑", "酒店建筑"]:
        wall = random.choice(["玻璃幕墙", "复合结构", "混凝土"])
        glass_pct = random.uniform(40, 70)
    elif building_type in ["工业建筑", "仓储建筑"]:
        wall = random.choice(["钢结构", "混凝土", "复合结构"])
        glass_pct = random.uniform(5, 20)
    else:
        wall = random.choice(WALL_CONSTRUCTIONS)
        glass_pct = random.uniform(15, 40)

    # 生成月度能耗数据(2024年1-12月)
    monthly_data = {}
    for month in range(1, 13):
        month_str = f"2024-{month:02d}"
        monthly_data[month_str] = calculate_energy_data(area, building_type, region, month)

    building = {
        "basic_info": {
            "name": name,
            "building_type": building_type,
            "region": region,
            "floor_area_sqm": area,
            "num_floors": floors,
            "num_basements": random.randint(0, min(2, floors // 2)),
            "year_built": year_built,
            "num_employees": employees,
            "weekly_operating_hours": random.randint(30, 60)
        },
        "building_structure": {
            "wall_construction": wall,
            "roof_construction": random.choice(ROOF_CONSTRUCTIONS),
            "roof_type": random.choice(ROOF_TYPES),
            "building_shape": random.choice(BUILDING_SHAPES),
            "glass_percentage": round(glass_pct, 1),
            "floor_to_ceiling_height_m": random.uniform(2.8, 4.5)
        },
        "energy_systems": {
            "heating": {"primary_type": heating},
            "cooling": {"primary_type": cooling},
            "water_heating": {"primary_type": random.choice(WATER_HEATING_TYPES)}
        },
        "energy_consumption": {
            "uses_electricity": True,
            "uses_natural_gas": heating != "无供暖" and heating != "电采暖",
            "monthly_data": monthly_data
        }
    }

    return building


def generate_50_buildings():
    """生成50个建筑"""
    buildings = {}

    # 确保覆盖所有12种建筑类型，每种至少3个
    type_counts = {}
    for bt in BUILDING_TYPES:
        type_counts[bt] = 0

    building_id = 1

    # 首先为每种类型生成3-5个建筑
    for bt in BUILDING_TYPES:
        count = random.randint(3, 5)
        for i in range(count):
            bid = f"B{building_id:03d}"
            buildings[bid] = generate_building(bid, bt)
            type_counts[bt] += 1
            building_id += 1

    # 补充剩余建筑，随机分配类型
    while building_id <= 50:
        bid = f"B{building_id:03d}"
        bt = random.choice(BUILDING_TYPES)
        buildings[bid] = generate_building(bid, bt)
        type_counts[bt] += 1
        building_id += 1

    return buildings, type_counts


def main():
    """主函数"""
    buildings, type_counts = generate_50_buildings()

    data = {
        "metadata": {
            "version": "2.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "模拟生成 - 用于大数据演示",
            "total_buildings": len(buildings)
        },
        "buildings": buildings
    }

    # 输出到文件
    output_path = Path(__file__).parent / "generated_buildings_50.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("已生成 50 个建筑数据")
    print("=" * 60)
    print(f"输出文件: {output_path}")
    print()
    print("建筑类型分布:")
    for bt, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {bt}: {count} 栋")
    print()
    print("地区分布:")
    regions = {}
    for b in buildings.values():
        r = b["basic_info"]["region"]
        regions[r] = regions.get(r, 0) + 1
    for r, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {r}: {count} 栋")
    print()
    print("总建筑面积:", sum(b["basic_info"]["floor_area_sqm"] for b in buildings.values()), "平方米")
    print("总员工/居住人数:", sum(b["basic_info"]["num_employees"] for b in buildings.values()), "人")


if __name__ == "__main__":
    main()