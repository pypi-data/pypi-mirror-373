"""
Taple 服务幂等性混入类
"""
from typing import Optional, Dict, Any
from ...utils.idempotency import generate_idempotency_key


class IdempotentTapleMixin:
    """为 Taple 服务提供幂等性支持的混入类"""
    
    def _ensure_idempotency_key(
        self,
        idempotency_key: Optional[str],
        operation_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        确保有幂等性键，如果没有则自动生成
        
        Args:
            idempotency_key: 可选的幂等性键
            operation_type: 操作类型
            params: 操作参数
            
        Returns:
            幂等性键
        """
        if idempotency_key:
            return idempotency_key
            
        return generate_idempotency_key(operation_type, params, method="content")
    
    
    def _build_column_idempotency_key(
        self,
        operation: str,
        sheet_id: str,
        column_key: Optional[str] = None,
        name: Optional[str] = None,
        column_type: Optional[str] = None,
        position: Optional[int] = None,
        width: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None
    ) -> str:
        """构建列操作的幂等性键"""
        params = {
            "sheet_id": sheet_id,
            "column_key": column_key,
            "name": name,
            "column_type": column_type,
            "position": position,
            "width": width,
            "properties": properties
        }
        # 清理空值
        params = {k: v for k, v in params.items() if v is not None}
        
        return self._ensure_idempotency_key(
            idempotency_key,
            f"column_{operation}",
            params
        )
    
    def _build_row_idempotency_key(
        self,
        operation: str,
        sheet_id: str,
        row_key: Optional[str] = None,
        position: Optional[int] = None,
        height: Optional[int] = None,
        hidden: Optional[bool] = None,
        idempotency_key: Optional[str] = None
    ) -> str:
        """构建行操作的幂等性键"""
        params = {
            "sheet_id": sheet_id,
            "row_key": row_key,
            "position": position,
            "height": height,
            "hidden": hidden
        }
        # 清理空值
        params = {k: v for k, v in params.items() if v is not None}
        
        return self._ensure_idempotency_key(
            idempotency_key,
            f"row_{operation}",
            params
        )
    
    def _build_cell_idempotency_key(
        self,
        operation: str,
        sheet_id: str,
        column_key: str,
        row_key: str,
        raw_value: Optional[str] = None,
        formatted_value: Optional[str] = None,
        formula: Optional[str] = None,
        data_type: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> str:
        """构建单元格操作的幂等性键"""
        params = {
            "sheet_id": sheet_id,
            "column_key": column_key,
            "row_key": row_key,
            "raw_value": raw_value,
            "formatted_value": formatted_value,
            "formula": formula,
            "data_type": data_type
        }
        # 清理空值
        params = {k: v for k, v in params.items() if v is not None}
        
        return self._ensure_idempotency_key(
            idempotency_key,
            f"cell_{operation}",
            params
        )
    
    def _build_batch_idempotency_key(
        self,
        operation: str,
        sheet_id: str,
        operations_count: int,
        operations_hash: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> str:
        """构建批量操作的幂等性键"""
        params = {
            "sheet_id": sheet_id,
            "operations_count": operations_count,
            "operations_hash": operations_hash
        }
        
        return self._ensure_idempotency_key(
            idempotency_key,
            f"batch_{operation}",
            params
        )