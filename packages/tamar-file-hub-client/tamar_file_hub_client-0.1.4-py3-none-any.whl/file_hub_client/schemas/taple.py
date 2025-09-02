"""
Taple 相关数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Table(BaseModel):
    """表格信息模型"""
    id: str = Field(..., description="表格ID")
    file_id: str = Field(..., description="关联文件ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    name: Optional[str] = Field(None, description="表格名称")
    description: Optional[str] = Field(None, description="表格描述")
    created_by_role: str = Field(..., description="创建者角色")
    created_by: str = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Sheet(BaseModel):
    """工作表信息模型"""
    id: str = Field(..., description="工作表ID")
    table_id: str = Field(..., description="所属表格ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    name: str = Field(..., description="工作表名称")
    description: Optional[str] = Field(None, description="工作表描述")
    position: int = Field(..., description="工作表位置")
    version: int = Field(..., description="版本号")
    created_by_role: str = Field(..., description="创建者角色")
    created_by: str = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Column(BaseModel):
    """列信息模型"""
    id: str = Field(..., description="列ID")
    sheet_id: str = Field(..., description="所属工作表ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    column_key: str = Field(..., description="列索引key")
    name: str = Field(..., description="列名称")
    column_type: str = Field(..., description="列数据类型")
    description: Optional[str] = Field(None, description="列描述信息")
    position: int = Field(..., description="列位置")
    width: Optional[int] = Field(None, description="列宽度")
    hidden: Optional[bool] = Field(None, description="是否隐藏")
    properties: Optional[Dict[str, Any]] = Field(None, description="列属性")
    version: int = Field(..., description="版本号")
    created_by_role: str = Field(..., description="创建者角色")
    created_by: str = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Row(BaseModel):
    """行信息模型"""
    id: str = Field(..., description="行ID")
    sheet_id: str = Field(..., description="所属工作表ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    row_key: str = Field(..., description="行索引key")
    position: int = Field(..., description="行位置")
    height: Optional[int] = Field(None, description="行高度")
    hidden: Optional[bool] = Field(None, description="是否隐藏")
    version: int = Field(..., description="版本号")
    created_by_role: str = Field(..., description="创建者角色")
    created_by: str = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Cell(BaseModel):
    """单元格信息模型"""
    id: str = Field(..., description="单元格ID")
    sheet_id: str = Field(..., description="所属工作表ID")
    column_id: str = Field(..., description="所属列ID")
    row_id: str = Field(..., description="所属行ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    column_key: str = Field(..., description="列索引key")
    row_key: str = Field(..., description="行索引key")
    raw_value: Optional[str] = Field(None, description="原始值")
    formatted_value: Optional[str] = Field(None, description="格式化值")
    formula: Optional[str] = Field(None, description="公式")
    styles: Optional[Dict[str, Any]] = Field(None, description="样式")
    data_type: Optional[str] = Field(None, description="数据类型")
    version: int = Field(..., description="版本号")
    created_by_role: str = Field(..., description="创建者角色")
    created_by: str = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MergedCell(BaseModel):
    """合并单元格信息模型"""
    id: str = Field(..., description="合并单元格ID")
    sheet_id: str = Field(..., description="所属工作表ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    start_column_id: str = Field(..., description="起始列ID")
    end_column_id: str = Field(..., description="结束列ID")
    start_row_id: str = Field(..., description="起始行ID")
    end_row_id: str = Field(..., description="结束行ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TableView(BaseModel):
    """表格视图信息模型"""
    id: str = Field(..., description="视图ID")
    table_id: str = Field(..., description="所属表格ID")
    sheet_id: str = Field(..., description="所属工作表ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    file_id: str = Field(..., description="关联文件ID")
    
    # 视图配置字段
    filter_criteria: Optional[Dict[str, Any]] = Field(None, description="过滤条件（JSON）")
    sort_criteria: Optional[Dict[str, Any]] = Field(None, description="排序条件（JSON）")
    visible_columns: Optional[Dict[str, bool]] = Field(None, description="可见列配置（字典格式 {column_id: bool}）")
    group_criteria: Optional[Dict[str, Any]] = Field(None, description="分组条件（JSON）")
    
    # 创建者信息
    created_by_role: str = Field(..., description="创建者角色：user-用户；agent-智能体")
    created_by: str = Field(..., description="创建者ID")
    
    # 视图基本信息
    view_name: str = Field(..., description="视图名称")
    view_type: str = Field(..., description="视图类型：table-表格视图; gantt-甘特图; calendar-日历视图等")
    
    # 视图状态
    is_hidden: bool = Field(False, description="是否隐藏")
    is_default: bool = Field(False, description="是否默认视图")
    
    # 扩展配置
    config: Optional[Dict[str, Any]] = Field(None, description="视图扩展配置（JSON）")
    
    # 时间戳
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 请求和响应模型
class CellUpdate(BaseModel):
    """单元格更新模型"""
    column_key: str = Field(..., description="列索引key")
    row_key: str = Field(..., description="行索引key")
    raw_value: Optional[str] = Field(None, description="原始值")
    formula: Optional[str] = Field(None, description="公式")
    styles: Optional[Dict[str, Any]] = Field(None, description="样式")


# 响应模型
class TableResponse(BaseModel):
    """表格响应模型"""
    table: Table = Field(..., description="表格信息")


class SheetResponse(BaseModel):
    """工作表响应模型"""
    sheet: Sheet = Field(..., description="工作表信息")


class ColumnResponse(BaseModel):
    """列响应模型"""
    column: Optional[Column] = Field(None, description="列信息")
    current_version: Optional[int] = Field(None, description="当前版本号")
    applied_immediately: Optional[bool] = Field(None, description="是否立即应用")


class RowResponse(BaseModel):
    """行响应模型"""
    row: Optional[Row] = Field(None, description="行信息")
    current_version: Optional[int] = Field(None, description="当前版本号")
    applied_immediately: Optional[bool] = Field(None, description="是否立即应用")
    success: Optional[bool] = Field(None, description="操作是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    conflict_info: Optional['ConflictInfo'] = Field(None, description="冲突信息")


class CellResponse(BaseModel):
    """单元格响应模型"""
    cell: Optional[Cell] = Field(None, description="单元格信息")
    current_version: Optional[int] = Field(None, description="当前版本号")
    applied_immediately: Optional[bool] = Field(None, description="是否立即应用")
    success: Optional[bool] = Field(None, description="操作是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    conflict_info: Optional['ConflictInfo'] = Field(None, description="冲突信息")


class MergedCellResponse(BaseModel):
    """合并单元格响应模型"""
    merged_cell: MergedCell = Field(..., description="合并单元格信息")


class ViewResponse(BaseModel):
    """视图响应模型"""
    view: TableView = Field(..., description="视图信息")


# 列表响应模型
class ListSheetsResponse(BaseModel):
    """工作表列表响应模型"""
    sheets: List[Sheet] = Field(..., description="工作表列表")


class ListColumnsResponse(BaseModel):
    """列列表响应模型"""
    columns: List[Column] = Field(..., description="列列表")


class ListRowsResponse(BaseModel):
    """行列表响应模型"""
    rows: List[Row] = Field(..., description="行列表")
    total: int = Field(..., description="总数")


class BatchCreateRowsResponse(BaseModel):
    """批量创建行响应模型"""
    rows: List[Row] = Field(..., description="创建的行列表")


class BatchUpdateCellsResponse(BaseModel):
    """批量更新单元格响应模型"""
    cells: List[Cell] = Field(..., description="更新的单元格列表")


class GetCellsByRangeResponse(BaseModel):
    """按范围获取单元格响应模型"""
    cells: List[Cell] = Field(..., description="单元格列表")


class ListMergedCellsResponse(BaseModel):
    """合并单元格列表响应模型"""
    merged_cells: List[MergedCell] = Field(..., description="合并单元格列表")


class ListViewsResponse(BaseModel):
    """视图列表响应模型"""
    views: List[TableView] = Field(..., description="视图列表")


class GetSheetVersionResponse(BaseModel):
    """获取工作表版本响应模型"""
    sheet_id: str = Field(..., description="工作表ID")
    version: int = Field(..., description="当前版本号")
    metadata: Optional[Sheet] = Field(None, description="工作表元数据")


class GetSheetDataResponse(BaseModel):
    """获取工作表数据响应模型"""
    sheet_id: str = Field(..., description="工作表ID")
    version: int = Field(..., description="当前版本号")
    metadata: Optional[Sheet] = Field(None, description="工作表元数据")
    columns: List[Column] = Field(default_factory=list, description="列数据")
    rows: List[Row] = Field(default_factory=list, description="行数据")
    cells: List[Cell] = Field(default_factory=list, description="单元格数据")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConflictInfo(BaseModel):
    """冲突信息模型"""
    has_conflict: bool = Field(..., description="是否有冲突")
    server_version: int = Field(..., description="服务器版本号")
    conflict_type: str = Field(..., description="冲突类型")
    conflicted_columns: List[str] = Field(default_factory=list, description="冲突的列")
    resolution_suggestion: Optional[str] = Field(None, description="解决建议")


class BatchEditSheetResponse(BaseModel):
    """批量编辑工作表响应模型"""
    success: bool = Field(..., description="是否成功")
    batch_id: str = Field(..., description="批次ID")
    current_version: int = Field(..., description="当前版本号")
    results: List[Any] = Field(default_factory=list, description="操作结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    conflict_info: Optional[ConflictInfo] = Field(None, description="冲突信息")


class CloneTableDataResponse(BaseModel):
    """克隆表格数据响应模型"""
    success: bool = Field(..., description="是否成功")
    new_table_id: str = Field(..., description="新创建的表格ID")
    new_file_id: str = Field(..., description="新创建的文件ID")
    sheets_cloned: int = Field(..., description="克隆的工作表数量")
    cells_cloned: int = Field(..., description="克隆的单元格数量")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExportTableDataResponse(BaseModel):
    """导出表格数据响应模型"""
    success: bool = Field(..., description="是否成功")
    export_id: str = Field(..., description="导出记录ID")
    file_url: str = Field(..., description="GCS文件URL（内部使用）")
    download_url: str = Field(..., description="下载链接（带签名的临时链接）")
    file_size: int = Field(..., description="文件大小（字节）")
    file_name: str = Field(..., description="导出的文件名")
    format: str = Field(..., description="导出格式")  # Changed from 'ExportFormat' to str
    sheets_exported: int = Field(..., description="导出的工作表数量")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="导出时间")
    expires_at: datetime = Field(..., description="下载链接过期时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }




class TableViewResponse(BaseModel):
    """表格视图响应模型"""
    view: TableView = Field(..., description="视图信息")


class BatchCreateTableViewResult(BaseModel):
    """批量创建表格视图结果模型"""
    success: bool = Field(..., description="是否成功")
    view: Optional[TableView] = Field(None, description="成功时返回创建的视图")
    error_message: Optional[str] = Field(None, description="失败时的错误信息")
    view_name: Optional[str] = Field(None, description="视图名称（用于标识是哪个视图）")


class BatchCreateTableViewsResponse(BaseModel):
    """批量创建表格视图响应模型"""
    results: List[BatchCreateTableViewResult] = Field(default_factory=list, description="批量创建结果")
    success_count: int = Field(..., description="成功创建的数量")
    failed_count: int = Field(..., description="失败的数量")


class ListTableViewsResponse(BaseModel):
    """列出表格视图响应模型"""
    views: List[TableView] = Field(default_factory=list, description="视图列表")
    total_count: int = Field(..., description="总数量")


class ImportTableDataResponse(BaseModel):
    """导入表格数据响应模型"""
    success: bool = Field(..., description="是否成功")
    table_id: str = Field(..., description="导入的表格ID（新建或现有）")
    file_id: Optional[str] = Field(None, description="创建的文件ID（如果创建了新表格）")
    sheets_imported: int = Field(..., description="导入的工作表数量")
    rows_imported: int = Field(..., description="导入的行数")
    cells_imported: int = Field(..., description="导入的单元格数量")
    sheet_results: List[Dict[str, Any]] = Field(default_factory=list, description="每个工作表的导入结果")
    error_message: Optional[str] = Field(None, description="错误信息（如果失败）")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告信息")
    created_at: datetime = Field(..., description="导入时间")
    processing_time_ms: int = Field(..., description="处理时间（毫秒）")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }