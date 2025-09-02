import gc
import logging
import threading
import time
import weakref
from typing import Any, Dict

import psutil

logger = logging.getLogger(__name__)


class MemoryManager:
    """内存管理器，提供内存监控、缓存清理和垃圾回收功能"""

    def __init__(self):
        self.process = psutil.Process()
        self.cache_registry: Dict[str, weakref.ref] = {}
        self.memory_threshold = 0.8  # 内存使用率阈值 (80%)
        self.cleanup_interval = 300  # 清理间隔 (5分钟)
        self.monitor_thread = None
        self.is_monitoring = False

    def get_memory_usage(self) -> Dict[str, float]:
        """获取当前内存使用情况"""
        memory_info = self.process.memory_info()
        system_memory = psutil.virtual_memory()

        return {
            'process_rss_mb': memory_info.rss / 1024 / 1024,  # 进程物理内存 (MB)
            'process_vms_mb': memory_info.vms / 1024 / 1024,  # 进程虚拟内存 (MB)
            'system_usage_percent': system_memory.percent,  # 系统内存使用率
            'system_available_mb': system_memory.available / 1024 / 1024,  # 系统可用内存 (MB)
        }

    def register_cache(self, name: str, cache_object: Any):
        """注册缓存对象，用于自动清理"""
        self.cache_registry[name] = weakref.ref(cache_object)
        logger.info(f"注册缓存: {name}")

    def unregister_cache(self, name: str):
        """注销缓存对象"""
        if name in self.cache_registry:
            del self.cache_registry[name]
            logger.info(f"注销缓存: {name}")

    def clear_cache(self, name: str | None = None):
        """清理指定缓存或所有缓存"""
        if name:
            if name in self.cache_registry:
                cache_ref = self.cache_registry[name]
                cache_obj = cache_ref()
                if cache_obj and hasattr(cache_obj, 'clear'):
                    cache_obj.clear()
                    logger.info(f"清理缓存: {name}")
        else:
            # 清理所有缓存
            for cache_name, cache_ref in self.cache_registry.items():
                cache_obj = cache_ref()
                if cache_obj and hasattr(cache_obj, 'clear'):
                    cache_obj.clear()
                    logger.info(f"清理缓存: {cache_name}")

    def force_garbage_collection(self):
        """强制垃圾回收"""
        collected = gc.collect()
        logger.info(f"垃圾回收完成，回收对象数: {collected}")
        return collected

    def check_memory_pressure(self) -> bool:
        """检查内存压力"""
        memory_usage = self.get_memory_usage()
        return memory_usage['system_usage_percent'] > (self.memory_threshold * 100)

    def cleanup_if_needed(self):
        """如果需要则进行清理"""
        if self.check_memory_pressure():
            logger.warning("检测到内存压力，开始清理...")
            self.clear_cache()
            self.force_garbage_collection()
            return True
        return False

    def start_monitoring(self):
        """开始内存监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("内存监控已启动")

    def stop_monitoring(self):
        """停止内存监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("内存监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                memory_usage = self.get_memory_usage()
                logger.debug(
                    f"内存使用: {memory_usage['process_rss_mb']:.1f}MB, "
                    f"系统使用率: {memory_usage['system_usage_percent']:.1f}%"
                )

                # 检查是否需要清理
                if self.check_memory_pressure():
                    self.cleanup_if_needed()

                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"内存监控错误: {e}")
                time.sleep(60)  # 出错时等待1分钟再继续

    def get_memory_report(self) -> Dict[str, Any]:
        """获取内存使用报告"""
        memory_usage = self.get_memory_usage()
        cache_count = len(self.cache_registry)

        return {
            'memory_usage': memory_usage,
            'cache_count': cache_count,
            'cache_names': list(self.cache_registry.keys()),
            'is_monitoring': self.is_monitoring,
            'memory_pressure': self.check_memory_pressure(),
        }


# 全局内存管理器实例
memory_manager = MemoryManager()


class CacheManager:
    """缓存管理器，提供智能缓存功能"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl  # 生存时间 (秒)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}

        # 注册到内存管理器
        memory_manager.register_cache('cache_manager', self)

    def get(self, key: str) -> Any:
        """获取缓存值"""
        if key in self.cache:
            # 检查是否过期
            if time.time() - self.access_times[key] > self.ttl:
                self.delete(key)
                return None

            # 更新访问时间
            self.access_times[key] = time.time()
            return self.cache[key]['value']
        return None

    def set(self, key: str, value: Any):
        """设置缓存值"""
        # 检查缓存大小
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = {'value': value, 'created': time.time()}
        self.access_times[key] = time.time()

    def delete(self, key: str):
        """删除缓存项"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
        logger.info("缓存已清空")

    def _evict_oldest(self):
        """驱逐最旧的缓存项"""
        if not self.access_times:
            return

        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(oldest_key)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'usage_percent': (len(self.cache) / self.max_size) * 100,
            'ttl': self.ttl,
        }


# 全局缓存管理器实例
cache_manager = CacheManager()
