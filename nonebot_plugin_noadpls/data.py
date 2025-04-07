import yaml
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field
import os
from pathlib import Path

from .utils.constants import GetStorePath
from .utils.log import log

DATA_PATH = Path(GetStorePath.DATA_FILE)


class NoticeType(str, Enum):
    """通知类型枚举"""
    BAN = "ban_notice"
    "禁言通知"

# 为NoticeType枚举定义YAML表示方法
def enum_representer(dumper, adata):
    """自定义枚举类型的YAML表示"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', adata.value)

# 注册表示方法
yaml.SafeDumper.add_representer(NoticeType, enum_representer)

class DataModel(BaseModel):
    """
    数据模型
    禁言: 群ID -> 用户ID -> 禁言次数
    通知管理: 群ID -> 用户ID -> 通知内容 -> 开关Bool
    """
    ban_count: Dict[int, Dict[int, int]] = Field(default_factory=dict)
    notice_manager: Dict[int, Dict[int, Dict[str, bool]]
                         ] = Field(default_factory=dict)

    def get_ban_count(self, group_id: int, user_id: int) -> int:
        """获取用户在指定群的禁言次数"""
        return self.ban_count.get(group_id, {}).get(user_id, 0)

    def increase_ban_count(self, group_id: int, user_id: int, count: int = 1) -> int:
        """增加用户在指定群的禁言次数"""
        if group_id not in self.ban_count:
            self.ban_count[group_id] = {}

        if user_id not in self.ban_count[group_id]:
            self.ban_count[group_id][user_id] = 0

        self.ban_count[group_id][user_id] += count
        return self.ban_count[group_id][user_id]

    def reset_ban_count(self, group_id: Optional[int] = None, user_id: Optional[int] = None) -> None:
        """重置禁言次数

        Args:
            group_id: 指定群ID，为None则重置所有群
            user_id: 指定用户ID，为None则重置指定群中的所有用户
        """
        if group_id is None:
            self.ban_count = {}
            return

        if group_id not in self.ban_count:
            return

        if user_id is None:
            self.ban_count[group_id] = {}
        else:
            self.ban_count[group_id][user_id] = 0

    def get_notice_state(self, group_id: int, user_id: int, notice_type: NoticeType) -> bool:
        """获取用户在指定群对某类通知的开启状态

        Args:
            group_id: 群ID
            user_id: 用户ID
            notice_type: 通知类型

        Returns:
            通知是否开启，默认为False
        """
        return self.notice_manager.get(group_id, {}).get(user_id, {}).get(notice_type, False)

    def set_notice_state(self, group_id: int, user_id: int, notice_type: NoticeType, state: bool = True) -> bool:
        """设置用户在指定群对某类通知的开启状态

        Args:
            group_id: 群ID
            user_id: 用户ID
            notice_type: 通知类型
            state: 开启状态，默认为True

        Returns:
            设置后的状态
        """
        if group_id not in self.notice_manager:
            self.notice_manager[group_id] = {}

        if user_id not in self.notice_manager[group_id]:
            self.notice_manager[group_id][user_id] = {}

        self.notice_manager[group_id][user_id][notice_type] = state
        return state

    def get_user_notices(self, group_id: int, user_id: int) -> Dict[str, bool]:
        """获取用户在指定群的所有通知设置

        Args:
            group_id: 群ID
            user_id: 用户ID

        Returns:
            通知类型到开启状态的映射
        """
        return self.notice_manager.get(group_id, {}).get(user_id, {})

    def get_notice_list(self, group_id: int, notice_type: NoticeType) -> set[int]:
        """获取指定群所有需要某类通知的用户

        Args:
            group_id (int): 群ID
            notice_type (NoticeType): 通知类型

        Returns:
            set[int]: 需要某类通知的用户ID列表
        """
        if group_id not in self.notice_manager:
            return set()
        return {user_id for user_id, notices in self.notice_manager[group_id].items() if notices.get(notice_type, False)}

    def reset_notice_state(self, group_id: Optional[int] = None, user_id: Optional[int] = None,
                           notice_type: Optional[NoticeType] = None) -> None:
        """重置通知设置

        Args:
            group_id: 指定群ID，为None则重置所有群
            user_id: 指定用户ID，为None则重置指定群中的所有用户
            notice_type: 指定通知类型，为None则重置指定用户的所有通知类型
        """
        if group_id is None:
            self.notice_manager = {}
            return

        if group_id not in self.notice_manager:
            return

        if user_id is None:
            self.notice_manager[group_id] = {}
            return

        if user_id not in self.notice_manager[group_id]:
            return

        if notice_type is None:
            self.notice_manager[group_id][user_id] = {}
        else:
            if notice_type in self.notice_manager[group_id][user_id]:
                del self.notice_manager[group_id][user_id][notice_type]


# 全局数据实例
data = DataModel()


def load_data() -> DataModel:
    """从文件加载数据"""
    if not os.path.exists(DATA_PATH):
        # 如果文件不存在，创建默认数据
        save_data()
        return data

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            loaded_data = yaml.safe_load(f) or {}

        # 将加载的数据更新到全局数据实例
        data.ban_count = loaded_data.get("ban_count", {})
        
        # 处理通知管理器数据
        notice_manager = loaded_data.get("notice_manager", {})
        if notice_manager:
            processed_notice_manager = {}
            for group_id, users in notice_manager.items():
                processed_notice_manager[group_id] = {}
                for user_id, notices in users.items():
                    processed_notice_manager[group_id][user_id] = {}
                    for notice_str, state in notices.items():
                        # 将字符串转换为枚举
                        try:
                            notice_type = NoticeType(notice_str)
                            processed_notice_manager[group_id][user_id][notice_type] = state
                        except ValueError:
                            # 处理无法识别的通知类型
                            log.warning(f"无法识别的通知类型: {notice_str}")
            data.notice_manager = processed_notice_manager
        
        log.debug("数据文件加载成功")
        return data
    except Exception as e:
        log.error(f"加载数据文件失败: {e}")
        return data


def save_data() -> None:
    """保存数据到文件"""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 创建可序列化的字典
        serializable_data = {
            "ban_count": data.ban_count,
            "notice_manager": {}
        }
        
        # 处理通知管理器，将枚举转换为字符串
        for group_id, users in data.notice_manager.items():
            serializable_data["notice_manager"][group_id] = {}
            for user_id, notices in users.items():
                serializable_data["notice_manager"][group_id][user_id] = {}
                for notice_type, state in notices.items():
                    # 确保枚举值被转换为字符串
                    notice_key = notice_type.value if isinstance(notice_type, NoticeType) else str(notice_type)
                    serializable_data["notice_manager"][group_id][user_id][notice_key] = state
        
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            yaml.dump(serializable_data, f, allow_unicode=True)
        
        log.debug("数据文件保存成功")
    except Exception as e:
        log.error(f"保存数据文件失败: {e}")


load_data()
