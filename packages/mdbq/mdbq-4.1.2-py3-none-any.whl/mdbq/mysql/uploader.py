# -*- coding:utf-8 -*-
import datetime
import re
import time
from functools import wraps
import warnings
import pymysql
import pandas as pd
import os
from mdbq.log import mylogger
from mdbq.myconf import myconf
from typing import Union, List, Dict, Optional, Any, Tuple, Set
from dbutils.pooled_db import PooledDB
from decimal import Decimal, InvalidOperation
import math
import json

warnings.filterwarnings('ignore')
logger = mylogger.MyLogger(
    logging_mode='file',
    log_level='info',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=1,  # 采样DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段过滤
    enable_metrics=False,  # 是否启用性能指标
)


def count_decimal_places(num_str: str) -> Tuple[int, int]:
    """
    统计小数点前后位数，支持科学计数法。
    返回：(整数位数, 小数位数)
    """
    try:
        d = Decimal(str(num_str))
        sign, digits, exponent = d.as_tuple()
        int_part = len(digits) + exponent if exponent < 0 else len(digits)
        dec_part = -exponent if exponent < 0 else 0
        return max(int_part, 0), max(dec_part, 0)
    except (InvalidOperation, ValueError, TypeError):
        return (0, 0)


class StatementCache(dict):
    """LRU缓存实现，用于SQL语句缓存"""
    def __init__(self, maxsize=100):
        super().__init__()
        self._maxsize = maxsize
        self._order = []
    def __getitem__(self, key):
        value = super().__getitem__(key)
        self._order.remove(key)
        self._order.append(key)
        return value
    def __setitem__(self, key, value):
        if key in self:
            self._order.remove(key)
        elif len(self._order) >= self._maxsize:
            oldest = self._order.pop(0)
            super().__delitem__(oldest)
        super().__setitem__(key, value)
        self._order.append(key)
    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

