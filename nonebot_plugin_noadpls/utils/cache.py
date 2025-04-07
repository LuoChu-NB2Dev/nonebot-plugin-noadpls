import os
import json
import time
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any, List, Tuple

from .constants import GetStorePath
from .log import log

# 缓存文件的根目录
CACHE_ROOT = GetStorePath.CACHE_PATH


class CacheManager:
    """缓存管理器"""

    def __init__(
        self,
        cache_dir: str = "default",
        default_ttl: int = 86400,  # 默认缓存时间 1 天（单位：秒）
        auto_clean: bool = True,
    ) -> None:
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存子目录名称，用于区分不同类型的缓存
            default_ttl: 默认缓存有效期（单位：秒）
            auto_clean: 是否在初始化时自动清理过期缓存
        """
        # self.cache_dir = CACHE_ROOT / cache_dir
        self.cache_dir = CACHE_ROOT
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 自动清理过期缓存
        if auto_clean:
            self.clean_expired_cache()

    def _get_cache_path(self, file_name: str) -> Path:
        """
        获取缓存文件路径

        Args:
            file_name: 缓存文件名或文件标识

        Returns:
            缓存文件的完整路径
        """
        # 计算文件名的哈希值，防止文件名中包含非法字符
        hashed_name = hashlib.md5(file_name.encode()).hexdigest()
        return self.cache_dir / f"{hashed_name}.cache"

    def save(
        self,
        file_name: str,
        content: Union[str, bytes, Dict, List, Any],
        ttl: Optional[int] = None,
    ) -> Path:
        """
        保存内容到缓存

        Args:
            file_name: 缓存文件标识
            content: 要缓存的内容
            ttl: 缓存有效期（单位：秒），默认使用初始化时设置的值

        Returns:
            缓存文件的路径
        """
        cache_path = self._get_cache_path(file_name)
        ttl = ttl if ttl is not None else self.default_ttl

        # 准备缓存数据
        cache_data = {
            "file_name": file_name,
            "timestamp": time.time(),
            "expires_at": time.time() + ttl,
            "content": content,
        }

        # 根据内容类型选择不同的保存方式
        try:
            if isinstance(content, bytes):
                # 保存元数据
                meta_path = cache_path.with_suffix(".meta")
                meta_data = {
                    "file_name": file_name,
                    "timestamp": time.time(),
                    "expires_at": time.time() + ttl,
                }
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta_data, f, ensure_ascii=False)

                # 保存二进制内容
                with open(cache_path, "wb") as f:
                    f.write(content)
            else:
                # 保存JSON格式的缓存数据
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False)

            log.debug(f"缓存成功保存: {file_name}")
            return cache_path

        except Exception as e:
            log.error(f"保存缓存失败 {file_name}: {e}")
            if cache_path.exists():
                os.remove(cache_path)
            return cache_path

    def load(
        self, file_name: str, default: Any = None, remove_if_expired: bool = True
    ) -> Any:
        """
        从缓存加载内容

        Args:
            file_name: 缓存文件标识
            default: 当缓存不存在或已过期时返回的默认值
            remove_if_expired: 如果缓存已过期是否自动删除

        Returns:
            缓存的内容，不存在或已过期则返回默认值
        """
        cache_path = self._get_cache_path(file_name)
        meta_path = cache_path.with_suffix(".meta")

        # 检查缓存是否存在
        if not cache_path.exists():
            return default

        try:
            # 判断是否为二进制缓存
            if meta_path.exists():
                # 读取元数据
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta_data = json.load(f)

                # 检查缓存是否过期
                if time.time() > meta_data.get("expires_at", 0):
                    if remove_if_expired:
                        os.remove(cache_path)
                        os.remove(meta_path)
                        log.debug(f"已删除过期缓存: {file_name}")
                    return default

                # 读取二进制内容
                with open(cache_path, "rb") as f:
                    log.debug(f"读取二进制缓存成功 {file_name}")
                    return f.read()
            else:
                # 读取JSON格式缓存
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                # 检查缓存是否过期
                if time.time() > cache_data.get("expires_at", 0):
                    if remove_if_expired:
                        os.remove(cache_path)
                        log.debug(f"已删除过期缓存: {file_name}")
                    return default
                log.debug(f"读取JSON缓存成功 {file_name}")
                return cache_data.get("content", default)

        except Exception as e:
            log.error(f"读取缓存失败 {file_name}: {e}")
            return default

    def exists(self, file_name: str, check_expired: bool = True) -> bool:
        """
        检查缓存是否存在

        Args:
            file_name: 缓存文件标识
            check_expired: 是否检查过期状态

        Returns:
            缓存是否存在且有效
        """
        cache_path = self._get_cache_path(file_name)
        meta_path = cache_path.with_suffix(".meta")

        # 检查缓存文件是否存在
        if not cache_path.exists():
            return False

        # 如果不需要检查过期状态，直接返回存在
        if not check_expired:
            return True

        try:
            # 判断是否为二进制缓存
            if meta_path.exists():
                # 读取元数据
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta_data = json.load(f)
                return time.time() <= meta_data.get("expires_at", 0)
            else:
                # 读取JSON格式缓存
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                return time.time() <= cache_data.get("expires_at", 0)

        except Exception as e:
            log.error(f"检查缓存状态失败 {file_name}: {e}")
            return False

    def remove(self, file_name: str) -> bool:
        """
        删除指定缓存

        Args:
            file_name: 缓存文件标识

        Returns:
            是否成功删除缓存
        """
        cache_path = self._get_cache_path(file_name)
        meta_path = cache_path.with_suffix(".meta")

        try:
            if cache_path.exists():
                os.remove(cache_path)
            if meta_path.exists():
                os.remove(meta_path)
            log.debug(f"已删除缓存: {file_name}")
            return True
        except Exception as e:
            log.error(f"删除缓存失败 {file_name}: {e}")
            return False

    def clean_expired_cache(self) -> int:
        """
        清理所有过期缓存

        Returns:
            已清理的缓存数量
        """
        count = 0

        try:
            # 遍历缓存目录中的所有文件
            for file_path in self.cache_dir.glob("*.cache"):
                meta_path = file_path.with_suffix(".meta")

                try:
                    # 判断是否为二进制缓存
                    if meta_path.exists():
                        # 读取元数据
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta_data = json.load(f)
                        if time.time() > meta_data.get("expires_at", 0):
                            os.remove(file_path)
                            os.remove(meta_path)
                            count += 1
                    else:
                        # 读取JSON格式缓存
                        with open(file_path, "r", encoding="utf-8") as f:
                            cache_data = json.load(f)
                        if time.time() > cache_data.get("expires_at", 0):
                            os.remove(file_path)
                            count += 1
                except Exception as e:
                    # 如果读取失败，考虑删除可能损坏的缓存文件
                    log.warning(f"检查缓存文件失败 {file_path}: {e}")
                    try:
                        os.remove(file_path)
                        if meta_path.exists():
                            os.remove(meta_path)
                        count += 1
                    except:
                        pass

            if count > 0:
                log.info(f"已清理 {count} 个过期缓存文件")
            return count

        except Exception as e:
            log.error(f"清理过期缓存失败: {e}")
            return count

    def clear_all(self) -> bool:
        """
        清除所有缓存

        Returns:
            是否成功清除所有缓存
        """
        try:
            # 删除整个缓存目录，然后重新创建
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            log.info(f"已清除所有缓存文件: {self.cache_dir}")
            return True
        except Exception as e:
            log.error(f"清除所有缓存失败: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            包含缓存统计数据的字典
        """
        total_files = 0
        valid_files = 0
        expired_files = 0
        total_size = 0

        try:
            # 遍历缓存目录中的所有文件
            for file_path in self.cache_dir.glob("*.cache"):
                total_files += 1
                total_size += file_path.stat().st_size

                meta_path = file_path.with_suffix(".meta")
                if meta_path.exists():
                    total_size += meta_path.stat().st_size

                # 检查文件是否过期
                try:
                    if meta_path.exists():
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta_data = json.load(f)
                        if time.time() <= meta_data.get("expires_at", 0):
                            valid_files += 1
                        else:
                            expired_files += 1
                    else:
                        with open(file_path, "r", encoding="utf-8") as f:
                            cache_data = json.load(f)
                        if time.time() <= cache_data.get("expires_at", 0):
                            valid_files += 1
                        else:
                            expired_files += 1
                except:
                    expired_files += 1

            return {
                "total_files": total_files,
                "valid_files": valid_files,
                "expired_files": expired_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": str(self.cache_dir),
                "default_ttl": self.default_ttl,
            }

        except Exception as e:
            log.error(f"获取缓存统计信息失败: {e}")
            return {
                "error": str(e),
                "total_files": total_files,
                "valid_files": valid_files,
                "expired_files": expired_files,
                "total_size_bytes": total_size,
                "cache_dir": str(self.cache_dir),
            }


# 提供一个默认的缓存管理器实例，方便直接使用
default_cache = CacheManager()


# 简单封装一些常用函数
def save_cache(file_name: str, content: Any, ttl: Optional[int] = None) -> Path:
    """保存内容到默认缓存"""
    return default_cache.save(file_name, content, ttl)


def load_cache(file_name: str, default: Any = None) -> Any:
    """从默认缓存加载内容"""
    return default_cache.load(file_name, default)


def cache_exists(file_name: str, check_expired: bool = True) -> bool:
    """检查默认缓存是否存在"""
    return default_cache.exists(file_name, check_expired)


def remove_cache(file_name: str) -> bool:
    """删除默认缓存"""
    return default_cache.remove(file_name)
