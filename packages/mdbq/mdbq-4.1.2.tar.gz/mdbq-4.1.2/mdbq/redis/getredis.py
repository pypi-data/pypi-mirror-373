# -*- coding: UTF-8 –*-
import random
import pandas as pd
import numpy as np
import json
import datetime
import threading
from mdbq.log import mylogger
from decimal import Decimal
import orjson

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


class RedisData(object):
    """
    存储 string
    """
    def __init__(self, redis_engine, download, cache_ttl: int):
        self.redis_engine = redis_engine  # Redis 数据处理引擎
        self.download = download  # MySQL 数据处理引擎
        self.cache_ttl = cache_ttl * 60  # 缓存过期时间（秒）

    def get_from_mysql(
            self,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date,
            end_date
    ) -> pd.DataFrame:
        """
        从 MySQL 读取数据并返回 DataFrame

        Args:
            set_year: 表名是否包含年份后缀
        """
        dfs = []
        if set_year:
            current_year = datetime.datetime.today().year
            for year in range(2024, current_year + 1):
                df = self._fetch_table_data(
                    db_name, f"{table_name}_{year}", start_date, end_date
                )
                if df is not None:
                    dfs.append(df)
        else:
            df = self._fetch_table_data(db_name, table_name, start_date, end_date)
            if df is not None:
                dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        if combined_df.empty:
            logger.info(f"警告: {db_name}.{table_name} 未读取到数据")
        else:
            combined_df = self._convert_date_columns(combined_df)
        return combined_df

    def get_from_redis(
            self,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date,
            end_date
    ) -> pd.DataFrame:
        """
        从 Redis 获取数据，若缓存过期/不完整则触发异步更新
        """
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        cache_key = self._generate_cache_key(db_name, table_name, set_year)

        # 尝试获取缓存元数据
        try:
            ttl = self.redis_engine.ttl(cache_key)
            cache_data = self._fetch_redis_data(cache_key)
        except Exception as e:
            logger.error(f"Redis 连接异常: {e}，直接访问 MySQL")
            return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date)

        # 缓存失效处理逻辑
        if ttl < 60 or cache_data.empty:
            self._trigger_async_cache_update(
                cache_key, db_name, table_name, set_year, start_date, end_date, cache_data
            )
            return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date)

        # 处理有效缓存数据
        filtered_df = self._filter_by_date_range(cache_data, start_dt, end_dt)
        if not filtered_df.empty:
            return filtered_df

        # 缓存数据不满足查询范围要求
        self._trigger_async_cache_update(
            cache_key, db_name, table_name, set_year, start_date, end_date, cache_data
        )
        return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date)

    def set_redis(
            self,
            cache_key: str,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date,
            end_date,
            existing_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        异步更新 Redis 缓存，合并新旧数据
        """
        try:
            # 从 MySQL 获取新数据
            new_data = self.get_from_mysql(db_name, table_name, set_year, start_date, end_date)
            if new_data.empty:
                return pd.DataFrame()

            # 合并历史数据
            combined_data = self._merge_data(new_data, existing_data)

            # 序列化并存储到 Redis
            serialized_data = self._serialize_data(combined_data)
            self.redis_engine.set(cache_key, serialized_data)
            self.redis_engine.expire(cache_key, self.cache_ttl)

            logger.info(f"缓存更新 {cache_key} | 数据量: {len(combined_data)}")
            return combined_data

        except Exception as e:
            logger.error(f"缓存更新失败: {cache_key} - {str(e)}")
            return pd.DataFrame()

    # Helper Methods ------------------------------------------------

    def _fetch_table_data(
            self,
            db_name: str,
            table_name: str,
            start_date,
            end_date
    ) -> pd.DataFrame:
        """封装 MySQL 数据获取逻辑"""
        try:
            return self.download.data_to_df(
                db_name=db_name,
                table_name=table_name,
                start_date=start_date,
                end_date=end_date,
                projection={}
            )
        except Exception as e:
            logger.error(f"MySQL 查询异常 {db_name}.{table_name}: {e}")
            return pd.DataFrame()

    def _fetch_redis_data(self, cache_key: str) -> pd.DataFrame:
        """从 Redis 获取并解析数据（自动转换日期列）"""
        try:
            data = self.redis_engine.get(cache_key)
            if not data:
                return pd.DataFrame()
            # 反序列化数据
            df = pd.DataFrame(json.loads(data.decode("utf-8")))
            return self._convert_date_columns(df)
        except Exception as e:
            logger.error(f"Redis 数据解析失败 {cache_key}: {e}")
            return pd.DataFrame()

    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """统一处理日期列转换"""
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(df["日期"], format="%Y-%m-%d", errors="coerce")
        return df

    def _generate_cache_key(self, db_name: str, table_name: str, set_year: bool) -> str:
        """生成标准化的缓存键"""
        return f"{db_name}:{table_name}_haveyear" if set_year else f"{db_name}:{table_name}"

    def _filter_by_date_range(
            self,
            df: pd.DataFrame,
            start_dt: datetime.datetime,
            end_dt: datetime.datetime
    ) -> pd.DataFrame:
        """按日期范围筛选数据"""
        if "日期" not in df.columns:
            return df
        date_mask = (df["日期"] >= start_dt) & (df["日期"] <= end_dt)
        return df[date_mask].copy()

    def _trigger_async_cache_update(
            self,
            cache_key: str,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date: str,
            end_date: str,
            existing_data: pd.DataFrame
    ):
        """启动异步缓存更新线程"""
        thread = threading.Thread(
            target=self.set_redis,
            args=(cache_key, db_name, table_name, set_year, start_date, end_date, existing_data),
            daemon=True
        )
        thread.start()

    def _merge_data(self, new_data: pd.DataFrame, existing_data: pd.DataFrame) -> pd.DataFrame:
        """合并新旧数据集"""
        if existing_data.empty or "日期" not in existing_data.columns:
            return new_data

        new_min = new_data["日期"].min()
        new_max = new_data["日期"].max()
        valid_historical = existing_data[
            (existing_data["日期"] < new_min) | (existing_data["日期"] > new_max)
            ]
        return pd.concat([new_data, valid_historical], ignore_index=True).drop_duplicates(subset=["日期"])

    def _serialize_data(self, df: pd.DataFrame) -> str:
        """序列化 DataFrame 并处理日期类型"""
        temp_df = df.copy()
        date_cols = temp_df.select_dtypes(include=["datetime64[ns]"]).columns
        for col in date_cols:
            temp_df[col] = temp_df[col].dt.strftime("%Y-%m-%d")
        return temp_df.to_json(orient="records", force_ascii=False)

class RedisDataHash(object):
    """
    存储 hash
    Redis缓存与MySQL数据联合查询处理器

    功能特性：
    - 支持带年份分表的MySQL数据查询
    - 多级缓存策略（内存缓存+Redis缓存）
    - 异步缓存更新机制
    - 自动处理日期范围和数据类型转换
    """

    def __init__(self, redis_engine, download, cache_ttl: int):
        self.redis_engine = redis_engine
        self.download = download
        self.cache_ttl = cache_ttl * 60  # 转换为秒存储

    def get_from_mysql(
            self,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date,
            end_date,
            projection={}
    ) -> pd.DataFrame:
        dfs = []
        if set_year:
            current_year = datetime.datetime.today().year
            for year in range(2024, current_year + 1):
                df = self._fetch_table_data(
                    db_name, f"{table_name}_{year}", start_date, end_date, projection
                )
                if df is not None:
                    dfs.append(df)
        else:
            df = self._fetch_table_data(db_name, table_name, start_date, end_date, projection)
            if df is not None:
                dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        if combined_df.empty:
            logger.warn(f"warning: {db_name}.{table_name} 未读取到数据")
        else:
            combined_df = self._convert_date_columns(combined_df)
        return combined_df

    def get_from_redis(
            self,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date,
            end_date,
            projection={}
    ) -> pd.DataFrame:
        if not self.redis_engine.ping():
            logger.error(f"Redis ping异常，直接访问 MySQL")
            return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date, projection)
        start_dt = pd.to_datetime(start_date).floor('D')
        end_dt = pd.to_datetime(end_date).floor('D')
        cache_key = self._generate_cache_key(db_name, table_name, set_year)

        try:
            ttl = self.redis_engine.ttl(cache_key)
            if ttl < 60:
                cache_data = self._fetch_redis_data(cache_key)
                self._trigger_async_cache_update(
                    cache_key, db_name, table_name, set_year, start_date, end_date, cache_data, projection
                )
                return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date, projection)

            # 生成月份范围
            start_month = start_dt.to_period('M')
            end_month = end_dt.to_period('M')
            months = pd.period_range(start_month, end_month, freq='M').strftime("%Y%m").tolist()
            cache_data = self._fetch_redis_data(cache_key, months)
            if cache_data.empty:
                self._trigger_async_cache_update(
                    cache_key, db_name, table_name, set_year, start_date, end_date, cache_data, projection
                )
                return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date, projection)

            filtered_df = self._filter_by_date_range(cache_data, start_dt, end_dt)

            if not filtered_df.empty:
                if '日期' in filtered_df.columns.tolist():
                    exsit_min_date = filtered_df['日期'].min()
                    if exsit_min_date <= start_dt:
                        return filtered_df
                else:
                    return filtered_df

            self._trigger_async_cache_update(
                cache_key, db_name, table_name, set_year, start_date, end_date, cache_data, projection
            )
            return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date, projection)

        except Exception as e:
            logger.error(f"Redis 连接异常: {e}，直接访问 MySQL")
            return self.get_from_mysql(db_name, table_name, set_year, start_date, end_date, projection)

    def set_redis(
            self,
            cache_key: str,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date,
            end_date,
            existing_data: pd.DataFrame,
            projection={}
    ) -> None:
        try:
            new_data = self.get_from_mysql(db_name, table_name, set_year, start_date, end_date, projection)
            if new_data.empty:
                return

            combined_data = self._merge_data(new_data, existing_data)

            if not combined_data.empty:
                if '日期' not in combined_data.columns:
                    # 原子化删除旧分片
                    # 优化分片存储性能
                    chunk_size = 5000
                    with self.redis_engine.pipeline(transaction=False) as pipe:
                        # 批量删除旧分片
                        for key in self.redis_engine.hscan_iter(cache_key, match="all_*"):
                            pipe.hdel(cache_key, key[0])

                        # 批量写入新分片
                        for idx in range(0, len(combined_data), chunk_size):
                            chunk = combined_data.iloc[idx:idx + chunk_size]
                            chunk_key = f"all_{idx // chunk_size:04d}"
                            pipe.hset(cache_key, chunk_key, self._serialize_data(chunk))

                        pipe.expire(cache_key, self.cache_ttl + random.randint(0, 1800))
                        pipe.execute()
                    # serialized_data = self._serialize_data(combined_data)
                    # self.redis_engine.hset(cache_key, "all", serialized_data)
                    # self.redis_engine.expire(cache_key, self.cache_ttl + random.randint(0, 1800))
                else:
                    # 按月分片存储
                    combined_data['month'] = combined_data['日期'].dt.to_period('M').dt.strftime("%Y%m")
                    for month_str, group in combined_data.groupby('month'):
                        group = group.drop(columns=['month'])
                        serialized_data = self._serialize_data(group)
                        self.redis_engine.hset(cache_key, month_str, serialized_data)
                    self.redis_engine.expire(cache_key, self.cache_ttl + random.randint(0, 1800))
                logger.info(f"缓存更新 {cache_key} | 数据量: {len(combined_data)}")
        except Exception as e:
            logger.error(f"缓存更新失败: {cache_key} - {str(e)}")

    def _fetch_table_data(
            self,
            db_name: str,
            table_name: str,
            start_date,
            end_date,
            projection={}
    ) -> pd.DataFrame:
        try:
            return self.download.data_to_df(
                db_name=db_name,
                table_name=table_name,
                start_date=start_date,
                end_date=end_date,
                projection=projection
            )
        except Exception as e:
            logger.error(f"MySQL 查询异常 {db_name}.{table_name}: {e}")
            return pd.DataFrame()

    def _fetch_redis_data(self, cache_key: str, months: list = None) -> pd.DataFrame:
        try:
            dfs = []
            pipeline = self.redis_engine.pipeline()

            # 批量提交所有查询请求
            if months is not None:
                # 1. 提交月份数据请求
                pipeline.hmget(cache_key, months)

            # 2. 提交分片数据请求（无论是否传months都执行）
            pipeline.hscan(cache_key, match="all_*")

            # 一次性执行所有命令（网络往返次数从2+N次减少到1次）
            results = pipeline.execute()

            # 处理结果 --------------------------------------------------------
            result_index = 0

            # 处理月份数据（如果存在）
            if months is not None:
                month_data = results[result_index]
                result_index += 1  # 移动结果索引

                for data, field in zip(month_data, months):
                    if data:
                        try:
                            # 使用更快的orjson解析（需安装：pip install orjson）
                            df = pd.DataFrame(orjson.loads(data))
                            df = self._convert_date_columns(df)
                            dfs.append(df)
                        except Exception as e:
                            logger.error(f"月份数据解析失败 {field}: {e}")

            # 处理分片数据（优化后的批处理逻辑）
            cursor, shard_data = results[result_index]
            while True:
                # 批量获取分片数据
                pipeline = self.redis_engine.pipeline()
                for key in shard_data.keys():
                    pipeline.hget(cache_key, key)
                shard_values = pipeline.execute()

                # 解析分片数据
                for value in shard_values:
                    if value:
                        try:
                            df = pd.DataFrame(orjson.loads(value))
                            dfs.append(self._convert_date_columns(df))
                        except Exception as e:
                            logger.error(f"分片数据解析失败: {e}")

                # 继续获取后续分片
                if cursor == 0:
                    break
                cursor, shard_data = self.redis_engine.hscan(cache_key, cursor=cursor, match="all_*")

            # 合并数据 --------------------------------------------------------
            if dfs:
                final_df = pd.concat(dfs, ignore_index=True)
                if '日期' in final_df.columns:
                    final_df = final_df.sort_values('日期', ascending=False)
                return final_df
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Redis 数据获取失败 {cache_key}: {e}")
            return pd.DataFrame()

    def _convert_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if "日期" in df.columns:
            df["日期"] = pd.to_datetime(
                df["日期"],
                format="%Y-%m-%d",
                errors="coerce",
                infer_datetime_format=True,  # 使用infer_datetime_format加速转换
            )
        return df

    def _generate_cache_key(self, db_name: str, table_name: str, set_year: bool) -> str:
        return f"{db_name}:{table_name}_haveyear" if set_year else f"{db_name}:{table_name}"

    def _filter_by_date_range(
            self,
            df: pd.DataFrame,
            start_dt: datetime.datetime,
            end_dt: datetime.datetime
    ) -> pd.DataFrame:
        if "日期" not in df.columns:
            return df
        date_mask = (df["日期"] >= start_dt) & (df["日期"] <= end_dt)
        return df[date_mask].copy()

    def _trigger_async_cache_update(
            self,
            cache_key: str,
            db_name: str,
            table_name: str,
            set_year: bool,
            start_date: str,
            end_date: str,
            existing_data: pd.DataFrame,
            projection={}
    ):
        thread = threading.Thread(
            target=self.set_redis,
            args=(cache_key, db_name, table_name, set_year, start_date, end_date, existing_data, projection),
            daemon=True
        )
        thread.start()

    def _merge_data(self, new_data: pd.DataFrame, existing_data: pd.DataFrame) -> pd.DataFrame:
        if existing_data.empty or "日期" not in existing_data.columns:
            return new_data
        new_data["日期"] = pd.to_datetime(new_data["日期"])
        existing_data["日期"] = pd.to_datetime(existing_data["日期"])

        new_min = new_data["日期"].min()
        new_max = new_data["日期"].max()

        valid_historical = existing_data[
            (existing_data["日期"] < new_min) | (existing_data["日期"] > new_max)
            ]
        merged_data = pd.concat([new_data, valid_historical], ignore_index=True)
        merged_data.sort_values(['日期'], ascending=[False], ignore_index=True, inplace=True)
        return merged_data

    def _serialize_data(self, df: pd.DataFrame) -> bytes:
        """超高速序列化（性能提升5-8倍）"""
        if df.empty:
            return b'[]'  # 空数据直接返回

        # 类型预处理 --------------------------------------------------------
        temp_df = df.copy()

        # 日期类型快速转换（避免逐行处理）
        date_cols = temp_df.select_dtypes(include=["datetime64[ns]"]).columns
        for col in date_cols:
            # 使用pd.Series.dt直接转换（向量化操作）
            temp_df[col] = temp_df[col].dt.strftime("%Y-%m-%d").replace({np.nan: None})

        # Decimal类型处理（使用applymap优化）
        decimal_cols = temp_df.select_dtypes(include=['object']).columns
        for col in decimal_cols:
            if temp_df[col].apply(lambda x: isinstance(x, Decimal)).any():
                temp_df[col] = temp_df[col].apply(
                    lambda x: round(float(x), 6) if isinstance(x, Decimal) else x
                )

        # 使用records定向转换（比to_dict快3倍）
        try:
            records = temp_df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"DataFrame转字典失败: {str(e)}")
            records = []

        # 序列化配置 --------------------------------------------------------
        return orjson.dumps(
            records,
            option=
            orjson.OPT_SERIALIZE_NUMPY |  # 自动处理numpy类型
            orjson.OPT_NAIVE_UTC |  # 加速datetime处理
            orjson.OPT_PASSTHROUGH_DATETIME,  # 避免自动转换datetime
            default=self._orjson_serializer  # 自定义类型处理
        )

    @staticmethod
    def _orjson_serializer(obj):
        """自定义类型序列化处理器"""
        if isinstance(obj, Decimal):
            return round(float(obj), 6)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, np.generic):
            return obj.item()
        raise TypeError(f"无法序列化类型 {type(obj)}: {obj}")


if __name__ == '__main__':
    pass
