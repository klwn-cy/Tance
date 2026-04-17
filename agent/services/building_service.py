"""
建筑服务模块 - 提供建筑CRUD操作
支持建筑信息的增删改查和能耗数据管理
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from project.logger_handler import logger


class BuildingService:
    """建筑服务类 - 管理建筑数据的CRUD操作"""

    def __init__(self, data_file: str = None):
        """
        初始化建筑服务

        Args:
            data_file: 数据文件路径，默认为 data/energy_data/buildings_v2.json
        """
        if data_file is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            data_file = project_root / "data" / "energy_data" / "buildings_v2.json"

        self.data_file = Path(data_file)
        self._ensure_data_file()

    def _ensure_data_file(self):
        """确保数据文件存在"""
        if not self.data_file.exists():
            # 创建数据目录
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            # 创建初始数据结构
            initial_data = {
                "metadata": {
                    "version": "2.0",
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_source": "CBECS 2012"
                },
                "buildings": {}
            }
            self._save_data(initial_data)
            logger.info(f"创建建筑数据文件: {self.data_file}")

    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载建筑数据失败: {e}")
            return {"metadata": {}, "buildings": {}}

    def _save_data(self, data: Dict):
        """保存数据"""
        data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"建筑数据已保存: {self.data_file}")

    def _generate_building_id(self) -> str:
        """生成新的建筑ID"""
        data = self._load_data()
        existing_ids = list(data.get("buildings", {}).keys())
        max_num = 0
        for bid in existing_ids:
            if bid.startswith("B"):
                try:
                    num = int(bid[1:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue
        return f"B{max_num + 1:03d}"

    def create_building(
        self,
        name: str,
        building_type: str,
        region: str,
        floor_area_sqm: float,
        num_floors: int = 1,
        num_basements: int = 0,
        year_built: int = None,
        num_employees: int = 0,
        weekly_operating_hours: int = 40,
        wall_construction: str = "混凝土",
        roof_construction: str = "混凝土平顶",
        roof_type: str = "平顶",
        building_shape: str = "矩形",
        glass_percentage: float = 30.0,
        floor_to_ceiling_height_m: float = 3.0,
        heating_type: str = "集中供暖",
        cooling_type: str = "中央空调",
        water_heating_type: str = "天然气热水器",
        uses_electricity: bool = True,
        uses_natural_gas: bool = True
    ) -> Dict[str, Any]:
        """
        创建新建筑

        Args:
            name: 建筑名称
            building_type: 建筑类型
            region: 所在地区
            floor_area_sqm: 建筑面积（平方米）
            num_floors: 楼层数
            num_basements: 地下层数
            year_built: 建造年份
            num_employees: 员工人数
            weekly_operating_hours: 每周运营小时数
            wall_construction: 墙体结构
            roof_construction: 屋顶结构
            roof_type: 屋顶类型
            building_shape: 建筑形状
            glass_percentage: 玻璃幕墙占比（%）
            floor_to_ceiling_height_m: 层高（米）
            heating_type: 供暖类型
            cooling_type: 制冷类型
            water_heating_type: 热水供应类型
            uses_electricity: 是否使用电力
            uses_natural_gas: 是否使用天然气

        Returns:
            包含新建筑ID和信息的字典
        """
        data = self._load_data()
        building_id = self._generate_building_id()

        building = {
            "basic_info": {
                "name": name,
                "building_type": building_type,
                "region": region,
                "floor_area_sqm": floor_area_sqm,
                "num_floors": num_floors,
                "num_basements": num_basements,
                "year_built": year_built or datetime.now().year,
                "num_employees": num_employees,
                "weekly_operating_hours": weekly_operating_hours
            },
            "building_structure": {
                "wall_construction": wall_construction,
                "roof_construction": roof_construction,
                "roof_type": roof_type,
                "building_shape": building_shape,
                "glass_percentage": glass_percentage,
                "floor_to_ceiling_height_m": floor_to_ceiling_height_m
            },
            "energy_systems": {
                "heating": {"primary_type": heating_type},
                "cooling": {"primary_type": cooling_type},
                "water_heating": {"primary_type": water_heating_type}
            },
            "energy_consumption": {
                "uses_electricity": uses_electricity,
                "uses_natural_gas": uses_natural_gas,
                "monthly_data": {}
            }
        }

        data["buildings"][building_id] = building
        self._save_data(data)

        logger.info(f"创建建筑成功: {building_id} - {name}")
        return {"building_id": building_id, "building": building}

    def get_building(self, building_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个建筑信息

        Args:
            building_id: 建筑ID

        Returns:
            建筑信息字典，如果不存在返回None
        """
        data = self._load_data()
        return data.get("buildings", {}).get(building_id)

    def list_buildings(
        self,
        building_type: str = None,
        region: str = None,
        min_area: float = None,
        max_area: float = None,
        year_built_min: int = None,
        year_built_max: int = None
    ) -> Dict[str, Dict]:
        """
        查询建筑列表（支持筛选）

        Args:
            building_type: 建筑类型筛选
            region: 地区筛选
            min_area: 最小建筑面积
            max_area: 最大建筑面积
            year_built_min: 最小建造年份
            year_built_max: 最大建造年份

        Returns:
            符合条件的建筑字典
        """
        data = self._load_data()
        buildings = data.get("buildings", {})

        result = {}
        for bid, building in buildings.items():
            basic = building.get("basic_info", {})

            # 应用筛选条件
            if building_type and basic.get("building_type") != building_type:
                continue
            if region and basic.get("region") != region:
                continue
            if min_area and basic.get("floor_area_sqm", 0) < min_area:
                continue
            if max_area and basic.get("floor_area_sqm", 0) > max_area:
                continue
            if year_built_min and basic.get("year_built", 0) < year_built_min:
                continue
            if year_built_max and basic.get("year_built", 0) > year_built_max:
                continue

            result[bid] = building

        return result

    def update_building(
        self,
        building_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        更新建筑信息

        Args:
            building_id: 建筑ID
            **kwargs: 要更新的字段

        Returns:
            更新后的建筑信息，如果建筑不存在返回None
        """
        data = self._load_data()
        buildings = data.get("buildings", {})

        if building_id not in buildings:
            logger.warning(f"建筑不存在: {building_id}")
            return None

        building = buildings[building_id]

        # 更新basic_info字段
        basic_fields = [
            "name", "building_type", "region", "floor_area_sqm",
            "num_floors", "num_basements", "year_built",
            "num_employees", "weekly_operating_hours"
        ]
        for field in basic_fields:
            if field in kwargs:
                building["basic_info"][field] = kwargs[field]

        # 更新building_structure字段
        structure_fields = [
            "wall_construction", "roof_construction", "roof_type",
            "building_shape", "glass_percentage", "floor_to_ceiling_height_m"
        ]
        for field in structure_fields:
            if field in kwargs:
                building["building_structure"][field] = kwargs[field]

        # 更新energy_systems字段
        if "heating_type" in kwargs:
            building["energy_systems"]["heating"]["primary_type"] = kwargs["heating_type"]
        if "cooling_type" in kwargs:
            building["energy_systems"]["cooling"]["primary_type"] = kwargs["cooling_type"]
        if "water_heating_type" in kwargs:
            building["energy_systems"]["water_heating"]["primary_type"] = kwargs["water_heating_type"]

        # 更新energy_consumption字段
        if "uses_electricity" in kwargs:
            building["energy_consumption"]["uses_electricity"] = kwargs["uses_electricity"]
        if "uses_natural_gas" in kwargs:
            building["energy_consumption"]["uses_natural_gas"] = kwargs["uses_natural_gas"]

        data["buildings"][building_id] = building
        self._save_data(data)

        logger.info(f"更新建筑成功: {building_id}")
        return building

    def delete_building(self, building_id: str) -> bool:
        """
        删除建筑

        Args:
            building_id: 建筑ID

        Returns:
            是否删除成功
        """
        data = self._load_data()
        buildings = data.get("buildings", {})

        if building_id not in buildings:
            logger.warning(f"建筑不存在，无法删除: {building_id}")
            return False

        del data["buildings"][building_id]
        self._save_data(data)

        logger.info(f"删除建筑成功: {building_id}")
        return True

    def add_monthly_energy_data(
        self,
        building_id: str,
        month: str,
        electricity_kwh: float = 0,
        natural_gas_m3: float = 0,
        water_m3: float = 0
    ) -> bool:
        """
        添加月度能耗数据

        Args:
            building_id: 建筑ID
            month: 月份（格式：YYYY-MM）
            electricity_kwh: 电力消耗（kWh）
            natural_gas_m3: 天然气消耗（m³）
            water_m3: 用水量（m³）

        Returns:
            是否添加成功
        """
        data = self._load_data()
        buildings = data.get("buildings", {})

        if building_id not in buildings:
            logger.warning(f"建筑不存在: {building_id}")
            return False

        # 确保monthly_data存在
        if "monthly_data" not in buildings[building_id]["energy_consumption"]:
            buildings[building_id]["energy_consumption"]["monthly_data"] = {}

        buildings[building_id]["energy_consumption"]["monthly_data"][month] = {
            "electricity_kwh": electricity_kwh,
            "natural_gas_m3": natural_gas_m3,
            "water_m3": water_m3
        }

        self._save_data(data)
        logger.info(f"添加能耗数据成功: {building_id} - {month}")
        return True

    def get_energy_data(
        self,
        building_id: str,
        start_month: str = None,
        end_month: str = None
    ) -> Dict[str, Dict]:
        """
        获取建筑能耗数据

        Args:
            building_id: 建筑ID
            start_month: 起始月份（可选）
            end_month: 结束月份（可选）

        Returns:
            能耗数据字典
        """
        building = self.get_building(building_id)
        if not building:
            return {}

        monthly_data = building.get("energy_consumption", {}).get("monthly_data", {})

        if not start_month and not end_month:
            return monthly_data

        result = {}
        for month, data in monthly_data.items():
            if start_month and month < start_month:
                continue
            if end_month and month > end_month:
                continue
            result[month] = data

        return result

    def get_all_building_ids(self) -> List[str]:
        """获取所有建筑ID列表"""
        data = self._load_data()
        return list(data.get("buildings", {}).keys())

    def get_building_summary(self, building_id: str) -> str:
        """
        获取建筑摘要信息（用于显示）

        Args:
            building_id: 建筑ID

        Returns:
            格式化的建筑摘要字符串
        """
        building = self.get_building(building_id)
        if not building:
            return f"未找到建筑ID: {building_id}"

        basic = building.get("basic_info", {})
        structure = building.get("building_structure", {})
        systems = building.get("energy_systems", {})

        summary = f"""【建筑信息】
建筑ID: {building_id}
建筑名称: {basic.get('name', '未命名')}
建筑类型: {basic.get('building_type', '未知')}
所在地区: {basic.get('region', '未知')}
建筑面积: {basic.get('floor_area_sqm', 0):,.0f} 平方米
楼层数: {basic.get('num_floors', 0)} 层（地上{basic.get('num_floors', 0)}层，地下{basic.get('num_basements', 0)}层）
建造年份: {basic.get('year_built', '未知')}
员工人数: {basic.get('num_employees', 0)} 人
每周运营: {basic.get('weekly_operating_hours', 0)} 小时

【建筑结构】
墙体结构: {structure.get('wall_construction', '未知')}
屋顶结构: {structure.get('roof_construction', '未知')}
屋顶类型: {structure.get('roof_type', '未知')}
建筑形状: {structure.get('building_shape', '未知')}
玻璃幕墙占比: {structure.get('glass_percentage', 0):.1f}%
层高: {structure.get('floor_to_ceiling_height_m', 0):.1f} 米

【能源系统】
供暖系统: {systems.get('heating', {}).get('primary_type', '未知')}
制冷系统: {systems.get('cooling', {}).get('primary_type', '未知')}
热水系统: {systems.get('water_heating', {}).get('primary_type', '未知')}
"""
        return summary


# 创建全局单例
building_service = BuildingService()
