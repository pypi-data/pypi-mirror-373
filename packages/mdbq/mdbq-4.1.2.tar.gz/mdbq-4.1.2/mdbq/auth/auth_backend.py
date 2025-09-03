"""
独立用户认证系统 - 后端核心库

功能特性:
- 基于JWT的双令牌认证机制
- MySQL数据库支持
- 多设备会话管理
- IP限流和安全防护
- 用户注册和权限管理
- 密码加密和设备指纹验证
- 连接池和性能优化

依赖说明:
- 核心功能: 无需Flask，可独立使用
- 装饰器功能: 需要Flask (pip install flask)
- 其他依赖: pymysql, PyJWT, cryptography, dbutils

"""

from tkinter import N
import jwt # type: ignore
import pymysql
import hashlib
import secrets
import json
import re
from datetime import datetime, timedelta, timezone
from functools import wraps
from dbutils.pooled_db import PooledDB  # type: ignore

# Flask相关导入 - 用于装饰器功能
try:
    from flask import request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    request = None


# 角色权限配置
ROLE_PERMISSIONS = {
    "super_admin": [
        # 所有权限
        "read", "write", "delete", "admin", "database",
        "execute", "import", "export", "backup", "restore",
        "create", "update", "publish", "moderate",
        "configure", "settings", "maintenance",
        "user_management", "role_management", "permission_management",
        "view_logs", "view_analytics", "audit", "monitor",
        "security_audit", "access_control",
        "api_read", "api_write", "webhook", "integration",
        "file_upload", "file_download", "file_manage",
        "resource_quota", "storage_manage"
    ],
    
    "admin": [
        # 管理员权限（除了系统级配置）
        "read", "write", "delete", "database",
        "execute", "import", "export", "backup",
        "create", "update", "publish", "moderate",
        "user_management", "view_logs", "view_analytics",
        "audit", "monitor", "api_read", "api_write",
        "file_upload", "file_download", "file_manage"
    ],
    
    "manager": [
        # 经理权限
        "read", "write", "database",
        "create", "update", "publish", "moderate",
        "import", "export", "view_analytics",
        "api_read", "file_upload", "file_download"
    ],
    
    "editor": [
        # 编辑权限
        "read", "write", "create", "update",
        "file_upload", "file_download", "api_read"
    ],

    "user": [
        # 普通用户权限
        "read", "write", "create", "update", "database", 
        "file_upload", "file_download", "api_read"
    ],
    
    "viewer": [
        # 只读权限
        "read", "view_analytics", "file_download"
    ],
    
    "api_user": [
        # API专用用户
        "api_read", "api_write", "read", "write"
    ],
    
    "auditor": [
        # 审计员权限
        "read", "view_logs", "view_analytics", "audit", "monitor"
    ]
}


