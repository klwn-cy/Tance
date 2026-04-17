"""
对话历史存储服务 - 提供与智能体对话历史的持久化存储
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from project.logger_handler import logger


class ChatHistoryService:
    """对话历史存储服务"""

    def __init__(self, history_dir: str = None):
        if history_dir is None:
            project_root = Path(__file__).parent.parent.parent
            history_dir = project_root / "data" / "chat_history"

        self.history_dir = Path(history_dir)
        self.history_file = self.history_dir / "chat_history.json"

        # 确保目录存在
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def load_history(self) -> List[Dict]:
        """加载对话历史"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("messages", [])
        except Exception as e:
            logger.error(f"加载对话历史失败: {e}")
            return []

    def save_history(self, messages: List[Dict]) -> bool:
        """保存对话历史"""
        try:
            data = {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message_count": len(messages),
                "messages": messages
            }

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"保存对话历史成功，共 {len(messages)} 条消息")
            return True
        except Exception as e:
            logger.error(f"保存对话历史失败: {e}")
            return False

    def clear_history(self) -> bool:
        """清空对话历史"""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            logger.info("对话历史已清空")
            return True
        except Exception as e:
            logger.error(f"清空对话历史失败: {e}")
            return False

    def get_history_info(self) -> Dict:
        """获取历史信息"""
        if not self.history_file.exists():
            return {
                "exists": False,
                "message_count": 0,
                "last_updated": None
            }

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "exists": True,
                    "message_count": data.get("message_count", 0),
                    "last_updated": data.get("last_updated", "未知")
                }
        except:
            return {
                "exists": False,
                "message_count": 0,
                "last_updated": None
            }


# 创建全局单例
chat_history_service = ChatHistoryService()