import re
import pymysql
from typing import List, Dict, Any, Tuple
from mdbq.log import mylogger
from mdbq.myconf import myconf
from dbutils.pooled_db import PooledDB
import os

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

class UniqueManager:
    """
    MySQL唯一约束批量添加工具
    """
    def __init__(self, username: str, password: str, host: str, port: int = 3306):
        """
        初始化MySQL连接参数和日志，创建连接池
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = int(port)
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=0,
            maxcached=0,
            blocking=True,
            host=self.host,
            user=self.username,
            password=self.password,
            port=self.port,
            charset='utf8mb4',
            autocommit=True
        )

    def add_unique(self, my_databases: List[Dict[str, Any]]) -> None:
        """
        主入口，遍历所有库表，批量添加唯一约束
        """
        total_databases, success_cnt, fail_cnt, skip_cnt, detail_results = 0, 0, 0, 0, []
        for db_group in my_databases:
            for db_name, tables in db_group.items():
                total_databases += 1
                db_result = self._process_database(db_name, tables)
                success_cnt += db_result['success_cnt']
                fail_cnt += db_result['fail_cnt']
                skip_cnt += db_result['skip_cnt']
                detail_results.extend(db_result['details'])
        # 分组详细结果
        success_list = [d for d in detail_results if d.get('result') == '成功']
        fail_list = [d for d in detail_results if d.get('result') == '失败']
        skip_list = [d for d in detail_results if d.get('result') == '跳过']
        total_tables = len(success_list) + len(fail_list) + len(skip_list)  # 处理过的表数量
        if success_list:
            logger.info('成功表', {
                '数量': len(success_list),
                '详情': success_list
            })
        if fail_list:
            logger.error('失败表', {
                '数量': len(fail_list),
                '详情': fail_list
            })
        if skip_list:
            logger.info('跳过表', {
                '数量': len(skip_list),
                '详情': skip_list
            })
        logger.info('全部执行完成', {
            '库统计': total_databases,
            '表统计': total_tables,
            '成功': success_cnt,
            '失败': fail_cnt,
            '跳过': skip_cnt
        })

    def _process_database(self, db_name: str, tables: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个数据库下所有表，支持模糊匹配表名，限定在当前数据库
        """
        # 用于统计所有被处理过的表名
        processed_tables = set()
        success_cnt, fail_cnt, skip_cnt = 0, 0, 0
        details = []
        # 获取当前数据库下所有表名
        conn = self.pool.connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{db_name}`")
                cursor.execute("SHOW TABLES")
                all_tables = [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
        all_table_count = len(all_tables)  # 新增：该库下所有表数量
        # 只在当前db_name下做模糊匹配
        for table_pattern, unique_keys_list in tables.items():
            # 支持通配符 * 或 ?，转为正则
            if '*' in table_pattern or '?' in table_pattern:
                regex = re.compile('^' + table_pattern.replace('*', '.*').replace('?', '.') + '$')
                matched_tables = [t for t in all_tables if regex.match(t)]
            else:
                # 也支持部分匹配（如“明细”）
                matched_tables = [t for t in all_tables if table_pattern in t]
                if table_pattern in all_tables:
                    matched_tables.append(table_pattern)
            matched_tables = list(set(matched_tables))
            if not matched_tables:
                logger.warning('未找到匹配的数据表', {'库': db_name, '表模式': table_pattern})
                skip_cnt += 1
                details.append({'库': db_name, '表': table_pattern, 'result': '跳过'})
                continue
            for real_table in matched_tables:
                processed_tables.add(real_table)
                try:
                    res = self._process_table(db_name, real_table, unique_keys_list)
                    success_cnt += res['success_cnt']
                    fail_cnt += res['fail_cnt']
                    skip_cnt += res['skip_cnt']
                    details.extend(res['details'])
                except Exception as e:
                    logger.error('唯一约束失败', {'库': db_name, '表': real_table, 'error': str(e)})
                    fail_cnt += 1
                    details.append({'库': db_name, '表': real_table, 'result': '失败'})
        table_count = len(processed_tables)
        return {'table_count': table_count, 'all_table_count': all_table_count, 'success_cnt': success_cnt, 'fail_cnt': fail_cnt, 'skip_cnt': skip_cnt, 'details': details}

    def _process_table(self, db_name: str, table_name: str, unique_keys_list: List[List[str]]) -> Dict[str, Any]:
        """
        处理单个表的所有唯一约束，返回本表的成功/失败/跳过计数和详细结果
        修复唯一约束重命名后原约束未删除的问题。
        """
        success_cnt, fail_cnt, skip_cnt = 0, 0, 0
        details = []
        conn = self.pool.connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{db_name}`")
                # 获取所有唯一索引信息
                cursor.execute(f"SHOW INDEX FROM `{table_name}` WHERE Non_unique=0")
                indexes = cursor.fetchall()
                from collections import defaultdict
                key_columns = defaultdict(list)
                key_names = set()
                for idx in indexes:
                    key_name = idx[2]
                    col_name = idx[4]
                    seq_in_index = idx[3]
                    key_columns[key_name].append((seq_in_index, col_name))  # SEQ_IN_INDEX, COLUMN_NAME
                    key_names.add(key_name)
                # 统计唯一索引数量
                unique_count = len(key_columns)
                if unique_count >= 20:
                    logger.warning('唯一索引数量超限，跳过全部', {'库': db_name, '表': table_name, '唯一索引数': unique_count})
                    for unique_cols in unique_keys_list:
                        clean_cols = [self._clean_column_name(col) for col in unique_cols]
                        details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '跳过', '原因': '唯一索引数量超限'})
                        skip_cnt += 1
                    return {'success_cnt': success_cnt, 'fail_cnt': fail_cnt, 'skip_cnt': skip_cnt, 'details': details}
                for idx, unique_cols in enumerate(unique_keys_list):
                    clean_cols = [self._clean_column_name(col) for col in unique_cols]
                    target_name = self._gen_constraint_name(table_name, clean_cols, idx)
                    # 检查是否有相同字段组合的唯一索引（顺序必须一致）
                    found = False
                    found_key_name = None
                    for kname, col_seq_list in key_columns.items():
                        sorted_cols = [col for _, col in sorted(col_seq_list)]
                        if sorted_cols == clean_cols:
                            found = True
                            found_key_name = kname
                            break
                    if found:
                        if found_key_name == target_name:
                            # 名称和字段都相同，跳过
                            skip_cnt += 1
                            details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '跳过', '原因': '名称和字段都相同'})
                        else:
                            # 字段相同但名称不同，重命名（先删后加，确保原唯一约束被删除）
                            try:
                                cursor.execute(f"ALTER TABLE `{table_name}` DROP INDEX `{found_key_name}`")
                                # 刷新索引信息，防止后续误判
                                cursor.execute(f"SHOW INDEX FROM `{table_name}` WHERE Non_unique=0")
                                # 再添加新唯一约束
                                self._add_unique(cursor, table_name, clean_cols, target_name)
                                logger.info('唯一约束重命名成功', {'库': db_name, '表': table_name, '唯一约束': clean_cols, '原名': found_key_name, '新名': target_name})
                                success_cnt += 1
                                details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '成功', '操作': '重命名', '原名': found_key_name, '新名': target_name})
                            except Exception as e:
                                logger.error('唯一约束重命名失败', {'库': db_name, '表': table_name, '唯一约束': clean_cols, '原名': found_key_name, '新名': target_name, 'error': str(e)})
                                fail_cnt += 1
                                details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '失败', '操作': '重命名', '原名': found_key_name, '新名': target_name, 'error': str(e)})
                    else:
                        # 字段组合不存在，直接添加
                        try:
                            self._add_unique(cursor, table_name, clean_cols, target_name)
                            logger.info('添加唯一约束成功', {'库': db_name, '表': table_name, '唯一约束': clean_cols})
                            success_cnt += 1
                            details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '成功', '操作': '添加'})
                        except Exception as e:
                            err_str = str(e)
                            if 'Duplicate key name' in err_str:
                                skip_cnt += 1
                                details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '跳过', '原因': '唯一约束名已存在'})
                                logger.info('唯一约束名已存在，跳过', {'库': db_name, '表': table_name, '唯一约束': clean_cols, 'error': err_str})
                            else:
                                logger.error('添加唯一约束失败', {'库': db_name, '表': table_name, '唯一约束': clean_cols, 'error': err_str})
                                fail_cnt += 1
                                details.append({'库': db_name, '表': table_name, '唯一约束': clean_cols, 'result': '失败', '操作': '添加', 'error': err_str})
        finally:
            conn.close()
        return {'success_cnt': success_cnt, 'fail_cnt': fail_cnt, 'skip_cnt': skip_cnt, 'details': details}

    def _clean_column_name(self, col: str) -> str:
        """
        支持中英文字段名，清理非法字符，只保留中英文、数字、下划线，并统一转为小写
        """
        col = col.strip()
        col = re.sub(r'[^\w\u4e00-\u9fff$]', '_', col)
        col = re.sub(r'_+', '_', col).strip('_')
        col = col.lower()
        if len(col) > 64:
            col = col[:64]
        return col

    def _gen_constraint_name(self, table: str, cols: List[str], idx: int) -> str:
        """
        生成唯一约束名，最长64字符，所有列名先规范化，保证与实际索引字段一致
        """
        base = f"uniq"
        for col in cols:
            clean_col = self._clean_column_name(col)
            base += f"_{clean_col}"
        if len(base) > 64:
            base = base[:63] + 'x'
        return base

    def _unique_exists(self, cursor, table: str, cols: List[str]) -> bool:
        """
        检查唯一约束是否已存在，支持多列唯一约束
        """
        sql = f"SHOW INDEX FROM `{table}` WHERE Non_unique=0"
        cursor.execute(sql)
        indexes = cursor.fetchall()
        # MySQL返回的索引信息，需按Key_name分组，收集每个唯一索引的所有列
        from collections import defaultdict
        key_columns = defaultdict(list)
        for idx in indexes:
            key_name = idx[2]  # Key_name
            col_name = idx[4]  # Column_name
            key_columns[key_name].append(col_name)
        for col_list in key_columns.values():
            if set(col_list) == set(cols) and len(col_list) == len(cols):
                return True
        return False

    def _add_unique(self, cursor, table: str, cols: List[str], constraint_name: str) -> None:
        """
        添加唯一约束
        """
        cols_sql = ','.join([f'`{c}`' for c in cols])
        sql = f"ALTER TABLE `{table}` ADD CONSTRAINT `{constraint_name}` UNIQUE ({cols_sql})"
        cursor.execute(sql)


