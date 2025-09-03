# -*- coding: utf-8 -*-
"""
加密解密管理模块
"""

import os
import json
import base64
import time
import hashlib
import hmac
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Union, List, Protocol, runtime_checkable, Tuple
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from mdbq.myconf import myconf # type: ignore
from mdbq.log import mylogger


# ==================== 配置和常量 ====================

@dataclass
class CryptoConfig:
    """
    加密配置类
    """
    # 密钥配置
    key_dir_path: str = os.path.expanduser("~")
    keys_subdir: str = 'dpsk_keys'
    public_key_filename: str = 'public_key'
    private_key_filename: str = 'private_key'
    
    # 缓存配置
    enable_key_cache: bool = True
    key_cache_ttl_seconds: int = 3600
    
    # 验证配置
    time_window_seconds: int = 300
    enable_nonce_check: bool = False
    nonce_expire_seconds: int = 600
    nonce_redis_prefix: str = "crypto_nonce"


# ==================== 结果类 ====================

@dataclass
class AuthenticationResult:
    """认证结果"""
    success: bool
    payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    
    @classmethod
    def success_result(cls, payload: Dict[str, Any], execution_time: float = 0.0):
        return cls(success=True, payload=payload, execution_time_ms=execution_time)
    
    @classmethod
    def failure_result(cls, error_message: str, execution_time: float = 0.0):
        return cls(success=False, error_message=error_message, execution_time_ms=execution_time)


# ==================== 密钥管理 ====================

