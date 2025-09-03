"""
数据分析工具

主要功能：
1. 实时监控数据查询
2. 访问趋势分析
3. 性能分析报告
4. 异常检测和告警
5. 用户行为分析

"""

import os
import json
import pymysql
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dbutils.pooled_db import PooledDB
from mdbq.myconf import myconf


class MonitorAnalytics:
    """监控数据分析类"""
    
    def __init__(self, database='api_monitor_logs'):
        """初始化分析工具"""
        self.database = database
        self.init_database_pool()
    
    def init_database_pool(self):
        """初始化数据库连接池"""
        dir_path = os.path.expanduser("~")
        config_file = os.path.join(dir_path, 'spd.txt')
        parser = myconf.ConfigParser()
        
        host, port, username, password = parser.get_section_values(
            file_path=config_file,
            section='mysql',
            keys=['host', 'port', 'username', 'password'],
        )
        
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=5,  # 增加连接数避免冲突
            mincached=2,  # 增加最小缓存连接数
            maxcached=5,  # 增加最大缓存连接数
            blocking=True,
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=self.database,
            ping=1,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            # 添加连接超时设置
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30
        )
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """获取实时监控指标"""
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    now = datetime.now()
                    last_hour = now - timedelta(hours=1)
                    last_day = now - timedelta(days=1)
                    
                    # 最近1小时的请求统计
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as requests_last_hour,
                            COUNT(DISTINCT client_ip) as unique_ips_last_hour,
                            AVG(process_time) as avg_response_time,
                            MAX(process_time) as max_response_time,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as error_count,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) / COUNT(*) * 100 as error_rate,
                            SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) as bot_requests,
                            SUM(CASE WHEN is_mobile = 1 THEN 1 ELSE 0 END) as mobile_requests
                        FROM api_request_logs 
                        WHERE timestamp >= %s
                    """, (last_hour,))
                    
                    hourly_stats = cursor.fetchone() or {}
                    
                    # 最近24小时趋势对比
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as requests_last_day,
                            COUNT(DISTINCT client_ip) as unique_ips_last_day,
                            AVG(process_time) as avg_response_time_day
                        FROM api_request_logs 
                        WHERE timestamp >= %s
                    """, (last_day,))
                    
                    daily_stats = cursor.fetchone() or {}
                    
                    # 热门端点（最近1小时）
                    cursor.execute("""
                        SELECT endpoint, COUNT(*) as request_count,
                               AVG(process_time) as avg_time
                        FROM api_request_logs 
                        WHERE timestamp >= %s AND endpoint IS NOT NULL
                        GROUP BY endpoint
                        ORDER BY request_count DESC
                        LIMIT 5
                    """, (last_hour,))
                    
                    top_endpoints = cursor.fetchall()
                    
                    # 慢查询（最近1小时）
                    cursor.execute("""
                        SELECT endpoint, process_time, client_ip, timestamp
                        FROM api_request_logs 
                        WHERE timestamp >= %s AND process_time > 5000
                        ORDER BY process_time DESC
                        LIMIT 10
                    """, (last_hour,))
                    
                    slow_requests = cursor.fetchall()
                    
                    # 错误请求（最近1小时）
                    cursor.execute("""
                        SELECT endpoint, response_status, COUNT(*) as error_count
                        FROM api_request_logs 
                        WHERE timestamp >= %s AND response_status >= 400
                        GROUP BY endpoint, response_status
                        ORDER BY error_count DESC
                        LIMIT 10
                    """, (last_hour,))
                    
                    error_requests = cursor.fetchall()
                    
                    return {
                        'realtime_metrics': {
                            'requests_per_hour': hourly_stats.get('requests_last_hour', 0),
                            'requests_per_day': daily_stats.get('requests_last_day', 0),
                            'unique_ips_hour': hourly_stats.get('unique_ips_last_hour', 0),
                            'unique_ips_day': daily_stats.get('unique_ips_last_day', 0),
                            'avg_response_time': round(hourly_stats.get('avg_response_time', 0) or 0, 2),
                            'max_response_time': round(hourly_stats.get('max_response_time', 0) or 0, 2),
                            'error_rate': round(hourly_stats.get('error_rate', 0) or 0, 2),
                            'error_count': hourly_stats.get('error_count', 0),
                            'bot_requests': hourly_stats.get('bot_requests', 0),
                            'mobile_requests': hourly_stats.get('mobile_requests', 0)
                        },
                        'top_endpoints': top_endpoints,
                        'slow_requests': slow_requests,
                        'error_requests': error_requests,
                        'timestamp': now.isoformat()
                    }
            finally:
                connection.close()
                    
        except Exception as e:
            return {'error': str(e)}
    
    def get_traffic_trend(self, days: int = 7) -> Dict[str, Any]:
        """获取流量趋势分析"""
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=days)
                    
                    # 按小时统计（最近7天）
                    cursor.execute("""
                        SELECT 
                            DATE(timestamp) as date,
                            HOUR(timestamp) as hour,
                            COUNT(*) as requests,
                            COUNT(DISTINCT client_ip) as unique_ips,
                            AVG(process_time) as avg_response_time,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        GROUP BY DATE(timestamp), HOUR(timestamp)
                        ORDER BY date, hour
                    """, (start_date, end_date))
                    
                    hourly_data = cursor.fetchall()
                    
                    # 按天统计
                    cursor.execute("""
                        SELECT 
                            DATE(timestamp) as date,
                            COUNT(*) as requests,
                            COUNT(DISTINCT client_ip) as unique_ips,
                            AVG(process_time) as avg_response_time,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors,
                            SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) as bot_requests,
                            SUM(CASE WHEN is_mobile = 1 THEN 1 ELSE 0 END) as mobile_requests
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        GROUP BY DATE(timestamp)
                        ORDER BY date
                    """, (start_date, end_date))
                    
                    daily_data = cursor.fetchall()
                    
                    # 周中模式分析
                    cursor.execute("""
                        SELECT 
                            DAYOFWEEK(timestamp) as day_of_week,
                            DAYNAME(timestamp) as day_name,
                            COUNT(*) as total_requests,
                            AVG(process_time) as avg_response_time
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        GROUP BY DAYOFWEEK(timestamp), DAYNAME(timestamp)
                        ORDER BY day_of_week
                    """, (start_date, end_date))
                    
                    weekly_pattern = cursor.fetchall()
                    
                    # 小时模式分析
                    cursor.execute("""
                        SELECT 
                            HOUR(timestamp) as hour,
                            COUNT(*) as total_requests,
                            AVG(process_time) as avg_response_time
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        GROUP BY HOUR(timestamp)
                        ORDER BY hour
                    """, (start_date, end_date))
                    
                    hourly_pattern = cursor.fetchall()
                    
                    return {
                        'period': f'{start_date} to {end_date}',
                        'hourly_data': hourly_data,
                        'daily_data': daily_data,
                        'weekly_pattern': weekly_pattern,
                        'hourly_pattern': hourly_pattern
                    }
            finally:
                connection.close()
                    
        except Exception as e:
            return {'error': str(e)}
    
    def get_endpoint_analysis(self, days: int = 7) -> Dict[str, Any]:
        """获取端点性能分析"""
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=days)
                    
                    # 端点性能统计
                    cursor.execute("""
                        SELECT 
                            endpoint,
                            COUNT(*) as total_requests,
                            AVG(process_time) as avg_response_time,
                            MIN(process_time) as min_response_time,
                            MAX(process_time) as max_response_time,
                            STDDEV(process_time) as response_time_stddev,
                            COUNT(DISTINCT client_ip) as unique_users,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as error_count,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) / COUNT(*) * 100 as error_rate,
                            SUM(request_size) as total_request_size,
                            SUM(response_size) as total_response_size
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        AND endpoint IS NOT NULL
                        GROUP BY endpoint
                        ORDER BY total_requests DESC
                    """, (start_date, end_date))
                    
                    endpoint_stats = cursor.fetchall()
                    
                    # 最慢的端点
                    slowest_endpoints = sorted(
                        [ep for ep in endpoint_stats if ep['avg_response_time']],
                        key=lambda x: x['avg_response_time'] or 0,
                        reverse=True
                    )[:10]
                    
                    # 错误率最高的端点
                    error_prone_endpoints = sorted(
                        [ep for ep in endpoint_stats if (ep['error_rate'] or 0) > 0],
                        key=lambda x: x['error_rate'] or 0,
                        reverse=True
                    )[:10]
                    
                    # 最热门的端点
                    popular_endpoints = endpoint_stats[:10]
                    
                    return {
                        'period': f'{start_date} to {end_date}',
                        'all_endpoints': endpoint_stats,
                        'slowest_endpoints': slowest_endpoints,
                        'error_prone_endpoints': error_prone_endpoints,
                        'popular_endpoints': popular_endpoints
                    }
            finally:
                connection.close()
                    
        except Exception as e:
            return {'error': str(e)}
    
    def get_user_behavior_analysis(self, days: int = 7) -> Dict[str, Any]:
        """获取用户行为分析"""
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=days)
                    
                    # IP访问模式分析
                    cursor.execute("""
                        SELECT 
                            client_ip,
                            COUNT(*) as total_requests,
                            COUNT(DISTINCT endpoint) as unique_endpoints,
                            COUNT(DISTINCT DATE(timestamp)) as active_days,
                            MIN(timestamp) as first_access,
                            MAX(timestamp) as last_access,
                            AVG(process_time) as avg_response_time,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors,
                            SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) as bot_requests,
                            user_agent
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        GROUP BY client_ip, user_agent
                        HAVING total_requests >= 10
                        ORDER BY total_requests DESC
                        LIMIT 50
                    """, (start_date, end_date))
                    
                    ip_analysis = cursor.fetchall()
                    
                    # 设备类型统计
                    cursor.execute("""
                        SELECT 
                            browser_name,
                            os_name,
                            COUNT(*) as request_count,
                            COUNT(DISTINCT client_ip) as unique_users
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        AND browser_name != 'Unknown'
                        GROUP BY browser_name, os_name
                        ORDER BY request_count DESC
                    """, (start_date, end_date))
                    
                    device_stats = cursor.fetchall()
                    
                    # 可疑活动检测
                    cursor.execute("""
                        SELECT 
                            client_ip,
                            COUNT(*) as requests_per_hour,
                            COUNT(DISTINCT endpoint) as endpoints_accessed,
                            SUM(CASE WHEN response_status = 404 THEN 1 ELSE 0 END) as not_found_errors,
                            SUM(CASE WHEN response_status = 403 THEN 1 ELSE 0 END) as forbidden_errors,
                            MAX(is_bot) as is_bot
                        FROM api_request_logs 
                        WHERE timestamp >= %s
                        GROUP BY client_ip
                        HAVING requests_per_hour > 100 
                        OR not_found_errors > 10 
                        OR forbidden_errors > 5
                        ORDER BY requests_per_hour DESC
                    """, (datetime.now() - timedelta(hours=1),))
                    
                    suspicious_activity = cursor.fetchall()
                    
                    # 用户会话分析
                    cursor.execute("""
                        SELECT 
                            session_id,
                            COUNT(*) as session_requests,
                            COUNT(DISTINCT endpoint) as endpoints_in_session,
                            TIMESTAMPDIFF(MINUTE, MIN(timestamp), MAX(timestamp)) as session_duration,
                            MIN(timestamp) as session_start,
                            MAX(timestamp) as session_end
                        FROM api_request_logs 
                        WHERE DATE(timestamp) BETWEEN %s AND %s
                        AND session_id IS NOT NULL
                        GROUP BY session_id
                        HAVING session_requests >= 5
                        ORDER BY session_duration DESC
                        LIMIT 20
                    """, (start_date, end_date))
                    
                    session_analysis = cursor.fetchall()
                    
                    return {
                        'period': f'{start_date} to {end_date}',
                        'ip_analysis': ip_analysis,
                        'device_statistics': device_stats,
                        'suspicious_activity': suspicious_activity,
                        'session_analysis': session_analysis
                    }
            finally:
                connection.close()
                    
        except Exception as e:
            return {'error': str(e)}
    
    def get_performance_alerts(self) -> Dict[str, Any]:
        """获取性能告警信息"""
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    now = datetime.now()
                    last_hour = now - timedelta(hours=1)
                    
                    alerts = []
                    
                    # 检查响应时间异常
                    cursor.execute("""
                        SELECT endpoint, AVG(process_time) as avg_time
                        FROM api_request_logs 
                        WHERE timestamp >= %s AND process_time IS NOT NULL
                        GROUP BY endpoint
                        HAVING avg_time > 3000
                        ORDER BY avg_time DESC
                    """, (last_hour,))
                    
                    slow_endpoints = cursor.fetchall()
                    for endpoint in slow_endpoints:
                        alerts.append({
                            'type': 'SLOW_RESPONSE',
                            'severity': 'HIGH' if (endpoint['avg_time'] or 0) > 5000 else 'MEDIUM',
                            'message': f"端点 {endpoint['endpoint']} 平均响应时间 {endpoint['avg_time']:.0f}ms",
                            'timestamp': now.isoformat()
                        })
                    
                    # 检查错误率异常
                    cursor.execute("""
                        SELECT 
                            endpoint,
                            COUNT(*) as total,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) / COUNT(*) * 100 as error_rate
                        FROM api_request_logs 
                        WHERE timestamp >= %s
                        GROUP BY endpoint
                        HAVING total >= 10 AND error_rate > 10
                        ORDER BY error_rate DESC
                    """, (last_hour,))
                    
                    error_endpoints = cursor.fetchall()
                    for endpoint in error_endpoints:
                        alerts.append({
                            'type': 'HIGH_ERROR_RATE',
                            'severity': 'HIGH' if (endpoint['error_rate'] or 0) > 20 else 'MEDIUM',
                            'message': f"端点 {endpoint['endpoint']} 错误率 {endpoint['error_rate']:.1f}%",
                            'timestamp': now.isoformat()
                        })
                    
                    # 检查异常流量
                    cursor.execute("""
                        SELECT 
                            client_ip,
                            COUNT(*) as request_count
                        FROM api_request_logs 
                        WHERE timestamp >= %s
                        GROUP BY client_ip
                        HAVING request_count > 500
                        ORDER BY request_count DESC
                    """, (last_hour,))
                    
                    high_traffic_ips = cursor.fetchall()
                    for ip_data in high_traffic_ips:
                        alerts.append({
                            'type': 'HIGH_TRAFFIC',
                            'severity': 'MEDIUM',
                            'message': f"IP {ip_data['client_ip']} 请求量异常: {ip_data['request_count']} 次/小时",
                            'timestamp': now.isoformat()
                        })
                    
                    # 检查系统整体负载
                    cursor.execute("""
                        SELECT COUNT(*) as total_requests
                        FROM api_request_logs 
                        WHERE timestamp >= %s
                    """, (last_hour,))
                    
                    total_requests = cursor.fetchone()['total_requests']
                    if total_requests > 10000:  # 每小时超过1万请求
                        alerts.append({
                            'type': 'HIGH_SYSTEM_LOAD',
                            'severity': 'HIGH',
                            'message': f"系统负载异常: {total_requests} 请求/小时",
                            'timestamp': now.isoformat()
                        })
                    
                    return {
                        'alerts': alerts,
                        'alert_count': len(alerts),
                        'high_severity_count': len([a for a in alerts if a['severity'] == 'HIGH']),
                        'timestamp': now.isoformat()
                    }
            finally:
                connection.close()
                    
        except Exception as e:
            return {'error': str(e)}
    
    def generate_daily_report(self, target_date: datetime = None) -> Dict[str, Any]:
        """生成日报告"""
        if target_date is None:
            target_date = datetime.now().date() - timedelta(days=1)
        
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    # 整体统计
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_requests,
                            COUNT(DISTINCT client_ip) as unique_ips,
                            COUNT(DISTINCT endpoint) as unique_endpoints,
                            AVG(process_time) as avg_response_time,
                            MAX(process_time) as max_response_time,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as total_errors,
                            SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) / COUNT(*) * 100 as error_rate,
                            SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) as bot_requests,
                            SUM(CASE WHEN is_mobile = 1 THEN 1 ELSE 0 END) as mobile_requests,
                            SUM(request_size) as total_request_size,
                            SUM(response_size) as total_response_size
                        FROM api_request_logs 
                        WHERE DATE(timestamp) = %s
                    """, (target_date,))
                    
                    daily_summary = cursor.fetchone()
                    
                    # 热门端点
                    cursor.execute("""
                        SELECT endpoint, COUNT(*) as requests, AVG(process_time) as avg_time
                        FROM api_request_logs 
                        WHERE DATE(timestamp) = %s
                        GROUP BY endpoint
                        ORDER BY requests DESC
                        LIMIT 10
                    """, (target_date,))
                    
                    top_endpoints = cursor.fetchall()
                    
                    # 错误统计
                    cursor.execute("""
                        SELECT response_status, COUNT(*) as count
                        FROM api_request_logs 
                        WHERE DATE(timestamp) = %s AND response_status >= 400
                        GROUP BY response_status
                        ORDER BY count DESC
                    """, (target_date,))
                    
                    error_breakdown = cursor.fetchall()
                    
                    # 流量分布（按小时）
                    cursor.execute("""
                        SELECT 
                            HOUR(timestamp) as hour,
                            COUNT(*) as requests,
                            AVG(process_time) as avg_time
                        FROM api_request_logs 
                        WHERE DATE(timestamp) = %s
                        GROUP BY HOUR(timestamp)
                        ORDER BY hour
                    """, (target_date,))
                    
                    hourly_distribution = cursor.fetchall()
                    
                    return {
                        'date': target_date.isoformat(),
                        'summary': daily_summary,
                        'top_endpoints': top_endpoints,
                        'error_breakdown': error_breakdown,
                        'hourly_distribution': hourly_distribution,
                        'generated_at': datetime.now().isoformat()
                    }
            finally:
                connection.close()
                    
        except Exception as e:
            return {'error': str(e)}


# 全局分析实例
analytics = MonitorAnalytics()

# 导出分析函数
def get_realtime_metrics():
    """获取实时监控指标"""
    return analytics.get_realtime_metrics()

def get_traffic_trend(days: int = 7):
    """获取流量趋势"""
    return analytics.get_traffic_trend(days)

def get_endpoint_analysis(days: int = 7):
    """获取端点分析"""
    return analytics.get_endpoint_analysis(days)

def get_user_behavior_analysis(days: int = 7):
    """获取用户行为分析"""
    return analytics.get_user_behavior_analysis(days)

def get_performance_alerts():
    """获取性能告警"""
    return analytics.get_performance_alerts()

def generate_daily_report(target_date: datetime = None):
    """生成日报告"""
    return analytics.generate_daily_report(target_date) 