def main():
    dir_path = os.path.expanduser("~")
    parser = myconf.ConfigParser()
    host, port, username, password = parser.get_section_values(
        file_path=os.path.join(dir_path, 'spd.txt'),
        section='mysql',
        keys=['host', 'port', 'username', 'password'],
    )
    # host = 'localhost'

    my_databases = [
        {
            # '京东数据3': {
            #     "u_商品明细": [['日期', '店铺名称', '商品id', '访客数', '浏览量']],
            #     "商智_店铺来源": [['日期', '店铺名称', '一级来源', '二级来源', '三级来源', '访客数', '浏览量']],
            #     '推广数据_京准通': [['日期', '店铺名称', '产品线', '触发sku_id', '跟单sku_id', 'spu_id', '花费', '展现数', '点击数']],
            #     '推广数据_关键词报表': [['日期', '店铺名称', '产品线', '计划id', '搜索词', '关键词', '花费', '展现数', '点击数']],
            #     '推广数据_搜索词报表': [['日期', '店铺名称', '产品线', '搜索词', '花费', '展现数', '点击数']],
            #     '推广数据_全站营销': [['日期', '店铺名称', '产品线', '花费']],
            # },
            # "人群画像2": {
            #     "*": [['日期', '账户id', '人群id', '画像id', '标签id']],
            # },
            # "属性设置3": {
            #     "京东商品属性": [['sku_id']],
            #     "商品sku属性": [['日期', 'sku_id']],
            #     "商品主图视频": [['日期', '商品主图', '750主图', '商品视频']],
            #     "商品类目属性": [['日期', '商品id']],
            #     "商品素材中心": [['商品id']],
            #     "商品索引表_主推排序调用": [['商品id']],
            #     "地理区域": [['省份']],
            #     "城市等级": [['城市']],
            #     "货品年份基准": [['平台', '上市年份']],
            # },
            # "市场数据3": {
            #     "京东_商家榜单": [['日期', '分类', '类型', '店铺名称', '成交金额指数']],
            #     "市场排行_2025": [['日期', '接口类型', '类目等级', '类目名称', '商品id']],
            #     "搜索流失_细分单品": [['日期', '店铺名称', '分类', '商品id', '竞品id', '竞店id', '统计周期']],
            #     "搜索流失榜单": [['日期', '店铺名称', '分类', '商品id', '统计周期']],
            #     "浏览流失_细分单品": [['日期', '店铺名称', '分类', '商品id', '竞品id', '竞店id', '统计周期']],
            #     "浏览流失榜单": [['日期', '店铺名称', '分类', '商品id', '统计周期']],
            #     "淘宝店铺数据": [['日期', '店铺id', '商品id']],
            #     "竞店流失": [['日期', '店铺名称', '竞店商家id']],
            # },
            # "数据引擎2": {
            #     "供给投入": [['日期', '报告id', '品牌ID', '类目Id', '指标名称', '父级指标']],
            #     "新老客贡献": [['日期', '报告id', '品牌ID', '类目Id']],
            #     "进店搜索词": [['日期', '报告id', '品牌ID', '搜索词', '类目Id']],
            # },
            # "爱库存2": {
            #     "sku榜单": [['日期', '平台', '店铺名称', '条码']],
            #     "spu榜单": [['日期', '平台', '店铺名称', '商品款号', '访客量']],
            # },
            # "生意参谋3": {
            #     "crm成交客户": [['客户id']],
            #     "商品排行": [['日期', '店铺名称', '商品id']],
            #     "流量来源构成": [['日期', '店铺名称', '来源构成', '类别', '一级来源', '二级来源', '三级来源']],
            #     "手淘搜索": [['日期', '店铺名称', '搜索词', '词类型', '访客数']],
            #     "新品追踪": [['日期', '店铺名称', '商品id']],
            #     "直播分场次效果": [['场次id']],
            # },
            # "生意经3": {
            #     "sku销量_按名称": [['日期', '店铺名称', '宝贝id', 'sku名称', '销售额']],
            #     "sku销量_按商家编码": [['日期', '店铺名称', '宝贝id', 'sku编码', '销售额']],
            #     "地域分析_城市": [['日期', '店铺名称', '城市', '销售额']],
            #     "地域分析_省份": [['日期', '店铺名称', '省份', '销售额']],
            #     "宝贝指标": [['日期', '店铺名称', '宝贝id', '销售额']],
            #     "店铺销售指标": [['日期', '店铺名称', '销售额']],
            #     "订单数据": [['日期', '店铺名称', '订单号', '商品链接', '净销售额_已扣退款_分摊邮费优惠等', '退款额']],
            # },
            # "达摩盘3": {
            #     "dmp人群报表": [['日期', '店铺名称', '人群id', '推广单元信息', '消耗_元', '展现量']],
            #     "全域洞察": [['日期', '起始日期', '店铺名称', '场景id', '父渠道id', '展现量', '花费']],
            #     "关键词_人群画像_关联购买类目": [['日期', '数据周期', '店铺名称', '关键词', '关联类目id']],
            #     "关键词_人群画像_性别": [['日期', '数据周期', '店铺名称', '关键词', '词']],
            #     "关键词_人群画像_消费层级": [['日期', '数据周期', '店铺名称', '关键词', '层级id', '层级值', '标签分类']],
            #     "关键词_市场总结": [['日期', '关键词', '数据周期', '板块']],
            #     "关键词_市场趋势": [['日期', '关键词']],
            #     "关键词_竞争透视_地域分布": [['日期', '数据周期', '店铺名称', '关键词', '省份id']],
            #     "关键词_竞争透视_搜索时段分布": [['日期', '数据周期', '店铺名称', '关键词', '时段']],
            #     "关键词_竞争透视_搜索资源位": [['日期', '数据周期', '店铺名称', '关键词', '渠道id']],
            #     "关键词_竞争透视_竞争度": [['日期', '数据周期', '店铺名称', '关键词', '出价区间']],
            #     "店铺deeplink人群洞察": [['日期', '店铺名称', '人群类型', '人群规模', '人群总计']],
            #     "我的人群属性": [['日期', '人群id']],
            #     "货品_潜品加速": [['日期', '店铺名称', '商品id']],
            #     "货品洞察_全店单品": [['日期', '店铺名称', '数据周期', '商品id']],
            #     "货品洞察_品类洞察": [['日期', '店铺名称', '数据周期', '叶子类目名称']],
            # },

            # "聚合数据": {
            #     "多店推广场景_按日聚合": [["日期", "店铺名称", "营销场景", "花费"]],
            #     "天猫_主体报表": [['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '花费']],
            # }
        }
    ]
    manager = UniqueManager(
        username=username,
        password=password,
        host=host,
        port=int(port)
    )
    manager.add_unique(my_databases)


if __name__ == "__main__":
    main()
    pass