class StandaloneAuthManager:
    """独立的身份验证管理器"""
    
    def __init__(self, db_config, auth_config=None):
        """
        初始化认证管理器
        
        Args:
            db_config (dict): 数据库配置
                {
                    'host': 'localhost',
                    'port': 3306,
                    'user': 'root',
                    'password': 'password',
                    'database': 'auth_db'
                }
            auth_config (dict): 认证配置，可选
        """
        self.db_config = db_config
        self.db_name = db_config.get('database', 'standalone_auth')
        
        # 默认认证配置
        self.auth_config = {
            'secret_key': auth_config.get('secret_key', secrets.token_hex(32)) if auth_config else secrets.token_hex(32),
            'algorithm': 'HS256',
            'access_token_expires': 30 * 60,  # 30分钟
            'refresh_token_expires': 7 * 24 * 60 * 60,  # 7天
            'absolute_refresh_expires_days': 30,  # 30天绝对过期
            'max_refresh_rotations': 100,  # 最大轮换次数
            'session_expires_hours': 24,  # 会话过期时间
            'max_login_attempts': 5,  # 最大登录尝试次数
            'lockout_duration': 15 * 60,  # 锁定时长
            'max_concurrent_devices': 20,  # 最大并发设备数
            'device_session_expires_days': 30,  # 设备会话过期时间
            'ip_max_attempts': 10,  # IP最大尝试次数
            'ip_window_minutes': 30,  # IP限制时间窗口
            'ip_lockout_duration': 60 * 60,  # IP锁定时长
            **(auth_config or {})
        }
        
        self._init_mysql_pool()
        self.init_database()
    
    def _init_mysql_pool(self):
        """初始化MySQL连接池"""
        try:
            # 创建数据库
            self._create_database_if_not_exists()
            
            self.pool = PooledDB(
                creator=pymysql,
                maxconnections=4,   # 最大连接数
                mincached=2,        # 初始空闲连接数
                maxcached=4,        # 最大缓存连接数
                maxshared=0,        # 不使用共享连接
                blocking=True,
                maxusage=1000,      # 连接最大使用次数，防止连接泄漏
                setsession=[],      # 连接建立时执行的SQL
                reset=True,         # 连接归还时重置状态
                failures=None,      # 异常处理
                ping=7,             # 增加ping间隔：1 -> 7（7秒检查一次连接）
                host=self.db_config['host'],
                port=int(self.db_config['port']),
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,    # 启用自动提交，避免锁冲突
                # 添加连接超时设置
                connect_timeout=10,  # 连接超时10秒
                read_timeout=30,     # 读取超时30秒
                write_timeout=30,    # 写入超时30秒
                # 使用系统本地时区，不强制设置UTC
            )
            
        except Exception as e:
            print(f"MySQL连接池初始化失败: {e}")
            raise
    
    def _create_database_if_not_exists(self):
        """创建数据库（如果不存在）"""
        try:
            # 不指定数据库的连接
            conn = pymysql.connect(
                host=self.db_config['host'],
                port=int(self.db_config['port']),
                user=self.db_config['user'],
                password=self.db_config['password'],
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"创建数据库失败: {e}")
            raise
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    password_plain TEXT NOT NULL,
                    salt VARCHAR(64) NOT NULL,
                    role ENUM('super_admin', 'admin', 'manager', 'editor', 'user', 'viewer', 'api_user', 'auditor') NOT NULL DEFAULT 'user',
                    permissions JSON DEFAULT (JSON_ARRAY()),
                    is_active TINYINT(1) NOT NULL DEFAULT 1,
                    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
                    last_login TIMESTAMP(3) NULL DEFAULT NULL,
                    login_attempts TINYINT UNSIGNED NOT NULL DEFAULT 0,
                    locked_until TIMESTAMP(3) NULL DEFAULT NULL,
                    password_reset_token VARCHAR(64) NULL DEFAULT NULL COMMENT '密码重置令牌',
                    password_reset_expires TIMESTAMP(3) NULL DEFAULT NULL COMMENT '重置令牌过期时间',
                    
                    UNIQUE KEY uk_users_username (username),
                    UNIQUE KEY uk_users_email (email),
                    UNIQUE KEY uk_users_reset_token (password_reset_token),
                    KEY idx_users_role (role),
                    KEY idx_users_created_at (created_at),
                    KEY idx_users_is_active (is_active),
                    KEY idx_users_locked_until (locked_until),
                    KEY idx_users_reset_expires (password_reset_expires)
                ) ENGINE=InnoDB 
                  DEFAULT CHARSET=utf8mb4 
                  COLLATE=utf8mb4_0900_ai_ci
            ''')
            
            # 设备会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_sessions (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT UNSIGNED NOT NULL,
                    device_id VARCHAR(255) CHARACTER SET ascii NOT NULL,
                    device_fingerprint VARCHAR(255) CHARACTER SET ascii NOT NULL,
                    login_domain VARCHAR(255) NOT NULL DEFAULT '' COMMENT '登录时的域名',
                    session_version INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '会话版本号',
                    device_name VARCHAR(255) NOT NULL DEFAULT 'Unknown Device',
                    custom_name VARCHAR(255) DEFAULT NULL COMMENT '用户自定义设备名称',
                    device_type ENUM('mobile', 'desktop', 'tablet', 'unknown') NOT NULL DEFAULT 'unknown',
                    platform VARCHAR(50) DEFAULT NULL,
                    browser VARCHAR(50) DEFAULT NULL,
                    browser_version VARCHAR(40) DEFAULT NULL,
                    screen_resolution VARCHAR(40) DEFAULT NULL COMMENT '屏幕分辨率',
                    timezone_offset INT DEFAULT NULL COMMENT '时区偏移（分钟）',
                    language VARCHAR(20) DEFAULT NULL COMMENT '浏览器语言',
                    hardware_concurrency TINYINT UNSIGNED DEFAULT NULL COMMENT 'CPU核心数',
                    current_ip VARCHAR(45) NOT NULL COMMENT '当前IP地址',
                    first_ip VARCHAR(45) NOT NULL COMMENT '首次登录IP',
                    user_agent TEXT NOT NULL,
                    last_activity TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
                    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
                    is_active TINYINT(1) NOT NULL DEFAULT 1,
                    trust_level ENUM('trusted', 'normal', 'suspicious') NOT NULL DEFAULT 'normal' COMMENT '设备信任级别',
                    
                    UNIQUE KEY uk_device_sessions_device_id (device_id),
                    UNIQUE KEY uk_device_sessions_user_fingerprint_domain_version (user_id, device_fingerprint, login_domain, session_version),
                    KEY idx_device_sessions_user_id (user_id),
                    KEY idx_device_sessions_user_device (user_id, device_id),
                    KEY idx_device_sessions_last_activity (last_activity),
                    KEY idx_device_sessions_is_active (is_active),
                    KEY idx_device_sessions_fingerprint (device_fingerprint),
                    KEY idx_device_sessions_trust_level (trust_level),
                    KEY idx_device_sessions_login_domain (login_domain),
                    KEY idx_device_sessions_user_domain (user_id, login_domain),
                    
                    CONSTRAINT fk_device_sessions_user_id 
                        FOREIGN KEY (user_id) 
                        REFERENCES users (id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE
                ) ENGINE=InnoDB 
                  DEFAULT CHARSET=utf8mb4 
                  COLLATE=utf8mb4_0900_ai_ci
            ''')
            
            # 刷新令牌表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    token_hash VARCHAR(64) CHARACTER SET ascii NOT NULL,
                    token_original TEXT NOT NULL,
                    user_id BIGINT UNSIGNED NOT NULL,
                    device_session_id BIGINT UNSIGNED NOT NULL,
                    expires_at TIMESTAMP(3) NOT NULL,
                    absolute_expires_at TIMESTAMP(3) NOT NULL,
                    rotation_count INT UNSIGNED NOT NULL DEFAULT 0,
                    max_rotations INT UNSIGNED NOT NULL DEFAULT 30,
                    is_revoked TINYINT(1) NOT NULL DEFAULT 0,
                    revoked_at TIMESTAMP(3) NULL DEFAULT NULL,
                    revoked_reason VARCHAR(50) NULL DEFAULT NULL,
                    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
                    last_used_at TIMESTAMP(3) NULL DEFAULT NULL,
                    
                    UNIQUE KEY uk_refresh_tokens_token_hash (token_hash),
                    UNIQUE KEY uk_refresh_tokens_device_session (device_session_id),
                    KEY idx_refresh_tokens_user_id (user_id),
                    KEY idx_refresh_tokens_expires_at (expires_at),
                    KEY idx_refresh_tokens_absolute_expires_at (absolute_expires_at),
                    KEY idx_refresh_tokens_is_revoked (is_revoked),
                    
                    CONSTRAINT fk_refresh_tokens_user_id 
                        FOREIGN KEY (user_id) 
                        REFERENCES users (id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE,
                    CONSTRAINT fk_refresh_tokens_device_session_id 
                        FOREIGN KEY (device_session_id) 
                        REFERENCES device_sessions (id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE
                ) ENGINE=InnoDB 
                  DEFAULT CHARSET=utf8mb4 
                  COLLATE=utf8mb4_0900_ai_ci
            ''')
            
            # 登录日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_logs (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT UNSIGNED DEFAULT NULL,
                    username VARCHAR(50) DEFAULT NULL,
                    ip_address VARCHAR(45) CHARACTER SET ascii DEFAULT NULL,
                    user_agent TEXT DEFAULT NULL,
                    login_time TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
                    login_result ENUM('success', 'failure') NOT NULL,
                    failure_reason VARCHAR(100) DEFAULT NULL,
                    
                    KEY idx_login_logs_user_id (user_id),
                    KEY idx_login_logs_username (username),
                    KEY idx_login_logs_login_time (login_time),
                    KEY idx_login_logs_login_result (login_result),
                    KEY idx_login_logs_ip_address (ip_address),
                    
                    CONSTRAINT fk_login_logs_user_id 
                        FOREIGN KEY (user_id) 
                        REFERENCES users (id) 
                        ON DELETE SET NULL 
                        ON UPDATE CASCADE
                ) ENGINE=InnoDB 
                  DEFAULT CHARSET=utf8mb4 
                  COLLATE=utf8mb4_0900_ai_ci
            ''')
            
            # IP限流表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_rate_limits (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    ip_address VARCHAR(45) CHARACTER SET ascii NOT NULL,
                    action_type ENUM('login', 'register', 'password_reset') NOT NULL,
                    failure_count SMALLINT UNSIGNED NOT NULL DEFAULT 0,
                    last_failure TIMESTAMP(3) NULL DEFAULT NULL,
                    first_failure TIMESTAMP(3) NULL DEFAULT NULL,
                    locked_until TIMESTAMP(3) NULL DEFAULT NULL,
                    lockout_count SMALLINT UNSIGNED NOT NULL DEFAULT 0,
                    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
                    updated_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
                    
                    UNIQUE KEY uk_ip_rate_limits_ip_action (ip_address, action_type),
                    KEY idx_ip_rate_limits_locked_until (locked_until),
                    KEY idx_ip_rate_limits_last_failure (last_failure),
                    KEY idx_ip_rate_limits_created_at (created_at)
                ) ENGINE=InnoDB 
                  DEFAULT CHARSET=utf8mb4 
                  COLLATE=utf8mb4_0900_ai_ci
            ''')
            
            # 用户详细资料表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT UNSIGNED NOT NULL,
                    real_name VARCHAR(50) DEFAULT '' COMMENT '真实姓名',
                    nickname VARCHAR(50) DEFAULT '' COMMENT '昵称',
                    avatar_url VARCHAR(500) DEFAULT '' COMMENT '头像URL',
                    phone VARCHAR(20) DEFAULT '' COMMENT '手机号',
                    birth_date DATE DEFAULT NULL COMMENT '出生日期',
                    gender ENUM('male', 'female', 'other') DEFAULT 'other' COMMENT '性别',
                    bio TEXT COMMENT '个人简介',
                    location VARCHAR(100) DEFAULT '' COMMENT '所在地',
                    website VARCHAR(255) DEFAULT '' COMMENT '个人网站',
                    company VARCHAR(100) DEFAULT '' COMMENT '公司',
                    position VARCHAR(100) DEFAULT '' COMMENT '职位',
                    education VARCHAR(255) DEFAULT '' COMMENT '教育背景',
                    interests TEXT COMMENT '兴趣爱好',
                    social_links JSON DEFAULT NULL COMMENT '社交链接',
                    privacy_settings JSON DEFAULT NULL COMMENT '隐私设置',
                    notification_settings JSON DEFAULT NULL COMMENT '通知设置',
                    timezone VARCHAR(50) DEFAULT 'UTC' COMMENT '时区',
                    language VARCHAR(10) DEFAULT 'zh-CN' COMMENT '语言',
                    theme VARCHAR(20) DEFAULT 'light' COMMENT '主题偏好',
                    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
                    updated_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
                    
                    UNIQUE KEY uk_user_profiles_user_id (user_id),
                    KEY idx_user_profiles_real_name (real_name),
                    KEY idx_user_profiles_nickname (nickname),
                    KEY idx_user_profiles_company (company),
                    KEY idx_user_profiles_location (location),
                    
                    CONSTRAINT fk_user_profiles_user_id 
                        FOREIGN KEY (user_id) 
                        REFERENCES users (id) 
                        ON DELETE CASCADE 
                        ON UPDATE CASCADE
                ) ENGINE=InnoDB 
                  DEFAULT CHARSET=utf8mb4 
                  COLLATE=utf8mb4_0900_ai_ci
            ''')
            
        except Exception as e:
            print(f"数据库表创建失败: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def _hash_password(self, password, salt):
        """密码哈希"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password, password_hash, salt):
        """验证密码"""
        return self._hash_password(password, salt) == password_hash
    
    def _log_login_attempt(self, username, ip_address, user_agent, result, failure_reason=None, user_id=None):
        """记录登录尝试"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO login_logs (user_id, username, ip_address, user_agent, login_result, failure_reason)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, username, ip_address, user_agent, result, failure_reason))
        except Exception as e:
            print(f"记录登录日志失败: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def register_user(self, username, password, role='user', permissions=None, email=None):
        """用户注册"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 验证输入
            if not username or not password or not email:
                return {'success': False, 'message': '用户名、密码和邮箱不能为空'}
            
            if len(username.strip()) < 3:
                return {'success': False, 'message': '用户名至少需要3个字符'}
                
            if len(password) < 6:
                return {'success': False, 'message': '密码至少需要6个字符'}
            
            # 邮箱格式验证
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return {'success': False, 'message': '请输入有效的邮箱地址'}
            
            # 检查用户名是否已存在
            username_exists = self.check_username_exists(username)
            if username_exists.get('exists'):
                return {'success': False, 'message': '用户名已被占用'}
            
            # 检查邮箱是否已存在
            email_exists = self.check_email_exists(email)
            if email_exists.get('exists'):
                return {'success': False, 'message': '邮箱已被注册'}
            
            # 生成盐值和密码哈希
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            # 设置默认权限
            if permissions is None:
                permissions = ROLE_PERMISSIONS.get(role, ['read'])
            permissions_json = json.dumps(permissions)
            
            # 创建新用户
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, password_plain, salt, role, permissions, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (username, email, password_hash, password, salt, role, permissions_json, True))
            
            user_id = cursor.lastrowid
            
            return {
                'success': True,
                'message': '注册成功',
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'permissions': permissions
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'注册失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def check_username_exists(self, username):
        """
        专门检查用户名是否存在
        """
        if not username or not isinstance(username, str):
            return {
                'exists': False,
                'message': '请提供有效的用户名',
                'user_info': None
            }
        
        username = username.strip()
        if not username:
            return {
                'exists': False,
                'message': '用户名不能为空'
            }
        
        # 验证用户名格式（3-50个字符，支持字母、数字、下划线、中文）
        if len(username) < 3 or len(username) > 50:
            return {
                'exists': False,
                'message': '用户名长度应在3-50个字符之间'
            }
        
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cursor.fetchone():
                return {
                    'exists': True,
                    'message': '用户名已被占用'
                }
        except Exception as e:
            return {
                'exists': False,
                'message': '检查用户名时发生错误'
            }
        finally:
            cursor.close()
            conn.close()
        return {
            'exists': False,
            'message': '用户名可以使用'
        }
    
    def check_email_exists(self, email):
        """
        专门检查邮箱是否存在
        """
        if not email or not isinstance(email, str):
            return {
                'exists': False,
                'message': '请提供有效的邮箱地址',
            }
        
        email = email.strip().lower()
        if not email:
            return {
                'exists': False,
                'message': '邮箱地址不能为空'
            }
        
        # 验证邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {
                'exists': False,
                'message': '邮箱格式不正确'
            }
        
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            if cursor.fetchone():
                return {
                    'exists': True,
                    'message': '邮箱已被注册'
                }
        except Exception as e:
            return {
                'exists': False,
                'message': '检查邮箱时发生错误'
            }
        finally:
            cursor.close()
            conn.close()
        return {
            'exists': False,
            'message': '邮箱可以使用'
        }

    def authenticate_user(self, username_or_email, password, ip_address=None, user_agent=None):
        """用户身份验证 - 支持用户名或邮箱登录"""
        
        # 检查IP是否被限流
        ip_check = self._check_ip_rate_limit(ip_address, 'login')
        if ip_check['blocked']:
            self._log_login_attempt(username_or_email, ip_address, user_agent, 'failure', f'ip_blocked_{ip_check["remaining_time"]}s')
            return {
                'success': False,
                'error': 'ip_blocked',
                'message': ip_check['reason'],
                'remaining_time': ip_check['remaining_time']
            }
        
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 获取用户信息 - 支持用户名或邮箱
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, permissions, 
                       is_active, login_attempts, locked_until
                FROM users WHERE username = %s OR email = %s
            ''', (username_or_email, username_or_email))
            
            user = cursor.fetchone()
            if not user:
                self._log_login_attempt(username_or_email, ip_address, user_agent, 'failure', 'user_not_found')
                self._record_ip_failure(ip_address, 'login')
                return {
                    'success': False,
                    'error': 'invalid_credentials',
                    'message': '用户名/邮箱或密码错误'
                }
            
            user_id = user['id']
            username = user['username']
            email = user['email']
            password_hash = user['password_hash']
            salt = user['salt']
            role = user['role']
            permissions = user['permissions']
            is_active = user['is_active']
            login_attempts = user['login_attempts']
            locked_until = user['locked_until']
            
            # 检查账户状态
            if not is_active:
                self._log_login_attempt(username_or_email, ip_address, user_agent, 'failure', 'account_disabled', user_id)
                self._record_ip_failure(ip_address, 'login')
                return {
                    'success': False,
                    'error': 'account_disabled',
                    'message': '账户已被禁用'
                }
            
            # 检查账户锁定状态
            current_time = datetime.now()
            if locked_until and locked_until > current_time:
                    remaining_seconds = int((locked_until - current_time).total_seconds())
                    self._log_login_attempt(username_or_email, ip_address, user_agent, 'failure', 'account_locked', user_id)
                    self._record_ip_failure(ip_address, 'login')
                    return {
                        'success': False,
                        'error': 'account_locked',
                        'message': f'账户已被锁定，请在 {remaining_seconds} 秒后重试',
                        'remaining_time': remaining_seconds
                    }
            
            # 验证密码
            if not self._verify_password(password, password_hash, salt):
                # 记录失败尝试
                login_attempts += 1
                
                if login_attempts >= self.auth_config['max_login_attempts']:
                    lockout_duration = self.auth_config['lockout_duration']
                    locked_until = current_time + timedelta(seconds=lockout_duration)
                    cursor.execute('''
                        UPDATE users SET login_attempts = %s, locked_until = %s WHERE id = %s
                    ''', (login_attempts, locked_until, user_id))
                    
                    self._log_login_attempt(username_or_email, ip_address, user_agent, 'failure', f'password_incorrect_locked_{lockout_duration}s', user_id)
                    self._record_ip_failure(ip_address, 'login')
                    
                    return {
                        'success': False,
                        'error': 'account_locked',
                        'message': f'密码错误次数过多，账户已被锁定 {lockout_duration} 秒',
                        'remaining_time': lockout_duration
                    }
                else:
                    cursor.execute('''
                        UPDATE users SET login_attempts = %s WHERE id = %s
                    ''', (login_attempts, user_id))
                    
                    self._log_login_attempt(username_or_email, ip_address, user_agent, 'failure', f'password_incorrect_attempt_{login_attempts}', user_id)
                    self._record_ip_failure(ip_address, 'login')
                    
                    remaining_attempts = self.auth_config['max_login_attempts'] - login_attempts
                    return {
                        'success': False,
                        'error': 'invalid_credentials',
                        'message': f'用户名/邮箱或密码错误，还可以尝试 {remaining_attempts} 次',
                        'remaining_attempts': remaining_attempts
                    }
            
            # 登录成功，重置尝试次数
            cursor.execute('''
                UPDATE users SET login_attempts = 0, locked_until = NULL, last_login = %s WHERE id = %s
            ''', (current_time, user_id))
            
            # 记录成功登录
            self._log_login_attempt(username_or_email, ip_address, user_agent, 'success', None, user_id)
            self._reset_ip_failures(ip_address, 'login')
            
            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'permissions': self._safe_json_parse(permissions),
                'last_login': current_time.isoformat()
            }
            
        finally:
            cursor.close()
            conn.close()
    
    def generate_access_token(self, user_info):
        """生成访问令牌"""
        now = datetime.now()
        exp = now + timedelta(seconds=self.auth_config['access_token_expires'])
        
        payload = {
            'user_id': user_info['user_id'],
            'username': user_info['username'],
            'role': user_info['role'],
            'permissions': user_info['permissions'],
            'iat': int(now.timestamp()),
            'exp': int(exp.timestamp()),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.auth_config['secret_key'], algorithm=self.auth_config['algorithm'])
    
    def verify_access_token(self, token):
        """验证访问令牌"""
        try:
            payload = jwt.decode(token, self.auth_config['secret_key'], algorithms=[self.auth_config['algorithm']])

            if not payload:
                return None
            
            if payload.get('type') != 'access':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def create_or_update_device_session(self, user_id, ip_address, user_agent, device_info=None, login_domain=''):
        """创建或更新设备会话"""
        # 解析用户代理获取基本信息
        parsed_ua = self._parse_user_agent(user_agent)
        
        # 合并设备信息
        full_device_info = {
            'user_agent': user_agent,
            'platform': parsed_ua.get('platform'),
            **parsed_ua,
            **(device_info or {})
        }
        
        # 生成包含域名的设备指纹
        device_fingerprint = self._generate_device_fingerprint(full_device_info, login_domain)
        device_id = secrets.token_urlsafe(32)
        
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            
            # 软删除：将该用户在该域名下的相同设备指纹的所有活跃会话标记为非活跃
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE user_id = %s AND device_fingerprint = %s AND login_domain = %s AND is_active = 1
            ''', (user_id, device_fingerprint, login_domain))
            
            # 获取下一个版本号
            cursor.execute('''
                SELECT COALESCE(MAX(session_version), 0) + 1 as next_version
                FROM device_sessions 
                WHERE user_id = %s AND device_fingerprint = %s AND login_domain = %s
            ''', (user_id, device_fingerprint, login_domain))
            
            next_version = cursor.fetchone()['next_version']
            
            # 检查设备数量限制
            cursor.execute('''
                SELECT COUNT(*) as active_count FROM device_sessions 
                WHERE user_id = %s AND is_active = 1
                        ''', (user_id,))
            
            active_count = cursor.fetchone()['active_count']
            
            if active_count >= self.auth_config['max_concurrent_devices']:
                # 踢出最旧的设备
                cursor.execute('''
                    SELECT id FROM device_sessions 
                    WHERE user_id = %s AND is_active = 1 
                    ORDER BY last_activity ASC 
                    LIMIT %s
                ''', (user_id, active_count - self.auth_config['max_concurrent_devices'] + 1))
                
                old_sessions = cursor.fetchall()
                for old_session in old_sessions:
                    self._revoke_device_session(cursor, old_session['id'], 'device_limit')
            
            # 创建新设备会话
            cursor.execute('''
                INSERT INTO device_sessions (
                    user_id, device_id, device_fingerprint, login_domain, session_version, device_name, device_type,
                    platform, browser, browser_version, screen_resolution, timezone_offset,
                    language, hardware_concurrency, current_ip, first_ip, user_agent, last_activity
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, device_id, device_fingerprint, login_domain, next_version,
                  full_device_info.get('device_name', 'Unknown Device'),
                  full_device_info.get('device_type', 'unknown'),
                  full_device_info.get('platform'), 
                  full_device_info.get('browser'),
                  full_device_info.get('browser_version'),
                  full_device_info.get('screen_resolution'),
                  full_device_info.get('timezone_offset'),
                  full_device_info.get('language'),
                  full_device_info.get('hardware_concurrency'),
                  ip_address, ip_address, user_agent, current_time))
            
            device_session_id = cursor.lastrowid
            
            return device_session_id, device_id, full_device_info.get('device_name', 'Unknown Device')
            
        finally:
            cursor.close()
            conn.close()
    
    def generate_refresh_token(self, user_info, device_session_id):
        """生成刷新令牌"""
        token = secrets.token_urlsafe(64)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        current_time = datetime.now()
        expires_at = current_time + timedelta(seconds=self.auth_config['refresh_token_expires'])
        absolute_expires_at = current_time + timedelta(days=self.auth_config['absolute_refresh_expires_days'])
        
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 清理该设备的旧token
            cursor.execute('''
                DELETE FROM refresh_tokens 
                WHERE device_session_id = %s
            ''', (device_session_id,))
            
            # 插入新token
            cursor.execute('''
                INSERT INTO refresh_tokens (
                    token_hash, token_original, user_id, device_session_id, expires_at, absolute_expires_at,
                    rotation_count, max_rotations, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (token_hash, token, user_info['user_id'], device_session_id, expires_at,
                  absolute_expires_at, 0, self.auth_config['max_refresh_rotations'], current_time))
            
            return token
            
        finally:
            cursor.close()
            conn.close()
    
    def refresh_access_token(self, refresh_token, ip_address=None, user_agent=None):
        """刷新访问令牌"""
        try:
            if not refresh_token:
                return None
            
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            conn = self.pool.connection()
            cursor = conn.cursor()
            
            try:
                # 验证刷新令牌
                current_time = datetime.now()
                
                cursor.execute('''
                    SELECT rt.user_id, rt.device_session_id, rt.expires_at, rt.absolute_expires_at,
                           rt.rotation_count, rt.max_rotations, 
                           u.username, u.role, u.permissions,
                           ds.device_id, ds.device_name, ds.is_active as device_active
                    FROM refresh_tokens rt
                    JOIN users u ON rt.user_id = u.id
                    JOIN device_sessions ds ON rt.device_session_id = ds.id
                    WHERE rt.token_hash = %s 
                      AND rt.expires_at > %s 
                      AND rt.absolute_expires_at > %s 
                      AND rt.rotation_count < rt.max_rotations
                      AND rt.is_revoked = 0
                      AND ds.is_active = 1
                ''', (token_hash, current_time, current_time))
                
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                # 更新设备活动时间
                cursor.execute('''
                    UPDATE device_sessions 
                    SET last_activity = %s 
                    WHERE id = %s
                ''', (current_time, result['device_session_id']))
                
                # 生成新的tokens
                user_info = {
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'role': result['role'],
                    'permissions': self._safe_json_parse(result['permissions'])
                }
                
                # 生成新的access token
                access_token = self.generate_access_token(user_info)
                
                # 生成新的refresh token（轮换）
                new_token = secrets.token_urlsafe(64)
                new_token_hash = hashlib.sha256(new_token.encode()).hexdigest()
                token_expires_at = current_time + timedelta(seconds=self.auth_config['refresh_token_expires'])
                
                # 删除旧token并插入新token
                cursor.execute('''
                    DELETE FROM refresh_tokens 
                    WHERE device_session_id = %s
                ''', (result['device_session_id'],))
                
                cursor.execute('''
                    INSERT INTO refresh_tokens (
                        token_hash, token_original, user_id, device_session_id, expires_at, absolute_expires_at,
                        rotation_count, max_rotations, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (new_token_hash, new_token, result['user_id'], result['device_session_id'], 
                      token_expires_at, result['absolute_expires_at'],
                      result['rotation_count'] + 1, result['max_rotations'], current_time))
                
                return {
                    'access_token': access_token,
                    'refresh_token': new_token,
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'device_info': {
                        'device_id': result['device_id'],
                        'device_name': result['device_name']
                    },
                    'rotation_info': {
                        'current_rotation': result['rotation_count'] + 1,
                        'max_rotations': result['max_rotations'],
                        'absolute_expires_at': result['absolute_expires_at'].isoformat()
                    }
                }
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"刷新访问令牌失败: {str(e)}")
            return None
    
    def logout_user(self, user_id, ip_address=None, user_agent=None):
        """用户登出（所有设备）"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            
            # 先查询要登出的设备数量
            cursor.execute('''
                SELECT COUNT(*) as device_count FROM device_sessions 
                WHERE user_id = %s AND is_active = 1
            ''', (user_id,))
            
            device_count = cursor.fetchone()['device_count']
            
            # 撤销用户的所有刷新令牌
            cursor.execute('''
                UPDATE refresh_tokens 
                SET is_revoked = 1, revoked_at = %s, revoked_reason = 'logout' 
                WHERE user_id = %s AND is_revoked = 0
            ''', (current_time, user_id))
            
            # 停用用户的所有设备会话
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE user_id = %s AND is_active = 1
            ''', (user_id,))
            
            return {
                'success': True, 
                'message': '已成功登出所有设备',
                'logged_out_devices': device_count
            }
            
        except Exception as e:
            return {'success': False, 'message': f'登出失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()
    
    def change_password(self, user_id, old_password, new_password):
        """修改密码"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 验证输入
            if not old_password or not new_password:
                return {'success': False, 'message': '旧密码和新密码不能为空'}
                
            if len(new_password) < 6:
                return {'success': False, 'message': '新密码至少需要6个字符'}
            
            # 获取用户当前密码信息
            cursor.execute('''
                SELECT username, password_hash, salt, is_active
                FROM users WHERE id = %s
            ''', (user_id,))
            
            user = cursor.fetchone()
            if not user:
                return {'success': False, 'message': '用户不存在'}
            
            if not user['is_active']:
                return {'success': False, 'message': '账户已被禁用'}
            
            # 验证旧密码
            if not self._verify_password(old_password, user['password_hash'], user['salt']):
                return {'success': False, 'message': '旧密码错误'}
            
            # 生成新的盐值和密码哈希
            new_salt = secrets.token_hex(32)
            new_password_hash = self._hash_password(new_password, new_salt)
            
            current_time = datetime.now()
            
            # 更新密码
            cursor.execute('''
                UPDATE users 
                SET password_hash = %s, password_plain = %s, salt = %s,
                    login_attempts = 0, locked_until = NULL
                WHERE id = %s
            ''', (new_password_hash, new_password, new_salt, user_id))
            
            # 撤销所有刷新令牌（强制重新登录）
            cursor.execute('''
                UPDATE refresh_tokens 
                SET is_revoked = 1, revoked_at = %s, revoked_reason = 'password_changed' 
                WHERE user_id = %s AND is_revoked = 0
            ''', (current_time, user_id))
            
            # 停用所有设备会话
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE user_id = %s AND is_active = 1
            ''', (user_id,))
            
            return {
                'success': True, 
                'message': '密码修改成功，请重新登录'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'密码修改失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()
    
    def get_user_masked_email(self, username):
        """根据用户名获取脱敏邮箱（用于忘记密码提示）"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 查找用户邮箱
            cursor.execute('''
                SELECT email, is_active
                FROM users WHERE username = %s
            ''', (username,))
            
            user = cursor.fetchone()
            if not user or not user['is_active']:
                return {'success': False, 'message': '用户不存在'}
            
            # 返回脱敏邮箱
            masked_email = self._mask_email(user['email'])
            return {
                'success': True,
                'masked_email': masked_email
            }
            
        except Exception as e:
            return {'success': False, 'message': f'查询用户邮箱失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def request_password_reset(self, username, email):
        """请求密码重置 - 需要同时验证用户名和邮箱"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 查找用户 - 必须用户名和邮箱都匹配
            cursor.execute('''
                SELECT id, username, email, is_active
                FROM users WHERE username = %s AND email = %s
            ''', (username, email))
            
            user = cursor.fetchone()
            if not user:
                # 为安全起见，统一返回错误信息
                return {
                    'success': False, 
                    'message': '用户名或邮箱不正确'
                }
            
            if not user['is_active']:
                # 账户被禁用，也返回用户名或邮箱不正确
                return {
                    'success': False, 
                    'message': '用户名或邮箱不正确'
                }
            
            # 生成重置令牌
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)  # 1小时有效期
            
            # 保存重置令牌
            cursor.execute('''
                UPDATE users 
                SET password_reset_token = %s, password_reset_expires = %s
                WHERE id = %s
            ''', (reset_token, expires_at, user['id']))
            
            # 邮箱脱敏处理
            masked_email = self._mask_email(user['email'])
            
            # 直接返回重置令牌给前端
            return {
                'success': True,
                'message': f'验证成功，重置令牌已生成（邮箱：{masked_email}）',
                'data': {
                    'reset_token': reset_token,
                    'masked_email': masked_email,
                    'username': user['username'],
                    'expires_at': expires_at.isoformat()
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'密码重置请求失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()
    
    def reset_password_with_token(self, reset_token, new_password):
        """使用重置令牌重置密码"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 验证输入
            if not reset_token or not new_password:
                return {'success': False, 'message': '重置令牌和新密码不能为空'}
                
            if len(new_password) < 6:
                return {'success': False, 'message': '新密码至少需要6个字符'}
            
            current_time = datetime.now()
            
            # 查找有效的重置令牌
            cursor.execute('''
                SELECT id, username, is_active, password_reset_expires
                FROM users 
                WHERE password_reset_token = %s 
                  AND password_reset_expires > %s
                  AND is_active = 1
            ''', (reset_token, current_time))
            
            user = cursor.fetchone()
            if not user:
                return {'success': False, 'message': '重置令牌无效或已过期'}
            
            # 生成新的盐值和密码哈希
            new_salt = secrets.token_hex(32)
            new_password_hash = self._hash_password(new_password, new_salt)
            
            # 更新密码并清除重置令牌
            cursor.execute('''
                UPDATE users 
                SET password_hash = %s, password_plain = %s, salt = %s,
                    password_reset_token = NULL, password_reset_expires = NULL,
                    login_attempts = 0, locked_until = NULL
                WHERE id = %s
            ''', (new_password_hash, new_password, new_salt, user['id']))
            
            # 撤销所有刷新令牌
            cursor.execute('''
                UPDATE refresh_tokens 
                SET is_revoked = 1, revoked_at = %s, revoked_reason = 'password_reset' 
                WHERE user_id = %s AND is_revoked = 0
            ''', (current_time, user['id']))
            
            # 停用所有设备会话
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE user_id = %s AND is_active = 1
            ''', (user['id'],))
            
            return {
                'success': True,
                'message': '密码重置成功，请使用新密码登录',
                'username': user['username']
            }
            
        except Exception as e:
            return {'success': False, 'message': f'密码重置失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()
    
    # ==================== 辅助方法 ====================
    
    def _check_ip_rate_limit(self, ip_address, action_type='login'):
        """检查IP是否被限流"""
        if not ip_address:
            return {'blocked': False, 'remaining_time': 0, 'reason': ''}
            
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT failure_count, locked_until, lockout_count, last_failure, first_failure
                FROM ip_rate_limits 
                WHERE ip_address = %s AND action_type = %s
            ''', (ip_address, action_type))
            
            record = cursor.fetchone()
            
            if not record:
                return {'blocked': False, 'remaining_time': 0, 'reason': ''}
            
            locked_until = record['locked_until']
            
            current_time = datetime.now()
            if locked_until and locked_until > current_time:
                remaining_seconds = int((locked_until - current_time).total_seconds())
                return {
                        'blocked': True, 
                        'remaining_time': remaining_seconds,
                        'reason': f'IP被锁定，剩余时间: {remaining_seconds}秒'
                    }
            
            return {'blocked': False, 'remaining_time': 0, 'reason': ''}
            
        finally:
            cursor.close()
            conn.close()
    
    def _record_ip_failure(self, ip_address, action_type='login'):
        """记录IP级别的失败尝试"""
        if not ip_address:
            return
            
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now()
            
            cursor.execute('''
                SELECT failure_count, first_failure, lockout_count
                FROM ip_rate_limits 
                WHERE ip_address = %s AND action_type = %s
                FOR UPDATE
            ''', (ip_address, action_type))
            
            record = cursor.fetchone()
            
            if record:
                window_minutes = self.auth_config['ip_window_minutes']
                window_start = now - timedelta(minutes=window_minutes)
                first_failure = record['first_failure']
                
                if first_failure and first_failure <= window_start:
                    # 重置计数器
                    cursor.execute('''
                        UPDATE ip_rate_limits 
                        SET failure_count = 1, first_failure = %s, last_failure = %s
                        WHERE ip_address = %s AND action_type = %s
                    ''', (now, now, ip_address, action_type))
                else:
                    # 增加失败计数
                    new_count = record['failure_count'] + 1
                    cursor.execute('''
                        UPDATE ip_rate_limits 
                        SET failure_count = %s, last_failure = %s
                        WHERE ip_address = %s AND action_type = %s
                    ''', (new_count, now, ip_address, action_type))
            else:
                # 创建新记录
                cursor.execute('''
                    INSERT INTO ip_rate_limits 
                    (ip_address, action_type, failure_count, first_failure, last_failure)
                    VALUES (%s, %s, 1, %s, %s)
                ''', (ip_address, action_type, now, now))
            
        finally:
            cursor.close()
            conn.close()
    
    def _reset_ip_failures(self, ip_address, action_type='login'):
        """重置IP失败计数"""
        if not ip_address:
            return
            
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM ip_rate_limits 
                WHERE ip_address = %s AND action_type = %s
            ''', (ip_address, action_type))
        finally:
            cursor.close()
            conn.close()
    
    def _revoke_device_session(self, cursor, device_session_id, reason='manual'):
        """撤销设备会话"""
        current_time = datetime.now()
        
        # 撤销设备相关的refresh token
        cursor.execute('''
            UPDATE refresh_tokens 
            SET is_revoked = 1, revoked_at = %s, revoked_reason = %s 
            WHERE device_session_id = %s AND is_revoked = 0
        ''', (current_time, reason, device_session_id))
        
        # 停用设备会话
        cursor.execute('''
            UPDATE device_sessions 
            SET is_active = 0 
            WHERE id = %s
        ''', (device_session_id,))
    
    def _generate_device_fingerprint(self, device_info, login_domain=''):
        """
        生成稳定的设备指纹（包含登录域名）
        
        Args:
            device_info (dict): 设备信息
                - user_agent: 用户代理
                - screen_resolution: 屏幕分辨率
                - timezone_offset: 时区偏移
                - language: 浏览器语言
                - hardware_concurrency: CPU核心数
                - platform: 平台信息
            login_domain (str): 登录时的域名
        """
        # 提取稳定的设备特征（包含登录域名）
        stable_features = [
            device_info.get('user_agent', ''),
            device_info.get('screen_resolution', ''),
            str(device_info.get('timezone_offset', 0)),
            device_info.get('language', ''),
            str(device_info.get('hardware_concurrency', 0)),
            device_info.get('platform', ''),
            login_domain or '',  # 登录域名作为设备指纹的一部分
        ]
        
        # 过滤空值并连接
        fingerprint_data = ':'.join(filter(None, stable_features))
        
        # 生成SHA256哈希
        return hashlib.sha256(fingerprint_data.encode('utf-8')).hexdigest()[:32]
    
    def _parse_user_agent(self, user_agent):
        """解析User-Agent获取设备信息"""
        if not user_agent:
            return {
                'device_type': 'unknown',
                'platform': None,
                'browser': None,
                'device_name': 'Unknown Device'
            }
        
        user_agent_lower = user_agent.lower()
        
        # 设备类型判断
        if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone', 'ipad']):
            device_type = 'tablet' if 'ipad' in user_agent_lower else 'mobile'
        elif 'tablet' in user_agent_lower:
            device_type = 'tablet'
        else:
            device_type = 'desktop'
        
        # 平台识别
        platform = None
        if 'windows' in user_agent_lower:
            platform = 'Windows'
        elif 'mac' in user_agent_lower:
            platform = 'macOS'
        elif 'linux' in user_agent_lower:
            platform = 'Linux'
        elif 'android' in user_agent_lower:
            platform = 'Android'
        elif 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
            platform = 'iOS'
        
        # 浏览器识别
        browser = None
        if 'chrome' in user_agent_lower:
            browser = 'Chrome'
        elif 'firefox' in user_agent_lower:
            browser = 'Firefox'
        elif 'safari' in user_agent_lower:
            browser = 'Safari'
        elif 'edge' in user_agent_lower:
            browser = 'Edge'
        
        # 生成设备名称
        device_name = f"{platform or 'Unknown'}"
        if browser:
            device_name += f" - {browser}"
        if device_type != 'desktop':
            device_name += f" ({device_type.title()})"
        
        return {
            'device_type': device_type,
            'platform': platform,
            'browser': browser,
            'device_name': device_name
        }
    
    def _safe_json_parse(self, json_str):
        """安全解析JSON"""
        if isinstance(json_str, str):
            try:
                return json.loads(json_str)
            except:
                return []
        return json_str or []

    def _mask_email(self, email):
        """邮箱脱敏处理"""
        if not email or '@' not in email:
            return email
        
        local_part, domain_part = email.split('@', 1)
        
        # 处理本地部分（@前面的部分）
        if len(local_part) <= 3:
            # 短邮箱名，只显示第一个字符
            masked_local = local_part[0] + '***'
        else:
            # 长邮箱名，显示前3个字符
            masked_local = local_part[:3] + '***'
        
        # 处理域名部分
        if '.' in domain_part:
            domain_name, domain_ext = domain_part.rsplit('.', 1)
            if len(domain_name) <= 2:
                masked_domain = '***.' + domain_ext
            else:
                masked_domain = domain_name[:2] + '***.' + domain_ext
        else:
            masked_domain = '***'
        
        return f"{masked_local}@{masked_domain}"

    def get_user_devices(self, user_id, current_device_fingerprint=None):
        """获取用户的所有设备"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT device_id, device_fingerprint, login_domain, device_name, custom_name, device_type, 
                       platform, browser, browser_version, screen_resolution, timezone_offset,
                       language, hardware_concurrency, current_ip, first_ip, 
                       last_activity, created_at, is_active, trust_level
                FROM device_sessions 
                WHERE user_id = %s AND is_active = 1
                ORDER BY last_activity DESC
            ''', (user_id,))
            
            devices = cursor.fetchall()
            current_device_id = None
            
            devices_list = []
            for device in devices:
                is_current = device['device_fingerprint'] == current_device_fingerprint
                if is_current:
                    current_device_id = device['device_id']
                
                # 生成显示名称（优先使用自定义名称）
                display_name = device['custom_name'] or device['device_name']
                
                devices_list.append({
                    'device_id': device['device_id'],
                    'device_fingerprint': device['device_fingerprint'],  # 添加设备指纹
                    'device_name': display_name,
                    'custom_name': device['custom_name'],
                    'login_domain': device['login_domain'],
                    'device_type': device['device_type'],
                    'platform': device['platform'],
                    'browser': device['browser'],
                    'browser_version': device['browser_version'],
                    'screen_resolution': device['screen_resolution'],
                    'timezone_offset': device['timezone_offset'],
                    'language': device['language'],
                    'hardware_concurrency': device['hardware_concurrency'],
                    'current_ip': device['current_ip'],
                    'first_ip': device['first_ip'],
                    'trust_level': device['trust_level'],
                    'last_activity': device['last_activity'].isoformat() if device['last_activity'] else None,
                    'created_at': device['created_at'].isoformat() if device['created_at'] else None,
                    'is_current': is_current
                })
            
            return {
                'devices': devices_list,
                'total_count': len(devices_list),
                'current_device_id': current_device_id
            }
            
        finally:
            cursor.close()
            conn.close()

    def logout_device(self, user_id, device_id=None, ip_address=None, user_agent=None, device_info=None, login_domain=''):
        """
        【已废弃】
        登出设备（支持两种识别方式）
        
        Args:
            user_id: 用户ID
            device_id: 设备ID（用于指定设备登出）
            ip_address: IP地址（用于当前设备登出）
            user_agent: 用户代理（用于当前设备登出）
            device_info: 设备信息（用于当前设备登出）
            login_domain: 登录域名（用于当前设备登出）
        
        Returns:
            dict: 登出结果
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            
            if device_id:
                # 方式1：通过device_id查找设备（用于设备管理界面）
                cursor.execute('''
                    SELECT id, device_name FROM device_sessions 
                    WHERE user_id = %s AND device_id = %s AND is_active = 1
                ''', (user_id, device_id))
                
                device = cursor.fetchone()
                logout_reason = 'single_device_logout'
                
                if not device:
                    return {'success': False, 'message': '设备不存在或已登出'}
                    
            else:
                # 方式2：通过设备指纹查找当前设备（用于当前设备登出）
                if not user_agent:
                    return {'success': False, 'message': '缺少设备识别信息'}
                
                # 解析用户代理获取基本信息
                parsed_ua = self._parse_user_agent(user_agent)
                
                # 合并设备信息
                full_device_info = {
                    'user_agent': user_agent,
                    'platform': parsed_ua.get('platform'),
                    **parsed_ua,
                    **(device_info or {})
                }
                
                # 生成包含域名的设备指纹来识别当前设备
                device_fingerprint = self._generate_device_fingerprint(full_device_info, login_domain)
                
                # 查找当前活跃的设备会话
                cursor.execute('''
                    SELECT ds.id, ds.device_name
                    FROM device_sessions ds
                    WHERE ds.user_id = %s AND ds.device_fingerprint = %s AND ds.login_domain = %s 
                      AND ds.is_active = 1
                    ORDER BY ds.session_version DESC
                    LIMIT 1
                ''', (user_id, device_fingerprint, login_domain))
                
                device = cursor.fetchone()
                logout_reason = 'current_device_logout'
                
                if not device:
                    return {'success': False, 'message': '当前设备会话不存在或已失效'}
            
            device_session_id = device['id']
            device_name = device['device_name']
            
            # 撤销该设备的刷新令牌
            cursor.execute('''
                UPDATE refresh_tokens 
                SET is_revoked = 1, revoked_at = %s, revoked_reason = %s 
                WHERE device_session_id = %s AND is_revoked = 0
            ''', (current_time, logout_reason, device_session_id))
            
            # 停用设备会话
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE id = %s
            ''', (device_session_id,))
            
            message = f'设备 "{device_name}" 已成功登出' if device_id else f'已成功登出当前设备 "{device_name}"'
            return {'success': True, 'message': message}
            
        except Exception as e:
            return {'success': False, 'message': f'登出设备失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def logout_current_device(self, user_id, access_token=None):
        """
        退出当前设备（通过token识别）
        
        Args:
            user_id: 用户ID
            access_token: 当前的访问令牌（用于识别设备会话）
        
        Returns:
            dict: 登出结果
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            
            if access_token:
                # 方式1：通过access_token解析出设备会话信息
                try:
                    payload = self.verify_access_token(access_token)
                    if not payload:
                        return {'success': False, 'message': '无效的访问令牌'}
                    
                    # 查找该用户最近活跃的设备（作为当前设备的近似）
                    cursor.execute('''
                        SELECT ds.id, ds.device_name, rt.id as token_id
                        FROM device_sessions ds
                        LEFT JOIN refresh_tokens rt ON ds.id = rt.device_session_id AND rt.is_revoked = 0
                        WHERE ds.user_id = %s AND ds.is_active = 1
                        ORDER BY ds.last_activity DESC
                        LIMIT 1
                    ''', (user_id,))
                    
                except Exception:
                    # token解析失败，使用备用方案
                    cursor.execute('''
                        SELECT id, device_name FROM device_sessions 
                        WHERE user_id = %s AND is_active = 1
                        ORDER BY last_activity DESC
                        LIMIT 1
                    ''', (user_id,))
            else:
                # 方式2：没有token时，登出最新活跃的设备
                cursor.execute('''
                    SELECT id, device_name FROM device_sessions 
                    WHERE user_id = %s AND is_active = 1
                    ORDER BY last_activity DESC
                    LIMIT 1
                ''', (user_id,))
            
            device = cursor.fetchone()
            
            if not device:
                return {'success': False, 'message': '没有找到活跃的设备会话'}
            
            device_session_id = device['id']
            device_name = device['device_name']
            
            # 撤销该设备的刷新令牌
            cursor.execute('''
                UPDATE refresh_tokens 
                SET is_revoked = 1, revoked_at = %s, revoked_reason = 'current_device_logout' 
                WHERE device_session_id = %s AND is_revoked = 0
            ''', (current_time, device_session_id))
            
            # 停用设备会话
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE id = %s
            ''', (device_session_id,))
            
            return {'success': True, 'message': f'已成功退出当前设备 "{device_name}"'}
            
        except Exception as e:
            return {'success': False, 'message': f'退出当前设备失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def logout_specific_device(self, user_id, device_id):
        """
        退出指定设备（通过device_id）
        
        Args:
            user_id: 用户ID
            device_id: 要退出的设备ID
        
        Returns:
            dict: 登出结果
        """
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            
            # 通过device_id查找设备，确保属于该用户
            cursor.execute('''
                SELECT id, device_name FROM device_sessions 
                WHERE user_id = %s AND device_id = %s AND is_active = 1
            ''', (user_id, device_id))
            
            device = cursor.fetchone()
            
            if not device:
                return {'success': False, 'message': '设备不存在或已退出'}
            
            device_session_id = device['id']
            device_name = device['device_name']
            
            # 撤销该设备的刷新令牌
            cursor.execute('''
                UPDATE refresh_tokens 
                SET is_revoked = 1, revoked_at = %s, revoked_reason = 'specific_device_logout' 
                WHERE device_session_id = %s AND is_revoked = 0
            ''', (current_time, device_session_id))
            
            # 停用设备会话
            cursor.execute('''
                UPDATE device_sessions 
                SET is_active = 0 
                WHERE id = %s
            ''', (device_session_id,))
            
            return {'success': True, 'message': f'已成功退出设备 "{device_name}"'}
            
        except Exception as e:
            return {'success': False, 'message': f'退出指定设备失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def get_user_profile_stats(self, user_id):
        """获取用户资料统计信息"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 获取用户基本信息
            cursor.execute('''
                SELECT username, email, role, permissions, created_at, last_login, is_active
                FROM users WHERE id = %s
            ''', (user_id,))
            
            user_info = cursor.fetchone()
            
            if not user_info:
                return {'error': '用户不存在', 'user_id': user_id, '数据库查询结果': user_info}
            
            # 获取活跃设备数
            cursor.execute('''
                SELECT COUNT(*) as active_devices FROM device_sessions 
                WHERE user_id = %s AND is_active = 1
            ''', (user_id,))
            
            active_devices = cursor.fetchone()['active_devices']
            
            # 获取登录次数（成功的登录）
            cursor.execute('''
                SELECT COUNT(*) as login_count FROM login_logs 
                WHERE user_id = %s AND login_result = 'success'
            ''', (user_id,))
            
            login_count = cursor.fetchone()['login_count']
            
            # 获取最近登录记录
            cursor.execute('''
                SELECT ip_address, user_agent, login_time FROM login_logs 
                WHERE user_id = %s AND login_result = 'success'
                ORDER BY login_time DESC LIMIT 5
            ''', (user_id,))
            
            recent_logins = cursor.fetchall()
            
            return {
                'user_info': {
                    'username': user_info['username'],
                    'email': user_info['email'],
                    'role': user_info['role'],
                    'permissions': self._safe_json_parse(user_info['permissions']),
                    'created_at': user_info['created_at'].isoformat() if user_info['created_at'] else None,
                    'last_login': user_info['last_login'].isoformat() if user_info['last_login'] else None,
                    'is_active': user_info['is_active']
                },
                'statistics': {
                    'active_devices': active_devices,
                    'total_login_count': login_count,
                    'max_concurrent_devices': self.auth_config['max_concurrent_devices']
                },
                'recent_logins': [
                    {
                        'ip_address': login['ip_address'],
                        'user_agent': login['user_agent'],
                        'login_time': login['login_time'].isoformat() if login['login_time'] else None
                    }
                    for login in recent_logins
                ]
            }
            
        except Exception as e:
            return {'error': f'获取用户统计信息失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def cleanup_inactive_devices(self, user_id, days_threshold=30):
        """清理不活跃设备"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            threshold_time = current_time - timedelta(days=days_threshold)
            
            # 查找不活跃的设备
            cursor.execute('''
                SELECT id, device_name FROM device_sessions 
                WHERE user_id = %s AND is_active = 1 
                  AND last_activity < %s
            ''', (user_id, threshold_time))
            
            inactive_devices = cursor.fetchall()
            cleaned_count = len(inactive_devices)
            
            if cleaned_count > 0:
                # 撤销这些设备的令牌
                device_session_ids = [device['id'] for device in inactive_devices]
                cursor.execute('''
                    UPDATE refresh_tokens 
                    SET is_revoked = 1, revoked_at = %s, revoked_reason = 'inactive_cleanup' 
                    WHERE device_session_id IN ({})
                      AND is_revoked = 0
                '''.format(','.join(['%s'] * len(device_session_ids))), 
                [current_time] + device_session_ids)
                
                # 停用设备会话
                cursor.execute('''
                    UPDATE device_sessions 
                    SET is_active = 0 
                    WHERE id IN ({})
                '''.format(','.join(['%s'] * len(device_session_ids))), device_session_ids)
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'message': f'成功清理 {cleaned_count} 个不活跃设备'
            }
            
        except Exception as e:
            return {
                'success': False, 
                'cleaned_count': 0, 
                'message': f'清理不活跃设备失败: {str(e)}'
            }
        finally:
            cursor.close()
            conn.close()

    def rename_device(self, user_id, device_id, custom_name):
        """重命名设备"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 验证设备是否属于该用户
            cursor.execute('''
                SELECT id FROM device_sessions 
                WHERE user_id = %s AND device_id = %s AND is_active = 1
            ''', (user_id, device_id))
            
            device = cursor.fetchone()
            
            if not device:
                return {'success': False, 'message': '设备不存在或已失效'}
            
            # 更新自定义名称
            cursor.execute('''
                UPDATE device_sessions 
                SET custom_name = %s 
                WHERE id = %s
            ''', (custom_name.strip() if custom_name else None, device['id']))
            
            return {'success': True, 'message': '设备重命名成功'}
            
        except Exception as e:
            return {'success': False, 'message': f'设备重命名失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def set_device_trust_level(self, user_id, device_id, trust_level):
        """设置设备信任级别"""
        if trust_level not in ['trusted', 'normal', 'suspicious']:
            return {'success': False, 'message': '无效的信任级别'}
        
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 验证设备是否属于该用户
            cursor.execute('''
                SELECT id FROM device_sessions 
                WHERE user_id = %s AND device_id = %s AND is_active = 1
            ''', (user_id, device_id))
            
            device = cursor.fetchone()
            
            if not device:
                return {'success': False, 'message': '设备不存在或已失效'}
            
            # 更新信任级别
            cursor.execute('''
                UPDATE device_sessions 
                SET trust_level = %s 
                WHERE id = %s
            ''', (trust_level, device['id']))
            
            return {'success': True, 'message': '设备信任级别更新成功'}
            
        except Exception as e:
            return {'success': False, 'message': f'设备信任级别更新失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()

    def get_device_session_history(self, user_id, device_fingerprint, login_domain, limit=10):
        """获取设备会话历史记录"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT device_id, session_version, device_name, current_ip, first_ip,
                       last_activity, created_at, is_active, trust_level
                FROM device_sessions 
                WHERE user_id = %s AND device_fingerprint = %s AND login_domain = %s
                ORDER BY session_version DESC
                LIMIT %s
            ''', (user_id, device_fingerprint, login_domain, limit))
            
            sessions = cursor.fetchall()
            
            return [
                {
                    'device_id': session['device_id'],
                    'session_version': session['session_version'],
                    'device_name': session['device_name'],
                    'current_ip': session['current_ip'],
                    'first_ip': session['first_ip'],
                    'last_activity': session['last_activity'].isoformat() if session['last_activity'] else None,
                    'created_at': session['created_at'].isoformat() if session['created_at'] else None,
                    'is_active': session['is_active'],
                    'trust_level': session['trust_level']
                }
                for session in sessions
            ]
            
        finally:
            cursor.close()
            conn.close()

    def cleanup_old_device_sessions(self, user_id=None, days_threshold=90):
        """清理旧的非活跃设备会话记录"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            current_time = datetime.now()
            threshold_time = current_time - timedelta(days=days_threshold)
            
            if user_id:
                # 清理特定用户的旧记录
                cursor.execute('''
                    DELETE FROM device_sessions 
                    WHERE user_id = %s AND is_active = 0 AND last_activity < %s
                ''', (user_id, threshold_time))
            else:
                # 清理所有用户的旧记录
                cursor.execute('''
                    DELETE FROM device_sessions 
                    WHERE is_active = 0 AND last_activity < %s
                ''', (threshold_time,))
            
            cleaned_count = cursor.rowcount
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'message': f'成功清理 {cleaned_count} 条旧设备会话记录'
            }
            
        except Exception as e:
            return {
                'success': False, 
                'cleaned_count': 0, 
                'message': f'清理旧设备会话记录失败: {str(e)}'
            }
        finally:
            cursor.close()
            conn.close()

    def init_user_profile(self, user_id):
        """为用户初始化默认资料"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在资料
            cursor.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                return True  # 已存在，不需要初始化
            
            # 创建默认资料
            cursor.execute('''
                INSERT INTO user_profiles (
                    user_id, privacy_settings, social_links, notification_settings
                ) VALUES (%s, %s, %s, %s)
            ''', (
                user_id,
                json.dumps({
                    "profile_visibility": "public",
                    "contact_visibility": "registered",
                    "activity_visibility": "friends"
                }),
                json.dumps({
                    "github": "",
                    "linkedin": "",
                    "twitter": "",
                    "personal_site": ""
                }),
                json.dumps({
                    "email_notifications": True,
                    "login_alerts": True,
                    "security_updates": True
                })
            ))
            
            return True
            
        except Exception as e:
            print(f"初始化用户资料失败: {str(e)}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_profile(self, user_id):
        """获取用户详细资料"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 获取用户基本信息
            cursor.execute('''
                SELECT u.id, u.username, u.email, u.role, u.permissions, u.created_at, u.last_login,
                       p.real_name, p.nickname, p.avatar_url, p.phone, p.birth_date, p.gender,
                       p.bio, p.location, p.website, p.company, p.position, p.education,
                       p.interests, p.social_links, p.privacy_settings, p.notification_settings,
                       p.timezone, p.language, p.theme, p.updated_at as profile_updated_at
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.id = %s
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # 如果用户资料不存在，初始化一个
            if not result['real_name'] and not result['nickname']:
                self.init_user_profile(user_id)
                # 重新查询
                return self.get_user_profile(user_id)
            
            profile = {
                'id': result['id'],
                'username': result['username'],
                'email': result['email'],
                'role': result['role'],
                'permissions': self._safe_json_parse(result['permissions']),
                'created_at': result['created_at'].isoformat() if result['created_at'] else None,
                'last_login': result['last_login'].isoformat() if result['last_login'] else None,
                'real_name': result['real_name'] or '',
                'nickname': result['nickname'] or '',
                'avatar_url': result['avatar_url'] or '',
                'phone': result['phone'] or '',
                'birth_date': result['birth_date'].isoformat() if result['birth_date'] else None,
                'gender': result['gender'] or 'other',
                'bio': result['bio'] or '',
                'location': result['location'] or '',
                'website': result['website'] or '',
                'company': result['company'] or '',
                'position': result['position'] or '',
                'education': result['education'] or '',
                'interests': result['interests'] or '',
                'social_links': self._safe_json_parse(result['social_links']) or {},
                'privacy_settings': self._safe_json_parse(result['privacy_settings']) or {},
                'notification_settings': self._safe_json_parse(result['notification_settings']) or {},
                'timezone': result['timezone'] or 'UTC',
                'language': result['language'] or 'zh-CN',
                'theme': result['theme'] or 'light',
                'profile_updated_at': result['profile_updated_at'].isoformat() if result['profile_updated_at'] else None
            }
            
            return profile
            
        except Exception as e:
            print(f"获取用户资料失败: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_user_profile(self, user_id, profile_data):
        """更新用户详细资料"""
        conn = self.pool.connection()
        cursor = conn.cursor()
        
        try:
            # 先确保用户资料记录存在
            cursor.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
            if not cursor.fetchone():
                self.init_user_profile(user_id)
            
            # 可更新的字段
            updatable_fields = [
                'real_name', 'nickname', 'avatar_url', 'phone', 'birth_date', 'gender',
                'bio', 'location', 'website', 'company', 'position', 'education',
                'interests', 'timezone', 'language', 'theme'
            ]
            
            # JSON字段需要特殊处理
            json_fields = ['social_links', 'privacy_settings', 'notification_settings']
            
            update_fields = []
            update_values = []
            
            # 处理普通字段
            for field in updatable_fields:
                if field in profile_data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(profile_data[field])
            
            # 处理JSON字段
            for field in json_fields:
                if field in profile_data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(json.dumps(profile_data[field]))
            
            if not update_fields:
                return {'success': True, 'message': '没有需要更新的字段'}
            
            # 执行更新
            update_sql = f'''
                UPDATE user_profiles 
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            '''
            update_values.append(user_id)
            
            cursor.execute(update_sql, update_values)
            
            if cursor.rowcount > 0:
                return {'success': True, 'message': '用户资料更新成功'}
            else:
                return {'success': False, 'message': '用户资料更新失败'}
            
        except Exception as e:
            return {'success': False, 'message': f'用户资料更新失败: {str(e)}'}
        finally:
            cursor.close()
            conn.close()


# Flask集成装饰器
def require_auth(auth_manager):
    """
    认证装饰器 - 需要Flask环境
    
    使用方法:
    @require_auth(auth_manager)
    def protected_route():
        return {'user': request.current_user['username']}
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask未安装，无法使用require_auth装饰器。请安装Flask: pip install flask")
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # OPTIONS请求不需要认证
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)
            
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'status': 'error', 'message': '未提供认证令牌'}, 401
            
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            payload = auth_manager.verify_access_token(token)
            
            if not payload:
                return {'status': 'error', 'message': '无效或过期的令牌'}, 401
            
            # 将用户信息添加到请求上下文
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permissions(auth_manager, required_permissions):
    """
    权限检查装饰器 - 需要Flask环境
    
    使用方法:
    @require_permissions(auth_manager, ['admin', 'write'])
    def admin_route():
        return {'message': 'Admin only'}
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask未安装，无法使用require_permissions装饰器。请安装Flask: pip install flask")
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # OPTIONS请求不需要认证
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)
            
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'status': 'error', 'message': '未提供认证令牌'}, 401
            
            token = auth_header[7:]
            payload = auth_manager.verify_access_token(token)
            
            if not payload:
                return {'status': 'error', 'message': '无效或过期的令牌'}, 401
            
            user_permissions = payload.get('permissions', [])
            
            # 检查是否拥有所需权限
            if not any(perm in user_permissions for perm in required_permissions):
                return {'status': 'error', 'message': '权限不足'}, 403
            
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def create_auth_middleware(auth_manager):
    """
    创建通用的认证中间件函数 - 框架无关
    
    使用方法:
    auth_middleware = create_auth_middleware(auth_manager)
    
    # 在你的框架中使用
    def your_route_handler(request_headers):
        user = auth_middleware(request_headers.get('Authorization'))
        if user:
            return {'message': f'Hello {user["username"]}'}
        else:
            return {'error': 'Unauthorized'}, 401
    """
    def middleware(auth_header):
        """
        认证中间件函数
        
        Args:
            auth_header (str): Authorization头部值
            
        Returns:
            dict: 用户信息，如果认证失败返回None
        """
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        payload = auth_manager.verify_access_token(token)
        
        return payload
    
    return middleware


def create_permission_checker(auth_manager, required_permissions):
    """
    创建权限检查函数 - 框架无关
    
    使用方法:
    check_admin = create_permission_checker(auth_manager, ['admin'])
    
    def your_admin_route(request_headers):
        user = check_admin(request_headers.get('Authorization'))
        if user:
            return {'message': 'Admin access granted'}
        else:
            return {'error': 'Permission denied'}, 403
    """
    def permission_checker(auth_header):
        """
        权限检查函数
        
        Args:
            auth_header (str): Authorization头部值
            
        Returns:
            dict: 用户信息，如果权限不足返回None
        """
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]
        payload = auth_manager.verify_access_token(token)
        
        if not payload:
            return None
        
        user_permissions = payload.get('permissions', [])
        
        # 检查是否拥有所需权限
        if not any(perm in user_permissions for perm in required_permissions):
            return None
        
        return payload
    
    return permission_checker


def main():
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'standalone_auth'
    }
    
    # 认证配置
    auth_config = {
        'secret_key': 'your-secret-key',
        'access_token_expires': 30 * 60,  # 30分钟
        'refresh_token_expires': 7 * 24 * 60 * 60,  # 7天
    }
    
    # 初始化认证管理器
    auth_manager = StandaloneAuthManager(db_config, auth_config)
    
    # 注册用户
    result = auth_manager.register_user('admin', 'password123', 'admin', ['read', 'write', 'admin'], 'admin@example.com')
    print("注册结果:", result)
    
    # 用户认证
    auth_result = auth_manager.authenticate_user('admin', 'password123', '127.0.0.1', 'Mozilla/5.0...')
    print("认证结果:", auth_result)
    
    if auth_result['success']:
        # 创建设备会话
        device_session_id, device_id, device_name = auth_manager.create_or_update_device_session(
            auth_result['user_id'], '127.0.0.1', 'Mozilla/5.0...'
        )
        
        # 生成tokens
        access_token = auth_manager.generate_access_token(auth_result)
        refresh_token = auth_manager.generate_refresh_token(auth_result, device_session_id)
        
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)
        
        # 验证token
        payload = auth_manager.verify_access_token(access_token)
        print("Token验证结果:", payload)
        
        # 刷新token
        refresh_result = auth_manager.refresh_access_token(refresh_token, '127.0.0.1', 'Mozilla/5.0...')
        print("Token刷新结果:", refresh_result) 


# 使用示例
if __name__ == "__main__":
    main()