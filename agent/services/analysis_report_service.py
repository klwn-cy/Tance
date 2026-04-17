"""
分析报告查询服务 - 提供历史分析报告的查询功能
基于CBECS 2012数据生成的10份专业分析报告
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from project.logger_handler import logger


class AnalysisReportService:
    """分析报告查询服务"""

    def __init__(self, reports_dir: str = None):
        if reports_dir is None:
            project_root = Path(__file__).parent.parent.parent
            reports_dir = project_root / "data" / "analysis_reports"

        self.reports_dir = Path(reports_dir)
        self._reports_cache = None

    def _load_all_reports(self) -> Dict:
        """加载所有报告到缓存"""
        if self._reports_cache is not None:
            return self._reports_cache

        self._reports_cache = {}

        if not self.reports_dir.exists():
            logger.warning(f"报告目录不存在: {self.reports_dir}")
            return self._reports_cache

        for report_file in self.reports_dir.glob("*.json"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    report_id = report.get("report_id", report_file.stem)
                    self._reports_cache[report_id] = report
                    logger.info(f"加载报告: {report_id}")
            except Exception as e:
                logger.error(f"加载报告失败 {report_file}: {e}")

        return self._reports_cache

    def list_reports(self) -> List[Dict]:
        """获取所有报告列表"""
        reports = self._load_all_reports()
        return [
            {
                "report_id": rid,
                "title": r.get("title", "未命名"),
                "date": r.get("date", "未知"),
                "summary": r.get("summary", "")[:100] + "..."
            }
            for rid, r in reports.items()
        ]

    def list_reports_dict(self) -> List[Dict]:
        """获取所有报告列表（字典格式，包含更多信息）"""
        reports = self._load_all_reports()
        return [
            {
                "report_id": rid,
                "title": r.get("title", "未命名"),
                "date": r.get("date", "未知"),
                "summary": r.get("summary", ""),
                "keywords": r.get("keywords", []),
                "data_source": r.get("data_source", "CBECS 2012")
            }
            for rid, r in reports.items()
        ]

    def get_report(self, report_id: str) -> Optional[Dict]:
        """获取单个报告详情"""
        reports = self._load_all_reports()
        return reports.get(report_id)

    def search_reports(self, query: str) -> List[Dict]:
        """搜索报告"""
        reports = self._load_all_reports()
        query_lower = query.lower()

        results = []
        for rid, report in reports.items():
            # 在标题、摘要和关键词中搜索
            title = report.get("title", "").lower()
            summary = report.get("summary", "").lower()
            keywords = " ".join(report.get("keywords", [])).lower()

            if query_lower in title or query_lower in summary or query_lower in keywords:
                results.append({
                    "report_id": rid,
                    "title": report.get("title", "未命名"),
                    "date": report.get("date", "未知"),
                    "summary": report.get("summary", ""),
                    "relevance": "high" if query_lower in title else "medium"
                })

        return results

    def get_report_summary(self, report_id: str) -> str:
        """获取报告摘要（用于显示）"""
        report = self.get_report(report_id)
        if not report:
            return f"未找到报告: {report_id}"

        summary = f"""【{report.get('title', '未命名报告')}】

报告ID: {report.get('report_id', '未知')}
日期: {report.get('date', '未知')}
数据来源: {report.get('data_source', '未知')}

【摘要】
{report.get('summary', '无摘要')}

【主要发现】
"""
        for finding in report.get("key_findings", []):
            summary += f"- {finding.get('finding', '')}: {finding.get('value', '')}\n"
            summary += f"  {finding.get('description', '')}\n"

        summary += f"""
【建议】
"""
        for i, rec in enumerate(report.get("recommendations", []), 1):
            summary += f"{i}. {rec}\n"

        summary += f"""
【关键词】
{', '.join(report.get('keywords', []))}
"""
        return summary

    def get_all_reports_summary(self) -> str:
        """获取所有报告的概览"""
        reports = self.list_reports()

        if not reports:
            return "暂无分析报告"

        summary = f"""【CBECS 2012建筑能耗分析报告库】

共收录 {len(reports)} 份专业分析报告，基于美国商业建筑能耗调查数据（CBECS 2012）。

【报告列表】
"""
        for r in reports:
            summary += f"\n{r['report_id']}: {r['title']}\n"
            summary += f"  日期: {r['date']}\n"
            summary += f"  摘要: {r['summary']}\n"

        summary += """
【如何查询】
- 按编号查询：输入"查询报告R001"或"查看报告R002"
- 按关键词搜索：输入"搜索供暖"或"搜索照明节能"
- 查看全部：输入"列出所有报告"
"""
        return summary


# 创建全局单例
analysis_report_service = AnalysisReportService()
