# -*- coding: utf-8 -*-
"""
Redis智能缓存系统

主要功能：
1. Redis缓存的CRUD操作
2. 命名空间隔离
3. 智能TTL策略
4. 专业统计分析并提交到MySQL
5. 缓存健康检查和监控
6. 热点键分析
7. 响应时间分析
8. 业务指标计算
"""

import json
import time
import threading
import socket
import os
import statistics
import enum
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from threading import Event
from collections import defaultdict, deque
import redis
from mdbq.log import mylogger


# 全局日志器
logger = mylogger.MyLogger(
    logging_mode='file',
    log_level='info',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,
    sample_rate=1,
    sensitive_fields=[],
    enable_metrics=False,
)


class CacheStatsCollector:
    """缓存统计收集器 """
    
    def __init__(self, enabled: bool = True, mysql_pool=None, config: dict = None):
        self.enabled = enabled
        self.mysql_pool = mysql_pool
        self.config = config or {}
        self.process_id = os.getpid()
        self.instance_name = self.config.get('instance_name', 'default')
        
        # 统计数据
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'total_operations': 0,
            'start_time': time.time()
        }
        self._lock = threading.RLock()
        self.response_times = deque(maxlen=1000)
        self.namespace_stats = defaultdict(int)
        
        # 定时提交控制
        self.submit_interval = self.config.get('submit_interval', 600)  # 每隔N秒定时提交一次（期间有新操作时）
        self.last_submit_time = time.time()
        self.last_operation_count = 0  # 上次提交时的操作总数
        
        # 后台定时器
        self._timer = None
        self._shutdown_event = threading.Event()
        self._error_count = 0  # 连续错误计数
        self._max_errors = 5   # 最大连续错误次数
        
        # 启动后台定时提交
        if self.enabled and self.mysql_pool:
            self._start_background_timer()

    def record_operation(self, operation: str, response_time: float = 0, namespace: str = ""):
        """记录操作统计"""
        if not self.enabled:
            return
        
        try:
            with self._lock:
                old_total = self.stats['total_operations']
                
                self.stats['total_operations'] += 1
                self.stats[operation] = self.stats.get(operation, 0) + 1
                
                if response_time > 0:
                    self.response_times.append(response_time)
                
                if namespace:
                    self.namespace_stats[namespace] += 1
                
                # 检查是否需要提交统计数据（容错处理）
                try:
                    self._check_and_submit()
                except Exception as submit_error:
                    # 统计提交失败不应影响统计记录
                    logger.error("统计数据提交检查失败，但统计记录继续", {
                        'instance_name': self.instance_name,
                        'process_id': self.process_id,
                        'operation': operation,
                        'submit_error': str(submit_error)
                    })
        except Exception as e:
            # 统计记录失败不应影响缓存操作
            logger.error("统计记录失败，但缓存操作继续", {
                'instance_name': self.instance_name,
                'process_id': self.process_id,
                'operation': operation,
                'error': str(e)
            })
    
    def _start_background_timer(self):
        """启动后台定时提交线程"""
        if self._timer is not None:
            return  # 已经启动
        
        logger.debug("启动后台定时提交", {
            'instance_name': self.instance_name,
            'submit_interval': self.submit_interval
        })
        
        self._timer = threading.Timer(self.submit_interval, self._background_submit)
        self._timer.daemon = True  # 设置为守护线程
        self._timer.start()
    
    def _background_submit(self):
        """后台定时提交方法"""
        if self._shutdown_event.is_set():
            return  # 已关闭，不再提交
        
        try:
            # 执行提交检查（强制检查，不受时间间隔限制）
            self._check_and_submit(force_check=True)
            # 成功执行，重置错误计数
            self._error_count = 0
            
        except Exception as e:
            self._error_count += 1
            logger.error("后台定时提交失败", {
                'instance_name': self.instance_name,
                'process_id': self.process_id,
                'error': str(e),
                'error_type': type(e).__name__,
                'error_count': self._error_count,
                'max_errors': self._max_errors
            })
            
            # 如果连续错误次数过多，停止定时器
            if self._error_count >= self._max_errors:
                logger.error("后台定时器连续错误过多，停止定时提交", {
                    'instance_name': self.instance_name,
                    'process_id': self.process_id,
                    'error_count': self._error_count
                })
                return  # 不再安排下一次定时器
                
        finally:
            # 安排下一次定时提交（仅在未达到最大错误次数时）
            if not self._shutdown_event.is_set() and self._error_count < self._max_errors:
                self._timer = threading.Timer(self.submit_interval, self._background_submit)
                self._timer.daemon = True
                self._timer.start()
    
    def _check_and_submit(self, force_check=False):
        """检查并提交统计数据
        
        Args:
            force_check: 是否强制检查（用于后台定时器）
        """
        if not self.mysql_pool:
            return
            
        current_time = time.time()
        time_since_last_submit = current_time - self.last_submit_time
        
        # 提交逻辑：每隔固定秒数且期间有新操作则提交
        should_check_time = force_check or time_since_last_submit >= self.submit_interval
        
        if should_check_time:
            # 检查是否有新的操作（与上次提交时相比）
            new_operations = self.stats['total_operations'] - self.last_operation_count
            
            if new_operations > 0:
                # 有新操作，提交统计数据
                try:
                    self._submit_to_mysql()
                    self.last_submit_time = current_time
                    self.last_operation_count = self.stats['total_operations']
                    
                    logger.info("统计数据提交成功", {
                        'instance_name': self.instance_name,
                        'total_operations': self.stats['total_operations'],
                        'new_operations': new_operations,
                        'trigger_type': 'background_timer' if force_check else 'operation_triggered'
                    })
                except Exception as e:
                    logger.error("统计数据提交失败", {
                        'instance_name': self.instance_name,
                        'error': str(e),
                        'trigger_type': 'background_timer' if force_check else 'operation_triggered'
                    })
            else:
                # 无新操作，跳过提交但更新时间
                self.last_submit_time = current_time
                if force_check:  # 仅在后台定时器触发时记录
                    logger.debug("后台检查：无新操作，跳过提交", {
                        'instance_name': self.instance_name,
                        'total_operations': self.stats['total_operations']
                    })
    
    def _submit_to_mysql(self):
        """同步提交统计数据到MySQL"""
        if not self.mysql_pool:
            return
            
        stats_data = self.get_stats()
        if not stats_data.get('enabled'):
            return
        
        db_name = self.config.get('db_name', 'redis_stats')
        table_name = self.config.get('table_name', 'cache_performance')
            
        try:
            connection = self.mysql_pool.connection()
            with connection.cursor() as cursor:
                # 选择数据库
                cursor.execute(f"USE `{db_name}`")
                
                # 插入统计数据
                insert_sql = f"""
                INSERT INTO `{table_name}` (
                    `日期`, `实例标识`, `主机名`, `进程ID`, `统计时间`,
                    `缓存命中`, `缓存未命中`, `缓存设置`, `缓存删除`, `缓存错误`, `总操作数`,
                    `命中率`, `平均响应时间`, `运行时间`, `命名空间统计`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                insert_data = (
                    datetime.now().strftime('%Y-%m-%d'),
                    f"{self.instance_name}_pid_{self.process_id}",
                    socket.gethostname(),
                    self.process_id,
                    datetime.now(),
                    stats_data['hits'],
                    stats_data['misses'],
                    stats_data['sets'],
                    stats_data['deletes'],
                    stats_data['errors'],
                    stats_data['total_operations'],
                    stats_data['hit_rate_percent'],
                    stats_data['avg_response_time_ms'],
                    stats_data['uptime_seconds'],
                    json.dumps(stats_data['namespace_stats'], ensure_ascii=False)
                )
                
                cursor.execute(insert_sql, insert_data)
                connection.commit()
                
            connection.close()
            
        except Exception as e:
            logger.error("MySQL提交失败", {
                'instance_name': self.instance_name,
                'database': db_name,
                'table': table_name,
                'error': str(e)
            })
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据"""
        if not self.enabled:
            return {'enabled': False, 'message': '统计功能已禁用'}
        
        with self._lock:
            uptime = time.time() - self.stats['start_time']
            total_cache_ops = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_cache_ops * 100) if total_cache_ops > 0 else 0
            avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
            
            return {
                'enabled': True,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'errors': self.stats['errors'],
                'total_operations': self.stats['total_operations'],
                'hit_rate_percent': round(hit_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'uptime_seconds': round(uptime, 2),
                'namespace_stats': dict(self.namespace_stats),
                'last_updated': datetime.now().isoformat(),
                'process_id': self.process_id
            }
    
    def shutdown(self):
        """关闭统计收集器，停止后台定时器"""
        logger.info("关闭统计收集器", {
            'instance_name': self.instance_name
        })
        
        # 设置关闭标志
        self._shutdown_event.set()
        
        # 取消定时器
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
    
    def reset_stats(self):
        """重置统计数据"""
        if not self.enabled:
            return
            
        with self._lock:
            self.stats = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'deletes': 0,
                'errors': 0,
                'total_operations': 0,
                'start_time': time.time()
            }
            self.response_times.clear()
            self.namespace_stats.clear()
            self.last_submit_time = time.time()
            self.last_operation_count = 0


