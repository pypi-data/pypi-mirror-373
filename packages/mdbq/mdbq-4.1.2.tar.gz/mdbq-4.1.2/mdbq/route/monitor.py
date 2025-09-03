"""
核心监控模块

主要功能：
1. 监控所有路由接口的访问请求
2. 记录详细的请求信息（IP、设备、请求头、请求体等）
3. 提供统计分析功能
4. 异常处理和数据清理

"""

import os
import json
import time
import uuid
import pymysql
import hashlib
import functools
from datetime import datetime, timedelta
from typing import Dict, Any
from urllib.parse import urlparse
from dbutils.pooled_db import PooledDB # type: ignore
from mdbq.myconf import myconf # type: ignore
from mdbq.log import mylogger
from flask import request, g
import re
import ipaddress

parser = myconf.ConfigParser()
host, port, username, password = parser.get_section_values(
    file_path=os.path.join(os.path.expanduser("~"), 'spd.txt'),
    section='mysql',
    keys=['host', 'port', 'username', 'password'],
)

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


class RouteMonitor:
    """路由监控核心类"""
    
    def __init__(self, database='api_monitor_logs'):
        """初始化监控系统"""
        self.database = database
        self.init_database_pool()
        self.init_database_tables()

    def init_database_pool(self):
        """初始化数据库连接池"""
        try:
            self.pool = PooledDB(
                creator=pymysql,
                maxconnections=2,  # 监控系统连接数较小
                mincached=1,
                maxcached=2,
                blocking=True,
                host=host,
                port=int(port),
                user=username,
                password=password,
                ping=1,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

            # 创建数据库并切换
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
                    cursor.execute(f"USE `{self.database}`")
            finally:
                connection.close()
                
        except Exception as e:
            logger.error("❌ 数据库连接池初始化失败", {
                "错误信息": str(e),
                "数据库": self.database
            })
            raise
    
    def ensure_database_context(self, cursor):
        """确保当前游标处于正确的数据库上下文中"""
        try:
            cursor.execute(f"USE `{self.database}`")
        except Exception as e:
            logger.warning("切换数据库上下文失败，尝试重新创建", {
                "数据库": self.database,
                "错误": str(e)
            })
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
            cursor.execute(f"USE `{self.database}`")
        
    def init_database_tables(self):
        """初始化数据库表结构"""
        try:
            logger.debug("🗄️ 开始创建/验证数据库表结构", {
                "操作": "表结构初始化",
                "预期表数": 4,
                "数据库": self.database
            })
            
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    # 确保使用正确的数据库上下文
                    self.ensure_database_context(cursor)
                    
                    # 创建详细请求记录表 - 修复MySQL 8.4+兼容性
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `api_request_logs` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                            `request_id` VARCHAR(128) NOT NULL COMMENT '请求唯一标识',
                            `timestamp` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '请求时间（精确到毫秒）',
                            `method` VARCHAR(10) NOT NULL COMMENT 'HTTP方法',
                            `endpoint` VARCHAR(500) NOT NULL COMMENT '请求端点',
                            `full_url` TEXT COMMENT '完整URL',
                            `client_ip` VARCHAR(45) NOT NULL COMMENT '客户端IP地址',
                            `real_ip` VARCHAR(45) COMMENT '真实IP地址',
                            `forwarded_ips` TEXT COMMENT '转发IP链',
                            `user_agent` TEXT COMMENT '用户代理',
                            `referer` VARCHAR(1000) COMMENT '来源页面',
                            `host` VARCHAR(255) COMMENT '请求主机',
                            `scheme` VARCHAR(10) COMMENT '协议类型',
                            `port` INT COMMENT '端口号',
                            `request_headers` JSON COMMENT '请求头信息',
                            `request_params` JSON COMMENT '请求参数',
                            `request_body` LONGTEXT COMMENT '请求体内容',
                            `request_size` INT DEFAULT 0 COMMENT '请求大小（字节）',
                            `response_status` INT COMMENT '响应状态码',
                            `response_size` INT COMMENT '响应大小（字节）',
                            `process_time` DECIMAL(10,3) COMMENT '处理时间（毫秒）',
                            `session_id` VARCHAR(128) COMMENT '会话ID',
                            `user_id` VARCHAR(64) COMMENT '用户ID',
                            `auth_token` TEXT COMMENT '认证令牌（脱敏）',
                            `device_fingerprint` VARCHAR(256) COMMENT '设备指纹',
                            `device_info` JSON COMMENT '设备信息',
                            `geo_country` VARCHAR(100) COMMENT '地理位置-国家',
                            `geo_region` VARCHAR(100) COMMENT '地理位置-地区',
                            `geo_city` VARCHAR(100) COMMENT '地理位置-城市',
                            `is_bot` BOOLEAN DEFAULT FALSE COMMENT '是否为机器人',
                            `is_mobile` BOOLEAN DEFAULT FALSE COMMENT '是否为移动设备',
                            `browser_name` VARCHAR(50) COMMENT '浏览器名称',
                            `browser_version` VARCHAR(20) COMMENT '浏览器版本',
                            `os_name` VARCHAR(50) COMMENT '操作系统名称',
                            `os_version` VARCHAR(20) COMMENT '操作系统版本',
                            `error_message` TEXT COMMENT '错误信息',
                            `business_data` JSON COMMENT '业务数据',
                            `tags` JSON COMMENT '标签信息',
                            UNIQUE KEY `uk_request_id` (`request_id`),
                            INDEX `idx_timestamp` (`timestamp`),
                            INDEX `idx_endpoint` (`endpoint`(191)),
                            INDEX `idx_client_ip` (`client_ip`),
                            INDEX `idx_user_id` (`user_id`),
                            INDEX `idx_status` (`response_status`),
                            INDEX `idx_method_endpoint` (`method`, `endpoint`(191)),
                            INDEX `idx_timestamp_endpoint` (`timestamp`, `endpoint`(191))
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='API请求详细日志表';
                    """)
                    # 创建访问统计汇总表
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `api_access_statistics` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                            `date` DATE NOT NULL COMMENT '统计日期',
                            `hour` TINYINT NOT NULL DEFAULT 0 COMMENT '小时（0-23）',
                            `endpoint` VARCHAR(500) NOT NULL COMMENT '端点',
                            `method` VARCHAR(10) NOT NULL COMMENT 'HTTP方法',
                            `total_requests` INT UNSIGNED DEFAULT 0 COMMENT '总请求数',
                            `success_requests` INT UNSIGNED DEFAULT 0 COMMENT '成功请求数',
                            `error_requests` INT UNSIGNED DEFAULT 0 COMMENT '错误请求数',
                            `unique_ips` INT UNSIGNED DEFAULT 0 COMMENT '唯一IP数',
                            `unique_users` INT UNSIGNED DEFAULT 0 COMMENT '唯一用户数',
                            `avg_response_time` DECIMAL(10,3) DEFAULT 0 COMMENT '平均响应时间（毫秒）',
                            `max_response_time` DECIMAL(10,3) DEFAULT 0 COMMENT '最大响应时间（毫秒）',
                            `min_response_time` DECIMAL(10,3) DEFAULT 0 COMMENT '最小响应时间（毫秒）',
                            `total_request_size` BIGINT UNSIGNED DEFAULT 0 COMMENT '总请求大小（字节）',
                            `total_response_size` BIGINT UNSIGNED DEFAULT 0 COMMENT '总响应大小（字节）',
                            `bot_requests` INT UNSIGNED DEFAULT 0 COMMENT '机器人请求数',
                            `mobile_requests` INT UNSIGNED DEFAULT 0 COMMENT '移动端请求数',
                            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                            `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                            UNIQUE KEY `uk_date_hour_endpoint_method` (`date`, `hour`, `endpoint`(191), `method`),
                            INDEX `idx_date` (`date`),
                            INDEX `idx_endpoint` (`endpoint`(191)),
                            INDEX `idx_date_endpoint` (`date`, `endpoint`(191))
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='API访问统计汇总表';
                    """)
                    
                    # 创建IP访问统计表
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `ip_access_statistics` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                            `date` DATE NOT NULL COMMENT '统计日期',
                            `ip_address` VARCHAR(45) NOT NULL COMMENT 'IP地址',
                            `total_requests` INT UNSIGNED DEFAULT 0 COMMENT '总请求数',
                            `unique_endpoints` INT UNSIGNED DEFAULT 0 COMMENT '访问的唯一端点数',
                            `success_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '成功率（%）',
                            `avg_response_time` DECIMAL(10,3) DEFAULT 0 COMMENT '平均响应时间（毫秒）',
                            `first_access` DATETIME COMMENT '首次访问时间',
                            `last_access` DATETIME COMMENT '最后访问时间',
                            `user_agent_hash` VARCHAR(64) COMMENT '用户代理哈希',
                            `is_suspicious` BOOLEAN DEFAULT FALSE COMMENT '是否可疑',
                            `risk_score` TINYINT UNSIGNED DEFAULT 0 COMMENT '风险评分（0-100）',
                            `geo_country` VARCHAR(50) COMMENT '地理位置-国家',
                            `geo_region` VARCHAR(100) COMMENT '地理位置-地区',
                            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                            `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                            UNIQUE KEY `uk_date_ip` (`date`, `ip_address`),
                            INDEX `idx_date` (`date`),
                            INDEX `idx_ip` (`ip_address`),
                            INDEX `idx_suspicious` (`is_suspicious`),
                            INDEX `idx_risk_score` (`risk_score`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='IP访问统计表';
                    """)
                    # 创建系统性能统计表
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `system_performance_stats` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
                            `timestamp` DATETIME NOT NULL COMMENT '统计时间',
                            `total_requests_per_minute` INT UNSIGNED DEFAULT 0 COMMENT '每分钟总请求数',
                            `avg_response_time` DECIMAL(10,3) DEFAULT 0 COMMENT '平均响应时间（毫秒）',
                            `error_rate` DECIMAL(5,2) DEFAULT 0 COMMENT '错误率（%）',
                            `active_ips` INT UNSIGNED DEFAULT 0 COMMENT '活跃IP数',
                            `peak_concurrent_requests` INT UNSIGNED DEFAULT 0 COMMENT '峰值并发请求数',
                            `slowest_endpoint` VARCHAR(500) COMMENT '最慢端点',
                            `slowest_response_time` DECIMAL(10,3) DEFAULT 0 COMMENT '最慢响应时间（毫秒）',
                            `most_accessed_endpoint` VARCHAR(500) COMMENT '最热门端点',
                            `most_accessed_count` INT UNSIGNED DEFAULT 0 COMMENT '最热门端点访问次数',
                            INDEX `idx_timestamp` (`timestamp`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='系统性能统计表';
                    """)
                connection.commit()
                logger.debug("🎯 所有数据库表结构初始化完成", {
                    "创建表数": 4,
                    "操作状态": "成功",
                    "数据库": self.database,
                    "数据库引擎": "InnoDB"
                })
                
            finally:
                connection.close()
                
        except Exception as e:
            logger.error("❌ 数据库表结构初始化失败", {
                "错误信息": str(e),
                "错误类型": type(e).__name__,
                "数据库": self.database,
                "影响": "监控系统可能无法正常工作"
            })
            # 静默处理初始化错误，避免影响主应用
            pass
    
    def generate_request_id(self) -> str:
        """生成唯一的请求ID"""
        timestamp = str(int(time.time() * 1000))  # 毫秒时间戳
        random_part = uuid.uuid4().hex[:8]
        return f"req_{timestamp}_{random_part}"
    
    def extract_device_info(self, user_agent: str) -> Dict[str, Any]:
        """提取设备信息"""
        device_info = {
            'is_mobile': False,
            'is_bot': False,
            'browser_name': 'Unknown',
            'browser_version': 'Unknown',
            'os_name': 'Unknown',
            'os_version': 'Unknown'
        }
        
        if not user_agent:
            return device_info
        
        user_agent_lower = user_agent.lower()
        
        # 检测移动设备
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'windows phone']
        device_info['is_mobile'] = any(keyword in user_agent_lower for keyword in mobile_keywords)
        
        # 检测机器人
        bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests']
        device_info['is_bot'] = any(keyword in user_agent_lower for keyword in bot_keywords)
        
        # 浏览器检测
        browsers = [
            ('chrome', r'chrome/(\d+)'),
            ('firefox', r'firefox/(\d+)'),
            ('safari', r'safari/(\d+)'),
            ('edge', r'edge/(\d+)'),
            ('opera', r'opera/(\d+)')
        ]
        
        for browser, pattern in browsers:
            match = re.search(pattern, user_agent_lower)
            if match:
                device_info['browser_name'] = browser.title()
                device_info['browser_version'] = match.group(1)
                break
        
        # 操作系统检测
        os_patterns = [
            ('Windows', r'windows nt (\d+\.\d+)'),
            ('macOS', r'mac os x (\d+_\d+)'),
            ('Linux', r'linux'),
            ('Android', r'android (\d+)'),
            ('iOS', r'os (\d+_\d+)')
        ]
        
        for os_name, pattern in os_patterns:
            match = re.search(pattern, user_agent_lower)
            if match:
                device_info['os_name'] = os_name
                if len(match.groups()) > 0:
                    device_info['os_version'] = match.group(1).replace('_', '.')
                break
        
        return device_info
    
    def generate_device_fingerprint(self, request_data: Dict) -> str:
        """生成设备指纹"""
        fingerprint_data = {
            'user_agent': request_data.get('user_agent', ''),
            'accept_language': request_data.get('request_headers', {}).get('Accept-Language', ''),
            'accept_encoding': request_data.get('request_headers', {}).get('Accept-Encoding', ''),
            'connection': request_data.get('request_headers', {}).get('Connection', ''),
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def sanitize_data(self, data: Any, max_length: int = 10000) -> Any:
        """数据清理和截断"""
        if data is None:
            return None
        
        if isinstance(data, str):
            # 移除敏感信息
            sensitive_patterns = [
                (r'password["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'password: [REDACTED]'),
                (r'token["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'token: [REDACTED]'),
                (r'key["\']?\s*[:=]\s*["\']?[^"\'&\s]+', 'key: [REDACTED]'),
            ]
            
            sanitized = data
            for pattern, replacement in sensitive_patterns:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            
            # 截断过长的内容
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length] + '...[TRUNCATED]'
            
            return sanitized
        
        elif isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['password', 'token', 'key', 'secret']:
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self.sanitize_data(value, max_length)
            return sanitized
        
        elif isinstance(data, list):
            return [self.sanitize_data(item, max_length) for item in data[:100]]  # 限制列表长度
        
        return data
    
    def get_real_ip(self, request) -> tuple:
        """获取真实IP地址"""
        # IP地址优先级顺序
        ip_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',  # Cloudflare
            'X-Client-IP',
            'X-Forwarded',
            'Forwarded-For',
            'Forwarded'
        ]
        
        forwarded_ips = []
        real_ip = request.remote_addr
        
        for header in ip_headers:
            header_value = request.headers.get(header)
            if header_value:
                # 处理多个IP的情况（用逗号分隔）
                ips = [ip.strip() for ip in header_value.split(',')]
                forwarded_ips.extend(ips)
                
                # 取第一个有效的IP作为真实IP
                for ip in ips:
                    if self.is_valid_ip(ip) and not self.is_private_ip(ip):
                        real_ip = ip
                        break
                
                if real_ip != request.remote_addr:
                    break
        
        return real_ip, forwarded_ips
    
    def is_valid_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def is_private_ip(self, ip: str) -> bool:
        """检查是否为私有IP"""
        try:
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            return False
    
    def collect_request_data(self, request) -> Dict[str, Any]:
        """收集请求数据"""
        start_time = getattr(g, 'request_start_time', time.time())
        request_id = self.generate_request_id()
        
        # 设置请求ID到全局变量中，供后续使用
        g.request_id = request_id
        
        logger.debug("📋 开始收集请求数据", {
            "请求ID": request_id,
            "请求方法": request.method,
            "端点": request.endpoint or request.path,
            "客户端IP": request.remote_addr
        })
        
        # 获取真实IP
        real_ip, forwarded_ips = self.get_real_ip(request)
        
        if real_ip != request.remote_addr:
            logger.debug("🔍 检测到IP转发", {
                "请求ID": request_id,
                "原始IP": request.remote_addr,
                "真实IP": real_ip,
                "转发链长度": len(forwarded_ips) if forwarded_ips else 0
            })
        
        # 获取请求头信息
        headers = dict(request.headers)
        sanitized_headers = self.sanitize_data(headers)
        
        # 获取请求参数
        request_params = {}
        if request.args:
            request_params.update(dict(request.args))
        
        # 获取请求体
        request_body = None
        request_size = 0
        
        try:
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    request_body = request.get_json()
                elif request.form:
                    request_body = dict(request.form)
                else:
                    body_data = request.get_data()
                    if body_data:
                        try:
                            request_body = body_data.decode('utf-8')
                        except UnicodeDecodeError:
                            request_body = f"[BINARY_DATA:{len(body_data)}_bytes]"
                            logger.debug("📁 检测到二进制数据", {
                                "请求ID": request_id,
                                "数据大小": len(body_data),
                                "处理方式": "标记为二进制"
                            })
                
                if request_body:
                    request_size = len(str(request_body).encode('utf-8'))
                    logger.debug("📊 请求体信息", {
                        "请求ID": request_id,
                        "数据类型": "JSON" if request.is_json else "表单" if request.form else "文本",
                        "大小": f"{request_size} bytes"
                    })
        except Exception as e:
            request_body = "[ERROR_READING_BODY]"
            logger.warning("⚠️ 读取请求体失败", {
                "请求ID": request_id,
                "错误": str(e)
            })
        
        # 清理敏感数据
        sanitized_body = self.sanitize_data(request_body)
        sanitized_params = self.sanitize_data(request_params)
        
        # 设备信息提取
        user_agent = request.headers.get('User-Agent', '')
        device_info = self.extract_device_info(user_agent)
        
        if device_info['is_bot']:
            logger.debug("🤖 检测到机器人请求", {
                "请求ID": request_id,
                "用户代理": user_agent[:100] + "..." if len(user_agent) > 100 else user_agent,
                "IP": real_ip
            })
        
        if device_info['is_mobile']:
            logger.debug("📱 检测到移动设备请求", {
                "请求ID": request_id,
                "操作系统": device_info['os_name'],
                "浏览器": device_info['browser_name']
            })
        
        # URL解析
        parsed_url = urlparse(request.url)
        
        # 构建请求数据
        request_data = {
            'request_id': request_id,
            'timestamp': datetime.now(),
            'method': request.method,
            'endpoint': request.endpoint or request.path,
            'full_url': request.url,
            'client_ip': request.remote_addr,
            'real_ip': real_ip,
            'forwarded_ips': json.dumps(forwarded_ips) if forwarded_ips else None,
            'user_agent': user_agent,
            'referer': request.headers.get('Referer'),
            'host': request.headers.get('Host'),
            'scheme': parsed_url.scheme,
            'port': parsed_url.port,
            'request_headers': json.dumps(sanitized_headers),
            'request_params': json.dumps(sanitized_params) if sanitized_params else None,
            'request_body': json.dumps(sanitized_body) if sanitized_body else None,
            'request_size': request_size,
            'session_id': request.cookies.get('session_id'),
            'user_id': getattr(request, 'current_user', {}).get('id') if hasattr(request, 'current_user') else None,
            'auth_token': self.mask_token(request.headers.get('Authorization')),
            'device_fingerprint': self.generate_device_fingerprint({
                'user_agent': user_agent,
                'request_headers': sanitized_headers
            }),
            'device_info': json.dumps(device_info),
            'is_bot': device_info['is_bot'],
            'is_mobile': device_info['is_mobile'],
            'browser_name': device_info['browser_name'],
            'browser_version': device_info['browser_version'],
            'os_name': device_info['os_name'],
            'os_version': device_info['os_version'],
        }
        
        logger.debug("✅ 请求数据收集完成", {
            "请求ID": request_id,
            "数据字段数": len(request_data),
            "请求大小": f"{request_size} bytes",
            "设备类型": "移动" if device_info['is_mobile'] else "桌面",
            "是否机器人": device_info['is_bot']
        })
        
        return request_data
    
    def mask_token(self, token: str) -> str:
        """脱敏处理令牌"""
        if not token:
            return None
        
        if len(token) <= 8:
            return '*' * len(token)
        
        if len(token) > 255:
            return token[:10] + '*' * (min(len(token), 10)) + token[-10:]
        
        return token[:4] + '*' * (len(token) - 8) + token[-4:]
    
    def save_request_log(self, request_data: Dict[str, Any], response_data: Dict[str, Any] = None):
        """保存请求日志到数据库"""
        request_id = request_data.get('request_id', 'unknown')
        
        try:
            # 合并响应数据
            if response_data:
                request_data.update(response_data)
            
            logger.debug("💾 保存请求日志到数据库", {
                "请求ID": request_id,
                "端点": request_data.get('endpoint', ''),
                "状态码": request_data.get('response_status', '未知'),
                "处理时间": f"{request_data.get('process_time', 0)}ms"
            })
            
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    # 确保使用正确的数据库上下文
                    self.ensure_database_context(cursor)
                    
                    # 插入请求日志
                    columns = ', '.join([f"`{key}`" for key in request_data.keys()])
                    placeholders = ', '.join(['%s'] * len(request_data))
                    
                    sql = f"""
                        INSERT INTO `api_request_logs` ({columns})
                        VALUES ({placeholders})
                    """
                    
                    cursor.execute(sql, list(request_data.values()))
                connection.commit()
                
                logger.debug("✅ 请求日志保存成功", {
                    "请求ID": request_id,
                    "写入状态": "成功",
                    "数据库表": "api_request_logs"
                })
                
            finally:
                connection.close()
                
        except Exception as e:
            logger.error("❌ 保存请求日志失败", {
                "请求ID": request_id,
                "错误信息": str(e),
                "错误类型": type(e).__name__,
                "影响": "日志丢失，但不影响主业务"
            })
            # 静默处理错误，不影响主业务
            pass
    
    def update_statistics(self, request_data: Dict[str, Any]):
        """更新统计数据"""
        request_id = request_data.get('request_id', 'unknown')
        endpoint = request_data.get('endpoint', '')
        status_code = request_data.get('response_status', 500)
        
        try:
            logger.debug("📈 更新统计数据", {
                "请求ID": request_id,
                "端点": endpoint,
                "状态码": status_code,
                "统计类型": "API访问统计和IP统计"
            })
            
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    # 确保使用正确的数据库上下文
                    self.ensure_database_context(cursor)
                    
                    now = datetime.now()
                    date = now.date()
                    hour = now.hour
                    
                    # 更新API访问统计
                    cursor.execute("""
                        INSERT INTO `api_access_statistics` 
                        (`date`, `hour`, `endpoint`, `method`, `total_requests`, 
                         `success_requests`, `error_requests`, `avg_response_time`)
                        VALUES (%s, %s, %s, %s, 1, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        `total_requests` = `total_requests` + 1,
                        `success_requests` = `success_requests` + %s,
                        `error_requests` = `error_requests` + %s,
                        `avg_response_time` = (
                            (`avg_response_time` * (`total_requests` - 1) + %s) / `total_requests`
                        ),
                        `updated_at` = CURRENT_TIMESTAMP
                    """, (
                        date, hour, 
                        request_data.get('endpoint', ''),
                        request_data.get('method', ''),
                        1 if (request_data.get('response_status', 500) < 400) else 0,
                        1 if (request_data.get('response_status', 500) >= 400) else 0,
                        request_data.get('process_time', 0),
                        1 if (request_data.get('response_status', 500) < 400) else 0,
                        1 if (request_data.get('response_status', 500) >= 400) else 0,
                        request_data.get('process_time', 0)
                    ))
                    
                    # 更新IP访问统计
                    cursor.execute("""
                        INSERT INTO `ip_access_statistics` 
                        (`date`, `ip_address`, `total_requests`, `first_access`, `last_access`,
                         `user_agent_hash`)
                        VALUES (%s, %s, 1, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        `total_requests` = `total_requests` + 1,
                        `last_access` = %s,
                        `updated_at` = CURRENT_TIMESTAMP
                    """, (
                        date,
                        request_data.get('real_ip', request_data.get('client_ip')),
                        now, now,
                        hashlib.md5((request_data.get('user_agent', '')).encode()).hexdigest(),
                        now
                    ))
                    
                connection.commit()
                
                logger.debug("✅ 统计数据更新成功", {
                    "请求ID": request_id,
                    "更新表": "api_access_statistics, ip_access_statistics",
                    "日期": str(date),
                    "小时": hour
                })
                
            finally:
                connection.close()
                
        except Exception as e:
            logger.error("❌ 更新统计数据失败", {
                "请求ID": request_id,
                "错误信息": str(e),
                "错误类型": type(e).__name__,
                "影响": "统计数据缺失，但不影响主业务"
            })
            # 静默处理错误
            pass

    def monitor_request(self, func):
        """请求监控装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 记录开始时间
            start_time = time.time()
            g.request_start_time = start_time
            
            # 收集请求数据
            request_data = self.collect_request_data(request)
            request_id = request_data.get('request_id', 'unknown')
            
            logger.debug("🎯 开始监控请求", {
                "请求ID": request_id,
                "函数名": func.__name__,
                "端点": request_data.get('endpoint', ''),
                "方法": request_data.get('method', ''),
                "来源IP": request_data.get('real_ip', request_data.get('client_ip'))
            })
            
            try:
                # 执行原函数
                response = func(*args, **kwargs)
                
                # 记录响应信息
                end_time = time.time()
                process_time = round((end_time - start_time) * 1000, 3)
                
                response_status = getattr(response, 'status_code', 200) if hasattr(response, 'status_code') else 200
                
                # 🚀 兼容流式响应：检查是否为直通模式
                response_size = 0
                try:
                    if hasattr(response, 'direct_passthrough') and response.direct_passthrough:
                        # 流式响应模式，无法获取准确大小，使用估算值
                        response_size = -1  # 标记为流式响应
                    elif hasattr(response, 'get_data'):
                        response_size = len(str(response.get_data()))
                    else:
                        response_size = 0
                except (RuntimeError, Exception):
                    # 如果获取数据失败（如直通模式），使用默认值
                    response_size = -1  # 标记为无法获取大小
                
                response_data = {
                    'response_status': response_status,
                    'process_time': process_time,
                    'response_size': response_size
                }
                
                logger.debug("✅ 请求处理完成", {
                    "请求ID": request_id,
                    "函数名": func.__name__,
                    "状态码": response_status,
                    "处理时间": f"{process_time}ms",
                    "响应大小": f"{response_size} bytes",
                    "结果": "成功"
                })
                
                # 保存日志
                self.save_request_log(request_data, response_data)
                
                # 更新统计
                request_data.update(response_data)
                self.update_statistics(request_data)
                
                return response
                
            except Exception as e:
                # 记录错误信息
                end_time = time.time()
                process_time = round((end_time - start_time) * 1000, 3)
                
                error_data = {
                    'response_status': 500,
                    'process_time': process_time,
                    'error_message': str(e),
                    'response_size': 0
                }
                
                logger.error("❌ 请求处理异常", {
                    "请求ID": request_id,
                    "函数名": func.__name__,
                    "错误信息": str(e),
                    "错误类型": type(e).__name__,
                    "处理时间": f"{process_time}ms",
                    "结果": "异常"
                })
                
                # 保存错误日志
                self.save_request_log(request_data, error_data)
                
                # 更新统计
                request_data.update(error_data)
                self.update_statistics(request_data)
                
                # 重新抛出异常
                raise e
                
        return wrapper

    def get_statistics_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取统计摘要"""
        try:
            logger.debug("📊 开始获取统计摘要", {
                "查询天数": days,
                "操作": "统计数据查询"
            })
            
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    # 确保使用正确的数据库上下文
                    self.ensure_database_context(cursor)
                    
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=days)
                    
                    logger.debug("📅 统计查询时间范围", {
                        "开始日期": str(start_date),
                        "结束日期": str(end_date),
                        "查询天数": days
                    })
                    
                    # 总体统计
                    cursor.execute("""
                        SELECT 
                            SUM(total_requests) as total_requests,
                            SUM(success_requests) as success_requests,
                            SUM(error_requests) as error_requests,
                            AVG(avg_response_time) as avg_response_time,
                            COUNT(DISTINCT endpoint) as unique_endpoints
                        FROM api_access_statistics 
                        WHERE date BETWEEN %s AND %s
                    """, (start_date, end_date))
                    
                    summary = cursor.fetchone() or {}
                    
                    logger.debug("📈 总体统计查询完成", {
                        "总请求数": summary.get('total_requests', 0) or 0,
                        "成功请求数": summary.get('success_requests', 0) or 0,
                        "错误请求数": summary.get('error_requests', 0) or 0,
                        "平均响应时间": f"{(summary.get('avg_response_time', 0) or 0):.2f}ms",
                        "唯一端点数": summary.get('unique_endpoints', 0) or 0
                    })
                    
                    # 热门端点
                    cursor.execute("""
                        SELECT endpoint, SUM(total_requests) as requests
                        FROM api_access_statistics 
                        WHERE date BETWEEN %s AND %s
                        GROUP BY endpoint
                        ORDER BY requests DESC
                        LIMIT 10
                    """, (start_date, end_date))
                    
                    top_endpoints = cursor.fetchall()
                    
                    logger.debug("🔥 热门端点查询完成", {
                        "查询结果数": len(top_endpoints),
                        "最热门端点": top_endpoints[0]['endpoint'] if top_endpoints else "无数据",
                        "最高请求数": top_endpoints[0]['requests'] if top_endpoints else 0
                    })
                    
                    # 活跃IP统计
                    cursor.execute("""
                        SELECT COUNT(DISTINCT ip_address) as unique_ips,
                               SUM(total_requests) as total_ip_requests
                        FROM ip_access_statistics 
                        WHERE date BETWEEN %s AND %s
                    """, (start_date, end_date))
                    
                    ip_stats = cursor.fetchone() or {}
                    
                    logger.debug("🌐 IP统计查询完成", {
                        "唯一IP数": ip_stats.get('unique_ips', 0),
                        "IP总请求数": ip_stats.get('total_ip_requests', 0)
                    })
                    
                    result = {
                        'period': f'{start_date} to {end_date}',
                        'summary': summary,
                        'top_endpoints': top_endpoints,
                        'ip_statistics': ip_stats
                    }
                    
                    logger.debug("✅ 统计摘要获取成功", {
                        "查询天数": days,
                        "数据完整性": "完整",
                        "结果状态": "成功"
                    })
                    
                    return result
                    
            finally:
                connection.close()
                    
        except Exception as e:
            logger.error("❌ 获取统计摘要失败", {
                "查询天数": days,
                "错误信息": str(e),
                "错误类型": type(e).__name__,
                "影响": "统计摘要不可用"
            })
            return {'error': str(e)}


# 全局监控实例
route_monitor = RouteMonitor()

# 导出监控装饰器
monitor_request = route_monitor.monitor_request

# 导出其他有用的函数
def get_request_id():
    """获取当前请求ID"""
    return getattr(g, 'request_id', None)

def get_statistics_summary(days: int = 7):
    """获取统计摘要"""
    return route_monitor.get_statistics_summary(days)