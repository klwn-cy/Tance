"""
测试脚本 - 验证建筑管理系统功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.services.building_service import building_service
from agent.services.analysis_report_service import analysis_report_service

def test_building_service():
    """测试建筑服务"""
    print("=" * 60)
    print("测试建筑服务")
    print("=" * 60)

    # 测试列出建筑
    buildings = building_service.list_buildings()
    print(f"\n1. 列出建筑: 发现 {len(buildings)} 个建筑")
    for bid, building in buildings.items():
        name = building.get("basic_info", {}).get("name", "未命名")
        print(f"   - {bid}: {name}")

    # 测试获取单个建筑
    if buildings:
        first_bid = list(buildings.keys())[0]
        print(f"\n2. 获取建筑详情: {first_bid}")
        print(building_service.get_building_summary(first_bid)[:200] + "...")

    print("\n✅ 建筑服务测试完成")


def test_analysis_report_service():
    """测试分析报告服务"""
    print("\n" + "=" * 60)
    print("测试分析报告服务")
    print("=" * 60)

    # 测试列出报告
    reports = analysis_report_service.list_reports()
    print(f"\n1. 列出报告: 发现 {len(reports)} 份报告")
    for r in reports:
        print(f"   - {r['report_id']}: {r['title']}")

    # 测试获取单个报告
    if reports:
        first_rid = reports[0]["report_id"]
        print(f"\n2. 获取报告详情: {first_rid}")
        print(analysis_report_service.get_report_summary(first_rid)[:300] + "...")

    # 测试搜索
    print("\n3. 搜索报告: '供暖'")
    results = analysis_report_service.search_reports("供暖")
    print(f"   找到 {len(results)} 条结果")
    for r in results:
        print(f"   - {r['report_id']}: {r['title']}")

    print("\n✅ 分析报告服务测试完成")


def test_create_building():
    """测试创建建筑"""
    print("\n" + "=" * 60)
    print("测试创建建筑")
    print("=" * 60)

    # 创建测试建筑
    result = building_service.create_building(
        name="测试办公楼",
        building_type="办公建筑",
        region="华东地区",
        floor_area_sqm=8000,
        num_floors=10,
        year_built=2020,
        num_employees=200
    )

    print(f"\n创建建筑成功!")
    print(f"   建筑ID: {result['building_id']}")
    print(f"   建筑名称: {result['building']['basic_info']['name']}")

    # 删除测试建筑
    building_service.delete_building(result['building_id'])
    print(f"\n已删除测试建筑: {result['building_id']}")

    print("\n✅ 创建建筑测试完成")


if __name__ == "__main__":
    try:
        test_building_service()
        test_analysis_report_service()
        test_create_building()

        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()