class CacheSystemState(enum.Enum):
    """缓存系统状态枚举"""
    INITIALIZING = "initializing"
    READY = "ready"
    MYSQL_READY = "mysql_ready"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class CacheConfig:
    """缓存配置类"""
    def __init__(self, **kwargs):
        # 基础配置
        self.default_ttl = kwargs.get('default_ttl', 3600)  # 默认过期时间(秒)
        self.stats_submit_interval = kwargs.get('stats_submit_interval', 600)  # 每隔N秒定时提交一次（期间有新操作时）
        self.enable_stats = kwargs.get('enable_stats', True)  # 是否启用统计功能
        self.max_value_size = kwargs.get('max_value_size', 10 * 1024 * 1024)  # 最大值大小(字节)
        self.cache_prefix = kwargs.get('cache_prefix', 'cache')  # 缓存键前缀
        self.enable_compression = kwargs.get('enable_compression', True)
        
        # 数据库配置
        self.db_name = kwargs.get('db_name', 'redis_stats')
        self.table_name = kwargs.get('table_name', 'cache_performance')
        
        # 智能TTL策略配置
        self.enable_smart_ttl = kwargs.get('enable_smart_ttl', True)  # 启用智能TTL
        self.ttl_min = kwargs.get('ttl_min', 60)  # 最小TTL(秒)
        self.ttl_max = kwargs.get('ttl_max', 7200)  # 最大TTL(秒)
        self.debug_ttl = kwargs.get('debug_ttl', False)  # TTL调试模式
        
        # 自定义TTL模式
        self.custom_namespace_patterns = kwargs.get('custom_namespace_patterns', {})
        self.custom_key_patterns = kwargs.get('custom_key_patterns', {})


