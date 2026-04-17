from langchain.agents import create_agent
from model.factory import chat_model
from project.prompt_loader import load_system_prompts
from agent.tools.energy_tools import (
    rag_summarize,
    get_building_energy_data,
    calculate_carbon_reduction,
    generate_energy_strategy,
    simulate_building_energy,
    list_all_buildings,
    # 建筑管理工具
    create_building,
    get_building_info,
    query_buildings,
    update_building_info,
    delete_building,
    add_energy_data,
    get_building_type_list,
    get_region_list,
    # 分析报告查询工具
    list_analysis_reports,
    get_analysis_report,
    search_reports
)
from agent.tools.web_tools import (
    get_weather,
    get_weather_by_ip,
    web_search,
    get_user_location,
    fetch_webpage,
    get_current_datetime
)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[
                # 建筑能耗工具
                rag_summarize,              # 知识库检索
                get_building_energy_data,   # 建筑能耗数据
                calculate_carbon_reduction, # 减碳计算
                generate_energy_strategy,   # 节能策略
                simulate_building_energy,   # 数字孪生仿真
                list_all_buildings,         # 建筑列表
                # 建筑管理工具
                create_building,            # 创建建筑
                get_building_info,          # 获取建筑详情
                query_buildings,            # 查询建筑列表
                update_building_info,       # 更新建筑信息
                delete_building,            # 删除建筑
                add_energy_data,            # 添加能耗数据
                get_building_type_list,     # 获取建筑类型列表
                get_region_list,            # 获取地区列表
                # 分析报告查询工具
                list_analysis_reports,      # 列出分析报告
                get_analysis_report,        # 获取报告详情
                search_reports,             # 搜索报告
                # 网络工具
                get_weather,                # 天气信息
                get_weather_by_ip,          # 基于IP自动获取天气
                web_search,                 # 网络搜索
                get_user_location,          # 用户位置
                fetch_webpage,              # 网页抓取
                get_current_datetime,       # 当前时间
            ],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("查询教学楼A栋的能耗数据"):
        print(chunk, end="", flush=True)