"""
幂等性支持工具
"""
import uuid
import hashlib
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta


class IdempotencyKeyGenerator:
    """幂等性键生成器"""
    
    @staticmethod
    def generate_uuid_key() -> str:
        """生成基于UUID的幂等性键"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_content_based_key(content: Dict[str, Any]) -> str:
        """
        基于内容生成幂等性键
        
        Args:
            content: 要处理的内容字典
            
        Returns:
            基于内容生成的幂等性键
        """
        # 排序内容以确保一致性
        sorted_content = _sort_dict_recursively(content)
        content_str = str(sorted_content)
        
        # 生成SHA256哈希
        hash_obj = hashlib.sha256(content_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def generate_timestamp_key(prefix: str = "taple") -> str:
        """
        基于时间戳生成幂等性键
        
        Args:
            prefix: 键前缀
            
        Returns:
            基于时间戳的幂等性键
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"


class IdempotencyManager:
    """幂等性管理器"""
    
    def __init__(self, default_ttl_minutes: int = 60):
        """
        初始化幂等性管理器
        
        Args:
            default_ttl_minutes: 默认的幂等性键TTL（分钟）
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = timedelta(minutes=default_ttl_minutes)
    
    def register_operation(
        self,
        idempotency_key: str,
        operation_type: str,
        params: Dict[str, Any],
        ttl_minutes: Optional[int] = None
    ) -> bool:
        """
        注册幂等性操作
        
        Args:
            idempotency_key: 幂等性键
            operation_type: 操作类型
            params: 操作参数
            ttl_minutes: TTL分钟数（可选）
            
        Returns:
            True if 新注册，False if 已存在
        """
        if idempotency_key in self._cache:
            # 检查是否过期
            cache_entry = self._cache[idempotency_key]
            if datetime.now() > cache_entry['expires_at']:
                # 过期，删除并重新注册
                del self._cache[idempotency_key]
            else:
                # 未过期，检查操作是否一致
                if (cache_entry['operation_type'] == operation_type and 
                    cache_entry['params'] == params):
                    return False  # 相同操作，幂等
                else:
                    raise ValueError(f"幂等性键冲突: {idempotency_key}")
        
        # 注册新操作
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes else self._default_ttl
        self._cache[idempotency_key] = {
            'operation_type': operation_type,
            'params': params,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + ttl,
            'result': None
        }
        return True
    
    def get_cached_result(self, idempotency_key: str) -> Optional[Any]:
        """
        获取缓存的结果
        
        Args:
            idempotency_key: 幂等性键
            
        Returns:
            缓存的结果，如果不存在返回None
        """
        if idempotency_key not in self._cache:
            return None
            
        cache_entry = self._cache[idempotency_key]
        if datetime.now() > cache_entry['expires_at']:
            del self._cache[idempotency_key]
            return None
            
        return cache_entry.get('result')
    
    def cache_result(self, idempotency_key: str, result: Any) -> None:
        """
        缓存操作结果
        
        Args:
            idempotency_key: 幂等性键
            result: 操作结果
        """
        if idempotency_key in self._cache:
            self._cache[idempotency_key]['result'] = result
    
    def cleanup_expired(self) -> int:
        """
        清理过期的缓存条目
        
        Returns:
            清理的条目数量
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
            
        return len(expired_keys)


def _sort_dict_recursively(obj: Any) -> Any:
    """递归排序字典，确保生成一致的哈希"""
    if isinstance(obj, dict):
        return {k: _sort_dict_recursively(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [_sort_dict_recursively(item) for item in obj]
    else:
        return obj


def generate_idempotency_key(
    operation_type: str,
    params: Optional[Dict[str, Any]] = None,
    method: str = "uuid"
) -> str:
    """
    生成幂等性键的便捷函数
    
    Args:
        operation_type: 操作类型
        params: 操作参数（可选）
        method: 生成方法（"uuid", "content", "timestamp"）
        
    Returns:
        生成的幂等性键
    """
    generator = IdempotencyKeyGenerator()
    
    if method == "uuid":
        return generator.generate_uuid_key()
    elif method == "content" and params:
        content = {"operation_type": operation_type, "params": params}
        return generator.generate_content_based_key(content)
    elif method == "timestamp":
        return generator.generate_timestamp_key(operation_type)
    else:
        # 默认使用UUID
        return generator.generate_uuid_key()