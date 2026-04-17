"""
建筑枚举定义模块 - 基于CBECS 2012数据标准
提供建筑类型、地区、能源系统类型等枚举
"""
from enum import Enum
from typing import List


class BuildingType(str, Enum):
    """建筑类型枚举 - 基于CBECS分类"""
    EDUCATION = "教育建筑"
    PUBLIC = "公共建筑"
    RESEARCH = "科研建筑"
    RESIDENTIAL = "居住建筑"
    SPORTS = "体育建筑"
    OFFICE = "办公建筑"
    HEALTHCARE = "医疗建筑"
    RETAIL = "商业建筑"
    HOTEL = "酒店建筑"
    WAREHOUSE = "仓储建筑"
    INDUSTRIAL = "工业建筑"
    OTHER = "其他建筑"


class Region(str, Enum):
    """中国气候分区"""
    NORTH = "北方地区"
    SOUTH = "南方地区"
    EAST = "华东地区"
    CENTRAL = "华中地区"
    SOUTHWEST = "西南地区"
    NORTHWEST = "西北地区"
    NORTHEAST = "东北地区"


class WallConstruction(str, Enum):
    """墙体结构类型"""
    CONCRETE = "混凝土"
    BRICK = "砖墙"
    STEEL = "钢结构"
    WOOD = "木结构"
    GLASS_CURTAIN = "玻璃幕墙"
    COMPOSITE = "复合结构"


class RoofConstruction(str, Enum):
    """屋顶结构类型"""
    CONCRETE_FLAT = "混凝土平顶"
    METAL = "金属屋面"
    TILE = "瓦片屋顶"
    GREEN_ROOF = "绿色屋顶"
    GLASS = "玻璃顶"


class RoofType(str, Enum):
    """屋顶类型"""
    FLAT = "平顶"
    PITCHED = "坡顶"
    DOMED = "穹顶"
    SAWTOOTH = "锯齿形"


class BuildingShape(str, Enum):
    """建筑形状"""
    RECTANGULAR = "矩形"
    L_SHAPED = "L形"
    U_SHAPED = "U形"
    CIRCULAR = "圆形"
    IRREGULAR = "不规则形状"


class HeatingType(str, Enum):
    """供暖类型"""
    CENTRAL_HEATING = "集中供暖"
    NATURAL_GAS_BOILER = "天然气锅炉"
    ELECTRIC_HEATING = "电采暖"
    HEAT_PUMP = "热泵"
    DISTRICT_HEATING = "区域供热"
    NONE = "无供暖"


class CoolingType(str, Enum):
    """制冷类型"""
    CENTRAL_AC = "中央空调"
    SPLIT_AC = "分体空调"
    VRV = "VRV多联机"
    CHILLED_WATER = "冷水机组"
    EVAPORATIVE = "蒸发冷却"
    NONE = "无制冷"


class WaterHeatingType(str, Enum):
    """热水供应类型"""
    NATURAL_GAS = "天然气热水器"
    ELECTRIC = "电热水器"
    SOLAR = "太阳能热水器"
    HEAT_PUMP = "热泵热水器"
    CENTRAL = "集中热水系统"
    NONE = "无集中热水"


# 获取所有建筑类型的列表
def get_building_types() -> List[str]:
    """获取所有建筑类型"""
    return [bt.value for bt in BuildingType]


def get_regions() -> List[str]:
    """获取所有地区"""
    return [r.value for r in Region]


def get_wall_constructions() -> List[str]:
    """获取所有墙体结构类型"""
    return [wc.value for wc in WallConstruction]


def get_roof_constructions() -> List[str]:
    """获取所有屋顶结构类型"""
    return [rc.value for rc in RoofConstruction]


def get_roof_types() -> List[str]:
    """获取所有屋顶类型"""
    return [rt.value for rt in RoofType]


def get_building_shapes() -> List[str]:
    """获取所有建筑形状"""
    return [bs.value for bs in BuildingShape]


def get_heating_types() -> List[str]:
    """获取所有供暖类型"""
    return [ht.value for ht in HeatingType]


def get_cooling_types() -> List[str]:
    """获取所有制冷类型"""
    return [ct.value for ct in CoolingType]


def get_water_heating_types() -> List[str]:
    """获取所有热水供应类型"""
    return [wht.value for wht in WaterHeatingType]