class KeyManager:
    """密钥管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    _cache = {}
    _cache_time = {}
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: CryptoConfig, logger: Any):
        if hasattr(self, '_initialized'):
            return
        self.config = config
        self.logger = logger
        self._initialized = True
    
    def get_public_key(self) -> Optional[str]:
        """获取公钥PEM字符串"""
        cache_key = 'public_key'
        
        # 检查缓存
        if self.config.enable_key_cache and cache_key in self._cache:
            cache_time = self._cache_time.get(cache_key, 0)
            if time.time() - cache_time < self.config.key_cache_ttl_seconds:
                return self._cache[cache_key]
        
        # 读取文件
        try:
            key_path = os.path.join(
                self.config.key_dir_path,
                self.config.keys_subdir,
                self.config.public_key_filename + '.pem'
            )
            
            with open(key_path, 'r', encoding='utf-8') as f:
                public_key_pem = f.read().strip()
            
            # 缓存结果
            if self.config.enable_key_cache:
                self._cache[cache_key] = public_key_pem
                self._cache_time[cache_key] = time.time()
            
            return public_key_pem
            
        except Exception as e:
            self.logger.error("读取公钥失败", {'error': str(e)})
            return None
    
    def get_private_key(self) -> Optional[Any]:
        """获取私钥对象"""
        cache_key = 'private_key'
        
        # 检查缓存
        if self.config.enable_key_cache and cache_key in self._cache:
            cache_time = self._cache_time.get(cache_key, 0)
            if time.time() - cache_time < self.config.key_cache_ttl_seconds:
                return self._cache[cache_key]
        
        # 读取文件
        try:
            key_path = os.path.join(
                self.config.key_dir_path,
                self.config.keys_subdir,
                self.config.private_key_filename + '.pem'
            )
            
            with open(key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # 缓存结果
            if self.config.enable_key_cache:
                self._cache[cache_key] = private_key
                self._cache_time[cache_key] = time.time()
            
            return private_key
            
        except Exception as e:
            self.logger.error("读取私钥失败", {'error': str(e)})
            return None
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        self._cache_time.clear()


# ==================== 加密服务 ====================

class CryptoService:
    """加密服务"""
    
    def __init__(self, key_manager: KeyManager, logger: Any):
        self.key_manager = key_manager
        self.logger = logger
    
    def decrypt_token(self, encrypted_token: str) -> Optional[Dict[str, Any]]:
        """解密令牌"""
        try:
            # 解析加密数据
            encrypted_data = json.loads(base64.b64decode(encrypted_token))

            # 获取私钥
            private_key = self.key_manager.get_private_key()
            if not private_key:
                self.logger.error("无法获取私钥")
                return None
            
            # 解密AES密钥
            encrypted_aes_key = base64.b64decode(encrypted_data['key'])
            
            # 使用SHA-512加密算法
            try:
                aes_key = private_key.decrypt(
                    encrypted_aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA512()),
                        algorithm=hashes.SHA512(),
                        label=None
                    )
                )
            except Exception as decrypt_error:
                self.logger.error("RSA解密失败", {'error': str(decrypt_error)})
            
            # 解密数据
            iv = base64.b64decode(encrypted_data['iv'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            
            # 检查是否有认证标签（AES-GCM需要）
            if 'tag' in encrypted_data:
                tag = base64.b64decode(encrypted_data['tag'])
                # 将tag附加到密文末尾（AES-GCM标准做法）
                ciphertext_with_tag = ciphertext + tag
            else:
                # 如果没有tag，假设密文已经包含tag
                ciphertext_with_tag = ciphertext
            
            try:
                aesgcm = AESGCM(aes_key)
                decrypted_data = aesgcm.decrypt(iv, ciphertext_with_tag, None)
            except Exception as aes_error:
                self.logger.error("AES-GCM解密失败", {'error': str(aes_error)})
                return None
            
            # 解析JSON
            try:
                payload = json.loads(decrypted_data.decode('utf-8'))
                return payload
            except json.JSONDecodeError as json_error:
                self.logger.error("JSON解析失败", {'error': str(json_error)})
                return None
            
        except Exception as e:
            self.logger.error("解密失败", {'error': str(e)})
            return None


# ==================== 验证服务 ====================

class Validator:
    """验证器"""
    
    def __init__(self, config: CryptoConfig, redis_client: Any, logger: Any):
        self.config = config
        self.redis_client = redis_client
        self.logger = logger
    
    def validate_timestamp(self, payload: Dict[str, Any]) -> bool:
        """验证时间戳"""
        try:
            current_time = int(time.time())
            payload_timestamp = payload.get('timestamp')
            
            if not isinstance(payload_timestamp, (int, float)):
                return False
            
            time_diff = abs(current_time - int(payload_timestamp))
            return time_diff <= self.config.time_window_seconds
            
        except Exception:
            return False
    
    def validate_nonce(self, payload: Dict[str, Any]) -> bool:
        """验证nonce（防重放）"""
        if not self.config.enable_nonce_check or not self.redis_client:
            return True
        
        try:
            nonce = payload.get('nonce')
            if not nonce:
                return False
            
            nonce_key = f"{self.config.nonce_redis_prefix}:{nonce}"
            
            # 检查nonce是否已存在
            if self.redis_client.exists(nonce_key):
                return False
            
            # 设置nonce（防止重复使用）
            self.redis_client.setex(
                nonce_key, 
                self.config.nonce_expire_seconds, 
                "used"
            )
            return True
            
        except Exception as e:
            self.logger.error("Nonce验证失败", {'error': str(e)})
            return False
    
    def validate(self, payload: Dict[str, Any]) -> bool:
        """执行所有验证"""
        return (self.validate_timestamp(payload) and 
                self.validate_nonce(payload))


# ==================== 主要管理器 ====================

class OptimizedCryptoManager:
    """
    加密管理器
    
    特点：
    1. 复用外部Redis连接，避免重复创建连接池
    2. 单例密钥管理，避免重复读取文件
    """
    
    def __init__(self, config: CryptoConfig, redis_client: Any = None, logger: Any = None):
        self.config = config
        self.redis_client = redis_client
        
        # 初始化日志器
        if logger is None:
            self.logger = mylogger.MyLogger(
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
        else:
            self.logger = logger
        
        # 初始化组件
        self.key_manager = KeyManager(config, self.logger)
        self.crypto_service = CryptoService(self.key_manager, self.logger)
        self.validator = Validator(config, redis_client, self.logger)
        
        self.logger.debug("OptimizedCryptoManager初始化完成")
    
    # ==================== 主要API ====================
    
    def authenticate_token(self, token: str) -> AuthenticationResult:
        """
        认证令牌 - 主要的认证API
        
        Args:
            token: 加密的令牌字符串
            
        Returns:
            AuthenticationResult: 标准化的认证结果
        """
        start_time = time.time()
        
        try:
            # 1. 解密令牌
            payload = self.crypto_service.decrypt_token(token)
            if not payload:
                return AuthenticationResult.failure_result(
                    "令牌解密失败",
                    (time.time() - start_time) * 1000
                )
            
            # 2. 验证载荷
            if not self.validator.validate(payload):
                return AuthenticationResult.failure_result(
                    "载荷验证失败",
                    (time.time() - start_time) * 1000
                )
            
            # 3. 认证成功
            execution_time = (time.time() - start_time) * 1000
            self.logger.debug(f"认证成功，耗时: {execution_time:.2f}ms")
            
            return AuthenticationResult.success_result(payload, execution_time)
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"认证异常: {str(e)}"
            self.logger.error(error_msg)
            
            return AuthenticationResult.failure_result(error_msg, execution_time)
    
    def decrypt_payload(self, encrypted_token: str) -> Optional[Dict[str, Any]]:
        """
        仅解密载荷数据（不进行验证）
        
        Args:
            encrypted_token: 加密的令牌字符串
            
        Returns:
            解密后的载荷数据或None
        """
        return self.crypto_service.decrypt_token(encrypted_token)
    
    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        验证解密后的载荷数据
        
        Args:
            payload: 解密后的载荷数据
            
        Returns:
            验证是否通过
        """
        if not payload:
            return False
        
        try:
            return self.validator.validate(payload)
        except Exception as e:
            self.logger.error("载荷验证异常", {'error': str(e)})
            return False
    
    def get_public_key(self) -> Optional[str]:
        """获取PEM格式的公钥字符串"""
        return self.key_manager.get_public_key()
    
    # ==================== 向后兼容API（简化版）====================
    
    def get_private_key(self, token: str) -> bool:
        """验证token成功性"""
        result = self.authenticate_token(token)
        return result.success
    
    def decrypt_token(self, token: str, time_window: int = None, return_data: bool = True) -> Union[bool, Dict[str, Any]]:
        """向后兼容方法"""
        result = self.authenticate_token(token)
        if return_data:
            return result.payload if result.success else None
        return result.success
    
    # ==================== 系统管理API ====================
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态信息"""
        redis_healthy = False
        if self.redis_client:
            try:
                self.redis_client.ping()
                redis_healthy = True
            except Exception:
                redis_healthy = False
        
        return {
            'redis_healthy': redis_healthy,
            'keys_available': bool(self.key_manager.get_public_key()),
            'cache_enabled': self.config.enable_key_cache,
            'nonce_check_enabled': self.config.enable_nonce_check,
            'time_window_seconds': self.config.time_window_seconds,
            'version': '2.1.0-optimized'
        }
    
    def clear_cache(self) -> None:
        """清除所有缓存"""
        self.key_manager.clear_cache()
        self.logger.debug("所有缓存已清除")


# ==================== 便捷的创建函数 ====================

def create_crypto_manager(config: Optional[CryptoConfig] = None, 
                         redis_client: Any = None) -> OptimizedCryptoManager:
    """
    创建函数
    
    Args:
        config: 可选的配置对象，如果不提供则使用默认配置
        redis_client: 可选的Redis客户端，如果提供则复用连接
        
    Returns:
        配置好的OptimizedCryptoManager实例
    """
    if config is None:
        config = CryptoConfig()
    
    return OptimizedCryptoManager(config, redis_client)


# ==================== 示例用法 ====================

if __name__ == "__main__":
    # 示例：使用默认配置创建加密管理器
    crypto_manager = create_crypto_manager()
    
    # 示例：获取系统状态
    status = crypto_manager.get_system_status()
    print(f"系统状态: {status}")
