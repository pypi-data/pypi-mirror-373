# -*- coding:utf-8 -*-
import re
import time
from functools import wraps
import warnings
import pymysql
import os
from mdbq.log import mylogger
from mdbq.myconf import myconf
from typing import List, Dict, Optional, Any, Tuple
from dbutils.pooled_db import PooledDB
import threading
import concurrent.futures
from collections import defaultdict
import sys
from datetime import datetime
import uuid
from contextlib import contextmanager

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


class MySQLDeduplicator:
    """
    MySQL 数据去重。

    支持按天分区（如有 date_column）或全表去重，支持自定义去重分组字段（columns），可排除指定列（exclude_columns），并支持多线程并发。

    主要参数说明：
    - columns: 指定去重分组字段，控制唯一性分组行为。若 columns 有值且不包含 date_column，则全表去重，否则按天分区。
    - exclude_columns: 去重时排除的列名列表，自动合并 ['id', '更新时间']，在分组时排除。
    - date_column: 指定日期分区字段，默认为 '日期'。如表存在该字段且 columns 未排除，则按天分区去重。
    - duplicate_keep_mode: 'keep_one'（默认，重复组保留一条），'remove_all'（全部删除重复组）。
    - dry_run: 是否为模拟运行，不实际删除数据。
    - use_python_dedup: 是否用 Python 方式去重（否则用 SQL）。

    分天/全表去重行为：
    - 若 columns 有值且不包含 date_column，则直接全表去重，分组字段为 columns。
    - 否则，若表存在 date_column，则按天分区去重，分组字段为 columns（如有）或全表字段。
    - exclude_columns 始终生效，分组时自动排除。
    """

    def __init__(
            self,
            username: str,
            password: str,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
            max_workers: int = 2,
            batch_size: int = 1000,
            skip_system_dbs: bool = True,
            max_retries: int = 3,
            retry_waiting_time: int = 5,
            pool_size: int = 20,
            mincached: int = 0,
            maxcached: int = 0,
            primary_key: str = 'id',
            date_range: Optional[List[str]] = None,
            recent_month: Optional[int] = None,
            date_column: str = '日期',
            exclude_columns: Optional[List[str]] = None,
            exclude_databases: Optional[List[str]] = None,
            exclude_tables: Optional[Dict[str, List[str]]] = None,
            duplicate_keep_mode: str = 'keep_one',
            keep_order: str = 'min'
    ) -> None:
        """
        初始化去重处理器
        :param date_range: 指定去重的日期区间 [start_date, end_date]，格式'YYYY-MM-DD'
        :param recent_month: 最近N个月的数据去重（与date_range互斥，优先生效）
        :param date_column: 时间列名，默认为'日期'
        :param exclude_columns: 去重时排除的列名列表，默认为['id', '更新时间']
        :param exclude_databases: 排除的数据库名列表
        :param exclude_tables: 排除的表名字典 {数据库名: [表名, ...]}
        :param duplicate_keep_mode: 'keep_one'（默认，重复组保留一条），'remove_all'（全部删除重复组）
        :param mincached: 空闲连接数量
        :param maxcached: 最大空闲连接数, 0表示不设上限, 由连接池自动管理
        
        """
        # 连接池状态标志
        self._closed = False
        logger.debug('初始化MySQLDeduplicator', {
            'host': host, 'port': port, 'user': username, 'charset': charset,
            'max_workers': max_workers, 'batch_size': batch_size, 'pool_size': pool_size,
            'exclude_columns': exclude_columns
        })
        # 初始化连接池
        self.pool = PooledDB(
            creator=pymysql,
            host=host,
            port=int(port),
            user=username,
            password=password,
            charset=charset,
            maxconnections=pool_size,
            cursorclass=pymysql.cursors.DictCursor,
            mincached=mincached,
            maxcached=maxcached,
        )

        # 并发模式要将 pool_size 加大
        MAX_POOL_SIZE = 200
        MAX_WORKERS = 4
        if max_workers > MAX_WORKERS:
            logger.warning(f"max_workers({max_workers}) 超过最大建议值({MAX_WORKERS})，自动将 max_workers 调整为 {MAX_WORKERS}")
            max_workers = MAX_WORKERS
        expected_threads = max_workers * 10
        if pool_size < expected_threads:
            logger.warning(f"pool_size({pool_size}) < max_workers({max_workers}) * 10，自动将 pool_size 调整为 {expected_threads}")
            pool_size = expected_threads
        if pool_size > MAX_POOL_SIZE:
            logger.warning(f"pool_size({pool_size}) 超过最大建议值({MAX_POOL_SIZE})，自动将 pool_size 调整为 {MAX_POOL_SIZE}")
            pool_size = MAX_POOL_SIZE
        self.max_workers = max_workers
        self.pool_size = pool_size

        # 配置参数
        self.batch_size = batch_size
        self.skip_system_dbs = skip_system_dbs
        self.max_retries = max_retries
        self.retry_waiting_time = retry_waiting_time
        self.primary_key = primary_key

        # 时间范围参数
        self.date_column = date_column
        self._dedup_start_date = None
        self._dedup_end_date = None
        if date_range and len(date_range) == 2:
            try:
                start, end = date_range
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
                if start_dt > end_dt:
                    logger.debug(
                        "date_range顺序不正确，自动交换开始和结束日期。",
                        {"start": start, "end": end}
                    )
                    start_dt, end_dt = end_dt, start_dt
                self._dedup_start_date = start_dt.strftime("%Y-%m-%d")
                self._dedup_end_date = end_dt.strftime("%Y-%m-%d")
            except Exception as e:
                logger.error(
                    "date_range参数格式错误，应为['YYYY-MM-DD', 'YYYY-MM-DD']，已忽略时间范围。",
                    {"date_range": date_range, "error": str(e)}
                )
                self._dedup_start_date = None
                self._dedup_end_date = None
        elif recent_month:
            today = datetime.today()
            month = today.month - recent_month
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            self._dedup_start_date = f"{year}-{month:02d}-01"
            self._dedup_end_date = today.strftime("%Y-%m-%d")
        
        if self._dedup_start_date and self._dedup_end_date:
            logger.debug('去重日期范围', {'开始': self._dedup_start_date, '结束': self._dedup_end_date})

        # 排除列处理，直接合并去重
        self.exclude_columns = list(set((exclude_columns or []) + ['id', '更新时间']))

        # 线程安全控制
        self._lock = threading.Lock()
        self._processing_tables = set()  # 正在处理的表集合

        # 系统数据库列表
        self.SYSTEM_DATABASES = {'information_schema', 'mysql', 'performance_schema', 'sys', 'sakila'}

        # 排除数据库和表的逻辑
        self.exclude_databases = set(db.lower() for db in (exclude_databases or []))
        self.exclude_tables = {k.lower(): set(t.lower() for t in v) for k, v in (exclude_tables or {}).items()}

        self.duplicate_keep_mode = duplicate_keep_mode if duplicate_keep_mode in ('keep_one', 'remove_all') else 'keep_one'
        self.keep_order = keep_order if keep_order in ('min', 'max') else 'min'

    def _get_connection(self) -> pymysql.connections.Connection:
        """
        从连接池获取一个数据库连接。
        
        Returns:
            pymysql.connections.Connection: 数据库连接对象。
        Raises:
            ConnectionError: 如果连接池已关闭或获取连接失败。
        """
        if self._closed:
            logger.error('尝试获取连接但连接池已关闭')
            raise ConnectionError("连接池已关闭")
        try:
            conn = self.pool.connection()
            return conn
        except Exception as e:
            logger.error(f"获取数据库连接失败: {str(e)}", {'error_type': type(e).__name__})
            raise ConnectionError(f"连接数据库失败: {str(e)}")

    @contextmanager
    def _conn_ctx(self):
        conn = self._get_connection()
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _retry_on_failure(func: Any) -> Any:
        """
        装饰器：为数据库操作方法提供自动重试机制。
        仅捕获pymysql的连接相关异常，重试指定次数后抛出最后一次异常。
        
        Args:
            func (Any): 被装饰的函数。
        Returns:
            Any: 被装饰函数的返回值。
        Raises:
            Exception: 多次重试后依然失败时抛出。
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(self.max_retries + 1):
                try:
                    logger.debug(f'调用{func.__name__}，第{attempt+1}次连接', {'args': args, 'kwargs': kwargs})
                    return func(self, *args, **kwargs)
                except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        wait_time = self.retry_waiting_time * (attempt + 1)
                        logger.warning(
                            f"数据库操作失败，准备重试 (尝试 {attempt + 1}/{self.max_retries})",
                            {'error': str(e), 'wait_time': wait_time, 'func': func.__name__})
                        time.sleep(wait_time)
                        continue
                except Exception as e:
                    last_exception = e
                    logger.error(f"操作失败: {str(e)}", {'error_type': type(e).__name__, 'func': func.__name__})
                    break
            if last_exception:
                logger.error('重试后依然失败', {'func': func.__name__, 'last_exception': str(last_exception)})
                raise last_exception
            raise Exception("未知错误")
        return wrapper

    def _get_databases(self) -> List[str]:
        """
        获取所有非系统数据库列表，排除 exclude_databases。
        
        Returns:
            List[str]: 数据库名列表。
        """
        sql = "SHOW DATABASES"
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                all_dbs = [row['Database'] for row in cursor.fetchall()]
                # 排除系统库和用户指定的库
                filtered = [db for db in all_dbs if db.lower() not in self.SYSTEM_DATABASES and db.lower() not in self.exclude_databases] if self.skip_system_dbs else [db for db in all_dbs if db.lower() not in self.exclude_databases]
                return filtered

    def _get_tables(self, database: str) -> List[str]:
        """
        获取指定数据库的所有表名（排除 temp_ 前缀的临时表）。
        
        Args:
            database (str): 数据库名。
        Returns:
            List[str]: 表名列表。
        """
        sql = "SHOW TABLES"
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{database}`")
                cursor.execute(sql)
                return [row[f'Tables_in_{database}'] for row in cursor.fetchall() if not re.match(r'^temp_.*', row[f'Tables_in_{database}'])]

    def _get_table_columns(self, database: str, table: str) -> List[str]:
        """
        获取指定表的所有列名（排除主键列）。
        
        Args:
            database (str): 数据库名。
            table (str): 表名。
        Returns:
            List[str]: 列名列表。
        """
        sql = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (database, table))
                return [row['COLUMN_NAME'] for row in cursor.fetchall()
                        if row['COLUMN_NAME'].lower() != self.primary_key.lower()]

    def _ensure_index(self, database: str, table: str, date_column: str) -> None:
        """
        检查并为 date_column 自动创建索引（如果未存在）。
        
        Args:
            database (str): 数据库名。
            table (str): 表名。
            date_column (str): 需要检查的日期列名。
        """
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                # 检查索引是否已存在
                cursor.execute(
                    """
                    SELECT COUNT(1) as idx_count FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
                    """,
                    (database, table, date_column)
                )
                idx_count = cursor.fetchone()['idx_count']
                if idx_count == 0:
                    # 自动创建索引
                    index_name = f"idx_{date_column}"
                    safe_index_name = self._make_safe_table_name(index_name, prefix='', suffix='', max_length=64)
                    try:
                        cursor.execute(f"CREATE INDEX `{safe_index_name}` ON `{database}`.`{table}` (`{date_column}`)")
                        conn.commit()
                        logger.debug('已自动为date_column创建索引', {"库": database, "表": table, "date_column": date_column, "索引名": safe_index_name})
                    except Exception as e:
                        logger.error('自动创建date_column索引失败', {"库": database, "表": table, "date_column": date_column, "异常": str(e)})

    def _row_generator(self, database, table, select_cols, select_where, batch_size=10000):
        """
        生成器：分批拉取表数据，避免一次性加载全部数据到内存。
        Args:
            database (str): 数据库名。
            table (str): 表名。
            select_cols (str): 选择的列字符串。
            select_where (str): where条件字符串。
            batch_size (int): 每批拉取的行数。
        Yields:
            dict: 每行数据。
        """
        offset = 0
        while True:
            sql = f"SELECT {select_cols} FROM `{database}`.`{table}` {select_where} LIMIT {batch_size} OFFSET {offset}"
            with self._conn_ctx() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    if not rows:
                        break
                    for row in rows:
                        yield row
            if len(rows) < batch_size:
                break
            offset += batch_size
            
    def _get_all_dates(self, database: str, table: str, date_column: str) -> List[str]:
        """
        获取表中所有不同的日期分区（按天）。
        
        Args:
            database (str): 数据库名。
            table (str): 表名。
            date_column (str): 日期列名。
        Returns:
            List[str]: 所有不同的日期（字符串）。
        """
        sql = f"SELECT DISTINCT `{date_column}` FROM `{database}`.`{table}` ORDER BY `{date_column}` ASC"
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return [row[date_column] for row in cursor.fetchall() if row[date_column] is not None]

    def _deduplicate_table(
        self,
        database: str,
        table: str,
        columns: Optional[List[str]] = None,
        dry_run: bool = False,
        use_python_dedup: bool = False,
        date_val: Optional[str] = None,
        lock_table: bool = True
    ) -> Tuple[int, int]:
        """
        执行单表单天或全表去重。根据 columns 和 date_column 决定分天或全表：
        - 若 columns 不包含 date_column，则全表去重（不分天）。
        - 若 columns 包含 date_column 或未指定 columns，则按天分区去重（date_val 为当前处理日期）。

        Args:
            database (str): 数据库名。
            table (str): 表名。
            columns (Optional[List[str]]): 指定去重列。若不含 date_column，则全表去重。
            dry_run (bool): 是否为模拟运行。
            use_python_dedup (bool): 是否用 Python 方式去重。
            date_val (Optional[str]): 指定处理的日期（如有 date_column 且分天时）。
            lock_table (bool): 是否加表级锁。
        Returns:
            Tuple[int, int]: (重复组数, 实际删除行数)
        """
        if lock_table and not self._acquire_table_lock(database, table):
            return (0, 0)
        temp_table = None
        try:
            all_columns = self._get_table_columns(database, table)
            all_columns_lower = [col.lower() for col in all_columns]
            exclude_columns_lower = [col.lower() for col in getattr(self, 'exclude_columns', [])]
            time_col = self.date_column
            time_col_lower = time_col.lower() if time_col else None
            # 如果传了columns且columns不包含date_column，则不分天，直接全表去重
            if columns and (not time_col_lower or time_col_lower not in [c.lower() for c in columns]):
                has_time_col = False  # 全表去重
            else:
                has_time_col = time_col_lower in all_columns_lower if time_col_lower else False  # 分天去重
            if has_time_col:
                self._ensure_index(database, table, time_col)
                # 获取去重列
                use_columns = columns or all_columns
                use_columns = [col for col in use_columns if col.lower() in all_columns_lower and col.lower() not in exclude_columns_lower]
                invalid_columns = set([col for col in (columns or []) if col.lower() not in all_columns_lower])
                if invalid_columns:
                    logger.warning('不存在的列', {"库": database, "表": table, "不存在以下列": invalid_columns, 'func': sys._getframe().f_code.co_name})
                if not use_columns:
                    logger.error('没有有效的去重列', {"库": database, "表": table, "func": sys._getframe().f_code.co_name})
                    return (0, 0)
                pk = self.primary_key
                pk_real = next((c for c in all_columns if c.lower() == pk.lower()), pk)
                where_sql = f"t.`{time_col}` = '{date_val}'"
                # 获取原始数据总量（只统计当天数据）
                with self._conn_ctx() as conn:
                    with conn.cursor() as cursor:
                        count_where = f"WHERE `{time_col}` = '{date_val}'"
                        count_sql = f"SELECT COUNT(*) as cnt FROM `{database}`.`{table}` {count_where}"
                        logger.debug('执行SQL', {'sql': count_sql})
                        cursor.execute(count_sql)
                        total_count_row = cursor.fetchone()
                        total_count = total_count_row['cnt'] if total_count_row and 'cnt' in total_count_row else 0
                logger.debug('执行', {"库": database, "表": table, "开始处理数据量": total_count, 'func': sys._getframe().f_code.co_name, "数据日期": date_val})
                column_list = ', '.join([f'`{col}`' for col in use_columns])

                # 用Python查找重复
                if use_python_dedup:
                    # 判断分组字段是否有“更新时间”
                    has_update_time = any(col == '更新时间' for col in use_columns)
                    select_cols = f'`{pk_real}`,' + ','.join([f'`{col}`' for col in use_columns])
                    if has_update_time:
                        select_cols += ',`更新时间`'
                    select_where = f"WHERE `{time_col}` = '{date_val}'" if date_val else ''
                    grouped = defaultdict(list)
                    for row in self._row_generator(database, table, select_cols, select_where, self.batch_size):
                        key = tuple(row[col] for col in use_columns)
                        grouped[key].append(row)
                    dup_count = 0
                    del_ids = []
                    for ids in grouped.values():
                        if len(ids) > 1:
                            dup_count += 1
                            if has_update_time:
                                # 按更新时间最大保留
                                keep_row = max(ids, key=lambda x: x.get('更新时间') or '')
                            else:
                                # 按id保留
                                if self.keep_order == 'max':
                                    keep_row = max(ids, key=lambda x: x[pk_real])
                                else:
                                    keep_row = min(ids, key=lambda x: x[pk_real])
                            del_ids.extend([r[pk_real] for r in ids if r[pk_real] != keep_row[pk_real]])
                    affected_rows = 0
                    if not dry_run and del_ids:
                        with self._conn_ctx() as conn:
                            with conn.cursor() as cursor:
                                format_ids = ','.join([str(i) for i in del_ids])
                                del_sql = f"DELETE FROM `{database}`.`{table}` WHERE `{pk_real}` IN ({format_ids})"
                                cursor.execute(del_sql)
                                affected_rows = cursor.rowcount
                                conn.commit()
                    logger.debug('去重完成', {"库": database, "表": table, "数据量": total_count, "重复组": dup_count, "实际删除": affected_rows, "去重方式": "Python", "数据处理": self.duplicate_keep_mode, "数据日期": date_val})
                    return (dup_count, affected_rows)
                # SQL方式查找重复
                temp_table = self._make_temp_table_name(table)
                drop_temp_sql = f"DROP TABLE IF EXISTS `{database}`.`{temp_table}`"
                create_temp_where = f"WHERE `{time_col}` = '{date_val}'"
                # 判断分组字段是否有“更新时间”
                has_update_time = any(col == '更新时间' for col in use_columns)
                if has_update_time:
                    keep_field = '更新时间'
                    keep_func = 'MAX'
                else:
                    keep_field = pk_real
                    keep_func = 'MAX' if self.keep_order == 'max' else 'MIN'
                keep_alias = 'keep_val'
                create_temp_sql = f"""
                CREATE TABLE `{database}`.`{temp_table}` AS
                SELECT {keep_func}(`{keep_field}`) as `{keep_alias}`, {column_list}, COUNT(*) as `dup_count`
                FROM `{database}`.`{table}`
                {create_temp_where}
                GROUP BY {column_list}
                HAVING COUNT(*) > 1
                """
                with self._conn_ctx() as conn:
                    with conn.cursor() as cursor:
                        logger.debug('创建临时表SQL', {'sql': create_temp_sql})
                        cursor.execute(create_temp_sql)
                        cursor.execute(f"SELECT COUNT(*) as cnt FROM `{database}`.`{temp_table}`")
                        dup_count_row = cursor.fetchone()
                        dup_count = dup_count_row['cnt'] if dup_count_row and 'cnt' in dup_count_row else 0
                        if dup_count == 0:
                            logger.debug('没有重复数据', {"库": database, "表": table, "数据量": total_count, "数据日期": date_val})
                            cursor.execute(drop_temp_sql)
                            conn.commit()
                            return (0, 0)
                        affected_rows = 0
                        if not dry_run:
                            while True:
                                where_clauses = []
                                if self.duplicate_keep_mode == 'keep_one':
                                    where_clauses.append(f"t.`{keep_field}` <> tmp.`{keep_alias}`")
                                if where_sql.strip():
                                    where_clauses.append(where_sql.strip())
                                where_full = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                                find_dup_ids_sql = f"""
                                SELECT t.`{pk_real}` as del_id
                                FROM `{database}`.`{table}` t
                                JOIN `{database}`.`{temp_table}` tmp
                                ON {' AND '.join([f't.`{col}` <=> tmp.`{col}`' for col in use_columns])}
                                {where_full}
                                LIMIT {self.batch_size}
                                """
                                logger.debug('查找待删除重复id SQL', {'sql': find_dup_ids_sql})
                                cursor.execute(find_dup_ids_sql)
                                del_ids = [row['del_id'] for row in cursor.fetchall()]
                                if not del_ids:
                                    break
                                del_ids_str = ','.join([str(i) for i in del_ids])
                                delete_sql = f"DELETE FROM `{database}`.`{table}` WHERE `{pk_real}` IN ({del_ids_str})"
                                logger.debug('按id批量删除SQL', {'sql': delete_sql, 'ids': del_ids})
                                cursor.execute(delete_sql)
                                batch_deleted = cursor.rowcount
                                affected_rows += batch_deleted
                                conn.commit()
                                if batch_deleted == 0:
                                    logger.warning('检测到未能删除任何数据，强制跳出循环，防止假死', {"库": database, "表": table})
                                    break
                                if batch_deleted < self.batch_size:
                                    break
                            logger.info('操作删除', {"库": database, "表": table, "数据量": total_count, "重复组": dup_count, "实际删除": affected_rows, "去重方式": "SQL", "数据处理": self.duplicate_keep_mode, "数据日期": date_val})
                        else:
                            logger.debug('dry_run模式，不执行删除', {"库": database, "表": table, "重复组": dup_count})
                            affected_rows = 0
                        cursor.execute(drop_temp_sql)
                        conn.commit()
                        return (dup_count, affected_rows)
            # 没有date_column，处理全表
            # ...existing code for full-table deduplication (as before, but without recursion)...
            use_columns = columns or all_columns
            use_columns = [col for col in use_columns if col.lower() in all_columns_lower and col.lower() not in exclude_columns_lower]
            invalid_columns = set([col for col in (columns or []) if col.lower() not in all_columns_lower])
            if invalid_columns:
                logger.warning('不存在的列', {"库": database, "表": table, "不存在以下列": invalid_columns, 'func': sys._getframe().f_code.co_name})
            if not use_columns:
                logger.error('没有有效的去重列', {"库": database, "表": table, "func": sys._getframe().f_code.co_name})
                return (0, 0)
            pk = self.primary_key
            pk_real = next((c for c in all_columns if c.lower() == pk.lower()), pk)
            # 获取原始数据总量
            with self._conn_ctx() as conn:
                with conn.cursor() as cursor:
                    count_sql = f"SELECT COUNT(*) as cnt FROM `{database}`.`{table}`"
                    logger.debug('执行SQL', {'sql': count_sql})
                    cursor.execute(count_sql)
                    total_count_row = cursor.fetchone()
                    total_count = total_count_row['cnt'] if total_count_row and 'cnt' in total_count_row else 0
            logger.debug('执行', {"库": database, "表": table, "开始处理数据量": total_count, 'func': sys._getframe().f_code.co_name})
            column_list = ', '.join([f'`{col}`' for col in use_columns])
            if use_python_dedup:
                select_cols = f'`{pk_real}`,' + ','.join([f'`{col}`' for col in use_columns])
                select_where = ''
                grouped = defaultdict(list)
                for row in self._row_generator(database, table, select_cols, select_where, self.batch_size):
                    key = tuple(row[col] for col in use_columns)
                    grouped[key].append(row[pk_real])
                dup_count = 0
                del_ids = []
                for ids in grouped.values():
                    if len(ids) > 1:
                        dup_count += 1
                        del_ids.extend(ids[1:])
                affected_rows = 0
                if not dry_run and del_ids:
                    with self._conn_ctx() as conn:
                        with conn.cursor() as cursor:
                            for i in range(0, len(del_ids), self.batch_size):
                                batch_ids = del_ids[i:i+self.batch_size]
                                del_ids_str = ','.join([str(i) for i in batch_ids])
                                delete_sql = f"DELETE FROM `{database}`.`{table}` WHERE `{pk_real}` IN ({del_ids_str})"
                                cursor.execute(delete_sql)
                                batch_deleted = cursor.rowcount
                                affected_rows += batch_deleted
                                conn.commit()
                logger.debug('去重完成', {"库": database, "表": table, "数据量": total_count, "重复组": dup_count, "实际删除": affected_rows, "去重方式": "Python", "数据处理": self.duplicate_keep_mode})
                return (dup_count, affected_rows)
            temp_table = self._make_temp_table_name(table)
            drop_temp_sql = f"DROP TABLE IF EXISTS `{database}`.`{temp_table}`"
            create_temp_sql = f"""
            CREATE TABLE `{database}`.`{temp_table}` AS
            SELECT MIN(`{pk_real}`) as `min_id`, {column_list}, COUNT(*) as `dup_count`
            FROM `{database}`.`{table}`
            GROUP BY {column_list}
            HAVING COUNT(*) > 1
            """
            with self._conn_ctx() as conn:
                with conn.cursor() as cursor:
                    logger.debug('创建临时表SQL', {'sql': create_temp_sql})
                    cursor.execute(create_temp_sql)
                    cursor.execute(f"SELECT COUNT(*) as cnt FROM `{database}`.`{temp_table}`")
                    dup_count_row = cursor.fetchone()
                    dup_count = dup_count_row['cnt'] if dup_count_row and 'cnt' in dup_count_row else 0
                    if dup_count == 0:
                        logger.debug('没有重复数据', {"库": database, "表": table, "数据量": total_count})
                        cursor.execute(drop_temp_sql)
                        conn.commit()
                        return (0, 0)
                    affected_rows = 0
                    if not dry_run:
                        while True:
                            where_clauses = []
                            if self.duplicate_keep_mode == 'keep_one':
                                where_clauses.append(f"t.`{pk_real}` <> tmp.`min_id`")
                            where_full = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                            find_dup_ids_sql = f"""
                            SELECT t.`{pk_real}` as del_id
                            FROM `{database}`.`{table}` t
                            JOIN `{database}`.`{temp_table}` tmp
                            ON {' AND '.join([f't.`{col}` <=> tmp.`{col}`' for col in use_columns])}
                            {where_full}
                            LIMIT {self.batch_size}
                            """
                            logger.debug('查找待删除重复id SQL', {'sql': find_dup_ids_sql})
                            cursor.execute(find_dup_ids_sql)
                            del_ids = [row['del_id'] for row in cursor.fetchall()]
                            if not del_ids:
                                break
                            del_ids_str = ','.join([str(i) for i in del_ids])
                            delete_sql = f"DELETE FROM `{database}`.`{table}` WHERE `{pk_real}` IN ({del_ids_str})"
                            logger.debug('按id批量删除SQL', {'sql': delete_sql, 'ids': del_ids})
                            cursor.execute(delete_sql)
                            batch_deleted = cursor.rowcount
                            affected_rows += batch_deleted
                            conn.commit()
                            if batch_deleted == 0:
                                logger.warning('检测到未能删除任何数据，强制跳出循环，防止假死', {"库": database, "表": table})
                                break
                            if batch_deleted < self.batch_size:
                                break
                        logger.info('操作删除', {"库": database, "表": table, "数据量": total_count, "重复组": dup_count, "实际删除": affected_rows, "去重方式": "SQL", "数据处理": self.duplicate_keep_mode})
                    else:
                        logger.debug('dry_run模式，不执行删除', {"库": database, "表": table, "重复组": dup_count})
                        affected_rows = 0
                    cursor.execute(drop_temp_sql)
                    conn.commit()
                    return (dup_count, affected_rows)
        except Exception as e:
            logger.error('异常', {"库": database, "表": table, "异常": str(e), 'func': sys._getframe().f_code.co_name, 'traceback': repr(e)})
            if temp_table:
                try:
                    with self._conn_ctx() as conn:
                        with conn.cursor() as cursor:
                            drop_temp_sql = f"DROP TABLE IF EXISTS `{database}`.`{temp_table}`"
                            cursor.execute(drop_temp_sql)
                            conn.commit()
                except Exception as drop_e:
                    logger.error('异常时清理临时表失败', {"库": database, "表": table, "异常": str(drop_e)})
            return (0, 0)
        finally:
            if lock_table:
                self._release_table_lock(database, table)

    def deduplicate_table(
        self,
        database: str,
        table: str,
        columns: Optional[List[str]] = None,
        dry_run: bool = False,
        reorder_id: bool = False,
        use_python_dedup: bool = True
    ) -> Tuple[int, int]:
        """
        对指定表进行去重。

        去重行为说明：
        - 若 columns 参数传入且不包含 date_column，则全表直接按 columns 去重。
        - 若 columns 包含 date_column 或未指定 columns，则按天分区去重（每一天独立去重）。
        - exclude_columns 中的字段始终不会参与去重分组。
        - date_column 默认为 '日期'，可自定义。
        - dry_run 模式下仅统计重复组和待删除行数，不实际删除。
        - reorder_id=True 时，去重后自动重排主键 id。

        Args:
            database (str): 数据库名。
            table (str): 表名。
            columns (Optional[List[str]]): 指定去重列。若不含 date_column，则全表去重。
            dry_run (bool): 是否为模拟运行。
            reorder_id (bool): 去重后是否自动重排 id 列。
            use_python_dedup (bool): 是否用 Python 方式去重。
        Returns:
            Tuple[int, int]: (重复组数, 实际删除行数)
        """
        if database.lower() in self.exclude_tables and table.lower() in self.exclude_tables[database.lower()]:
            logger.info('表被排除', {"库": database, "表": table, "操作": "跳过"})
            return (0, 0)
        try:
            if not self._check_table_exists(database, table):
                logger.warning('表不存在', {"库": database, "表": table, "warning": "跳过"})
                return (0, 0)
            logger.debug('单表开始', {
                "库": database, 
                "表": table, 
                # "参数": {
                #     "指定去重列": columns, 
                #     "去重方式": "Python" if use_python_dedup else "SQL", 
                #     "数据处理": self.duplicate_keep_mode,
                #     "模拟运行": dry_run, 
                #     '排除列': self.exclude_columns,
                #     },
                })
            all_columns = self._get_table_columns(database, table)
            all_columns_lower = [col.lower() for col in all_columns]
            # columns有效性检查
            if columns:
                invalid_columns = [col for col in columns if col.lower() not in all_columns_lower]
                if invalid_columns:
                    logger.warning('columns中存在表字段不存在的列，跳过该表', {
                        "库": database,
                        "表": table,
                        "columns": columns,
                        "实际表字段": all_columns,
                        "缺失字段": invalid_columns
                    })
                    return (0, 0)
            time_col = self.date_column
            time_col_lower = time_col.lower() if time_col else None
            # 如果传了columns且columns不包含date_column，则不分天，直接全表去重
            if columns and (not time_col_lower or time_col_lower not in [c.lower() for c in columns]):
                has_time_col = False  # 全表去重
            else:
                has_time_col = time_col_lower in all_columns_lower if time_col_lower else False  # 分天去重
            if has_time_col:
                self._ensure_index(database, table, time_col)
                all_dates = self._get_all_dates(database, table, time_col)
                # 按date_range/recent_month筛选日期
                start_date = self._dedup_start_date
                end_date = self._dedup_end_date
                if start_date and end_date:
                    all_dates = [d for d in all_dates if str(start_date) <= str(d) <= str(end_date)]
                if not all_dates:
                    logger.debug('无可处理日期', {"库": database, "表": table})
                    return (0, 0)
                total_dup = 0
                total_del = 0
                def process_date(date_val):
                    try:
                        logger.debug('按天分区去重', {"库": database, "表": table, "日期": date_val})
                        dup_count, affected_rows = self._deduplicate_table(
                            database, table, columns, dry_run, use_python_dedup,
                            date_val=date_val, lock_table=False
                        )
                        return (dup_count, affected_rows, date_val, None)
                    except Exception as e:
                        logger.error('分区去重异常', {"库": database, "表": table, "日期": date_val, "异常": str(e), "func": sys._getframe().f_code.co_name})
                        return (0, 0, date_val, str(e))
                if self.max_workers > 1:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        future_to_date = {executor.submit(process_date, date_val): date_val for date_val in all_dates}
                        for future in concurrent.futures.as_completed(future_to_date):
                            dup_count, affected_rows, date_val, err = future.result()
                            if err:
                                logger.warning('分区处理失败', {"库": database, "表": table, "日期": date_val, "异常": err, "func": sys._getframe().f_code.co_name})
                            total_dup += dup_count
                            total_del += affected_rows
                else:
                    for date_val in all_dates:
                        dup_count, affected_rows, _, err = process_date(date_val)
                        if err:
                            logger.warning('分区处理失败', {"库": database, "表": table, "日期": date_val, "异常": err, "func": sys._getframe().f_code.co_name})
                        total_dup += dup_count
                        total_del += affected_rows
                logger.debug('单表完成', {"库": database, "表": table, "结果[重复, 删除]": (total_dup, total_del), '日期范围': f"{start_date} - {end_date}", "唯一列": columns})
                # 自动重排id列（仅当有实际删除时且reorder_id为True）
                if reorder_id and total_del > 0:
                    try:
                        reorder_ok = self.reorder_id_column(database, table, id_column=self.primary_key, dry_run=dry_run)
                        logger.info('自动重排id列完成', {"库": database, "表": table, "结果": reorder_ok})
                    except Exception as e:
                        logger.error('自动重排id列异常', {"库": database, "表": table, "异常": str(e)})
                if affected_rows > 0:
                    logger.info('单表完成(仅显示有删除的结果)', {"库": database, "表": table, "重复组": total_dup, "实际删除": total_del, "唯一列": columns})
                return (total_dup, total_del)
            # 没有date_column，直接全表去重
            result = self._deduplicate_table(database, table, columns, dry_run, use_python_dedup, date_val=None)
            logger.info('单表完成', {"库": database, "表": table, "结果[重复, 删除]": result, '日期范围': '全表', "唯一列": columns})
            dup_count, affected_rows = result
            if reorder_id and affected_rows > 0:
                try:
                    reorder_ok = self.reorder_id_column(database, table, id_column=self.primary_key, dry_run=dry_run)
                    logger.info('自动重排id列完成', {"库": database, "表": table, "结果": reorder_ok})
                except Exception as e:
                    logger.error('自动重排id列异常', {"库": database, "表": table, "异常": str(e)})
            if affected_rows > 0:
                logger.info('单表完成(仅显示有删除的结果)', {"库": database, "表": table, "重复组": dup_count, "实际删除": affected_rows, "唯一列": columns})
            return result
        except Exception as e:
            logger.error('发生全局错误', {"库": database, "表": table, 'func': sys._getframe().f_code.co_name, "发生全局错误": str(e)})
            return (0, 0)

    def deduplicate_database(
        self,
        database: str,
        tables: Optional[List[str]] = None,
        columns_map: Optional[Dict[str, List[str]]] = None,
        dry_run: bool = False,
        parallel: bool = False,
        reorder_id: bool = False,
        use_python_dedup: bool = True
    ) -> Dict[str, Tuple[int, int]]:
        """
        对指定数据库的所有表进行去重。调用 deduplicate_table，自动适配分天。
        
        Args:
            database (str): 数据库名。
            tables (Optional[List[str]]): 指定表名列表。
            columns_map (Optional[Dict[str, List[str]]]): 每个表的去重列映射。
            dry_run (bool): 是否为模拟运行。
            parallel (bool): 是否并行处理表。
            reorder_id (bool): 去重后是否自动重排 id 列。
            use_python_dedup (bool): 是否用 Python 方式去重。
        Returns:
            Dict[str, Tuple[int, int]]: {表名: (重复组数, 实际删除行数)}
        """
        results = {}
        try:
            if not self._check_database_exists(database):
                logger.warning('数据库不存在', {"库": database})
                return results
            target_tables = tables or self._get_tables(database)
            exclude_tbls = self.exclude_tables.get(database.lower(), set())
            target_tables = [t for t in target_tables if t.lower() not in exclude_tbls]
            logger.debug('获取目标表', {'库': database, 'tables': target_tables})
            if not target_tables:
                logger.info('数据库中没有表', {"库": database, "操作": "跳过"})
                return results
            logger.debug('库统计', {"库": database, "表数量": len(target_tables), "表列表": target_tables})
            if parallel and self.max_workers > 1:
                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers
                ) as executor:
                    futures = {}
                    for table in target_tables:
                        columns = columns_map.get(table) if columns_map else None
                        logger.debug('提交表去重任务', {'库': database, '表': table, 'columns': columns})
                        futures[executor.submit(
                            self.deduplicate_table,
                            database, table, columns, dry_run, reorder_id, use_python_dedup
                        )] = table
                    for future in concurrent.futures.as_completed(futures):
                        table = futures[future]
                        try:
                            dup_count, affected_rows = future.result()
                            results[table] = (dup_count, affected_rows)
                        except Exception as e:
                            logger.error('异常', {"库": database, "表": table, "error": str(e), 'traceback': repr(e)})
                            results[table] = (0, 0)
            else:
                for table in target_tables:
                    columns = columns_map.get(table) if columns_map else None
                    dup_count, affected_rows = self.deduplicate_table(
                        database, table, columns, dry_run, reorder_id, use_python_dedup
                    )
                    results[table] = (dup_count, affected_rows)
            total_dup = sum(r[0] for r in results.values())
            total_del = sum(r[1] for r in results.values())
            logger.debug('库完成', {"库": database, "重复组": total_dup, "总删除行": total_del, "详细结果": results})
            # 只显示有删除的详细结果
            if total_del > 0:
                filtered_results = {tbl: res for tbl, res in results.items() if res[1] > 0}
                logger.info('库完成(仅显示有删除的结果)', {"库": database, "重复组": total_dup, "总删除行": total_del, "详细结果": filtered_results})
            return results
        except Exception as e:
            logger.error('发生全局错误', {"库": database, 'func': sys._getframe().f_code.co_name, "error": str(e), 'traceback': repr(e)})
            return results

    def deduplicate_all(
        self,
        databases: Optional[List[str]] = None,
        tables_map: Optional[Dict[str, List[str]]] = None,
        columns_map: Optional[Dict[str, Dict[str, List[str]]]] = None,
        dry_run: bool = False,
        parallel: bool = False,
        reorder_id: bool = False,
        use_python_dedup: bool = True
    ) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """
        对所有数据库进行去重。调用 deduplicate_database，自动适配分天。
        
        Args:
            databases (Optional[List[str]]): 指定数据库名列表。
            tables_map (Optional[Dict[str, List[str]]]): 每个库的表名映射。
            columns_map (Optional[Dict[str, Dict[str, List[str]]]]): 每个库每个表的去重列映射。
            dry_run (bool): 是否为模拟运行。
            parallel (bool): 是否并行处理库。
            reorder_id (bool): 去重后是否自动重排 id 列。
            use_python_dedup (bool): 是否用 Python 方式去重。
        Returns:
            Dict[str, Dict[str, Tuple[int, int]]]: {库: {表: (重复组数, 实际删除行数)}}
        """
        all_results: Dict[str, Dict[str, Tuple[int, int]]] = defaultdict(dict)
        try:
            target_dbs: List[str] = databases or self._get_databases()
            target_dbs = [db for db in target_dbs if db.lower() not in self.exclude_databases]
            logger.debug('获取目标数据库', {'databases': target_dbs})
            if not target_dbs:
                logger.warning('没有可处理的数据库')
                return all_results
            logger.info('全局开始', {
                "数据库数量": len(target_dbs), 
                "数据库列表": target_dbs, 
                "参数": {
                    "模拟运行": dry_run, 
                    "并行处理": parallel, 
                    '排除列': self.exclude_columns, 
                    '重排id': reorder_id, 
                    'use_python_dedup': use_python_dedup
                    },
                })
            # 如果parallel=True且库数量大于1，则只在外层并发，内层串行
            if parallel and self.max_workers > 1 and len(target_dbs) > 1:
                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers
                ) as executor:
                    futures: Dict[concurrent.futures.Future, str] = {}
                    for db in target_dbs:
                        tables = tables_map.get(db) if tables_map else None
                        db_columns_map = columns_map.get(db) if columns_map else None
                        # 内层强制串行
                        futures[executor.submit(
                            self.deduplicate_database,
                            db, tables, db_columns_map, dry_run, False, reorder_id, use_python_dedup
                        )] = db
                    for future in concurrent.futures.as_completed(futures):
                        db = futures[future]
                        try:
                            db_results = future.result()
                            all_results[db] = db_results
                        except Exception as e:
                            logger.error('异常', {"库": db, "error": str(e), 'traceback': repr(e)})
                            all_results[db] = {}
            else:
                for db in target_dbs:
                    tables = tables_map.get(db) if tables_map else None
                    db_columns_map = columns_map.get(db) if columns_map else None
                    db_results = self.deduplicate_database(
                        db, tables, db_columns_map, dry_run, parallel, reorder_id, use_python_dedup
                    )
                    all_results[db] = db_results
            total_dup = sum(
                r[0] for db in all_results.values()
                for r in db.values()
            )
            total_del = sum(
                r[1] for db in all_results.values()
                for r in db.values()
            )
            # 只显示有删除的详细结果
            if total_del > 0:
                filtered_results = {
                    db: {tbl: res for tbl, res in tbls.items() if res[1] > 0}
                    for db, tbls in all_results.items()
                }
                filtered_results = {db: tbls for db, tbls in filtered_results.items() if tbls}
                logger.info('全局完成(仅显示有删除的结果)', {
                    "总重复组": total_dup,
                    "总删除行": total_del,
                    "参数": {
                        "模拟运行": dry_run,
                        "并行处理": parallel,
                        '排除列': self.exclude_columns,
                        '重排id': reorder_id,
                        'use_python_dedup': use_python_dedup
                    },
                    "详细结果": filtered_results
                })
            return all_results
        except Exception as e:
            logger.error('异常', {"error": str(e), 'traceback': repr(e)})
            return all_results

    def _check_database_exists(self, database: str) -> bool:
        """
        检查数据库是否存在。
        
        Args:
            database (str): 数据库名。
        Returns:
            bool: 数据库是否存在。
        """
        sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s"
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (database,))
                return bool(cursor.fetchone())

    def _check_table_exists(self, database: str, table: str) -> bool:
        """
        检查表是否存在。
        
        Args:
            database (str): 数据库名。
            table (str): 表名。
        Returns:
            bool: 表是否存在。
        """
        sql = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (database, table))
                return bool(cursor.fetchone())

    def _get_table_info(self, database: str, table: str, id_column: str = None):
        """
        获取表的所有列名、主键列名列表、指定id列是否为主键。
        Args:
            database (str): 数据库名。
            table (str): 表名。
            id_column (str): id列名，默认使用self.primary_key。
        Returns:
            Tuple[List[str], List[str], bool]: (所有列名, 主键列名, id列是否为主键)
        """
        id_column = id_column or self.primary_key
        with self._conn_ctx() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COLUMN_NAME, COLUMN_KEY
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
                """, (database, table))
                columns_info = cursor.fetchall()
                columns = [row['COLUMN_NAME'] for row in columns_info]
                pk_cols = [row['COLUMN_NAME'] for row in columns_info if row['COLUMN_KEY'] == 'PRI']
                id_is_pk = any(row['COLUMN_NAME'].lower() == id_column.lower() and row['COLUMN_KEY'] in ('PRI', 'UNI') for row in columns_info)
        return columns, pk_cols, id_is_pk

    def close(self) -> None:
        """
        关闭连接池。
        
        Returns:
            None
        """
        try:
            if hasattr(self, 'pool') and self.pool and not self._closed:
                self.pool.close()
                self._closed = True
                logger.debug("数据库连接池已关闭")
            else:
                logger.debug('连接池已关闭或不存在')
        except Exception as e:
            logger.error(f"关闭连接池时出错", {'error_type': type(e).__name__, 'error': str(e)})

    def __enter__(self) -> 'MySQLDeduplicator':
        """
        上下文管理器进入方法。
        
        Returns:
            MySQLDeduplicator: 实例自身。
        """
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """
        上下文管理器退出方法，自动关闭连接池。
        
        Args:
            exc_type (Optional[type]): 异常类型。
            exc_val (Optional[BaseException]): 异常值。
            exc_tb (Optional[Any]): 异常追踪。
        Returns:
            None
        """
        self.close()

    def reorder_id_column(
        self,
        database: str,
        table: Optional[str] = None,
        id_column: str = "id",
        dry_run: bool = False,
        auto_drop_backup: bool = True
    ) -> Any:
        """
        安全重排指定表或指定库下所有表的 id 列为顺序自增（1,2,3...）。
        
        Args:
            database (str): 数据库名。
            table (Optional[str]): 表名，None 时批量处理该库所有表。
            id_column (str): id 列名，默认 "id"。
            dry_run (bool): 是否为模拟运行。
            auto_drop_backup (bool): 校验通过后自动删除备份表。
        Returns:
            bool 或 dict: 单表时 bool，批量时 {表名: bool}
        """
        if not table:
            # 批量模式，对库下所有表执行
            try:
                all_tables = self._get_tables(database)
            except Exception as e:
                logger.error('获取库下所有表失败', {"库": database, "异常": str(e)})
                return {}
            results = {}
            for tbl in all_tables:
                try:
                    res = self.reorder_id_column(database, tbl, id_column, dry_run, auto_drop_backup)
                    results[tbl] = res
                except Exception as e:
                    logger.error('批量id重排异常', {"库": database, "表": tbl, "异常": str(e)})
                    results[tbl] = False
            logger.info('批量id重排完成', {"库": database, "结果": results})
            return results
        # 单表模式
        table_quoted = f"`{database}`.`{table}`"
        if not self._acquire_table_lock(database, table):
            logger.warning('表级锁获取失败，跳过id重排', {"库": database, "表": table})
            return False
        try:
            # 检查表是否存在
            if not self._check_table_exists(database, table):
                logger.warning('表不存在，跳过id重排', {"库": database, "表": table})
                return False
            # 检查id列、主键信息（用_get_table_info）
            columns, pk_cols, id_is_pk = self._get_table_info(database, table, id_column)
            if id_column not in columns:
                logger.warning('表无id列，跳过id重排', {"库": database, "表": table})
                return False
            # 检查主键是否为单列id
            if len(pk_cols) != 1 or pk_cols[0].lower() != id_column.lower():
                logger.warning('主键不是单列id，跳过id重排', {"库": database, "表": table, "主键列": pk_cols})
                return False
            # 检查外键约束
            with self._conn_ctx() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND REFERENCED_TABLE_NAME IS NOT NULL
                    """, (database, table))
                    if cursor.fetchone():
                        logger.warning('表存在外键约束，跳过id重排', {"库": database, "表": table})
                        return False
            # 获取表结构
            with self._conn_ctx() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SHOW CREATE TABLE {table_quoted}")
                    create_table_sql = cursor.fetchone()['Create Table']
            logger.debug('开始id重排', {"库": database, "表": table, "重排列": id_column, "试运行": dry_run, "DDL警告": "MySQL DDL操作不可回滚，建议提前备份！"})
            if dry_run:
                logger.info('dry_run模式，打印原表结构', {"库": database, "表": table, "建表语句": create_table_sql})
                return True
            temp_table = self._make_temp_table_name(table)
            temp_table_quoted = f"`{database}`.`{temp_table}`"
            backup_table = self._make_backup_table_name(table)
            backup_table_quoted = f"`{database}`.`{backup_table}`"
            try:
                with self._conn_ctx() as conn:
                    with conn.cursor() as cursor:
                        # 1. 创建临时表，结构同原表
                        try:
                            cursor.execute(f"CREATE TABLE {temp_table_quoted} LIKE {table_quoted}")
                        except Exception as e:
                            logger.error('创建临时表失败', {"库": database, "表": table, "异常": str(e)})
                            return False
                        # 2. 插入数据，id列用ROW_NUMBER重排（MySQL 8+）
                        all_cols = ','.join([f'`{col}`' for col in columns])
                        all_cols_noid = ','.join([f'`{col}`' for col in columns if col != id_column])
                        insert_sql = f"""
                            INSERT INTO {temp_table_quoted} ({all_cols})
                            SELECT ROW_NUMBER() OVER (ORDER BY `{id_column}` ASC) as `{id_column}`, {all_cols_noid}
                            FROM {table_quoted}
                        """
                        try:
                            cursor.execute(insert_sql)
                        except Exception as e:
                            logger.error('插入重排数据失败', {"库": database, "表": table, "异常": str(e)})
                            try:
                                cursor.execute(f"DROP TABLE IF EXISTS {temp_table_quoted}")
                            except Exception as drop_e:
                                logger.error('插入失败后删除临时表失败', {"库": database, "表": table, "异常": str(drop_e)})
                            return False
                        # 如果id不是主键，尝试加主键（如不冲突）
                        if not id_is_pk:
                            try:
                                cursor.execute(f"ALTER TABLE {temp_table_quoted} ADD PRIMARY KEY(`{id_column}`)")
                            except Exception as e:
                                logger.warning('id列加主键失败，可能已存在其他主键', {"库": database, "表": table, "异常": str(e)})
                        # 3. 原表重命名为备份，临时表重命名为正式表
                        try:
                            cursor.execute(f"RENAME TABLE {table_quoted} TO {backup_table_quoted}, {temp_table_quoted} TO {table_quoted}")
                        except Exception as e:
                            logger.error('RENAME TABLE失败', {"库": database, "表": table, "异常": str(e)})
                            # 回滚：删除临时表
                            try:
                                cursor.execute(f"DROP TABLE IF EXISTS {temp_table_quoted}")
                            except Exception as drop_e:
                                logger.error('RENAME失败后删除临时表失败', {"库": database, "表": table, "异常": str(drop_e)})
                            return False
                        # 4. 校验新表和备份表数据量一致
                        try:
                            cursor.execute(f"SELECT COUNT(*) as cnt FROM {table_quoted}")
                            new_cnt = cursor.fetchone()['cnt']
                            cursor.execute(f"SELECT COUNT(*) as cnt FROM {backup_table_quoted}")
                            old_cnt = cursor.fetchone()['cnt']
                        except Exception as e:
                            logger.error('校验数据量失败', {"库": database, "表": table, "异常": str(e)})
                            return False
                        if new_cnt != old_cnt:
                            logger.error('id重排后数据量不一致，自动回滚', {"库": database, "表": table, "新表": new_cnt, "备份表": old_cnt})
                            # 回滚：恢复原表
                            try:
                                cursor.execute(f"DROP TABLE {table_quoted}")
                                cursor.execute(f"RENAME TABLE {backup_table_quoted} TO {table_quoted}")
                            except Exception as e:
                                logger.error('回滚恢复原表失败', {"库": database, "表": table, "异常": str(e)})
                            return False
                        logger.info('id重排成功且数据量一致', {"库": database, "表": table, "新表": new_cnt, "备份表": old_cnt, "备份表名": backup_table})
                        # 5. 自动删除备份表
                        if auto_drop_backup:
                            try:
                                cursor.execute(f"DROP TABLE {backup_table_quoted}")
                                logger.info('已自动删除备份表', {"库": database, "表": table, "备份表名": backup_table})
                            except Exception as e:
                                logger.error('自动删除备份表失败', {"库": database, "表": table, "异常": str(e)})
                        return True
            except Exception as e:
                logger.error('id重排异常，准备回滚', {"库": database, "表": table, "异常": str(e)})
                # 回滚：如临时表存在则删掉，恢复原表结构
                with self._conn_ctx() as conn:
                    with conn.cursor() as cursor:
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {temp_table_quoted}")
                        except Exception as drop_e:
                            logger.error('回滚时删除临时表失败', {"库": database, "表": table, "异常": str(drop_e)})
                        # 恢复原表（如备份表存在）
                        try:
                            with self._conn_ctx() as conn2:
                                with conn2.cursor() as cursor2:
                                    if self._check_table_exists(database, backup_table):
                                        cursor2.execute(f"DROP TABLE IF EXISTS {table_quoted}")
                                        cursor2.execute(f"RENAME TABLE {backup_table_quoted} TO {table_quoted}")
                                        logger.info('已自动恢复原表', {"库": database, "表": table, "备份表名": backup_table})
                        except Exception as recover_e:
                            logger.error('回滚时恢复原表失败', {"库": database, "表": table, "异常": str(recover_e)})
                return False
        finally:
            self._release_table_lock(database, table)

    def _acquire_table_lock(self, database: str, table: str, timeout: int = 60) -> bool:
        """
        获取表级锁，防止多线程/多进程并发操作同一张表。
        Args:
            database (str): 数据库名。
            table (str): 表名。
            timeout (int): 等待锁的超时时间（秒）。
        Returns:
            bool: 是否成功获取锁。
        """
        key = f"{database.lower()}::{table.lower()}"
        start_time = time.time()
        while True:
            with self._lock:
                if key not in self._processing_tables:
                    self._processing_tables.add(key)
                    return True
            if time.time() - start_time > timeout:
                logger.warning('获取表级锁超时', {"库": database, "表": table, "timeout": timeout})
                return False
            time.sleep(0.2)

    def _release_table_lock(self, database: str, table: str) -> None:
        """
        释放表级锁。
        Args:
            database (str): 数据库名。
            table (str): 表名。
        Returns:
            None
        """
        key = f"{database.lower()}::{table.lower()}"
        with self._lock:
            self._processing_tables.discard(key)

    @staticmethod
    def _make_safe_table_name(base: str, prefix: str = '', suffix: str = '', max_length: int = 64) -> str:
        """
        生成安全的MySQL表名，确保总长度不超过max_length字节。
        :param base: 原始表名
        :param prefix: 前缀
        :param suffix: 后缀
        :param max_length: 最大长度，默认64
        :return: 安全表名
        """
        # 只允许字母数字下划线
        base = re.sub(r'[^a-zA-Z0-9_]', '_', base)
        prefix = re.sub(r'[^a-zA-Z0-9_]', '_', prefix)
        suffix = re.sub(r'[^a-zA-Z0-9_]', '_', suffix)
        remain = max_length - len(prefix) - len(suffix)
        if remain < 1:
            # 前后缀太长，直接截断
            return (prefix + suffix)[:max_length]
        return f"{prefix}{base[:remain]}{suffix}"[:max_length]

    def _make_temp_table_name(self, base: str) -> str:
        """
        生成临时表名，带有 temp_ 前缀和 _dedup_ 进程线程后缀。
        """
        suffix = f"_dedup_{os.getpid()}_{threading.get_ident()}"
        return self._make_safe_table_name(base, prefix="temp_", suffix=suffix)

    def _make_backup_table_name(self, base: str) -> str:
        """
        生成备份表名，带有 backup_ 前缀和时间戳+uuid后缀。
        """
        suffix = f"_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        return self._make_safe_table_name(base, prefix="backup_", suffix=suffix)


def main():
    logger.info('去重任务开始')
    dir_path = os.path.expanduser("~")
    parser = myconf.ConfigParser()
    host, port, username, password = parser.get_section_values(
        file_path=os.path.join(dir_path, 'spd.txt'),
        section='mysql',
        keys=['host', 'port', 'username', 'password'],
    )
    # host = 'localhost'
    
    deduplicator = MySQLDeduplicator(
        username=username,
        password=password,
        host=host,
        port=int(port),
        max_workers= 2,
        batch_size=1000,
        skip_system_dbs=True,
        max_retries=3,
        retry_waiting_time=5,
        pool_size=20,
        mincached=5,
        maxcached=10,
        # recent_month=1,
        # date_range=['2025-06-09', '2025-06-10'],
        exclude_columns=['更新时间'],
        exclude_databases=['cookie文件', '日志', '视频数据', '云电影'],
        # exclude_tables={
        #     '推广数据2': [
        #         '地域报表_城市_2025_04', 
        #         # '地域报表_城市_2025_04_copy1', 
        #     ],
        #     "生意参谋3": [
        #         "商品排行_2025",
        #     ],
        # },
        keep_order='MAX',  # 保留重复组中指定列的最大值
    )

    # 全库去重(单线程)
    # deduplicator.deduplicate_all(dry_run=False, parallel=True, reorder_id=True)

    # # 指定数据库去重(多线程)
    # deduplicator.deduplicate_database('数据引擎2', dry_run=False, parallel=True, reorder_id=True)

    # # 指定表去重(使用特定列)
    deduplicator.deduplicate_table(
        '生意参谋3', 
        '新品追踪_旧接口_2025', 
        columns=['商品id', '累计商品浏览量', '累计商品访客数'], 
        dry_run=False, 
        reorder_id=True,
        )

    # # 重排id列
    # deduplicator.reorder_id_column('my_db', 'my_table', 'id', dry_run=False, auto_drop_backup=True)

    # 关闭连接
    deduplicator.close()
    logger.info('去重任务结束')


if __name__ == '__main__':
    main()
    pass