class SmartCacheSystem:
    """智能缓存系统 - 单线程"""
    
    def __init__(self, redis_client: redis.Redis, mysql_pool=None, instance_name: str = "default", **config):
        self.redis_client = redis_client
        self.mysql_pool = mysql_pool
        self.instance_name = instance_name
        self.config = CacheConfig(**config)
        
        # 系统状态管理
        self._state = CacheSystemState.INITIALIZING
        self._ready_event = Event()
        
        # 直接初始化统计系统
        self.stats_collector = None
        if self.config.enable_stats:
            self.stats_collector = CacheStatsCollector(
                enabled=True,
                mysql_pool=self.mysql_pool,
                config={
                    'instance_name': self.instance_name,
                    'submit_interval': self.config.stats_submit_interval,  # 每隔N秒定时提交一次（期间有新操作时）
                    'table_name': self.config.table_name,
                    'db_name': self.config.db_name
                }
            )
        
        # 初始化系统
        self._initialize()
    
    def _initialize(self):
        """初始化缓存系统"""
        # 测试Redis连接
        if self._test_redis_connection():
            self._state = CacheSystemState.READY
            self._ready_event.set()
            
            # 如果启用统计且有MySQL连接，创建统计表
            if self.config.enable_stats and self.mysql_pool:
                try:
                    self._create_simple_stats_table()
                    self._state = CacheSystemState.MYSQL_READY
                    logger.info("统计功能已启用", {
                        'instance_name': self.instance_name,
                        'process_id': os.getpid()
                    })
                except Exception as e:
                    logger.error("统计表创建失败", {
                        'instance_name': self.instance_name,
                        'error': str(e)
                    })
        else:
            self._state = CacheSystemState.ERROR
            logger.error("Redis连接失败", {'instance_name': self.instance_name})
    
    def _test_redis_connection(self) -> bool:
        """测试Redis连接"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error("Redis连接测试失败", {'error': str(e)})
            return False
    
    def _create_simple_stats_table(self):
        """创建统计表"""
        if not self.mysql_pool:
            return
        
        try:
            connection = self.mysql_pool.connection()
            with connection.cursor() as cursor:
                # 创建数据库
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.config.db_name}` DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")
                cursor.execute(f"USE `{self.config.db_name}`")
                
                # 创建统计表
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS `{self.config.table_name}` (
                    `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
                    `日期` date NOT NULL COMMENT '统计日期',
                    `实例标识` varchar(64) NOT NULL COMMENT '缓存实例标识',
                    `主机名` varchar(100) NOT NULL COMMENT '服务器主机名',
                    `进程ID` int NOT NULL COMMENT '进程ID',
                    `统计时间` timestamp NOT NULL COMMENT '统计时间',
                    
                    -- 基础操作统计
                    `缓存命中` bigint DEFAULT 0 COMMENT '缓存命中次数',
                    `缓存未命中` bigint DEFAULT 0 COMMENT '缓存未命中次数',
                    `缓存设置` bigint DEFAULT 0 COMMENT '缓存设置次数',
                    `缓存删除` bigint DEFAULT 0 COMMENT '缓存删除次数',
                    `缓存错误` bigint DEFAULT 0 COMMENT '缓存错误次数',
                    `总操作数` bigint DEFAULT 0 COMMENT '总操作次数',
                    
                    -- 性能指标
                    `命中率` decimal(5,2) DEFAULT 0.00 COMMENT '命中率百分比',
                    `平均响应时间` decimal(10,2) DEFAULT 0.00 COMMENT '平均响应时间(毫秒)',
                    `运行时间` bigint DEFAULT 0 COMMENT '运行时间(秒)',
                    
                    -- 命名空间统计
                    `命名空间统计` json COMMENT '命名空间统计详情',
                    
                    -- 时间戳
                    `创建时间` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                    
                    PRIMARY KEY (`id`),
                    KEY `idx_日期` (`日期`),
                    KEY `idx_实例时间` (`实例标识`, `统计时间`),
                    KEY `idx_创建时间` (`创建时间`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Redis缓存统计表'
                """
                
                cursor.execute(create_table_sql)
                connection.commit()
                
            connection.close()
            
        except Exception as e:
            logger.error("统计表初始化失败", {'error': str(e)})
            raise
    
    @property
    def is_ready(self) -> bool:
        """检查系统是否就绪"""
        return self._ready_event.is_set()
    
    @property
    def is_mysql_ready(self) -> bool:
        """检查MySQL是否就绪"""
        return self._state == CacheSystemState.MYSQL_READY
    
    def get(self, key: str, namespace: str = "", default=None) -> Any:
        """获取缓存值"""
        return self._get_with_stats(key, namespace, default)
    
    def _get_with_stats(self, key: str, namespace: str = "", default=None) -> Any:
        """带统计的获取缓存值"""
        if not self.is_ready:
            return default
        
        start_time = time.time()
        try:
            cache_key = self._generate_cache_key(key, namespace)
            value = self.redis_client.get(cache_key)
            response_time = (time.time() - start_time) * 1000
            
            if value is not None:
                # 缓存命中
                if self.stats_collector:
                    self.stats_collector.record_operation('hits', response_time, namespace)
                try:
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return value.decode('utf-8')
            else:
                # 缓存未命中
                if self.stats_collector:
                    self.stats_collector.record_operation('misses', response_time, namespace)
                return default
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            if self.stats_collector:
                self.stats_collector.record_operation('errors', response_time, namespace)
            logger.error("缓存获取失败", {
                'key': key,
                'namespace': namespace,
                'error': str(e)
            })
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "") -> bool:
        """设置缓存值"""
        return self._set_with_stats(key, value, ttl, namespace)
    
    def _set_with_stats(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "") -> bool:
        """带统计的设置缓存值"""
        if not self.is_ready:
            return False
        
        start_time = time.time()
        try:
            cache_key = self._generate_cache_key(key, namespace)
            
            # 智能TTL策略
            if ttl is None:
                ttl = self._get_smart_ttl(namespace, key, len(json.dumps(value, ensure_ascii=False, default=str)))
            
            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            else:
                serialized_value = str(value)
            
            # 检查值大小
            value_size = len(serialized_value.encode('utf-8'))
            if value_size > self.config.max_value_size:
                if self.stats_collector:
                    self.stats_collector.record_operation('errors', 0, namespace)
                logger.warning("缓存值过大，跳过设置", {
                    'key': key,
                    'size': len(serialized_value),
                    'max_size': self.config.max_value_size
                })
                return False
            
            result = self.redis_client.setex(cache_key, ttl, serialized_value)
            response_time = (time.time() - start_time) * 1000
            
            if self.stats_collector:
                self.stats_collector.record_operation('sets', response_time, namespace)
            return bool(result)
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            if self.stats_collector:
                self.stats_collector.record_operation('errors', response_time, namespace)
            logger.error("缓存设置失败", {
                'key': key,
                'namespace': namespace,
                'error': str(e)
            })
            return False
    
    def delete(self, key: str, namespace: str = "") -> bool:
        """删除缓存值"""
        return self._delete_with_stats(key, namespace)
    
    def _delete_with_stats(self, key: str, namespace: str = "") -> bool:
        """带统计的删除缓存值"""
        if not self.is_ready:
            return False
        
        start_time = time.time()
        try:
            cache_key = self._generate_cache_key(key, namespace)
            result = self.redis_client.delete(cache_key)
            response_time = (time.time() - start_time) * 1000
            if self.stats_collector:
                self.stats_collector.record_operation('deletes', response_time, namespace)
            return bool(result)
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            if self.stats_collector:
                self.stats_collector.record_operation('errors', response_time, namespace)
            logger.error("缓存删除失败", {
                'key': key,
                'namespace': namespace,
                'error': str(e)
            })
            return False
    
    def clear_namespace(self, namespace: str) -> int:
        """清除指定命名空间的所有缓存"""
        if not self.is_ready:
            return 0
        
        try:
            pattern = f"{self.config.cache_prefix}:{namespace}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                return deleted
            return 0
            
        except Exception as e:
            logger.error("清除命名空间失败", {
                'namespace': namespace,
                'error': str(e)
            })
            return 0
    
    def _generate_cache_key(self, key: str, namespace: str = "") -> str:
        """生成缓存键"""
        if namespace:
            return f"{self.config.cache_prefix}:{namespace}:{key}"
        return f"{self.config.cache_prefix}:{key}"
    
    def _get_smart_ttl(self, namespace: str, key: str = "", data_size: int = 0) -> int:
        """智能TTL策略 - 通用版本
        
        基于多种因素智能计算TTL：
        1. 命名空间模式匹配
        2. 数据类型推断
        3. 数据大小考虑
        4. 访问频率预测
        """
        
        # 如果禁用智能TTL，直接返回默认值
        if not self.config.enable_smart_ttl:
            return self.config.default_ttl
        
        # 1. 基于命名空间模式的智能匹配
        namespace_patterns = {
            # 数据库相关 - 变化频率低，TTL较长
            r'.*database.*|.*db.*|.*schema.*': 1800,  # 30分钟
            
            # 表结构相关 - 变化频率低，TTL较长  
            r'.*table.*|.*column.*|.*field.*': 1200,  # 20分钟
            
            # 数据查询相关 - 变化频率中等，TTL中等
            r'.*data.*|.*query.*|.*result.*': 600,    # 10分钟
            
            # 用户会话相关 - 变化频率高，TTL较短
            r'.*session.*|.*user.*|.*auth.*': 900,    # 15分钟
            
            # 配置相关 - 变化频率很低，TTL很长
            r'.*config.*|.*setting.*|.*param.*': 3600, # 1小时
            
            # 统计相关 - 变化频率中等，TTL中等
            r'.*stats.*|.*metric.*|.*count.*': 720,   # 12分钟
            
            # 缓存相关 - 变化频率高，TTL较短
            r'.*cache.*|.*temp.*|.*tmp.*': 180,       # 3分钟
            
            # 列表相关 - 变化频率中等，TTL中等
            r'.*list.*|.*index.*|.*catalog.*': 450,   # 7.5分钟
        }
        
        # 合并用户自定义模式（优先级更高）
        namespace_patterns.update(self.config.custom_namespace_patterns)
        
        # 2. 基于键名模式的智能匹配
        key_patterns = {
            # ID相关 - 相对稳定
            r'.*_id$|^id_.*': 1.2,  # TTL倍数
            
            # 详情相关 - 相对稳定
            r'.*detail.*|.*info.*': 1.1,
            
            # 列表相关 - 变化较频繁
            r'.*list.*|.*items.*': 0.8,
            
            # 计数相关 - 变化频繁
            r'.*count.*|.*num.*|.*total.*': 0.6,
            
            # 状态相关 - 变化很频繁
            r'.*status.*|.*state.*': 0.5,
        }
        
        # 合并用户自定义键模式
        key_patterns.update(self.config.custom_key_patterns)
        
        # 3. 基于数据大小的调整
        size_factor = 1.0
        if data_size > 0:
            if data_size > 100 * 1024 * 1024:  # > 100MB，延长TTL减少重建开销
                size_factor = 10.0
            elif data_size > 20 * 1024 * 1024:  # > 20MB，延长TTL减少重建开销
                size_factor = 8.0
            elif data_size > 10 * 1024 * 1024:  # > 10MB，延长TTL减少重建开销
                size_factor = 6.0
            elif data_size > 5 * 1024 * 1024:  # > 5MB，延长TTL减少重建开销
                size_factor = 4.0
            elif data_size > 1024 * 1024:  # > 1MB，延长TTL减少重建开销
                size_factor = 3.0
            elif data_size > 100 * 1024:  # > 100KB
                size_factor = 2.0
            elif data_size < 1024:  # < 1KB，缩短TTL减少内存占用
                size_factor = 1.0
        
        # 4. 计算基础TTL
        base_ttl = self.config.default_ttl
        
        # 匹配命名空间模式
        for pattern, ttl in namespace_patterns.items():
            if re.match(pattern, namespace.lower()):
                base_ttl = ttl
                break
        
        # 5. 应用键名模式调整
        key_factor = 1.0
        for pattern, factor in key_patterns.items():
            if re.match(pattern, key.lower()):
                key_factor = factor
                break
        
        # 6. 计算最终TTL
        final_ttl = int(base_ttl * key_factor * size_factor)
        
        # 7. TTL边界限制（使用配置值）
        final_ttl = max(self.config.ttl_min, min(self.config.ttl_max, final_ttl))
        
        # 8. 记录智能TTL决策（使用配置开关）
        if self.config.debug_ttl:
            logger.debug("智能TTL计算", {
                'namespace': namespace,
                'key': key[:50] + "..." if len(key) > 50 else key,
                'data_size': data_size,
                'base_ttl': base_ttl,
                'key_factor': key_factor,
                'size_factor': size_factor,
                'final_ttl': final_ttl
            })
        
        return final_ttl
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        # 确保统计系统已初始化
        if self.stats_collector:
            return self.stats_collector.get_stats()
        
        logger.debug("统计系统未初始化，返回空统计信息", {
            'instance_name': self.instance_name,
            'process_id': os.getpid()
        })
        return {
            'enabled': False,
            'message': '统计系统未初始化',
            'process_id': os.getpid()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # Redis连接检查
            redis_latency = time.time()
            self.redis_client.ping()
            redis_latency = (time.time() - redis_latency) * 1000
            
            # 获取Redis信息
            redis_info = self.redis_client.info()
            
            return {
                'status': 'healthy',
                'redis_connected': True,
                'redis_latency_ms': round(redis_latency, 2),
                'mysql_enabled': self.mysql_pool is not None,
                'mysql_ready': self.is_mysql_ready,
                'system_state': self._state.value,
                'uptime_seconds': time.time() - (self.stats_collector.stats['start_time'] if self.stats_collector else time.time()),
                'redis_memory_used': redis_info.get('used_memory', 0),
                'redis_connected_clients': redis_info.get('connected_clients', 0),
                'process_id': os.getpid()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'redis_connected': False,
                'system_state': self._state.value
            }
    
    def _record_operation(self, operation: str, response_time: float = 0, namespace: str = "", key: str = ""):
        """记录操作统计 """
        # 如果禁用统计功能，直接返回
        if not self.config.enable_stats:
            return
            
        logger.debug("调用操作记录", {
            'operation': operation,
            'response_time_ms': round(response_time, 2),
            'namespace': namespace,
            'key': key[:50] + "..." if len(key) > 50 else key,
            'instance_name': self.instance_name
        })
        
    def shutdown(self):
        """关闭缓存系统"""
        self._state = CacheSystemState.SHUTDOWN
        
        if self.stats_collector:
            # 关闭统计收集器（包括后台定时器）
            self.stats_collector.shutdown()
        
        logger.info("缓存系统已关闭", {'instance_name': self.instance_name})


class CacheManager:
    """缓存管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.cache_instance = None
            self._initialized = True
    
    def initialize(self, redis_client: redis.Redis, mysql_pool=None, instance_name: str = "default", **config):
        """初始化缓存系统"""
        if self.cache_instance is not None:
            logger.warning("缓存系统已初始化，跳过重复初始化", {
                'existing_instance': self.cache_instance.instance_name,
                'new_instance': instance_name
            })
            return
        
        self.cache_instance = SmartCacheSystem(
            redis_client=redis_client,
            mysql_pool=mysql_pool,
            instance_name=instance_name,
            **config
        )
    
    def get_cache(self) -> Optional[SmartCacheSystem]:
        """获取缓存实例"""
        return self.cache_instance
    
    def is_available(self) -> bool:
        """检查缓存是否可用"""
        return self.cache_instance is not None and self.cache_instance.is_ready
    
    def get_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        if self.cache_instance is None:
            return {
                'enabled': False,
                'available': False,
                'stats_enabled': False,
                'initialization_error': 'Cache not initialized'
            }
        
        return {
            'enabled': True,
            'available': self.cache_instance.is_ready,
            'mysql_ready': self.cache_instance.is_mysql_ready,
            'stats_enabled': self.cache_instance.config.enable_stats,
            'state': self.cache_instance._state.value,
            'instance_name': self.cache_instance.instance_name
        }


# 全局缓存管理器实例
cache_manager = CacheManager() 