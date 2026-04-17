"""
数据迁移脚本 - 将旧格式buildings.json迁移到新格式buildings_v2.json
"""
import json
import os
from datetime import datetime
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
OLD_DATA_FILE = PROJECT_ROOT / "data" / "energy_data" / "buildings.json"
NEW_DATA_FILE = PROJECT_ROOT / "data" / "energy_data" / "buildings_v2.json"

# 类型映射：旧类型 -> 新类型
TYPE_MAPPING = {
    "教育建筑": "教育建筑",
    "公共建筑": "公共建筑",
    "科研建筑": "科研建筑",
    "居住建筑": "居住建筑",
    "体育建筑": "体育建筑",
    "办公建筑": "办公建筑",
}

# 地区映射
REGION_MAPPING = {
    "北京": "北方地区",
    "上海": "华东地区",
    "广州": "南方地区",
    "深圳": "南方地区",
    "成都": "西南地区",
    "武汉": "华中地区",
    "西安": "西北地区",
    "沈阳": "东北地区",
}


def load_old_data():
    """加载旧格式数据"""
    if not OLD_DATA_FILE.exists():
        print(f"旧数据文件不存在: {OLD_DATA_FILE}")
        return {}

    with open(OLD_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def convert_building(bid: str, old_data: dict) -> dict:
    """将旧格式建筑数据转换为新格式"""
    old_type = old_data.get("type", "公共建筑")
    old_location = old_data.get("location", "北京")

    # 映射类型和地区
    new_type = TYPE_MAPPING.get(old_type, "公共建筑")
    new_region = REGION_MAPPING.get(old_location, "北方地区")

    # 转换能耗数据
    monthly_data = {}
    for month, data in old_data.get("energy_data", {}).items():
        monthly_data[month] = {
            "electricity_kwh": data.get("electricity", 0),
            "natural_gas_m3": data.get("gas", 0),
            "water_m3": data.get("water", 0)
        }

    # 创建新格式建筑数据
    new_building = {
        "basic_info": {
            "name": old_data.get("name", "未命名"),
            "building_type": new_type,
            "region": new_region,
            "floor_area_sqm": old_data.get("area", 10000),
            "num_floors": old_data.get("floors", 1),
            "num_basements": 0,
            "year_built": old_data.get("year_built", 2015),
            "num_employees": old_data.get("occupancy", 0),
            "weekly_operating_hours": 40
        },
        "building_structure": {
            "wall_construction": "混凝土",
            "roof_construction": "混凝土平顶",
            "roof_type": "平顶",
            "building_shape": "矩形",
            "glass_percentage": 30.0,
            "floor_to_ceiling_height_m": 3.0
        },
        "energy_systems": {
            "heating": {"primary_type": "集中供暖"},
            "cooling": {"primary_type": "中央空调"},
            "water_heating": {"primary_type": "天然气热水器"}
        },
        "energy_consumption": {
            "uses_electricity": True,
            "uses_natural_gas": True,
            "monthly_data": monthly_data
        }
    }

    return new_building


def migrate_data():
    """执行数据迁移"""
    print("=" * 60)
    print("建筑数据迁移脚本")
    print("=" * 60)
    print(f"源文件: {OLD_DATA_FILE}")
    print(f"目标文件: {NEW_DATA_FILE}")
    print()

    # 加载旧数据
    old_data = load_old_data()
    if not old_data:
        print("没有数据需要迁移")
        return

    print(f"发现 {len(old_data)} 个建筑需要迁移")
    print()

    # 创建新格式数据结构
    new_data = {
        "metadata": {
            "version": "2.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source": "CBECS 2012 - 迁移自旧格式"
        },
        "buildings": {}
    }

    # 转换每个建筑
    for bid, old_building in old_data.items():
        print(f"迁移: {bid} - {old_building.get('name', '未命名')}")
        new_data["buildings"][bid] = convert_building(bid, old_building)

    # 确保目录存在
    NEW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 保存新数据
    with open(NEW_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"迁移完成！已保存到: {NEW_DATA_FILE}")
    print(f"共迁移 {len(new_data['buildings'])} 个建筑")
    print("=" * 60)


if __name__ == "__main__":
    migrate_data()