class MySQLUploader:
    """
    MySQL数据上传
    
    用于将数据上传到MySQL数据库，支持自动建表、分表、数据验证等功能。
    使用连接池管理数据库连接。
    """
    def __init__(
            self,
            username: str,
            password: str,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
            collation: str = 'utf8mb4_0900_ai_ci',
            max_retries: int = 10,
            retry_waiting_time: int = 10,
            pool_size: int = 5,
            mincached: int = 0,
            maxcached: int = 0,
            connect_timeout: int = 10,
            read_timeout: int = 30,
            write_timeout: int = 30,
            ssl: Optional[Dict] = None
    ):
        """
        初始化MySQL上传器

        :param username: 数据库用户名
        :param password: 数据库密码
        :param host: 数据库主机地址，默认为localhost
        :param port: 数据库端口，默认为3306
        :param charset: 字符集，默认为utf8mb4
        :param collation: 排序规则，默认为utf8mb4_0900_ai_ci，对大小写不敏感，utf8mb4_0900_as_cs/utf8mb4_bin: 对大小写敏感
        :param max_retries: 最大重试次数，默认为10
        :param retry_waiting_time: 重试间隔(秒)，默认为10
        :param pool_size: 连接池大小，默认为5
        :param mincached: 空闲连接数量
        :param maxcached: 最大空闲连接数, 0表示不设上限, 由连接池自动管理
        :param connect_timeout: 连接超时(秒)，默认为10
        :param read_timeout: 读取超时(秒)，默认为30
        :param write_timeout: 写入超时(秒)，默认为30
        :param ssl: SSL配置字典，默认为None
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = int(port)
        self.charset = charset
        self.collation = collation
        self.max_retries = max(max_retries, 1)
        self.retry_waiting_time = max(retry_waiting_time, 1)
        self.pool_size = max(pool_size, 1)
        self.mincached = mincached
        self.maxcached = maxcached
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.base_excute_col = ['id', '更新时间']  # 排重插入数据时始终排除该列
        self.case_sensitive = False  # 是否保持大小写敏感，默认为False(转为小写)
        self.ssl = ssl
        self._prepared_statements = StatementCache(maxsize=100)
        self._max_cached_statements = 100  # 用于控制 StatementCache 类中缓存的 SQL 语句数量，最多缓存 100 条 SQL 语句
        self._table_metadata_cache = {}
        self.metadata_cache_ttl = 300  # 5分钟缓存时间
        self.pool = self._create_connection_pool()  # 创建连接池

    def _create_connection_pool(self) -> PooledDB:
        """
        创建数据库连接池

        :return: PooledDB连接池实例
        :raises ConnectionError: 当连接池创建失败时抛出
        """
        if hasattr(self, 'pool') and self.pool is not None and self._check_pool_health():
            return self.pool
        self.pool = None
        pool_params = {
            'creator': pymysql,
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'charset': self.charset,
            'cursorclass': pymysql.cursors.DictCursor,
            'maxconnections': self.pool_size,
            'mincached': self.mincached,
            'maxcached': self.maxcached,
            'ping': 7,
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
            'autocommit': False
        }
        if self.ssl:
            required_keys = {'ca', 'cert', 'key'}
            if not all(k in self.ssl for k in required_keys):
                error_msg = 'SSL配置必须包含ca、cert和key'
                logger.error(error_msg)
                raise ValueError(error_msg)
            pool_params['ssl'] = {
                'ca': self.ssl['ca'],
                'cert': self.ssl['cert'],
                'key': self.ssl['key'],
                'check_hostname': self.ssl.get('check_hostname', False)
            }
        try:
            pool = PooledDB(**pool_params)
            logger.debug('连接池创建成功', {'连接池': self.pool_size, 'host': self.host, 'port': self.port})
            return pool
        except Exception as e:
            self.pool = None
            logger.error('连接池创建失败', {'error': str(e), 'host': self.host, 'port': self.port})
            raise ConnectionError(f'连接池创建失败: {str(e)}')

    @staticmethod
    def _execute_with_retry(func):
        """
        带重试机制的装饰器，用于数据库操作
        :param func: 被装饰的函数
        :return: 装饰后的函数
        :raises: 可能抛出原始异常或最后一次重试的异常
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            operation = func.__name__
            for attempt in range(self.max_retries):
                try:
                    result = func(self, *args, **kwargs)
                    if attempt > 0:
                        logger.debug('操作成功(重试后)', {'operation': operation, 'attempts': attempt + 1})
                    return result
                except (pymysql.OperationalError, pymysql.err.MySQLError) as e:
                    last_exception = e
                    error_details = {
                        'operation': operation,
                        'error_code': e.args[0] if e.args else None,
                        'error_message': e.args[1] if len(e.args) > 1 else None,
                        'attempt': attempt + 1,
                        'max_retries': self.max_retries
                    }
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_waiting_time * (attempt + 1)
                        error_details['wait_time'] = wait_time
                        logger.warning('数据库操作失败，准备重试', error_details)
                        time.sleep(wait_time)
                        try:
                            self.pool = self._create_connection_pool()
                            logger.debug('成功重新建立数据库连接')
                        except Exception as reconnect_error:
                            logger.error('重连失败', {'error': str(reconnect_error)})
                    else:
                        logger.error('操作最终失败', error_details)
                except Exception as e:
                    last_exception = e
                    logger.error('发生意外错误', {
                        'operation': operation,
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'error_args': e.args if hasattr(e, 'args') else None
                    })
                    break
            raise last_exception if last_exception else Exception('发生未知错误')
        return wrapper

    @_execute_with_retry
    def _get_connection(self) -> pymysql.connections.Connection:
        """
        从连接池获取数据库连接

        :return: 数据库连接对象
        :raises ConnectionError: 当获取连接失败时抛出
        """
        try:
            conn = self.pool.connection()
            return conn
        except Exception as e:
            logger.error('从连接池获取数据库连接失败，尝试重建连接池', {'error': str(e)})
            # 强制重建连接池
            try:
                self.pool = self._create_connection_pool()
                conn = self.pool.connection()
                logger.debug('重建连接池后获取连接成功')
                return conn
            except Exception as e2:
                logger.error('重建连接池后依然获取连接失败', {'error': str(e2)})
                raise ConnectionError(f'连接数据库失败: {str(e2)}')

    @_execute_with_retry
    def _check_database_exists(self, db_name: str) -> bool:
        """
        检查数据库是否存在

        :param db_name: 数据库名称
        :return: 存在返回True，否则返回False
        :raises: 可能抛出数据库相关异常
        """
        db_name = self._validate_identifier(db_name, is_database=True)
        sql = 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s'
        conn = None
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name,))
                    exists = bool(cursor.fetchone())
                    logger.debug('数据库存在检查', {'库': db_name, '存在': exists})
                    return exists
        except Exception as e:
            logger.error('检查数据库是否存在时出错', {'库': db_name, '错误': str(e)})
            raise

    @_execute_with_retry
    def _create_database(self, db_name: str) -> None:
        """
        创建数据库

        :param db_name: 要创建的数据库名称
        :raises: 可能抛出数据库相关异常
        """
        db_name = self._validate_identifier(db_name, is_database=True)
        sql = f'CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET {self.charset} COLLATE {self.collation}'
        conn = None
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
                logger.debug('数据库已创建', {'库': db_name})
        except Exception as e:
            logger.error('无法创建数据库', {'库': db_name, '错误': str(e)})
            if conn is not None:
                conn.rollback()
            raise

    def _get_partition_table_name(self, table_name: str, date_value: str, partition_by: str) -> str:
        """
        获取分表名称

        :param table_name: 基础表名
        :param date_value: 日期值
        :param partition_by: 分表方式 ('year' 或 'month' 或 'none')
        :return: 分表名称
        :raises ValueError: 如果日期格式无效或分表方式无效
        """
        try:
            date_obj = self._validate_datetime(value=date_value, date_type=True, no_log=False)
        except ValueError:
            logger.error('无效的日期格式', {'表': table_name, '日期值': date_value})
            raise ValueError(f"`{table_name}` 无效的日期格式: `{date_value}`")
        if partition_by == 'year':
            return f"{table_name}_{date_obj.year}"
        elif partition_by == 'month':
            return f"{table_name}_{date_obj.year}_{date_obj.month:02d}"
        else:
            logger.error('分表方式无效', {'表': table_name, '分表方式': partition_by})
            raise ValueError("分表方式必须是 'year' 或 'month' 或 'None'")

    def _validate_identifier(self, identifier: str, is_database: bool = False) -> str:
        """
        验证并清理数据库标识符(表名、列名等)

        :param identifier: 要验证的标识符
        :param is_database: 是否为数据库名，数据库名不能以数字开头
        :return: 清理后的安全标识符
        :raises ValueError: 当标识符无效时抛出
        """
        if not identifier or not isinstance(identifier, str):
            logger.error('无效的标识符', {'标识符': identifier})
            raise ValueError(f"无效的标识符: `{identifier}`")
        # 始终做特殊字符清理
        cleaned = re.sub(r'[^\w\u4e00-\u9fff$]', '_', identifier)
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')
        # 如果清理后为空字符串，使用默认标识符
        if not cleaned:
            logger.warning('标识符清理后为空，使用默认标识符', {'原始标识符': identifier})
            # 使用原始标识符的哈希值作为后缀，保持可追溯性
            import hashlib
            hash_suffix = hashlib.md5(identifier.encode('utf-8')).hexdigest()[:8]
            cleaned = f'unknown_col_{hash_suffix}'
        
        # 数据库名不能以数字开头（MySQL要求），但表名和列名可以
        if is_database and cleaned and cleaned[0].isdigit():
            cleaned = f'db_{cleaned}'
            logger.warning('为数字开头的数据库名添加db_前缀', {
                '原始标识符': identifier,
                '清理后': cleaned
            })
        
        mysql_keywords = {
            'select', 'insert', 'update', 'delete', 'from', 'where', 'and', 'or',
            'not', 'like', 'in', 'is', 'null', 'true', 'false', 'between'
        }
        if len(cleaned) > 64:
            cleaned = cleaned[:64]
        if cleaned.lower() in mysql_keywords:
            logger.debug('存在MySQL保留字', {'标识符': cleaned})
            return f"`{cleaned}`"
        return cleaned

    @_execute_with_retry
    def _check_table_exists(self, db_name: str, table_name: str) -> bool:
        """
        检查表是否存在

        :param db_name: 数据库名
        :param table_name: 表名
        :return: 存在返回True，否则返回False
        :raises: 可能抛出数据库相关异常
        """
        cache_key = f"{db_name}.{table_name}"
        if cache_key in self._table_metadata_cache:
            cached_time, result = self._table_metadata_cache[cache_key]
            if time.time() - cached_time < self.metadata_cache_ttl:
                logger.debug('表存在缓存命中', {'库': db_name, '表': table_name, '存在': result})
                return result
        db_name = self._validate_identifier(db_name, is_database=True)
        table_name = self._validate_identifier(table_name)
        sql = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    result = bool(cursor.fetchone())
        except Exception as e:
            logger.error('检查数据表是否存在时发生未知错误', {'库': db_name, '表': table_name, '错误': str(e)})
            raise
        self._table_metadata_cache[cache_key] = (time.time(), result)
        logger.debug('表存在检查', {'库': db_name, '表': table_name, '存在': result})
        return result

    @_execute_with_retry
    def _create_table(
            self,
            db_name: str,
            table_name: str,
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            date_column: Optional[str] = None,
            indexes: Optional[List[str]] = None,
            allow_null: bool = False,
            unique_keys: Optional[List[List[str]]] = None
    ) -> None:
        """
        创建数据表，优化索引创建方式
        """
        db_name = self._validate_identifier(db_name, is_database=True)
        table_name = self._validate_identifier(table_name)
        if not set_typ:
            logger.error('建表时未指定set_typ', {'库': db_name, '表': table_name})
            raise ValueError('set_typ 未指定')
        # set_typ的键清洗
        set_typ = {self._normalize_col(k): v for k, v in set_typ.items()}
        
        # 处理id列和主键
        column_defs = []
        
        # 添加id列（仅在没有指定主键时）
        if not primary_keys:
            column_defs.append("`id` INT NOT NULL AUTO_INCREMENT")
        
        # 添加其他列
        for col_name, col_type in set_typ.items():
            if col_name == 'id':
                continue
            safe_col_name = self._normalize_col(col_name)
            col_def = f"`{safe_col_name}` {col_type}"
            if not allow_null and not col_type.lower().startswith('json'):
                col_def += " NOT NULL"
            column_defs.append(col_def)
            
        # 主键处理逻辑调整
        def _index_col_sql(col):
            col_type = set_typ.get(col, '').lower()
            if 'varchar' in col_type:
                m = re.search(r'varchar\((\d+)\)', col_type)
                if m:
                    maxlen = int(m.group(1))
                    prefix_len = min(100, maxlen)
                    return f"`{self._normalize_col(col)}`({prefix_len})"
                else:
                    return f"`{self._normalize_col(col)}`(100)"
            elif 'text' in col_type:
                return f"`{self._normalize_col(col)}`(100)"
            else:
                return f"`{self._normalize_col(col)}`"
            
        # 处理主键
        if primary_keys and len(primary_keys) > 0:
            # 验证主键列是否存在于set_typ中
            valid_primary_keys = []
            for pk in primary_keys:
                normalized_pk = self._normalize_col(pk)
                if normalized_pk in set_typ:
                    valid_primary_keys.append(pk)
                else:
                    logger.warning('主键列不存在于表结构中，跳过', {
                        '库': db_name,
                        '表': table_name,
                        '列': pk,
                        '规范化后': normalized_pk,
                        '可用列': list(set_typ.keys())
                    })
            
            if valid_primary_keys:
                # 如果指定了主键，直接使用指定的主键
                safe_primary_keys = [_index_col_sql(pk) for pk in valid_primary_keys]
                primary_key_sql = f"PRIMARY KEY ({','.join(safe_primary_keys)})"
            else:
                # 如果没有有效的主键，使用id作为主键
                logger.warning('所有主键列都不存在于表结构中，使用默认id主键', {
                    '库': db_name,
                    '表': table_name,
                    '原始主键': primary_keys
                })
                primary_key_sql = f"PRIMARY KEY (`id`)"
        else:
            # 如果没有指定主键，使用id作为主键
            primary_key_sql = f"PRIMARY KEY (`id`)"
            
        # 索引统一在CREATE TABLE中定义
        index_defs = []
        if date_column and date_column in set_typ:
            safe_date_col = _index_col_sql(date_column)
            index_defs.append(f"INDEX `idx_{self._normalize_col(date_column)}` ({safe_date_col})")
        
        # 收集所有唯一约束中涉及的列，避免重复创建普通索引
        unique_columns = set()
        if unique_keys:
            for unique_cols in unique_keys:
                if unique_cols:
                    for col in unique_cols:
                        normalized_col = self._normalize_col(col)
                        if normalized_col in set_typ:
                            unique_columns.add(normalized_col)
        
        if indexes:
            for idx_col in indexes:
                normalized_idx_col = self._normalize_col(idx_col)
                if normalized_idx_col in set_typ:
                    # 检查是否与唯一约束冲突
                    if normalized_idx_col in unique_columns:
                        logger.warning('索引列已在唯一约束中定义，跳过普通索引', {
                            '库': db_name,
                            '表': table_name,
                            '列': idx_col,
                            '原因': '列已在唯一约束中定义'
                        })
                        continue
                    safe_idx_col = _index_col_sql(idx_col)
                    index_defs.append(f"INDEX `idx_{normalized_idx_col}` ({safe_idx_col})")
                else:
                    logger.warning('索引列不存在于表结构中，跳过', {
                        '库': db_name,
                        '表': table_name,
                        '列': idx_col,
                        '规范化后': normalized_idx_col,
                        '可用列': list(set_typ.keys())
                    })
                    
        # UNIQUE KEY定义
        unique_defs = []
        if unique_keys:
            for unique_cols in unique_keys:
                if not unique_cols:
                    continue
                # 检查唯一约束是否与主键冲突
                if primary_keys:
                    # 如果唯一约束的列是主键的一部分，则跳过
                    if set(unique_cols).issubset(set(primary_keys)):
                        logger.warning('跳过与主键冲突的唯一约束', {
                            '库': db_name, 
                            '表': table_name, 
                            '唯一约束': unique_cols, 
                            '主键': primary_keys
                        })
                        continue
                
                # 验证唯一约束的列是否存在于set_typ中
                valid_unique_cols = []
                for col in unique_cols:
                    normalized_col = self._normalize_col(col)
                    if normalized_col in set_typ:
                        valid_unique_cols.append(col)
                    else:
                        logger.warning('唯一约束列不存在于表结构中，跳过', {
                            '库': db_name,
                            '表': table_name,
                            '列': col,
                            '规范化后': normalized_col,
                            '可用列': list(set_typ.keys())
                        })
                
                if not valid_unique_cols:
                    logger.warning('唯一约束的所有列都不存在于表结构中，跳过整个约束', {
                        '库': db_name,
                        '表': table_name,
                        '原始约束': unique_cols
                    })
                    continue
                
                safe_unique_cols = [_index_col_sql(col) for col in valid_unique_cols]
                unique_name = f"uniq_{'_'.join([self._normalize_col(c) for c in valid_unique_cols])}"
                unique_defs.append(f"UNIQUE KEY `{unique_name}` ({','.join(safe_unique_cols)})")
                
        index_defs = list(set(index_defs))
        all_defs = column_defs + [primary_key_sql] + index_defs + unique_defs
        
        # 添加调试日志
        logger.debug('建表SQL生成', {
            '库': db_name,
            '表': table_name,
            '列定义': column_defs,
            '主键': primary_key_sql,
            '索引': index_defs,
            '唯一约束': unique_defs,
            'set_typ键': list(set_typ.keys())
        })
        
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{db_name}`.`{table_name}` (
            {','.join(all_defs)}
        ) ENGINE=InnoDB DEFAULT CHARSET={self.charset} COLLATE={self.collation}
        """
        conn = None
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
                logger.debug('数据表及索引已创建', {'库': db_name, '表': table_name, '索引': indexes, '唯一约束': unique_keys})
        except Exception as e:
            logger.error('建表失败', {'库': db_name, '表': table_name, '错误': str(e), '异常类型': type(e).__name__})
            if conn is not None:
                conn.rollback()
            raise

    def _validate_datetime(self, value: str, date_type: bool = False, no_log: bool = False) -> Any:
        """
        验证并标准化日期时间格式

        :param value: 日期时间值
        :param date_type: 是否返回日期类型(True)或字符串(False)
        :param no_log: 记录日志，默认为False
        :return: 标准化后的日期时间字符串或日期对象
        :raises ValueError: 当日期格式无效时抛出
        """
        # 处理 pandas Timestamp 对象
        if hasattr(value, 'strftime'):
            # 如果是 Timestamp 或 datetime 对象，直接格式化
            if date_type:
                return pd.to_datetime(value.strftime('%Y-%m-%d'))
            else:
                return value.strftime('%Y-%m-%d %H:%M:%S')
        
        # 确保 value 是字符串
        if not isinstance(value, str):
            value = str(value)
            
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%-m/%-d',  # 2023/1/8
            '%Y-%-m-%-d',  # 2023-01-8
        ]
        for fmt in formats:
            try:
                if date_type:
                    result = pd.to_datetime(datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d'))
                    return result
                else:
                    result = datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d %H:%M:%S')
                    return result
            except ValueError:
                continue
        if not no_log:
            logger.error('无效的日期格式', {'值': value})
        raise ValueError(f"无效的日期格式: `{value}`")

    def _convert_to_int(self, value):
        """
        尝试将value转换为int
        """
        # 处理numpy/pandas标量
        if hasattr(value, 'item') and callable(getattr(value, 'item', None)):
            try:
                value = value.item()
            except Exception:
                pass
        elif hasattr(value, 'value') and not isinstance(value, str):
            try:
                extracted_value = value.value
                if isinstance(extracted_value, (int, float, str)) and str(extracted_value).replace('.', '').replace('-', '').isdigit():
                    value = extracted_value
            except Exception:
                pass
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                raise

    def _convert_to_float(self, value):
        """
        尝试将value转换为float，兼容常见数值类型。
        """
        if hasattr(value, 'item') and callable(getattr(value, 'item', None)):
            try:
                value = value.item()
            except Exception:
                pass
        elif hasattr(value, 'value') and not isinstance(value, str):
            try:
                extracted_value = value.value
                if isinstance(extracted_value, (int, float, str)) and str(extracted_value).replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                    value = extracted_value
            except Exception:
                pass
        return float(value)

    def _convert_to_decimal(self, value):
        """
        尝试将value转换为Decimal，兼容常见数值类型。
        """
        if hasattr(value, 'item') and callable(getattr(value, 'item', None)):
            try:
                value = value.item()
            except Exception:
                pass
        elif hasattr(value, 'value') and not isinstance(value, str):
            try:
                extracted_value = value.value
                if isinstance(extracted_value, (int, float, str)) and str(extracted_value).replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                    value = extracted_value
            except Exception:
                pass
        return Decimal(str(value))

    def _truncate_str(self, str_value, max_len):
        """
        截断字符串到指定字节长度（utf-8）。
        """
        return str_value.encode('utf-8')[:max_len].decode('utf-8', 'ignore')

    def _validate_value(self, value: Any, column_type: str, allow_null: bool, db_name: str = None, table_name: str = None, col_name: str = None) -> Any:
        """
        根据列类型验证并转换数据值
        """
        column_type_lower = column_type.lower() if column_type else ''
        
        # JSON类型验证和转换（优先处理，避免pd.isna的问题）
        if 'json' in column_type_lower:
            if isinstance(value, (dict, list)):
                try:
                    return json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError) as e:
                    logger.error(f"JSON序列化失败: {e}", {"库": db_name, "表": table_name, "列": col_name, "值": value})
                    raise ValueError(f"JSON序列化失败: {e}")
            elif isinstance(value, str):
                # 验证字符串是否为有效的JSON
                try:
                    json.loads(value)
                    return value
                except (TypeError, ValueError) as e:
                    logger.error(f"无效的JSON字符串: {e}", {"库": db_name, "表": table_name, "列": col_name, "值": value})
                    raise ValueError(f"无效的JSON字符串: {e}")
            else:
                # 其他类型转换为字符串
                return str(value)
        
        # 统一判断None/NaN（排除列表和字典类型）
        if value == '':
            if any(t in column_type_lower for t in ['varchar', 'text', 'char', 'mediumtext', 'longtext']):
                return ""
        
        # 安全地检查NaN值，避免对列表和字典使用pd.isna
        is_nan = False
        if isinstance(value, (list, dict)):
            is_nan = False  # 列表和字典不是NaN
        else:
            try:
                is_nan = pd.isna(value) or (isinstance(value, (float, Decimal)) and math.isinf(value))
            except (ValueError, TypeError):
                is_nan = False
        
        if value == '' or is_nan:
            # 兜底填充值映射
            fallback_map = {
                'int': 0,
                'bigint': 0,
                'tinyint': 0,
                'smallint': 0,
                'mediumint': 0,
                'decimal': 0.0,
                'float': 0.0,
                'double': 0.0,
                'date': '1970-01-01',
                'datetime': '1970-01-01 00:00:00',
                'timestamp': '1970-01-01 00:00:00',
                'json': '{}',
                'varchar': 'none',
                'text': 'none',
                'char': 'none',
                'mediumtext': 'none',
                'longtext': 'none',
            }
            fallback = 'none'
            for typ, val in fallback_map.items():
                if typ in column_type_lower:
                    fallback = val
                    break
            if not allow_null:
                logger.warning("该列不允许为空值", {"库": db_name, "表": table_name, "allow_null": allow_null, "列": col_name, "值": value, "兜底值": fallback})
                raise ValueError("该列不允许为空值")
            return fallback

        original_value = value

        # 日期时间类型验证
        if 'datetime' in column_type_lower or 'timestamp' in column_type_lower:
            return self._validate_datetime(value, date_type=False, no_log=True)
        elif 'date' in column_type_lower:
            return self._validate_datetime(value, date_type=True, no_log=True)
        # 数值类型验证
        elif 'int' in column_type_lower:
            try:
                return self._convert_to_int(value)
            except (ValueError, TypeError):
                logger.error(f"值 `{value}` 无法转换为整数", {"库": db_name, "表": table_name, "列": col_name})
                raise ValueError(f"值 `{value}` 无法转换为整数")
        elif any(t in column_type_lower for t in ['decimal', 'float', 'double']):
            # 百分比字符串处理
            if isinstance(value, str) and '%' in value:
                try:
                    if re.match(r'^-?\d+(\.\d+)?%$', value.strip()):
                        value = float(value.strip().replace('%', '')) / 100
                    else:
                        logger.warning("百分比字符串不符合格式，跳过转换", {"库": db_name, "表": table_name, "列": col_name, "原始": original_value})
                        value = original_value
                except (ValueError, TypeError):
                    logger.warning("百分比字符串转换失败，保留原始值", {"库": db_name, "表": table_name, "列": col_name, "原始": original_value})
                    value = original_value
            try:
                if 'decimal' in column_type_lower:
                    precision, scale = self._get_decimal_scale(column_type)
                    value_decimal = self._convert_to_decimal(value)
                    if len(value_decimal.as_tuple().digits) - abs(value_decimal.as_tuple().exponent) > precision - scale:
                        raise ValueError(f"整数部分超出范围")
                    return value_decimal
                else:  # float/double
                    return self._convert_to_float(value)
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.error(f"值 `{value}` 无法转换为数值类型: {e}", {"库": db_name, "表": table_name, "列": col_name})
                raise ValueError(f"值 `{value}` 无法转换为数值类型: {e}")
        # 字符串类型验证
        elif 'varchar' in column_type_lower:
            str_value = str(value)
            try:
                max_len = int(re.search(r'\((\d+)\)', column_type).group(1))
                if len(str_value.encode('utf-8')) > max_len:
                    logger.warning(f"列`{col_name}`的值`{str_value}`长度({len(str_value.encode('utf-8'))})超出varchar({max_len})限制，将进行截断", {"库": db_name, "表": table_name})
                    return self._truncate_str(str_value, max_len)
            except (AttributeError, IndexError):
                pass
            return str_value
        
        # 兜底处理：确保所有返回值都是基本数据类型
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(value)
        else:
            return str(value)

    @_execute_with_retry
    def _get_table_columns(self, db_name: str, table_name: str) -> Dict[str, str]:
        """
        获取表的列名和数据类型

        :param db_name: 数据库名
        :param table_name: 表名
        :return: 列名和数据类型字典 {列名: 数据类型}
        :raises: 可能抛出数据库相关异常
        """
        db_name = self._validate_identifier(db_name, is_database=True)
        table_name = self._validate_identifier(table_name)
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    if self.case_sensitive:
                        set_typ = {row['COLUMN_NAME']: row['DATA_TYPE'] for row in cursor.fetchall()}
                    else:
                        set_typ = {row['COLUMN_NAME'].lower(): row['DATA_TYPE'] for row in cursor.fetchall()}
                    logger.debug('获取表的列信息', {'库': db_name, '表': table_name, '列信息': set_typ})
                    return set_typ
        except Exception as e:
            logger.error('无法获取表列信息', {'库': db_name, '表': table_name, '错误': str(e)})
            raise

    def _ensure_index(self, db_name: str, table_name: str, column: str):
        """
        确保某列有索引，如果没有则创建。
        """
        db_name = self._validate_identifier(db_name, is_database=True)
        table_name = self._validate_identifier(table_name)
        column = self._validate_identifier(column)
        # 检查索引是否已存在
        sql_check = '''
            SELECT COUNT(1) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        '''
        sql_create = f'ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{column}` (`{column}`)'
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_check, (db_name, table_name, column))
                    exists = cursor.fetchone()
                    if exists and list(exists.values())[0] > 0:
                        logger.debug('索引检查', {'库': db_name, '表': table_name, '索引列': column})
                        return
                    cursor.execute(sql_create)
                conn.commit()
                logger.debug('已为列创建索引', {'库': db_name, '表': table_name, '列': column})
        except Exception as e:
            logger.error('创建索引失败', {'库': db_name, '表': table_name, '列': column, '错误': str(e)})
            raise

    def _get_existing_unique_keys(self, db_name: str, table_name: str) -> List[List[str]]:
        """
        获取表中所有UNIQUE KEY的列组合（不含主键）。
        返回：[[col1, col2], ...]
        """
        db_name = self._validate_identifier(db_name, is_database=True)
        table_name = self._validate_identifier(table_name)
        sql = '''
            SELECT INDEX_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND NON_UNIQUE = 0 AND INDEX_NAME != 'PRIMARY'
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
        '''
        unique_map = {}
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    for row in cursor.fetchall():
                        idx = row['INDEX_NAME']
                        col = row['COLUMN_NAME']
                        unique_map.setdefault(idx, []).append(col)
        except Exception as e:
            logger.warning('获取UNIQUE KEY信息失败', {'库': db_name, '表': table_name, '错误': str(e)})
        # 只返回列名组合，全部清洗小写
        return [[self._normalize_col(c) for c in cols] for cols in unique_map.values() if cols]

    def _add_unique_key(self, db_name: str, table_name: str, unique_cols: List[str]):
        """
        添加UNIQUE KEY
        """
        safe_cols = [self._normalize_col(col) for col in unique_cols]
        unique_name = f"uniq_{'_'.join(safe_cols)}"
        sql = f'ALTER TABLE `{db_name}`.`{table_name}` ADD UNIQUE KEY `{unique_name}` ({','.join(f'`{col}`' for col in safe_cols)})'
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
            logger.debug('添加唯一约束列成功', {'库': db_name, '表': table_name, '列': unique_cols})
        except Exception as e:
            logger.warning('唯一约束列添加失败', {'库': db_name, '表': table_name, '列': unique_cols, '错误': str(e)})

    def _upload_to_table(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]],
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            allow_null: bool,
            auto_create: bool,
            date_column: Optional[str],
            indexes: Optional[List[str]],
            batch_id: Optional[str] = None,
            update_on_duplicate: bool = False,
            transaction_mode: str = "batch",
            unique_keys: Optional[List[List[str]]] = None
    ):
        """实际执行表上传的方法"""
        table_existed = self._check_table_exists(db_name, table_name)
        if not table_existed:
            if auto_create:
                self._create_table(db_name, table_name, set_typ, primary_keys, date_column, indexes,
                                   allow_null=allow_null, unique_keys=unique_keys)
            else:
                logger.error('数据表不存在', {
                    '库': db_name,
                    '表': table_name,
                })
                raise ValueError(f"数据表不存在: `{db_name}`.`{table_name}`")
        if table_existed and unique_keys:
            try:
                exist_ukeys = self._get_existing_unique_keys(db_name, table_name)
                exist_ukeys_norm = [sorted([c.lower() for c in uk]) for uk in exist_ukeys]
                filtered_ukeys = [uk for uk in unique_keys if 1 <= len(uk) <= 20]
                to_add = []
                for uk in filtered_ukeys:
                    norm_uk = sorted([c.lower() for c in uk])
                    if norm_uk not in exist_ukeys_norm:
                        to_add.append(uk)
                max_unique_keys = 10
                if len(exist_ukeys) + len(to_add) > max_unique_keys:
                    logger.warning('unique_keys超限', {
                        '库': db_name,
                        '表': table_name,
                        '已存在': exist_ukeys,
                        '本次待添加': to_add,
                        '最大数量': max_unique_keys
                    })
                    to_add = to_add[:max_unique_keys - len(exist_ukeys)]
                for uk in to_add:
                    self._add_unique_key(db_name, table_name, uk)
            except Exception as e:
                logger.warning('动态unique key处理异常', {'库': db_name, '表': table_name, '错误': str(e)})
        table_columns = self._get_table_columns(db_name, table_name)
        if not table_columns:
            logger.error('获取列失败', {
                '库': db_name,
                '表': table_name,
                '列': self._shorten_for_log(table_columns),
            })
            raise ValueError(f"获取列失败 `{db_name}`.`{table_name}`")
        for col in set_typ:
            if col not in table_columns:
                logger.error('列不存在', {
                    '库': db_name,
                    '表': table_name,
                    '列': col,
                })
                raise ValueError(f"列不存在: `{col}` -> `{db_name}`.`{table_name}`")
        if date_column and date_column in table_columns:
            try:
                self._ensure_index(db_name, table_name, date_column)
            except Exception as e:
                logger.warning('分表参考字段索引创建失败', {'库': db_name, '表': table_name, '列': date_column, '错误': str(e)})
        inserted, skipped, failed = self._insert_data(
            db_name, table_name, data, set_typ,
            check_duplicate, duplicate_columns,
            batch_id=batch_id,
            update_on_duplicate=update_on_duplicate,
            transaction_mode=transaction_mode
        )
        return inserted, skipped, failed

    def _infer_data_type(self, value: Any, no_log: bool = False) -> str:
        """
        根据值推断合适的MySQL数据类型

        :param value: 要推断的值
        :param no_log: 记录日志，默认为False
        :return: MySQL数据类型字符串
        """
        if value is None or str(value).lower() in ['', 'none', 'nan']:
            return 'VARCHAR(255)'  # 默认字符串类型

        # 检查是否是百分比字符串
        if isinstance(value, str):
            if '%' in value:
                if re.match(r'^-?\d+(\.\d+)?%$', value.strip()):
                    return 'DECIMAL(10, 4)'  # 百分比转为小数，使用DECIMAL
                else:
                    return 'VARCHAR(255)' # 不符合格式的百分比，视为字符串

        if isinstance(value, bool):
            return 'TINYINT(1)'
        elif isinstance(value, int):
            # if -128 <= value <= 127:
            #     return 'TINYINT'
            # elif -32768 <= value <= 32767:
            #     return 'SMALLINT'
            # elif -8388608 <= value <= 8388607:
            #     return 'MEDIUMINT'
            if -2147483648 <= value <= 2147483647:
                return 'INT'
            else:
                return 'BIGINT'
        elif isinstance(value, float):
            # 计算小数位数
            num_str = str(value)
            _, decimal_places = count_decimal_places(num_str)
            return f'DECIMAL(20,{min(decimal_places, 6)})'  # 限制最大6位小数
        elif isinstance(value, (datetime.datetime, pd.Timestamp)):
            return 'DATETIME'
        elif isinstance(value, datetime.date):
            return 'DATE'
        elif isinstance(value, (list, dict)):
            return 'JSON'
        elif isinstance(value, str):
            # 尝试判断是否是日期时间
            try:
                self._validate_datetime(value=value, date_type=False, no_log=no_log)
                return 'DATETIME'
            except ValueError:
                pass

            # 根据字符串长度选择合适类型
            length = len(value)
            if length <= 255:
                return 'VARCHAR(255)'
            elif length <= 65535:
                return 'TEXT'
            elif length <= 16777215:
                return 'MEDIUMTEXT'
            else:
                return 'LONGTEXT'
            
        return 'VARCHAR(255)' # 默认字符串类型

    def normalize_column_names(self, data: Union[pd.DataFrame, List[Dict[str, Any]]]) -> Union[
        pd.DataFrame, List[Dict[str, Any]]]:
        """
        1. pandas：规范化列名
        2. 字典列表：规范化每个字典的键
        """
        if isinstance(data, pd.DataFrame):
            if self.case_sensitive:
                data.columns = [self._validate_identifier(col) for col in data.columns]
            else:
                data.columns = [self._validate_identifier(col).lower() for col in data.columns]
            return data
        elif isinstance(data, list):
            if self.case_sensitive:
                return [{self._validate_identifier(k): v for k, v in item.items()} for item in data]
            else:
                return [{self._validate_identifier(k).lower(): v for k, v in item.items()} for item in data]
        return data

    def _prepare_data(
            self,
            data: Union[Dict, List[Dict], pd.DataFrame],
            set_typ: Dict[str, str],
            allow_null: bool = False,
            db_name: str = None, 
            table_name: str = None, 
    ) -> Tuple[List[Dict], Dict[str, str]]:
        """
        准备要上传的数据，验证并转换数据类型
        """
        # 统一数据格式为字典列表
        if isinstance(data, pd.DataFrame):
            try:
                if self.case_sensitive:
                    data.columns = [col for col in data.columns]
                else:
                    data.columns = [col.lower() for col in data.columns]
                data = data.replace({pd.NA: None}).to_dict('records')
            except Exception as e:
                logger.error('数据转字典时发生错误', {
                    'error': str(e),
                    'data': self._shorten_for_log(data),
                })
                raise ValueError(f"数据转字典时发生错误: {e}")
        elif isinstance(data, dict):
            if self.case_sensitive:
                data = [{k: v for k, v in data.items()}]
            else:
                data = [{k.lower(): v for k, v in data.items()}]
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            if self.case_sensitive:
                data = [{k: v for k, v in item.items()} for item in data]
            else:
                data = [{k.lower(): v for k, v in item.items()} for item in data]
        else:
            logger.error('数据结构必须是字典、列表、字典列表或dataframe', {
                'data': self._shorten_for_log(data),
            })
            raise ValueError("数据结构必须是字典、列表、字典列表或dataframe")

        # 统一处理原始数据中列名的特殊字符
        data = self.normalize_column_names(data)

        if not set_typ:
            logger.warning('set_typ为空, 将自动推断数据类型, 可能存在数据类型识别错误')
        # set_typ的键清洗
        if not set_typ:
            set_typ = {}
        set_typ = {self._normalize_col(k): v for k, v in set_typ.items()}

        # 新实现：严格按set_typ顺序过滤，后补充data中有但set_typ没有的列
        filtered_set_typ = {}
        data_columns = list(data[0].keys()) if data and len(data) > 0 else []
        # 先按set_typ顺序
        for col in set_typ:
            if col in data_columns:
                filtered_set_typ[col] = set_typ[col]
        # 再补充data中有但set_typ没有的列
        for col in data_columns:
            if col not in filtered_set_typ:
                # 推断类型
                sample_values = [row[col] for row in data if col in row and row[col] is not None][:5]
                inferred_type = None
                for val in sample_values:
                    inferred_type = self._infer_data_type(val, no_log=True)
                    if inferred_type:
                        break
                if not inferred_type:
                    inferred_type = 'VARCHAR(255)'
                filtered_set_typ[col] = inferred_type
                logger.debug(f"自动推断列 `{col}` 的数据类型为: `{inferred_type}`")

        prepared_data = []
        for row_idx, row in enumerate(data, 1):
            prepared_row = {}
            for col_name in filtered_set_typ:
                # 跳过id列，不允许外部传入id
                if (self.case_sensitive and col_name == 'id') or (not self.case_sensitive and col_name.lower() == 'id'):
                    continue
                if col_name not in row:
                    if not allow_null:
                        error_msg = f"行号:{row_idx} -> 缺失列: `{col_name}`"
                        logger.error(error_msg, {'row': self._shorten_for_log(row)})
                        raise ValueError(error_msg)
                    prepared_row[col_name] = None
                else:
                    try:
                        prepared_row[col_name] = self._validate_value(row[col_name], filtered_set_typ[col_name], allow_null, db_name, table_name, col_name)
                    except ValueError as e:
                        logger.error('数据验证失败', {
                            '列': col_name,
                            '行': row_idx,
                            '报错': str(e),
                            'row': self._shorten_for_log(row),
                        })
                        raise ValueError(f"行:{row_idx}, 列:`{col_name}`-> 报错: {str(e)}")
            prepared_data.append(prepared_row)
        return prepared_data, filtered_set_typ

    def upload_data(
            self,
            db_name: str,
            table_name: str,
            data: Union[Dict, List[Dict], pd.DataFrame],
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            allow_null: bool = False,
            partition_by: Optional[str] = None,
            partition_date_column: str = '日期',
            auto_create: bool = True,
            indexes: Optional[List[str]] = None,
            update_on_duplicate: bool = False,
            transaction_mode: str = "batch",
            unique_keys: Optional[List[List[str]]] = None
    ):
        """
        上传数据到数据库的主入口方法

        :param db_name: 数据库名
        :param table_name: 表名
        :param data: 要上传的数据，支持字典、字典列表或DataFrame格式
        :param set_typ: 列名和数据类型字典 {列名: 数据类型}
        :param primary_keys: 主键列列表，可选。格式：['col1', 'col2'] 或 None
        :param check_duplicate: 是否检查重复数据，默认为False
        :param duplicate_columns: 用于检查重复的列，可选。格式：['col1', 'col2'] 或 None
        :param allow_null: 是否允许空值，默认为False
        :param partition_by: 分表方式('year'、'month'、'None')，可选
        :param partition_date_column: 用于分表的日期列名，默认为'日期', 默认会添加为索引
        :param auto_create: 表不存在时是否自动创建，默认为True
        :param indexes: 需要创建索引的列列表，可选。格式：['col1', 'col2'] 或 None
        :param update_on_duplicate: 遇到重复数据时是否更新旧数据，默认为False
        :param transaction_mode: 事务模式，可选值：
            - 'row'     : 逐行提交事务（错误隔离性好）
            - 'batch'   : 整批提交事务（性能最优）
            - 'hybrid'  : 混合模式（每N行提交，平衡性能与安全性）
        :param unique_keys: 唯一约束列表，每个元素为列名列表，支持多列组合唯一约束。格式：[['col1', 'col2'], ['col3']] 或 None
        :raises: 可能抛出各种验证和数据库相关异常

        ---
        参数格式验证：

        - primary_keys: 必须是字符串列表或None，如 ['col1', 'col2']
        - indexes: 必须是字符串列表或None，如 ['col1', 'col2']
        - unique_keys: 必须是嵌套列表或None，如 [['col1', 'col2'], ['col3']]
        - 错误示例：unique_keys=['col1', 'col2'] (应该是 [['col1', 'col2']])
        - 所有列名不能为空字符串，会自动去除首尾空格
        - 重复的列名会被自动去重

        空值处理规则：
        - None: 直接返回None，忽略此参数
        - []: 空列表，返回None，忽略此参数
        - [[]]: 包含空列表，跳过空列表，如果最终为空则返回None
        - ['']: 包含空字符串，抛出异常（不允许空字符串）
        - ['   ']: 包含纯空白字符，抛出异常（不允许纯空白字符）
        - ['', 'col1']: 混合空字符串和有效字符串，跳过空字符串，保留有效字符串

        ---
        关于 indexes 和 unique_keys 参数：

        - indexes 创建普通索引，unique_keys 创建唯一约束
        - 如果同一列同时出现在 indexes 和 unique_keys 中，系统会优先创建唯一约束，跳过普通索引
        - 唯一约束本身就具有索引功能，因此不会重复创建普通索引
        - 建议：如果某列需要唯一性约束，直接使用 unique_keys 参数，无需在 indexes 中重复指定

        ---
        unique_keys、check_duplicate、update_on_duplicate 三者组合下的行为总结：

        | unique_keys | check_duplicate | update_on_duplicate | 行为                         |
        |-------------|----------------|---------------------|------------------------------|
        | 有/无       | False          | False               | 冲突时报错/跳过，不覆盖      |
        | 有/无       | False          | True                | 冲突时覆盖（ON DUPLICATE KEY）|
        | 有/无       | True           | False               | 主动查重，冲突时跳过，不覆盖 |
        | 有/无       | True           | True                | 主动查重，冲突时覆盖         |

        - unique_keys 只决定唯一性，不决定是否覆盖。
        - check_duplicate=True 时，插入前主动查重，重复数据跳过或覆盖，取决于 update_on_duplicate。
        - update_on_duplicate=True 时，遇到唯一约束冲突会用新数据覆盖旧数据。
        - 只要 update_on_duplicate=True 且表存在唯一约束（如 unique_keys），无论 check_duplicate 是否为 True，都会更新旧数据（即 ON DUPLICATE KEY UPDATE 生效）。
        - 如需"覆盖"行为，务必设置 update_on_duplicate=True，不管 check_duplicate 是否为 True。
        - 如需"跳过"行为，设置 update_on_duplicate=False 即可。
        """
        # upload_start = time.time()
        # 检查data参数是否为None
        if data is None:
            logger.error('data参数不能为None', {
                '库': db_name,
                '表': table_name,
            })
            raise ValueError("data参数不能为None，请传入有效的数据")
            
        if isinstance(data, list) or (hasattr(data, 'shape') and hasattr(data, '__len__')):
            initial_row_count = len(data)
        else:
            initial_row_count = 1

        batch_id = f"batch_{int(time.time() * 1000)}"
        success_flag = False
        dropped_rows = 0
        total_inserted = 0
        total_skipped = 0
        total_failed = 0
        validated_primary_keys = None
        validated_indexes = None
        validated_unique_keys = None
        prepared_data = None
        filtered_set_typ = None
        inserted = None
        skipped = None
        failed = None

        try:
            # 验证参数格式
            validated_primary_keys = self._validate_primary_keys_format(primary_keys, db_name, table_name)
            validated_indexes = self._validate_indexes_format(indexes, db_name, table_name)
            validated_unique_keys = self._validate_unique_keys_format(unique_keys, db_name, table_name)
            
            logger.debug("开始上传", {
                '库': db_name,
                '表': table_name,
                '批次': batch_id,
                '传入': len(data) if hasattr(data, '__len__') else 1,
                '参数': {
                    '主键': validated_primary_keys,
                    '去重': check_duplicate,
                    '去重列': duplicate_columns,
                    '允许空值': allow_null,
                    '分表方式': partition_by,
                    '分表列': partition_date_column,
                    # '自动建表': auto_create,
                    '索引': validated_indexes,
                    '更新旧数据': update_on_duplicate,
                    '事务模式': transaction_mode,
                    '唯一约束': validated_unique_keys
                },
                # '数据样例': self._shorten_for_log(data, 2)
            })
            
            # 验证分表参数
            if partition_by:
                partition_by = str(partition_by).lower()
                if partition_by not in ['year', 'month']:
                    logger.error('分表方式必须是 "year" 或 "month" 或 "None', {
                        '库': db_name,
                        '表': table_name,
                        '批次': batch_id,
                        '分表方式': partition_by,
                    })
                    raise ValueError("分表方式必须是 'year' 或 'month' 或 'None'")

            # 准备数据
            prepared_data, filtered_set_typ = self._prepare_data(data, set_typ, allow_null, db_name, table_name)

            # 检查数据库是否存在
            if not self._check_database_exists(db_name):
                if auto_create:
                    self._create_database(db_name)
                else:
                    logger.error('数据库不存在', {
                        '库': db_name,
                    })
                    raise ValueError(f"数据库不存在: `{db_name}`")

            # 处理分表逻辑
            if partition_by:
                partitioned_data = {}
                for row in prepared_data:
                    try:
                        if partition_date_column not in row:
                            logger.error('异常缺失列',{
                                '库': db_name,
                                '表': table_name,
                                '批次': batch_id,
                                '缺失列': partition_date_column,
                                'row': self._shorten_for_log(row),
                            })
                            dropped_rows += 1
                            continue
                        part_table = self._get_partition_table_name(
                            table_name,
                            str(row[partition_date_column]),
                            partition_by
                        )
                        if part_table not in partitioned_data:
                            partitioned_data[part_table] = []
                        partitioned_data[part_table].append(row)
                    except Exception as e:
                        logger.error('分表处理异常', {
                            '库': db_name,
                            '表': table_name,
                            'row_data': self._shorten_for_log(row),
                            'error': str(e),
                        })
                        dropped_rows += 1
                        continue

                # 对每个分表执行上传
                total_inserted = 0
                total_skipped = dropped_rows  # 分表异常丢弃
                total_failed = 0
                for part_table, part_data in partitioned_data.items():
                    try:
                        inserted, skipped, failed = self._upload_to_table(
                            db_name, part_table, part_data, filtered_set_typ,
                            validated_primary_keys, check_duplicate, duplicate_columns,
                            allow_null, auto_create, partition_date_column,
                            validated_indexes, batch_id, update_on_duplicate, transaction_mode,
                            validated_unique_keys
                        )
                        total_inserted += inserted
                        total_skipped += skipped
                        total_failed += failed
                        if partition_date_column in filtered_set_typ:
                            try:
                                self._ensure_index(db_name, part_table, partition_date_column)
                            except Exception as e:
                                logger.warning('分表参考字段索引创建失败', {'库': db_name, '表': part_table, '列': partition_date_column, '错误': str(e)})
                    except Exception as e:
                        logger.error('分表上传异常', {
                            '库': db_name,
                            '表': table_name,
                            '分表': part_table,
                            'error': str(e),
                            '数据样例': self._shorten_for_log(part_data, 2),
                        })
                        continue  # 跳过当前分表，继续处理其他分表
            else:
                # 不分表，直接上传
                inserted, skipped, failed = self._upload_to_table(
                    db_name, table_name, prepared_data, filtered_set_typ,
                    validated_primary_keys, check_duplicate, duplicate_columns,
                    allow_null, auto_create, partition_date_column,
                    validated_indexes, batch_id, update_on_duplicate, transaction_mode,
                    validated_unique_keys
                )
                total_inserted = inserted
                total_skipped = skipped
                total_failed = failed
                if partition_date_column in filtered_set_typ:
                    try:
                        self._ensure_index(db_name, table_name, partition_date_column)
                    except Exception as e:
                        logger.warning('分表参考字段索引创建失败', {'库': db_name, '表': table_name, '列': partition_date_column, '错误': str(e)})

            success_flag = True

        except Exception as e:
            logger.error('上传过程发生全局错误', {
                '库': db_name,
                '表': table_name,
                'error': str(e),
                'error_type': type(e).__name__,
                '数据样例': self._shorten_for_log(data, 2),
            })
            return False
        finally:
            logger.info("存储完成", {
                '库': db_name,
                '表': table_name,
                '批次': batch_id,
                'finish': success_flag,
                '数据行': initial_row_count,
                '插入': total_inserted,
                '跳过': total_skipped,
                '失败': total_failed
            })

        # 更新索引（只有在成功时才执行）
        if success_flag and validated_indexes:
            try:
                self._update_indexes(db_name, table_name, validated_indexes)
            except Exception as e:
                logger.warning('更新索引时发生错误', {
                    '库': db_name,
                    '表': table_name,
                    '错误': str(e)
                })
        return True

    @_execute_with_retry
    def _insert_data(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            batch_id: Optional[str] = None,
            update_on_duplicate: bool = False,
            transaction_mode: str = "batch"
    ):
        """
        实际执行数据插入的方法

        :param db_name: 数据库名
        :param table_name: 表名
        :param data: 要插入的数据列表
        :param set_typ: 列名和数据类型字典 {列名: 数据类型}
        :param check_duplicate: 是否检查重复数据
        :param duplicate_columns: 用于检查重复的列，可选
        :param batch_id: 批次ID用于日志追踪，可选
        :param update_on_duplicate: 遇到重复数据时是否更新旧数据，默认为False
        :param transaction_mode: 事务模式，可选值：
            - 'row'     : 逐行提交事务（错误隔离性好）
            - 'batch'   : 整批提交事务（性能最优）
            - 'hybrid'  : 混合模式（每N行提交，平衡性能与安全性）
        """
        if not data:
            return 0, 0, 0
        transaction_mode = self._validate_transaction_mode(transaction_mode)
        sql = self._prepare_insert_sql(
            db_name, table_name, set_typ,
            check_duplicate, duplicate_columns,
            update_on_duplicate
        )
        total_inserted, total_skipped, total_failed = self._execute_batch_insert(
            db_name, table_name, data, set_typ,
            sql, check_duplicate, duplicate_columns,
            batch_id, transaction_mode,
            update_on_duplicate
        )
        logger.debug('插入完成', {
            '库': db_name,
            '表': table_name,
            '总计': len(data),
            '插入': total_inserted,
            '跳过': total_skipped,
            '失败': total_failed,
            '事务模式': transaction_mode,
        })
        return total_inserted, total_skipped, total_failed

    def _validate_transaction_mode(self, mode: str) -> str:
        """验证并标准化事务模式"""
        valid_modes = ('row', 'batch', 'hybrid')
        if mode.lower() not in valid_modes:
            logger.error('事务模式参数错误', {
                '错误值': mode,
                '可选值': valid_modes,
                '自动使用默认模式': 'batch',
            })
            return 'batch'
        return mode.lower()

    def _build_simple_insert_sql(self, db_name, table_name, columns, update_on_duplicate):
        safe_columns = [self._validate_identifier(col) for col in columns]
        placeholders = ','.join(['%s'] * len(safe_columns))

        sql = f"""
            INSERT INTO `{db_name}`.`{table_name}` 
            (`{'`,`'.join(safe_columns)}`) 
            VALUES ({placeholders})
        """

        # 情况2：不检查重复但允许更新
        if update_on_duplicate:
            update_clause = ", ".join([f"`{col}` = VALUES(`{col}`)"
                                     for col in columns])
            sql += f" ON DUPLICATE KEY UPDATE {update_clause}"

        return sql

    def _build_duplicate_check_sql(self, db_name, table_name, all_columns,
                                   duplicate_columns, update_on_duplicate, set_typ):
        if duplicate_columns is None:
            duplicate_columns = []
        duplicate_columns = [_item for _item in duplicate_columns if _item.lower() not in self.base_excute_col]
        safe_columns = [self._validate_identifier(col) for col in all_columns]
        placeholders = ','.join(['%s'] * len(safe_columns))

        # 确定排重列（排除id和更新时间列）
        dup_cols = duplicate_columns if duplicate_columns else all_columns

        # 构建排重条件
        conditions = []
        for col in dup_cols:
            col_type = set_typ.get(col, '').lower()
            if col_type.startswith('decimal'):
                _, scale = self._get_decimal_scale(col_type)
                conditions.append(f"ROUND(`{col}`, {scale}) = ROUND(%s, {scale})")
            else:
                conditions.append(f"`{col}` = %s")

        # 情况3/5：允许更新
        if update_on_duplicate:
            update_clause = ", ".join([f"`{col}` = VALUES(`{col}`)"
                                       for col in all_columns])
            sql = f"""
                INSERT INTO `{db_name}`.`{table_name}` 
                (`{'`,`'.join(safe_columns)}`) 
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_clause}
            """
        else:
            # 情况4/6：不允许更新
            sql = f"""
                INSERT INTO `{db_name}`.`{table_name}` 
                (`{'`,`'.join(safe_columns)}`) 
                SELECT {placeholders}
                FROM DUAL
                WHERE NOT EXISTS (
                    SELECT 1 FROM `{db_name}`.`{table_name}`
                    WHERE {' AND '.join(conditions)}
                )
            """
        return sql

    def _get_decimal_scale(self, decimal_type: str) -> Tuple[int, int]:
        """从DECIMAL类型字符串中提取精度和标度"""
        match = re.search(r'\((\d+)\s*,\s*(\d+)\)', decimal_type)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 18, 2  # 默认值

    def _prepare_insert_sql(
            self,
            db_name: str,
            table_name: str,
            set_typ: Dict[str, str],
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            update_on_duplicate: bool
    ) -> str:
        """
        准备插入SQL语句, 增加StatementCache缓存
        """
        cache_key = (db_name, table_name, tuple(sorted(set_typ.items())), check_duplicate, tuple(duplicate_columns) if duplicate_columns else (), update_on_duplicate)
        cached = self._prepared_statements.get(cache_key)
        if cached:
            return cached
        # 获取所有列名（排除id）
        all_columns = [col for col in set_typ.keys() if col.lower() != 'id']
        if not check_duplicate:
            sql = self._build_simple_insert_sql(db_name, table_name, all_columns,
                                                 update_on_duplicate)
        else:
            dup_cols = duplicate_columns if duplicate_columns else [
                col for col in all_columns
                if col.lower() not in self.base_excute_col
            ]
            sql = self._build_duplicate_check_sql(db_name, table_name, all_columns,
                                               dup_cols, update_on_duplicate, set_typ)
        self._prepared_statements[cache_key] = sql
        return sql

    def _execute_batch_insert(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            sql: str,
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            batch_id: Optional[str],
            transaction_mode: str,
            update_on_duplicate: bool = False
    ) -> Tuple[int, int, int]:
        """
        执行批量插入操作，优化batch和hybrid模式。

        - batch模式下，使用executemany批量插入（如SQL带ON DUPLICATE KEY UPDATE时），MySQL会对每一行单独判断唯一约束：
            - 不冲突的行会被正常插入。
            - 冲突的行会触发ON DUPLICATE KEY UPDATE，用新数据更新旧数据。
            - 不会因为一行冲突导致整批失败或回滚。
        - 只有遇到严重的数据库错误（如所有行都因唯一约束冲突且没有ON DUPLICATE KEY UPDATE），才会整体回滚。
        - 返回值为(插入行数, 跳过行数, 失败行数)。
        """
        def get_optimal_batch_size(total_rows: int) -> int:
            if total_rows <= 100:
                return total_rows
            elif total_rows <= 1000:
                return 500
            elif total_rows <= 10000:
                return 1000
            else:
                return 2000
        
        def ensure_basic_type(value):
            """确保值是基本数据类型，如果是字典或列表则转换为字符串"""
            if isinstance(value, (dict, list)):
                try:
                    return json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    return str(value)
            return value
        
        batch_size = get_optimal_batch_size(len(data))
        all_columns = [col for col in set_typ.keys() if col.lower() != 'id']
        total_inserted = 0
        total_skipped = 0
        total_failed = 0
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                if transaction_mode == 'batch':
                    for i in range(0, len(data), batch_size):
                        batch = data[i:i + batch_size]
                        values_list = []
                        for row in batch:
                            values = [ensure_basic_type(row.get(col)) for col in all_columns]
                            if check_duplicate and not update_on_duplicate:
                                dup_cols = duplicate_columns if duplicate_columns else [col for col in all_columns if col.lower() not in self.base_excute_col]
                                values += [ensure_basic_type(row.get(col)) for col in dup_cols]
                            values_list.append(values)
                        try:
                            cursor.executemany(sql, values_list)
                            conn.commit()
                            # 在batch模式下，affected_rows表示实际影响的行数
                            # 如果update_on_duplicate为True，则affected_rows包含更新的行数
                            # 如果update_on_duplicate为False，则affected_rows只包含插入的行数
                            affected = cursor.rowcount if cursor.rowcount is not None else 0
                            if update_on_duplicate:
                                # 当启用更新时，affected_rows包含插入和更新的行数
                                # 我们需要区分插入和更新的行数
                                # 由于无法准确区分，我们假设所有行都是插入的
                                total_inserted += len(batch)
                            else:
                                # 当不启用更新时，affected_rows只包含插入的行数
                                total_inserted += affected
                                total_skipped += len(batch) - affected
                        except pymysql.err.IntegrityError as e:
                            conn.rollback()
                            # 在唯一约束冲突时，所有行都被跳过
                            total_skipped += len(batch)
                            logger.debug('批量插入唯一约束冲突，全部跳过', {'库': db_name, '表': table_name, '错误': str(e)})
                        except Exception as e:
                            conn.rollback()
                            total_failed += len(batch)
                            logger.error('批量插入失败', {'库': db_name, '表': table_name, '错误': str(e)})
                elif transaction_mode == 'hybrid':
                    hybrid_n = 100  # 可配置
                    for i in range(0, len(data), hybrid_n):
                        batch = data[i:i + hybrid_n]
                        for row in batch:
                            try:
                                values = [ensure_basic_type(row.get(col)) for col in all_columns]
                                if check_duplicate and not update_on_duplicate:
                                    dup_cols = duplicate_columns if duplicate_columns else [col for col in all_columns if col.lower() not in self.base_excute_col]
                                    values += [ensure_basic_type(row.get(col)) for col in dup_cols]
                                cursor.execute(sql, values)
                                affected = cursor.rowcount if cursor.rowcount is not None else 0
                                if update_on_duplicate:
                                    # 当启用更新时，affected_rows包含插入和更新的行数
                                    # 假设所有行都是插入的，因为无法区分插入和更新
                                    total_inserted += 1
                                else:
                                    # 当不启用更新时，affected_rows只包含插入的行数
                                    if affected > 0:
                                        total_inserted += 1
                                    else:
                                        total_skipped += 1
                            except pymysql.err.IntegrityError as e:
                                conn.rollback()
                                total_skipped += 1
                                logger.debug('hybrid单行插入唯一约束冲突，跳过', {'库': db_name, '表': table_name, '错误': str(e)})
                            except Exception as e:
                                conn.rollback()
                                total_failed += 1
                                logger.error('hybrid单行插入失败', {'库': db_name, '表': table_name, '错误': str(e)})
                        conn.commit()
                else:  # row模式
                    for row in data:
                        try:
                            values = [ensure_basic_type(row.get(col)) for col in all_columns]
                            if check_duplicate and not update_on_duplicate:
                                dup_cols = duplicate_columns if duplicate_columns else [col for col in all_columns if col.lower() not in self.base_excute_col]
                                values += [ensure_basic_type(row.get(col)) for col in dup_cols]
                            cursor.execute(sql, values)
                            affected = cursor.rowcount if cursor.rowcount is not None else 0
                            if update_on_duplicate:
                                # 当启用更新时，affected_rows包含插入和更新的行数
                                # 假设所有行都是插入的，因为无法区分插入和更新
                                total_inserted += 1
                            else:
                                # 当不启用更新时，affected_rows只包含插入的行数
                                if affected > 0:
                                    total_inserted += 1
                                else:
                                    total_skipped += 1
                            conn.commit()
                        except pymysql.err.IntegrityError as e:
                            conn.rollback()
                            total_skipped += 1
                            logger.debug('单行插入唯一约束冲突，跳过', {'库': db_name, '表': table_name, '错误': str(e)})
                        except Exception as e:
                            conn.rollback()
                            total_failed += 1
                            logger.error('单行插入失败', {'库': db_name, '表': table_name, '错误': str(e)})
        return total_inserted, total_skipped, total_failed

    def _check_pool_health(self) -> bool:
        """
        检查连接池健康状态，防止连接泄露
        """
        conn = None
        try:
            if not hasattr(self, 'pool') or self.pool is None:
                return False
            conn = self.pool.connection()
            conn.ping(reconnect=True)
            logger.debug('连接池健康检查通过')
            return True
        except Exception as e:
            logger.warning('连接池健康检查失败', {'error': str(e)})
            return False
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning('关闭连接时出错', {'error': str(e)})

    @staticmethod
    def retry_on_failure(max_retries: int = 3, delay: int = 1):
        """
        通用重试装饰器
        :param max_retries: 最大重试次数
        :param delay: 重试间隔（秒）
        :return: 装饰器
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                        last_exception = e
                        logger.warning('操作失败，准备重试', {'attempt': attempt + 1, 'error': str(e)})
                        if attempt < max_retries - 1:
                            time.sleep(delay * (attempt + 1))
                            continue
                        logger.error(f'操作重试 {max_retries} 次后失败', {'error': str(e)})
                        raise
                    except Exception as e:
                        logger.error('操作失败', {'error': str(e)})
                        raise
                raise last_exception if last_exception else logger.error('操作重试失败，未知错误')
            return wrapper
        return decorator

    def _shorten_for_log(self, obj: Any, maxlen: int = 200) -> Any:
        """
        日志安全截断工具：对字符串、列表、字典等做长度限制，避免日志过长。
        :param obj: 原始对象
        :param maxlen: 最大长度/元素数
        :return: 截断后的对象
        """
        if isinstance(obj, str):
            return obj[:maxlen] + ("..." if len(obj) > maxlen else "")
        elif isinstance(obj, list):
            return obj[:maxlen] + (["..."] if len(obj) > maxlen else [])
        elif isinstance(obj, dict):
            short = {k: self._shorten_for_log(v, maxlen) for i, (k, v) in enumerate(obj.items()) if i < maxlen}
            if len(obj) > maxlen:
                short['...'] = f"total_keys={len(obj)}"
            return short
        elif hasattr(obj, 'shape') and hasattr(obj, 'head'):
            # pandas DataFrame
            return f"DataFrame shape={obj.shape}, head={obj.head(1).to_dict()}"
        return obj

    def _normalize_col(self, col: str) -> str:
        """
        列名自动清洗并转小写（如case_sensitive为False），保证和表结构一致。
        """
        safe = self._validate_identifier(col)
        return safe if self.case_sensitive else safe.lower()

    def _update_indexes(self, db_name: str, table_name: str, indexes: Optional[List[str]]):
        """
        更新索引，避免重复添加或更新，同时注意大小写一致性。
        注意：如果列已经在unique_keys中定义，则不会重复创建普通索引。

        :param db_name: 数据库名
        :param table_name: 表名
        :param indexes: 需要更新的索引列列表
        """
        if not indexes:
            return

        # 规范化索引列名
        normalized_indexes = [self._normalize_col(idx) for idx in indexes]

        # 获取现有索引（包括普通索引和唯一约束）
        try:
            existing_indexes = self._get_existing_indexes(db_name, table_name)
        except Exception as e:
            logger.error('获取现有索引时发生错误', {'库': db_name, '表': table_name, '错误': str(e)})
            raise

        # 获取表中现有的列名
        try:
            existing_columns = self._get_table_columns(db_name, table_name)
        except Exception as e:
            logger.error('获取现有列时发生错误', {'库': db_name, '表': table_name, '错误': str(e)})
            raise

        # 找出需要添加的索引（排除已存在的索引和不在表中的列）
        indexes_to_add = []
        for idx in normalized_indexes:
            if idx not in existing_indexes and idx in existing_columns:
                indexes_to_add.append(idx)
            elif idx in existing_indexes:
                logger.debug('索引已存在，跳过', {'库': db_name, '表': table_name, '列': idx})
            elif idx not in existing_columns:
                logger.warning('索引列不存在于表中，跳过', {'库': db_name, '表': table_name, '列': idx})

        # 添加新索引
        for idx in indexes_to_add:
            try:
                self._add_index(db_name, table_name, idx)
            except Exception as e:
                logger.error('添加索引时发生错误', {'库': db_name, '表': table_name, '列': idx, '错误': str(e)})
                raise

    def _get_existing_indexes(self, db_name: str, table_name: str) -> Set[str]:
        """
        获取表中现有的索引列名（包括普通索引和唯一约束）。

        :param db_name: 数据库名
        :param table_name: 表名
        :return: 现有索引列名的集合
        """
        sql = """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        existing_indexes = set()
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    existing_indexes = {row['COLUMN_NAME'] for row in cursor.fetchall()}
        except Exception as e:
            logger.error('获取现有索引失败', {'库': db_name, '表': table_name, '错误': str(e)})
            raise
        return existing_indexes

    def _add_index(self, db_name: str, table_name: str, column: str):
        """
        添加索引到指定列。

        :param db_name: 数据库名
        :param table_name: 表名
        :param column: 需要添加索引的列名
        """
        sql = f'ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{column}` (`{column}`)'
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
            conn.commit()
            logger.debug('已为列创建索引', {'库': db_name, '表': table_name, '列': column})
        except Exception as e:
            logger.error('创建索引失败', {'库': db_name, '表': table_name, '列': column, '错误': str(e)})
            raise
    
    def __enter__(self):
        return self

    def close(self) -> None:
        """
        关闭连接池并清理资源
        这个方法会安全地关闭数据库连接池，并清理相关资源。
        建议结束时手动调用此方法。
        :raises: 可能抛出关闭连接时的异常
        """
        try:
            if hasattr(self, 'pool') and self.pool is not None:
                try:
                    self.pool = None
                except Exception as e:
                    logger.warning('关闭连接池时出错', {'error': str(e)})
                logger.debug('finished', {'uploader.py': '连接池关闭'})
        except Exception as e:
            logger.error('关闭连接池失败', {'uploader.py': str(e)})
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # @_execute_with_retry
    def execute_query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict]:
        """
        执行查询SQL语句并返回结果
        
        :param sql: SQL查询语句
        :param params: SQL参数，可选
        :return: 查询结果列表，每个元素为字典格式
        :raises: 可能抛出数据库相关异常
        """
        if not sql or not isinstance(sql, str):
            logger.error('无效的SQL语句', {'sql': sql})
            raise ValueError('SQL语句不能为空且必须是字符串')
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    logger.debug('查询执行成功', {
                        'sql': self._shorten_for_log(sql, 100),
                        'params': self._shorten_for_log(params, 50),
                        '结果数量': len(results)
                    })
                    return results
        except Exception as e:
            logger.error('执行查询时出错', {
                'sql': self._shorten_for_log(sql, 100),
                'params': self._shorten_for_log(params, 50),
                'error': str(e)
            })
            raise

    # @_execute_with_retry
    def execute_update(self, sql: str, params: Optional[Tuple] = None) -> int:
        """
        执行更新SQL语句（INSERT、UPDATE、DELETE）并返回影响的行数
        
        :param sql: SQL更新语句
        :param params: SQL参数，可选
        :return: 影响的行数
        :raises: 可能抛出数据库相关异常
        """
        if not sql or not isinstance(sql, str):
            logger.error('无效的SQL语句', {'sql': sql})
            raise ValueError('SQL语句不能为空且必须是字符串')
        
        conn = None
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    affected_rows = cursor.execute(sql, params)
                    conn.commit()
                    logger.debug('更新执行成功', {
                        'sql': self._shorten_for_log(sql, 100),
                        'params': self._shorten_for_log(params, 50),
                        '影响行数': affected_rows
                    })
                    return affected_rows
        except Exception as e:
            logger.error('执行更新时出错', {
                'sql': self._shorten_for_log(sql, 100),
                'params': self._shorten_for_log(params, 50),
                'error': str(e)
            })
            if conn is not None:
                conn.rollback()
            raise

    def _validate_unique_keys_format(self, unique_keys: Optional[List[List[str]]], db_name: str = None, table_name: str = None) -> Optional[List[List[str]]]:
        """
        验证unique_keys参数的格式是否正确
        
        :param unique_keys: 唯一约束列表
        :param db_name: 数据库名，用于日志记录
        :param table_name: 表名，用于日志记录
        :return: 验证后的unique_keys，如果验证失败则抛出异常
        :raises ValueError: 当参数格式不正确时抛出
        """
        if unique_keys is None:
            return None
            
        if not isinstance(unique_keys, list):
            error_msg = f"unique_keys参数必须是列表类型，当前类型: {type(unique_keys).__name__}"
            logger.error(error_msg, {'库': db_name, '表': table_name, 'unique_keys': unique_keys})
            raise ValueError(error_msg)
        
        # 检查是否为空列表
        if len(unique_keys) == 0:
            logger.debug('unique_keys为空列表，将忽略此参数', {'库': db_name, '表': table_name})
            return None
        
        validated_keys = []
        empty_groups_count = 0
        
        for i, key_group in enumerate(unique_keys):
            # 检查每个元素是否为列表
            if not isinstance(key_group, list):
                error_msg = f"unique_keys[{i}]必须是列表类型，当前类型: {type(key_group).__name__}，值: {key_group}"
                logger.error(error_msg, {'库': db_name, '表': table_name, 'unique_keys': unique_keys})
                raise ValueError(error_msg)
            
            # 检查是否为空列表
            if len(key_group) == 0:
                empty_groups_count += 1
                logger.warning(f'unique_keys[{i}]为空列表，跳过', {'库': db_name, '表': table_name})
                continue
            
            # 检查每个列名是否为字符串
            validated_group = []
            for j, col_name in enumerate(key_group):
                if not isinstance(col_name, str):
                    error_msg = f"unique_keys[{i}][{j}]必须是字符串类型，当前类型: {type(col_name).__name__}，值: {col_name}"
                    logger.error(error_msg, {'库': db_name, '表': table_name, 'unique_keys': unique_keys})
                    raise ValueError(error_msg)
                
                # 检查是否为空字符串或纯空白字符
                stripped_name = col_name.strip()
                if not stripped_name:
                    error_msg = f"unique_keys[{i}][{j}]不能为空字符串或纯空白字符，原始值: '{col_name}'"
                    logger.error(error_msg, {'库': db_name, '表': table_name, 'unique_keys': unique_keys})
                    raise ValueError(error_msg)
                
                validated_group.append(stripped_name)
            
            # 去重并检查是否有重复列名
            if len(validated_group) != len(set(validated_group)):
                error_msg = f"unique_keys[{i}]中存在重复列名: {validated_group}"
                logger.error(error_msg, {'库': db_name, '表': table_name, 'unique_keys': unique_keys})
                raise ValueError(error_msg)
            
            validated_keys.append(validated_group)
        
        # 检查验证后的结果
        if not validated_keys:
            if empty_groups_count > 0:
                logger.warning(f'unique_keys包含{empty_groups_count}个空列表，验证后为空，将忽略此参数', {
                    '库': db_name, '表': table_name, '空列表数量': empty_groups_count
                })
            else:
                logger.warning('unique_keys验证后为空，将忽略此参数', {'库': db_name, '表': table_name})
            return None
        
        logger.debug('unique_keys格式验证通过', {
            '库': db_name, 
            '表': table_name, 
            '原始': unique_keys, 
            '验证后': validated_keys,
            '跳过的空列表': empty_groups_count
        })
        return validated_keys

    def _validate_indexes_format(self, indexes: Optional[List[str]], db_name: str = None, table_name: str = None) -> Optional[List[str]]:
        """
        验证indexes参数的格式是否正确
        
        :param indexes: 索引列列表
        :param db_name: 数据库名，用于日志记录
        :param table_name: 表名，用于日志记录
        :return: 验证后的indexes，如果验证失败则抛出异常
        :raises ValueError: 当参数格式不正确时抛出
        """
        if indexes is None:
            return None
            
        if not isinstance(indexes, list):
            error_msg = f"indexes参数必须是列表类型，当前类型: {type(indexes).__name__}"
            logger.error(error_msg, {'库': db_name, '表': table_name, 'indexes': indexes})
            raise ValueError(error_msg)
        
        # 检查是否为空列表
        if len(indexes) == 0:
            logger.debug('indexes为空列表，将忽略此参数', {'库': db_name, '表': table_name})
            return None
        
        validated_indexes = []
        empty_strings_count = 0
        
        for i, col_name in enumerate(indexes):
            if not isinstance(col_name, str):
                error_msg = f"indexes[{i}]必须是字符串类型，当前类型: {type(col_name).__name__}，值: {col_name}"
                logger.error(error_msg, {'库': db_name, '表': table_name, 'indexes': indexes})
                raise ValueError(error_msg)
            
            # 检查是否为空字符串或纯空白字符
            stripped_name = col_name.strip()
            if not stripped_name:
                empty_strings_count += 1
                logger.warning(f'indexes[{i}]为空字符串或纯空白字符，跳过，原始值: "{col_name}"', {
                    '库': db_name, '表': table_name, 'indexes': indexes
                })
                continue
            
            validated_indexes.append(stripped_name)
        
        # 去重
        validated_indexes = list(dict.fromkeys(validated_indexes))
        
        # 检查验证后的结果
        if not validated_indexes:
            if empty_strings_count > 0:
                logger.warning(f'indexes包含{empty_strings_count}个空字符串，验证后为空，将忽略此参数', {
                    '库': db_name, '表': table_name, '空字符串数量': empty_strings_count
                })
            else:
                logger.warning('indexes验证后为空，将忽略此参数', {'库': db_name, '表': table_name})
            return None
        
        logger.debug('indexes格式验证通过', {
            '库': db_name, 
            '表': table_name, 
            '原始': indexes, 
            '验证后': validated_indexes,
            '跳过的空字符串': empty_strings_count
        })
        return validated_indexes

    def _validate_primary_keys_format(self, primary_keys: Optional[List[str]], db_name: str = None, table_name: str = None) -> Optional[List[str]]:
        """
        验证primary_keys参数的格式是否正确
        
        :param primary_keys: 主键列列表
        :param db_name: 数据库名，用于日志记录
        :param table_name: 表名，用于日志记录
        :return: 验证后的primary_keys，如果验证失败则抛出异常
        :raises ValueError: 当参数格式不正确时抛出
        """
        if primary_keys is None:
            return None
            
        if not isinstance(primary_keys, list):
            error_msg = f"primary_keys参数必须是列表类型，当前类型: {type(primary_keys).__name__}"
            logger.error(error_msg, {'库': db_name, '表': table_name, 'primary_keys': primary_keys})
            raise ValueError(error_msg)
        
        # 检查是否为空列表
        if len(primary_keys) == 0:
            logger.debug('primary_keys为空列表，将忽略此参数', {'库': db_name, '表': table_name})
            return None
        
        validated_keys = []
        empty_strings_count = 0
        
        for i, col_name in enumerate(primary_keys):
            if not isinstance(col_name, str):
                error_msg = f"primary_keys[{i}]必须是字符串类型，当前类型: {type(col_name).__name__}，值: {col_name}"
                logger.error(error_msg, {'库': db_name, '表': table_name, 'primary_keys': primary_keys})
                raise ValueError(error_msg)
            
            # 检查是否为空字符串或纯空白字符
            stripped_name = col_name.strip()
            if not stripped_name:
                empty_strings_count += 1
                logger.warning(f'primary_keys[{i}]为空字符串或纯空白字符，跳过，原始值: "{col_name}"', {
                    '库': db_name, '表': table_name, 'primary_keys': primary_keys
                })
                continue
            
            validated_keys.append(stripped_name)
        
        # 去重并检查是否有重复列名
        if len(validated_keys) != len(set(validated_keys)):
            error_msg = f"primary_keys中存在重复列名: {validated_keys}"
            logger.error(error_msg, {'库': db_name, '表': table_name, 'primary_keys': primary_keys})
            raise ValueError(error_msg)
        
        # 检查验证后的结果
        if not validated_keys:
            if empty_strings_count > 0:
                logger.warning(f'primary_keys包含{empty_strings_count}个空字符串，验证后为空，将忽略此参数', {
                    '库': db_name, '表': table_name, '空字符串数量': empty_strings_count
                })
            else:
                logger.warning('primary_keys验证后为空，将忽略此参数', {'库': db_name, '表': table_name})
            return None
        
        logger.debug('primary_keys格式验证通过', {
            '库': db_name, 
            '表': table_name, 
            '原始': primary_keys, 
            '验证后': validated_keys,
            '跳过的空字符串': empty_strings_count
        })
        return validated_keys


