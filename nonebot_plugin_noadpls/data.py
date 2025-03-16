import yaml
from typing import Dict, Optional
from pydantic import BaseModel, Field
import os

from .utils.constants import GetStorePath
from .utils.log import log

DATA_PATH = GetStorePath.DATA_FILE

class DataModel(BaseModel):
    """禁言数据模型，三层结构: 群ID -> 用户ID -> 禁言次数"""
    ban_count: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    def get_ban_count(self, group_id: str, user_id: str) -> int:
        """获取用户在指定群的禁言次数"""
        return self.ban_count.get(group_id, {}).get(user_id, 0)
    
    def increase_ban_count(self, group_id: str, user_id: str, count: int = 1) -> int:
        """增加用户在指定群的禁言次数"""
        if group_id not in self.ban_count:
            self.ban_count[group_id] = {}
        
        if user_id not in self.ban_count[group_id]:
            self.ban_count[group_id][user_id] = 0
            
        self.ban_count[group_id][user_id] += count
        return self.ban_count[group_id][user_id]
    
    def reset_ban_count(self, group_id: Optional[str] = None, user_id: Optional[str] = None) -> None:
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
        log.debug("数据文件加载成功")
        return data
    except Exception as e:
        log.error(f"加载数据文件失败: {e}")
        return data

def save_data() -> None:
    """保存数据到文件"""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            yaml.dump(data.model_dump(), f, allow_unicode=True)
        log.debug("数据文件保存成功")
    except Exception as e:
        log.error(f"保存数据文件失败: {e}")