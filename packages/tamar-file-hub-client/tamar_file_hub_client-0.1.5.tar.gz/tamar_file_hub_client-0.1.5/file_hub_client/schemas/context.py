"""
用户上下文和请求上下文相关的Schema定义
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

from file_hub_client.enums import Role


@dataclass
class UserContext:
    """
    用户上下文信息
    
    包含两大类信息：
    1. ownership（所有权）: org_id, user_id - 表示资源归属
    2. operator（操作者）: actor_id, role - 表示实际操作者（可能是用户、agent或系统）
    3. request info（请求信息）: user_ip - 表示请求来源IP（用于审计和安全）
    """
    # Ownership - 资源所有权信息
    org_id: str  # 组织ID
    user_id: str  # 用户ID

    # Operator - 操作者信息
    actor_id: Optional[str] = None  # 实际操作者ID（如果为空，默认使用user_id）
    role: Role = Role.ACCOUNT  # 操作者角色（ACCOUNT, AGENT, SYSTEM等）
    
    # Request info - 请求信息
    user_ip: Optional[str] = None  # 用户IP地址（请求来源IP）

    def __post_init__(self):
        """初始化后处理，如果actor_id为空，默认使用user_id"""
        if self.actor_id is None:
            self.actor_id = self.user_id

    def to_metadata(self) -> Dict[str, str]:
        """转换为gRPC metadata格式"""
        metadata = {
            'x-org-id': self.org_id,
            'x-user-id': self.user_id,
            'x-actor-id': self.actor_id,
            'x-role': self.role,
        }
        
        # 只有当user_ip不为None时才添加x-user-ip
        if self.user_ip is not None:
            metadata['x-user-ip'] = self.user_ip
            
        return metadata

    @classmethod
    def from_metadata(cls, metadata: Dict[str, str]) -> Optional['UserContext']:
        """从metadata中解析用户上下文"""
        org_id = metadata.get('x-org-id')
        user_id = metadata.get('x-user-id')

        if not org_id or not user_id:
            return None

        return cls(
            org_id=org_id,
            user_id=user_id,
            actor_id=metadata.get('x-actor-id'),
            role=Role(metadata.get('x-role', Role.ACCOUNT)),
            user_ip=metadata.get('x-user-ip')
        )


@dataclass
class RequestContext:
    """
    请求上下文信息
    
    包含请求相关的元数据，如客户端信息、请求追踪等
    """
    request_id: Optional[str] = None  # 请求ID，用于追踪
    client_ip: Optional[str] = None  # 客户端IP地址
    client_version: Optional[str] = None  # 客户端版本
    client_type: Optional[str] = None  # 客户端类型（web, mobile, desktop, cli等）
    user_agent: Optional[str] = None  # User-Agent信息
    timestamp: Optional[datetime] = field(default_factory=datetime.now)  # 请求时间戳
    extra: Dict[str, Any] = field(default_factory=dict)  # 其他扩展信息

    def to_metadata(self) -> Dict[str, str]:
        """转换为gRPC metadata格式"""
        metadata = {}

        if self.request_id:
            metadata['x-request-id'] = self.request_id
        if self.client_ip:
            metadata['x-client-ip'] = self.client_ip
        if self.client_version:
            metadata['x-client-version'] = self.client_version
        if self.client_type:
            metadata['x-client-type'] = self.client_type
        if self.user_agent:
            metadata['x-user-agent'] = self.user_agent
        if self.timestamp:
            metadata['x-timestamp'] = self.timestamp.isoformat()

        # 添加扩展信息
        for key, value in self.extra.items():
            metadata[f'x-{key}'] = str(value)

        return metadata

    @classmethod
    def from_metadata(cls, metadata: Dict[str, str]) -> 'RequestContext':
        """从metadata中解析请求上下文"""
        # 提取标准字段
        request_id = metadata.get('x-request-id')
        client_ip = metadata.get('x-client-ip')
        client_version = metadata.get('x-client-version')
        client_type = metadata.get('x-client-type')
        user_agent = metadata.get('x-user-agent')

        # 解析时间戳
        timestamp = None
        if 'x-timestamp' in metadata:
            try:
                timestamp = datetime.fromisoformat(metadata['x-timestamp'])
            except:
                pass

        # 提取扩展字段
        extra = {}
        for key, value in metadata.items():
            if key.startswith('x-') and key not in [
                'x-request-id', 'x-client-ip', 'x-client-version',
                'x-client-type', 'x-user-agent', 'x-timestamp',
                'x-org-id', 'x-user-id', 'x-actor-id', 'x-role'
            ]:
                extra[key[2:]] = value  # 去掉 'x-' 前缀

        return cls(
            request_id=request_id,
            client_ip=client_ip,
            client_version=client_version,
            client_type=client_type,
            user_agent=user_agent,
            timestamp=timestamp,
            extra=extra
        )


@dataclass
class FullContext:
    """完整的上下文信息，包含用户上下文和请求上下文"""
    user_context: Optional[UserContext] = None
    request_context: Optional[RequestContext] = None

    def to_metadata(self) -> Dict[str, str]:
        """转换为gRPC metadata格式"""
        metadata = {}

        if self.user_context:
            metadata.update(self.user_context.to_metadata())

        if self.request_context:
            metadata.update(self.request_context.to_metadata())

        return metadata

    @classmethod
    def from_metadata(cls, metadata: Dict[str, str]) -> 'FullContext':
        """从metadata中解析完整上下文"""
        return cls(
            user_context=UserContext.from_metadata(metadata),
            request_context=RequestContext.from_metadata(metadata)
        )