def main():
    dir_path = os.path.expanduser("~")
    parser = myconf.ConfigParser()
    host, port, username, password = parser.get_section_values(
        file_path=os.path.join(dir_path, 'spd.txt'),
        section='mysql',
        keys=['host', 'port', 'username', 'password'],
    )
    host = 'localhost'

    uploader = MySQLUploader(
        username=username,
        password=password,
        host=host,
        port=int(port),
    )

    # 定义列和数据类型
    set_typ = {
        'name': 'VARCHAR(255)',
        'age': 'INT',
        'salary': 'DECIMAL(10,2)',
        '日期': 'DATE',
        'shop': None,
    }

    # 准备数据
    data = [
        {'日期': '2023-01-8', 'name': 'JACk', 'AGE': '24', 'salary': 555.1545},
        {'日期': '2023-01-15', 'name': 'Alice', 'AGE': 35, 'salary': '100'},
        {'日期': '2023-01-15', 'name': 'Alice', 'AGE': 5, 'salary': 15478},
        {'日期': '2023-02-20', 'name': 'Bob', 'AGE': 25, 'salary': 45000.75},
    ]

    # 测试参数验证功能
    print("=== 测试参数验证功能 ===")
    
    # 正确的格式
    print("1. 测试正确的unique_keys格式:")
    try:
        valid_unique_keys = [['日期', 'name'], ['age']]
        result = uploader._validate_unique_keys_format(valid_unique_keys, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 错误的格式 - 缺少一层嵌套
    print("2. 测试错误的unique_keys格式 (缺少嵌套):")
    try:
        invalid_unique_keys = ['日期', 'name']  # 错误：应该是 [['日期', 'name']]
        result = uploader._validate_unique_keys_format(invalid_unique_keys, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   正确捕获错误: {e}")
    
    # 错误的格式 - 包含非字符串元素
    print("3. 测试错误的unique_keys格式 (非字符串元素):")
    try:
        invalid_unique_keys = [['日期', 123]]  # 错误：123不是字符串
        result = uploader._validate_unique_keys_format(invalid_unique_keys, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   正确捕获错误: {e}")
    
    # 错误的格式 - 空字符串
    print("4. 测试错误的unique_keys格式 (空字符串):")
    try:
        invalid_unique_keys = [['日期', '']]  # 错误：空字符串
        result = uploader._validate_unique_keys_format(invalid_unique_keys, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   正确捕获错误: {e}")
    
    # 错误的格式 - 重复列名
    print("5. 测试错误的unique_keys格式 (重复列名):")
    try:
        invalid_unique_keys = [['日期', '日期']]  # 错误：重复列名
        result = uploader._validate_unique_keys_format(invalid_unique_keys, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   正确捕获错误: {e}")
    
    # 空值测试 - 空列表
    print("6. 测试空值情况 - 空列表:")
    try:
        empty_list = []
        result = uploader._validate_unique_keys_format(empty_list, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 空值测试 - 包含空列表
    print("7. 测试空值情况 - 包含空列表 [[]]:")
    try:
        empty_nested = [[]]
        result = uploader._validate_unique_keys_format(empty_nested, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 空值测试 - 混合空列表和有效列表
    print("8. 测试空值情况 - 混合空列表和有效列表 [[], ['col1']]:")
    try:
        mixed_empty = [[], ['col1']]
        result = uploader._validate_unique_keys_format(mixed_empty, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 空值测试 - 包含空字符串的列表
    print("9. 测试空值情况 - 包含空字符串的列表 [[''], ['col1']]:")
    try:
        empty_string_list = [[''], ['col1']]
        result = uploader._validate_unique_keys_format(empty_string_list, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   正确捕获错误: {e}")
    
    # 空值测试 - 包含纯空白字符的列表
    print("10. 测试空值情况 - 包含纯空白字符的列表 [['   '], ['col1']]:")
    try:
        whitespace_list = [['   '], ['col1']]
        result = uploader._validate_unique_keys_format(whitespace_list, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   正确捕获错误: {e}")
    
    # 测试indexes的空值处理
    print("\n=== 测试indexes空值处理 ===")
    print("11. 测试indexes包含空字符串 ['', 'col1']:")
    try:
        indexes_with_empty = ['', 'col1']
        result = uploader._validate_indexes_format(indexes_with_empty, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试primary_keys的空值处理
    print("12. 测试primary_keys包含空字符串 ['', 'col1']:")
    try:
        primary_keys_with_empty = ['', 'col1']
        result = uploader._validate_primary_keys_format(primary_keys_with_empty, 'test_db', 'test_table')
        print(f"   通过: {result}")
    except Exception as e:
        print(f"   失败: {e}")

    # 上传数据（使用正确的格式）
    print("\n=== 开始上传数据 ===")
    uploader.upload_data(
        db_name='测试库',
        table_name='测试表',
        data=data,
        set_typ=set_typ,  # 定义列和数据类型
        primary_keys=[],  # 创建唯一主键
        check_duplicate=False,  # 检查重复数据
        duplicate_columns=[],  # 指定排重的组合键
        update_on_duplicate=True,  # 更新旧数据
        allow_null=False,  # 允许插入空值
        partition_by='year',  # 分表方式
        partition_date_column='日期',  # 用于分表的日期列名，默认为'日期'
        indexes=[],  # 普通索引列
        transaction_mode='row',  # 事务模式
        unique_keys=[['日期', 'name', 'age']],  # 唯一约束列表 - 正确的格式
    )

    uploader.close()


if __name__ == '__main__':
    # main()
    pass
