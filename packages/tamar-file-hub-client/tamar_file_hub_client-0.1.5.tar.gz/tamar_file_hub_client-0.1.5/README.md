# File Hub Client

一个基于 gRPC 的文件管理系统 Python SDK，提供异步和同步两种客户端实现。

## 功能特性

- 🚀 **双模式支持**：提供异步（AsyncIO）和同步两种客户端实现
- 📁 **完整的文件管理**：支持文件上传、下载、重命名、删除等操作
- 📂 **文件夹管理**：支持文件夹的创建、重命名、移动、删除
- 🔗 **文件分享**：支持生成分享链接，设置访问权限和密码
- 🔄 **多种上传方式**：支持直传、断点续传、客户端直传到对象存储
- 🛡️ **错误处理**：完善的异常体系和错误重试机制
- 🔒 **TLS/SSL 支持**：支持安全的加密连接，保护数据传输
- 🔁 **自动重试**：连接失败时自动重试，提高可靠性
- 📝 **类型注解**：完整的类型提示支持
- 🧩 **模块化设计**：清晰的代码结构，易于扩展
- 🎨 **图片和视频压缩**：支持多种规格的媒体文件压缩变体生成和管理
- 🏗️ **分层服务架构**：文件服务分为传统文件（blob）和自定义类型（结构化数据），每种类型独立服务，语义清晰
- 🔧 **环境变量配置**：支持通过环境变量配置所有参数
- 👤 **用户上下文管理**：支持区分资源所有权（ownership）和操作者（operator）
- 📊 **请求上下文追踪**：自动收集客户端信息，支持请求追踪和审计
- 📊 **Taple 电子表格**：完整的类 Excel 功能支持，包括数据导入导出、查询筛选、样式管理等
- 📡 **gRPC 请求日志**：自动记录所有 gRPC 请求和响应，支持 JSON 格式日志

## 项目结构

```
file-hub-client/
├── file_hub_client/              # 主包目录
│   ├── __init__.py              # 包初始化，导出版本信息和主要类
│   ├── client.py                # 客户端入口（AsyncTamarFileHubClient, TamarFileHubClient）
│   ├── py.typed                 # PEP 561 类型标记文件
│   │
│   ├── rpc/                     # gRPC 相关
│   │   ├── __init__.py         # RPC 模块初始化
│   │   ├── async_client.py     # 异步 gRPC 客户端基类
│   │   ├── sync_client.py      # 同步 gRPC 客户端基类
│   │   ├── interceptors.py     # gRPC 拦截器（自动日志记录）
│   │   ├── generate_grpc.py    # Proto 文件代码生成脚本
│   │   ├── protos/             # Protocol Buffer 定义
│   │   │   ├── file_service.proto    # 文件服务定义
│   │   │   ├── folder_service.proto  # 文件夹服务定义
│   │   │   └── taple_service.proto   # Taple 服务定义
│   │   └── gen/                # 生成的 gRPC 代码（自动生成）
│   │       ├── __init__.py
│   │       ├── file_service_pb2.py
│   │       ├── file_service_pb2_grpc.py
│   │       ├── folder_service_pb2.py
│   │       └── folder_service_pb2_grpc.py
│   │
│   ├── services/                # 服务层（分层架构：传统文件用blob_service，自定义类型独立service）
│   │   ├── __init__.py         # 服务模块导出
│   │   ├── file/               # 文件服务（统一入口，按类型分层）
│   │   │   ├── __init__.py
│   │   │   ├── base_file_service.py     # 文件服务基类
│   │   │   ├── async_blob_service.py    # 异步二进制大对象服务（传统文件上传下载）
│   │   │   ├── sync_blob_service.py     # 同步二进制大对象服务（传统文件上传下载）
│   │   │   ├── async_file_service.py    # 异步文件元数据服务（所有类型通用）
│   │   │   └── sync_file_service.py     # 同步文件元数据服务（所有类型通用）
│   │   │   # 未来扩展：spreadsheet_service, document_service, canvas_service等
│   │   ├── folder/             # 文件夹服务
│   │   │   ├── __init__.py
│   │   │   ├── async_folder_service.py  # 异步文件夹服务实现
│   │   │   └── sync_folder_service.py   # 同步文件夹服务实现
│   │   └── taple/              # Taple（电子表格）服务
│   │       ├── __init__.py
│   │       ├── base_taple_service.py    # Taple 服务基类
│   │       ├── async_taple_service.py   # 异步 Taple 服务实现
│   │       ├── sync_taple_service.py    # 同步 Taple 服务实现
│   │       └── idempotent_taple_mixin.py # 幂等性支持混入类
│   │
│   ├── schemas/                 # 数据模型（Pydantic）
│   │   ├── __init__.py         # 模型导出
│   │   ├── file.py             # 文件相关模型
│   │   ├── folder.py           # 文件夹相关模型
│   │   ├── context.py          # 上下文相关模型（用户和请求上下文）
│   │   └── taple.py            # Taple 相关模型
│   │
│   ├── enums/                   # 枚举定义
│   │   ├── __init__.py         # 枚举导出
│   │   ├── role.py             # 角色枚举（ACCOUNT, AGENT, SYSTEM）
│   │   ├── upload_mode.py      # 上传模式枚举
│   │   └── export_format.py    # 导出格式枚举
│   │
│   ├── errors/                  # 异常定义
│   │   ├── __init__.py         # 异常导出
│   │   └── exceptions.py       # 自定义异常类
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py         # 工具函数导出
│       ├── file_utils.py       # 文件操作工具
│       ├── converter.py        # 数据转换工具
│       ├── retry.py            # 重试装饰器
│       ├── upload_helper.py    # 上传辅助工具（HTTP上传器）
│       ├── download_helper.py  # 下载辅助工具（HTTP下载器）
│       ├── idempotency.py      # 幂等性支持工具
│       └── logging.py          # 日志配置和工具
│
├── tests/                      # 测试文件
│   └── taple/                  # Taple 功能测试
│       ├── config.py           # 测试配置
│       ├── test_*.py           # 各种功能测试脚本
│       └── run_all_tests.py   # 运行所有测试
│
├── .gitignore                  # Git 忽略文件配置
├── .env.example                # 环境变量配置示例
├── README.md                   # 项目说明文档（本文件）
├── setup.py                    # 安装配置文件
├── pyproject.toml             # 项目配置文件（PEP 518）
└── MANIFEST.in                # 打包配置文件
```

## 模块说明

### 核心模块

- **client.py**: 提供 `AsyncTamarFileHubClient` 和 `TamarFileHubClient` 两个客户端类，是使用 SDK 的入口点
  - 提供了预配置的单例客户端 `tamar_client` 和 `async_tamar_client`
  - 支持分层服务访问：
    - `blobs`（传统文件内容：上传/下载）
    - `files`（文件元数据：所有类型通用的管理操作）
    - `folders`（文件夹管理）
    - `taples`（电子表格服务）
    - 未来扩展：`documents`、`canvases` 等自定义类型服务

### RPC 模块 (`rpc/`)

- **async_client.py/sync_client.py**: gRPC 客户端基类，处理连接管理、元数据构建、stub 缓存
- **interceptors.py**: gRPC 拦截器，自动记录所有请求和响应日志
- **generate_grpc.py**: 从 proto 文件生成 Python 代码的脚本
- **protos/**: 存放 Protocol Buffer 定义文件
    - `file_service.proto`: 定义文件相关的 RPC 服务
    - `folder_service.proto`: 定义文件夹相关的 RPC 服务
    - `taple_service.proto`: 定义 Taple 电子表格相关的 RPC 服务

### 服务模块 (`services/`)

#### 分层服务架构设计

File Hub Client 采用分层服务架构，将文件服务按类型和语义进行清晰分离：

**📁 统一文件入口**：所有文件类型都通过统一的 `files` 接口进行元数据管理（获取、重命名、删除、列表等）

**🔄 按类型分层服务**：
- **传统文件类型**（PDF、图片、视频等）→ `blob_service` 处理
  - 核心操作：**上传** 和 **下载**
  - 特点：二进制数据，重点是存储和传输
  
- **自定义文件类型**（在线表格、文档、画布等）→ 每种类型独立 `service`
  - 核心操作：**创建** 和 **导出**
  - 特点：结构化数据，重点是数据操作和格式转换

**🎯 设计优势**：
- **语义清晰**：不同类型的文件使用不同的操作语义，更符合实际使用场景
- **易于扩展**：新增自定义文件类型时，只需添加对应的独立服务
- **职责分离**：每个服务专注于特定类型的操作，代码更易维护
- **SDK 友好**：为 SDK 使用者提供更直观的 API 设计，而非通用的 REST API

#### 具体实现

- **file/**: 文件服务实现
    - **blob_service**: 处理传统文件（二进制大对象）
        - 支持多种上传模式（普通上传、流式上传、断点续传）
        - 智能选择上传模式（根据文件大小）
        - 生成上传/下载 URL
        - 支持临时文件上传
        - **媒体文件压缩**：支持图片和视频的多规格压缩变体生成
        - **压缩管理**：获取压缩状态、管理变体、触发重新压缩
        - 适用类型：PDF、图片、视频、音频、压缩包等
    - **file_service**: 处理文件元数据操作（所有类型通用）
        - 获取、重命名、删除文件
        - 列出文件
        - 生成分享链接
        - 记录文件访问
    - **[future] document_service**: 在线文档服务（规划中）  
        - 创建文档、编辑内容、插入元素
        - 导出为 Word、PDF、HTML 等格式
    - **[future] canvas_service**: 画布服务（规划中）
        - 创建画布、绘制图形、添加元素
        - 导出为 PNG、SVG、PDF 等格式

- **folder/**: 文件夹服务实现
    - 创建、重命名、移动、删除文件夹
    - 列出文件夹内容

- **taple/**: Taple 电子表格服务实现（已上线）
    - **taple_service**: 基础表格服务
        - 创建表格、工作表、列、行、单元格
        - 支持批量操作和乐观锁版本控制
        - 合并单元格和视图管理
    - **idempotent_taple_mixin**: 幂等性支持
        - 自动管理幂等性键
        - 防止重复操作

### 数据模型 (`schemas/`)

- **file.py**: 文件相关的数据模型
    - `File`: 文件信息
    - `FileUploadResponse`: 文件上传响应
    - `UploadUrlResponse`: URL上传响应
    - `ShareLinkRequest`: 分享链接请求
    - `FileListResponse`: 文件列表响应
    - `CompressedVariant`: 压缩变体信息
    - `CompressionStatusResponse`: 压缩状态响应
    - `GetVariantsResponse`: 获取变体响应
    - `RecompressionResponse`: 重新压缩响应
    - `VariantDownloadUrlResponse`: 变体下载URL响应

- **folder.py**: 文件夹相关的数据模型
    - `FolderInfo`: 文件夹信息
    - `FolderListResponse`: 文件夹列表响应

- **context.py**: 上下文相关的数据模型
    - `UserContext`: 用户上下文（组织、用户、角色、操作者）
    - `RequestContext`: 请求上下文（请求ID、客户端信息、追踪信息）
    - `FullContext`: 完整上下文

- **taple.py**: Taple 相关的数据模型
    - `Table`: 表格信息
    - `Sheet`: 工作表信息
    - `Column`: 列信息
    - `Row`: 行信息
    - `Cell`: 单元格信息
    - `ConflictInfo`: 冲突信息
    - `BatchEditSheetResponse`: 批量编辑响应

### 枚举定义 (`enums/`)

- **role.py**: 用户角色枚举（ACCOUNT、AGENT、SYSTEM）
- **upload_mode.py**: 上传模式枚举（NORMAL、STREAM、RESUMABLE）
- **export_format.py**: 导出格式枚举（XLSX、CSV、JSON、HTML、MARKDOWN）

### 工具模块 (`utils/`)

- **file_utils.py**: 文件操作相关工具函数
    - `get_file_mime_type`: 获取文件 MIME 类型（支持自定义映射）
    - `split_file_chunks`: 文件分块
    - `calculate_file_hash`: 计算文件哈希

- **converter.py**: 数据转换工具
    - `timestamp_to_datetime`: 时间戳转换
    - `convert_proto_to_model`: Proto 消息转模型

- **retry.py**: 提供重试装饰器 `retry_with_backoff`

- **upload_helper.py**: HTTP 上传辅助工具
    - `AsyncHttpUploader`: 异步 HTTP 上传器
    - `SyncHttpUploader`: 同步 HTTP 上传器
    - 支持普通上传和断点续传

- **download_helper.py**: HTTP 下载辅助工具
    - `AsyncHttpDownloader`: 异步 HTTP 下载器
    - `SyncHttpDownloader`: 同步 HTTP 下载器
    - 支持流式下载和断点续传

- **idempotency.py**: 幂等性支持工具
    - `IdempotencyKeyGenerator`: 幂等性键生成器
    - `IdempotencyManager`: 幂等性管理器
    - `generate_idempotency_key`: 生成幂等性键函数

- **logging.py**: 日志配置和工具
    - `GrpcJSONFormatter`: JSON 格式化器
    - `GrpcRequestLogger`: gRPC 请求日志记录器
    - 支持中文日志消息和图标

### 错误处理 (`errors/`)

- **exceptions.py**: 定义了完整的异常体系
    - `FileHubError`: 基础异常类
    - `FileNotFoundError`: 文件不存在
    - `FolderNotFoundError`: 文件夹不存在
    - `UploadError`: 上传错误
    - `DownloadError`: 下载错误
    - `ValidationError`: 验证错误
    - `ConnectionError`: 连接错误
    - `TimeoutError`: 超时错误
    - `PermissionError`: 权限错误
    - 等等...

## 安装

```bash
pip install tamar-file-hub-client
```

## 配置

### 环境变量配置

File Hub Client 支持通过环境变量配置连接参数，这在生产环境中特别有用。

1. **创建 `.env` 文件**：
   ```bash
   # 在项目根目录创建 .env 文件
   touch .env
   ```

2. **编辑 `.env` 文件**：
   
   **线上环境示例（使用域名，不需要端口）**：
   ```env
   # gRPC 服务器配置 - 线上环境
   FILE_HUB_HOST=api.filehub.example.com
   # FILE_HUB_PORT 不设置，使用域名默认端口
   FILE_HUB_SECURE=true
   FILE_HUB_API_KEY=your-api-key
   
   # 连接重试配置
   FILE_HUB_RETRY_COUNT=5
   FILE_HUB_RETRY_DELAY=2.0
   ```
   
   **本地开发环境示例（使用自定义端口）**：
   ```env
   # gRPC 服务器配置 - 本地开发
   FILE_HUB_HOST=localhost
   FILE_HUB_PORT=50051
   FILE_HUB_SECURE=false
   # FILE_HUB_API_KEY 本地开发可能不需要
   
   # 连接重试配置
   FILE_HUB_RETRY_COUNT=3
   FILE_HUB_RETRY_DELAY=1.0
   ```

3. **支持的环境变量**：

   | 环境变量 | 说明 | 默认值 |
   |---------|------|--------|
   | `FILE_HUB_HOST` | gRPC 服务器地址（域名或IP） | `localhost` |
   | `FILE_HUB_PORT` | gRPC 服务器端口（可选，不设置时直接使用HOST） | 无 |
   | `FILE_HUB_SECURE` | 是否启用 TLS/SSL | `false` |
   | `FILE_HUB_API_KEY` | API 认证密钥（可选） | 无 |
   | `FILE_HUB_RETRY_COUNT` | 连接重试次数 | `3` |
   | `FILE_HUB_RETRY_DELAY` | 重试延迟（秒） | `1.0` |

### TLS/SSL 配置

当 `FILE_HUB_SECURE` 设置为 `true` 时，客户端会使用 TLS 加密连接：

- 默认使用系统的根证书
- 如果提供了 `FILE_HUB_API_KEY`，会自动添加到请求头中进行认证

```python
# 通过代码配置 TLS
from file_hub_client import TamarFileHubClient

# 方式1：使用域名（不需要指定端口）
client = TamarFileHubClient(
    host="secure-server.com",  # 只需要域名
    secure=True,
    credentials={"api_key": "your-api-key"}
)

# 方式2：使用自定义端口
client = TamarFileHubClient(
    host="secure-server.com",
    port=8443,  # 自定义端口
    secure=True,
    credentials={"api_key": "your-api-key"}
)
```

### 端口配置说明

从 v0.0.3 版本开始，端口参数变为可选：

- **线上环境**：通常只需要提供域名，不需要指定端口
- **本地开发**：可以指定自定义端口

```python
# 线上环境（使用标准端口）
client = TamarFileHubClient(
    host="api.example.com",  # 只提供域名
    secure=True
)

# 本地开发（使用自定义端口）
client = TamarFileHubClient(
    host="localhost",
    port=50051,  # 自定义端口
    secure=False
)
```

### 连接重试

客户端支持自动重试连接，对于不稳定的网络环境特别有用：

```python
# 通过代码配置重试
from file_hub_client import TamarFileHubClient

client = TamarFileHubClient(
    host="server.com",
    retry_count=5,  # 重试5次
    retry_delay=2.0  # 每次重试间隔2秒
)
```

### 日志配置

File Hub Client 支持详细的 gRPC 请求日志记录：

```python
from file_hub_client import AsyncTamarFileHubClient

# 启用日志记录（默认启用）
client = AsyncTamarFileHubClient(
    enable_logging=True,
    log_level="INFO"  # DEBUG, INFO, WARNING, ERROR
)

# 日志输出示例（JSON格式）：
# {
#   "timestamp": "2025-07-15T17:30:00.123456",
#   "level": "INFO", 
#   "type": "request",
#   "uri": "CreateFolder",
#   "request_id": "test-123",
#   "data": {
#     "folder_name": "测试文件夹",
#     "parent_id": "parent-456"
#   },
#   "message": "📤 gRPC 请求: CreateFolder",
#   "logger": "file_hub_client.grpc"
# }
```

日志类型包括：
- 📡 初始化日志
- 📤 请求日志（包含请求参数）
- ✅ 响应日志（包含耗时）
- ❌ 错误日志
- 🔗 连接成功
- ⚠️ 连接重试
- 👋 关闭连接

### 加载环境变量

使用 `python-dotenv` 加载 `.env` 文件（需要额外安装）：

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 现在可以直接使用客户端，它会自动读取环境变量
from file_hub_client import AsyncTamarFileHubClient

# 示例1：如果 FILE_HUB_PORT 未设置，将使用域名作为完整地址
# .env: FILE_HUB_HOST=api.example.com, FILE_HUB_SECURE=true
async with AsyncTamarFileHubClient() as client:
    # 连接到 api.example.com（使用默认的 HTTPS 端口）
    pass

# 示例2：如果 FILE_HUB_PORT 设置了，将使用 host:port 格式
# .env: FILE_HUB_HOST=localhost, FILE_HUB_PORT=50051
async with AsyncTamarFileHubClient() as client:
    # 连接到 localhost:50051
    pass
```

### 配置优先级

客户端配置的优先级如下（从高到低）：

1. 直接传入的参数
2. 环境变量
3. 默认值

```python
# 示例：参数会覆盖环境变量
from file_hub_client import AsyncTamarFileHubClient

# 情况1：覆盖环境变量中的 host
client = AsyncTamarFileHubClient(
    host="override-host.com",  # 这会覆盖 FILE_HUB_HOST
    # port 将使用环境变量 FILE_HUB_PORT（如果设置了）
)

# 情况2：明确不使用端口（即使环境变量设置了端口）
client = AsyncTamarFileHubClient(
    host="api.production.com",
    port=None,  # 明确指定不使用端口，忽略 FILE_HUB_PORT
    secure=True
)
```

## 快速开始

### 文件上传

File Hub Client 提供了统一的上传接口，支持多种上传模式：

#### 上传模式

- **NORMAL（普通模式）**：适用于小文件，通过 gRPC 直接上传
- **STREAM（流式上传）**：适用于流式数据上传
- **RESUMABLE（断点续传）**：支持断点续传，适用于大文件和不稳定网络

#### 最简单的上传

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 最简单的用法 - 只需要文件路径
    file_info = await client.blobs.upload(
        "path/to/document.pdf",
        folder_id="1dee0f7b-2e4f-45cd-a462-4e1d82df9bdd"  # 上传到指定文件夹，不传则默认文件夹
    )
    print(f"上传成功: {file_info.file.id}")
    print(f"文件类型: {file_info.file.file_type}")  # 自动识别为 "pdf"
```

#### 从URL上传文件

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 从URL下载并上传文件（自动提取文件名）
    file_info = await client.blobs.upload(
        url="https://example.com/document.pdf"
    )
    print(f"上传成功: {file_info.file.id}")
    
    # 从URL上传并指定文件名
    file_info = await client.blobs.upload(
        url="https://example.com/some-file",
        file_name="my_document.pdf"  # 指定文件名
    )
    print(f"文件名: {file_info.file.file_name}")
```

#### 上传不同类型的内容

```python
from file_hub_client import AsyncTamarFileHubClient
from pathlib import Path

async with AsyncTamarFileHubClient() as client:
    # 1. 上传文件路径（字符串或Path对象）
    file_info = await client.blobs.upload("path/to/file.pdf")
    file_info = await client.blobs.upload(Path("path/to/file.pdf"))

    # 2. 上传字节数据（需要指定文件名）
    content = b"This is file content"
    file_info = await client.blobs.upload(
        content,
        file_name="document.txt"
    )

    # 3. 上传文件对象
    with open("image.png", "rb") as f:
        file_info = await client.blobs.upload(f)
```

#### 大文件上传（流式上传和断点续传）

```python
from file_hub_client import AsyncTamarFileHubClient, UploadMode

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 自动根据文件大小来选择是流式上传还是断点续传
    file_info = await client.blobs.upload(
        "large_video.mp4",
        # mode=UploadMode.RESUMABLE # 也可以手动指定上传的模式
    )
```

#### 临时文件上传

```python
from file_hub_client import AsyncTamarFileHubClient, UploadMode

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 自动根据文件大小来选择是流式上传还是断点续传
    file_info = await client.blobs.upload(
        "large_video.mp4",
        # mode=UploadMode.RESUMABLE,  # 也可以手动指定上传的模式
        is_temporary=True,  # 由这个参数指定是否临时文件，是则不会纳入整个文件体系，即用户查询不到这个文件
        # expire_seconds, # 过期秒数，默认30天
    )
```

#### 保留原始文件名上传

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 上传时保留原始文件名
    file_info = await client.blobs.upload(
        "document.pdf",
        keep_original_filename=True  # 保留原始文件名，默认为False
    )
    
    # 也可以指定文件夹和其他参数
    file_info = await client.blobs.upload(
        "report.xlsx",
        folder_id="folder-123",
        keep_original_filename=True,  # 保留原始文件名
        is_temporary=False
    )
```

### 文件下载

File Hub Client 提供了统一的下载接口，支持两种结构返回：

#### 下载返回结构

- **保存到本地（本地路径）**：适用于各种文件，直接下载到本地，分块流式下载，支持重试和断点续传
- **保存到内存（bytes）**：适用于小文件，直接下载到内存，分块流式下载，支持重试

#### 下载到内存（适用于小文件）

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 下载文件到内存（适用于小文件）
    content = await client.blobs.download(file_id="file-001")
    print(f"下载完成，文件大小: {len(content)} bytes")
```

#### 下载到本地文件

```python
from file_hub_client import AsyncTamarFileHubClient
from pathlib import Path

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")

    # 下载文件到本地
    save_path = await client.blobs.download(
        file_id="file-001",
        save_path="downloads/document.pdf"  # 或 Path 对象
    )
    print(f"文件已保存到: {save_path}")
```

#### 高级下载功能

File Hub Client 提供了高级的下载URL管理功能，支持批量操作和直接获取GCS URL：

##### 批量生成下载URL

当需要为多个文件生成下载URL时，使用批量接口可以显著提高效率：

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")
    
    # 批量生成下载URL
    file_ids = ["file-001", "file-002", "file-003"]
    
    result = await client.blobs.batch_generate_download_url(
        file_ids=file_ids,
        is_cdn=True,           # 使用CDN加速（可选，默认为True）
        expire_seconds=3600    # URL有效期1小时（可选）
    )
    
    # 处理结果
    for url_info in result.download_urls:
        if url_info.error:
            print(f"文件 {url_info.file_id} 生成URL失败: {url_info.error}")
        else:
            print(f"文件 {url_info.file_id}:")
            print(f"  下载URL: {url_info.url}")
            print(f"  MIME类型: {url_info.mime_type}")
            # 根据MIME类型处理文件
            if url_info.mime_type.startswith('image/'):
                print(f"  这是一个图片文件")
            elif url_info.mime_type == 'application/pdf':
                print(f"  这是一个PDF文件")
```

同步客户端示例：

```python
from file_hub_client import TamarFileHubClient

with TamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    result = client.blobs.batch_generate_download_url(
        file_ids=["file-001", "file-002"],
        is_cdn=False  # 不使用CDN，直接返回源站URL
    )
```

**注意**：`batch_generate_download_url` 方法返回一个 `BatchDownloadUrlResponse` 对象，其中 `download_urls` 字段包含 `DownloadUrlInfo` 对象列表，每个对象包含：
- `file_id`: 文件ID
- `url`: 下载URL（如果成功生成）
- `mime_type`: 文件的MIME类型，便于正确处理文件内容
- `error`: 错误信息（如果生成失败）

##### 获取GCS URL

对于需要直接访问Google Cloud Storage的场景，可以获取文件的GCS URL和MIME类型信息：

```python
# 异步客户端 - 获取单个文件的GCS URL
async with AsyncTamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    gcs_response = await client.blobs.get_gcs_url(file_id="file-001")
    print(f"GCS URL: {gcs_response.gcs_url}")
    print(f"MIME类型: {gcs_response.mime_type}")
    # 输出示例：
    # GCS URL: gs://bucket-name/path/to/file.pdf
    # MIME类型: application/pdf
```

**注意**：`get_gcs_url` 方法现在返回一个 `GetGcsUrlResponse` 对象，包含：
- `gcs_url`: Google Cloud Storage 的完整路径
- `mime_type`: 文件的MIME类型，便于正确处理文件内容

##### 批量获取GCS URL

批量获取多个文件的GCS URL和MIME类型信息：

```python
# 异步客户端 - 批量获取GCS URL
async with AsyncTamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    file_ids = ["file-001", "file-002", "file-003"]
    result = await client.blobs.batch_get_gcs_url(file_ids)
    
    # 处理结果
    for url_info in result.gcs_urls:
        if url_info.error:
            print(f"文件 {url_info.file_id} 获取GCS URL失败: {url_info.error}")
        else:
            print(f"文件 {url_info.file_id}:")
            print(f"  GCS URL: {url_info.gcs_url}")
            print(f"  MIME类型: {url_info.mime_type}")
            # 根据MIME类型处理文件
            if url_info.mime_type.startswith('image/'):
                print(f"  这是一个图片文件")
            elif url_info.mime_type == 'application/pdf':
                print(f"  这是一个PDF文件")
```

同步客户端示例：

```python
# 同步客户端 - 批量获取GCS URL
with TamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    # 获取单个GCS URL
    gcs_response = client.blobs.get_gcs_url(file_id="file-001")
    print(f"GCS URL: {gcs_response.gcs_url}")
    print(f"MIME类型: {gcs_response.mime_type}")
    
    # 批量获取GCS URL
    result = client.blobs.batch_get_gcs_url(["file-001", "file-002"])
```

##### 使用场景说明

1. **批量下载URL生成**：
   - 适用于需要同时下载多个文件的场景
   - 支持CDN加速，提供更好的下载体验
   - 可设置URL有效期，增强安全性
   - 批量操作减少网络往返，提高效率

2. **GCS URL获取**：
   - 适用于需要与Google Cloud服务集成的场景
   - 可用于数据分析、批处理等后端处理
   - 支持使用GCS工具进行文件操作
   - 返回的是永久有效的存储路径
   - 同时返回MIME类型信息，便于正确处理不同类型的文件
   - 可根据MIME类型选择合适的处理方式（如图片处理、文档解析等）

3. **错误处理**：
   - 每个文件独立处理，部分失败不影响其他文件
   - 错误信息通过 `error` 字段返回
   - 建议在批量操作时做好错误处理和重试逻辑

### 媒体文件压缩服务

File Hub Client 支持图片和视频文件的自动压缩处理，提供多种规格的压缩变体以满足不同使用场景的需求。

#### 获取文件压缩状态

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    # 获取文件压缩状态
    status = await client.blobs.get_compression_status(file_id="file-001")
    
    print(f"压缩状态: {status.status}")  # pending, processing, completed, failed
    if status.error_message:
        print(f"错误信息: {status.error_message}")
    
    # 查看可用的压缩变体
    for variant in status.variants:
        print(f"变体: {variant.variant_name}")
        print(f"  类型: {variant.variant_type}")  # image, video, thumbnail
        print(f"  尺寸: {variant.width}x{variant.height}")
        print(f"  大小: {variant.file_size} bytes")
        print(f"  格式: {variant.format}")
        print(f"  压缩比: {variant.compression_ratio:.2f}")
```

#### 获取压缩变体列表

```python
# 获取所有压缩变体
variants = await client.blobs.get_compressed_variants(file_id="file-001")

# 按类型过滤变体
image_variants = await client.blobs.get_compressed_variants(
    file_id="file-001",
    variant_type="image"  # image, video, thumbnail
)

# 处理变体信息
for variant in variants.variants:
    print(f"变体名称: {variant.variant_name}")  # large, medium, small, thumbnail
    print(f"媒体类型: {variant.media_type}")
    print(f"文件格式: {variant.format}")
    if variant.quality:
        print(f"质量: {variant.quality}")
    if variant.duration:
        print(f"时长: {variant.duration}秒")
    if variant.bitrate:
        print(f"比特率: {variant.bitrate}")
```

#### 下载压缩变体

```python
# 生成压缩变体的下载URL
variant_url = await client.blobs.generate_variant_download_url(
    file_id="file-001",
    variant_name="medium",  # large, medium, small, thumbnail
    expire_seconds=3600,    # URL有效期
    is_cdn=True            # 是否使用CDN
)

print(f"下载URL: {variant_url.url}")
if variant_url.error:
    print(f"生成URL错误: {variant_url.error}")

# 查看变体详细信息
if variant_url.variant_info:
    info = variant_url.variant_info
    print(f"变体信息:")
    print(f"  尺寸: {info.width}x{info.height}")
    print(f"  格式: {info.format}")
    print(f"  文件大小: {info.file_size} bytes")
```

#### 触发重新压缩

```python
# 触发文件重新压缩（当需要更新压缩设置时）
recompression = await client.blobs.trigger_recompression(
    file_id="file-001",
    force_reprocess=False  # 是否强制重新处理
)

print(f"任务ID: {recompression.task_id}")
print(f"状态: {recompression.status}")

# 监控压缩进度
import asyncio
while True:
    status = await client.blobs.get_compression_status(file_id="file-001")
    print(f"当前状态: {status.status}")
    
    if status.status in ["completed", "failed"]:
        break
    
    await asyncio.sleep(5)  # 等待5秒后再次检查
```

#### 同步客户端压缩服务

```python
from file_hub_client import TamarFileHubClient

with TamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    # 所有压缩服务方法都有对应的同步版本
    status = client.blobs.get_compression_status(file_id="file-001")
    variants = client.blobs.get_compressed_variants(file_id="file-001")
    recompression = client.blobs.trigger_recompression(file_id="file-001")
    variant_url = client.blobs.generate_variant_download_url(
        file_id="file-001",
        variant_name="thumbnail"
    )
```

#### 压缩服务使用场景

1. **多设备适配**：
   - `large` - 高分辨率显示设备
   - `medium` - 标准桌面和平板
   - `small` - 手机端显示
   - `thumbnail` - 缩略图预览

2. **带宽优化**：
   - 根据网络状况选择合适的变体
   - 移动端使用压缩变体节省流量
   - 预览场景使用缩略图快速加载

3. **存储优化**：
   - 自动生成多种规格，无需手动处理
   - 智能压缩算法平衡质量和大小
   - 支持视频和图片的不同压缩策略

4. **性能优化**：
   - 异步压缩处理，不阻塞上传流程
   - 支持重新压缩以应用新的压缩设置
   - 批量状态查询减少网络请求

### 文件管理操作

File Hub Client 提供了完整的文件管理功能，通过 `files` 服务访问：

#### 获取文件信息

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")
    
    # 获取文件详细信息（返回 GetFileResponse 对象）
    response = await client.files.get_file(file_id="file-001")
    
    # 访问文件基本信息
    file_info = response.file
    print(f"文件ID: {file_info.id}")
    print(f"文件名: {file_info.file_name}")
    print(f"文件类型: {file_info.file_type}")
    print(f"创建时间: {file_info.created_at}")
    
    # 访问上传文件详细信息（如果存在）
    if response.upload_file:
        upload_info = response.upload_file
        print(f"文件大小: {upload_info.file_size} bytes")
        print(f"MIME类型: {upload_info.mime_type}")
        print(f"存储类型: {upload_info.storage_type}")
        print(f"存储路径: {upload_info.stored_path}")
```

#### 重命名文件

```python
# 重命名文件
updated_file = await client.files.rename_file(
    file_id="file-001",
    new_name="新文档名称.pdf"
)
print(f"文件已重命名为: {updated_file.file_name}")
```

#### 删除文件

```python
# 删除文件
await client.files.delete_file(file_id="file-001")
print("文件已删除")
```

#### 列出文件

```python
# 列出文件夹中的文件
file_list = await client.files.list_files(
    folder_id="folder-001",  # 可选，不指定则列出根目录
    file_name="report",      # 可选，按名称过滤
    file_type=["pdf", "docx"],  # 可选，按类型过滤
    page_size=20,
    page=1
)

for file in file_list.files:
    print(f"- {file.file_name} ({file.file_size} bytes)")
```

#### 生成分享链接

```python
# 生成文件分享链接
share_id = await client.files.generate_share_link(
    file_id="file-001",
    is_public=True,           # 是否公开
    access_scope="view",      # 访问权限：view, download
    expire_seconds=86400,     # 24小时后过期
    share_password="secret"   # 可选，设置访问密码
)
print(f"分享ID: {share_id}")
```

### 文件夹操作

File Hub Client 提供了完整的文件夹管理功能，通过 `folders` 服务访问：

#### 创建文件夹

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")
    
    # 在根目录创建文件夹
    folder = await client.folders.create_folder(
        folder_name="我的文档"
    )
    print(f"创建文件夹: {folder.id}")
    
    # 在指定文件夹下创建子文件夹
    sub_folder = await client.folders.create_folder(
        folder_name="项目资料",
        parent_id=folder.id
    )
    print(f"创建子文件夹: {sub_folder.id}")
```

#### 重命名文件夹

```python
# 重命名文件夹
updated_folder = await client.folders.rename_folder(
    folder_id="folder-001",
    new_name="新文件夹名称"
)
print(f"文件夹已重命名为: {updated_folder.folder_name}")
```

#### 移动文件夹

```python
# 移动文件夹到另一个文件夹下
moved_folder = await client.folders.move_folder(
    folder_id="folder-001",
    new_parent_id="folder-002"  # 目标父文件夹ID
)
print(f"文件夹已移动到: {moved_folder.parent_id}")
```

#### 删除文件夹

```python
# 删除文件夹（包括其中的所有内容）
await client.folders.delete_folder(folder_id="folder-001")
print("文件夹已删除")
```

#### 列出文件夹

```python
# 列出根目录下的文件夹
folder_list = await client.folders.list_folders()

# 列出指定文件夹下的子文件夹
sub_folders = await client.folders.list_folders(
    parent_id="folder-001",
    folder_name="项目",  # 可选，按名称过滤
)

for folder in folder_list.items:
    print(f"- {folder.folder_name} (ID: {folder.id})")
    print(f"  创建者: {folder.created_by}")
    print(f"  创建时间: {folder.created_at}")
```

#### 完整示例：组织文件结构

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")
    
    # 创建项目文件夹结构
    project_folder = await client.folders.create_folder("我的项目")
    docs_folder = await client.folders.create_folder("文档", parent_id=project_folder.id)
    images_folder = await client.folders.create_folder("图片", parent_id=project_folder.id)
    
    # 上传文件到对应文件夹
    doc_file = await client.blobs.upload(
        "project_plan.pdf",
        folder_id=docs_folder.id
    )
    
    image_file = await client.blobs.upload(
        "logo.png",
        folder_id=images_folder.id
    )
    
    # 列出项目文件夹的内容
    print("项目结构：")
    
    # 列出子文件夹
    folders = await client.folders.list_folders(parent_id=project_folder.id)
    for folder in folders.items:
        print(f"📁 {folder.folder_name}/")
        
        # 列出每个文件夹中的文件
        files = await client.files.list_files(folder_id=folder.id)
        for file in files.files:
            print(f"  📄 {file.file_name}")
```

### Taple 电子表格操作

File Hub Client 提供了完整的类 Excel 电子表格功能，通过 `taples` 服务访问。支持表格、工作表、列、行、单元格的完整管理功能。

#### 基本操作

```python
from file_hub_client import AsyncTamarFileHubClient

async with AsyncTamarFileHubClient() as client:
    # 设置用户上下文
    client.set_user_context(org_id="123", user_id="456")
    
    # 创建表格
    table = await client.taples.create_table(
        name="员工信息表",
        folder_id="folder-123",  # 可选，不指定则使用默认文件夹
        description="公司员工基本信息"
    )
    
    # 创建工作表
    sheet = await client.taples.create_sheet(
        table_id=table.table.id,
        name="基本信息",
        description="员工基本信息工作表"
    )
    
    # 获取表格信息
    table_info = await client.taples.get_table(table_id=table.table.id)
    # 或通过文件ID获取
    # table_info = await client.taples.get_table(file_id="file-123")
```

#### 列、行、单元格操作

```python
async with AsyncTamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    # 创建列（支持幂等性）
    column = await client.taples.create_column(
        sheet_id=sheet.sheet.id,
        name="姓名",
        column_type="text",
        width=200,
        idempotency_key="create-column-name-001"
    )
    
    # 更新列
    updated_column = await client.taples.update_column(
        sheet_id=sheet.sheet.id,
        column_key=column.column.column_key,
        name="员工姓名",
        width=250,
        hidden=False
    )
    
    # 创建行（支持幂等性）
    row = await client.taples.create_row(
        sheet_id=sheet.sheet.id,
        position=0,  # 可选，指定位置
        height=30,   # 可选，行高
        hidden=False,  # 可选，是否隐藏
        idempotency_key="create-row-001"
    )
    
    # 编辑单元格（支持幂等性）
    cell = await client.taples.edit_cell(
        sheet_id=sheet.sheet.id,
        column_key=column.column.column_key,
        row_key=row.row.row_key,
        raw_value="张三",
        idempotency_key="edit-cell-001"
    )
    
    # 删除操作
    await client.taples.delete_cell(sheet_id=sheet.sheet.id, column_key="col_1", row_key="row_1")
    await client.taples.delete_row(sheet_id=sheet.sheet.id, row_key="row_1")
    await client.taples.delete_column(sheet_id=sheet.sheet.id, column_key="col_1")
```

#### 批量操作

```python
# 批量编辑列
column_operations = [
    {
        "create": {
            "name": "部门",
            "column_type": "text",
            "position": 1
        }
    },
    {
        "update": {
            "column_key": "col_1",
            "name": "新名称",
            "width": 300
        }
    },
    {
        "delete": {
            "column_key": "col_2"
        }
    }
]

result = await client.taples.batch_edit_columns(
    sheet_id=sheet.sheet.id,
    operations=column_operations,
    idempotency_key="batch-columns-001"
)

# 批量编辑行
row_operations = [
    {
        "create": {
            "position": 0,
            "height": 40
        }
    },
    {
        "update": {
            "row_key": "row_1",
            "height": 50,
            "hidden": True
        }
    }
]

result = await client.taples.batch_edit_rows(
    sheet_id=sheet.sheet.id,
    operations=row_operations
)

# 批量编辑单元格
cell_operations = [
    {
        "edit": {
            "column_key": "col_1",
            "row_key": "row_1",
            "raw_value": "销售部"
        }
    },
    {
        "clear": {
            "column_key": "col_2",
            "row_key": "row_1"
        }
    }
]

result = await client.taples.batch_edit_cells(
    sheet_id=sheet.sheet.id,
    operations=cell_operations
)
```

#### 数据获取

```python
# 获取工作表版本（轻量级）
version_info = await client.taples.get_sheet_version(sheet_id=sheet.sheet.id)
print(f"当前版本: {version_info.version}")

# 获取完整工作表数据
sheet_data = await client.taples.get_sheet_data(
    sheet_id=sheet.sheet.id,
    version=100  # 可选，获取从该版本以来的变化
)

# 获取列数据（包含该列所有单元格）
column_data = await client.taples.get_column_data(
    sheet_id=sheet.sheet.id,
    column_key="col_1"
)

# 获取行数据（包含该行所有单元格）
row_data = await client.taples.get_row_data(
    sheet_id=sheet.sheet.id,
    row_key="row_1"
)

# 获取单个单元格数据
cell_data = await client.taples.get_cell_data(
    sheet_id=sheet.sheet.id,
    column_key="col_1",
    row_key="row_1"
)
```

#### 版本控制和冲突处理

Taple 支持乐观锁版本控制，在并发编辑时自动处理版本冲突：

```python
# 方式1：自动获取版本（推荐）
# SDK 会自动获取最新版本号
column = await client.taples.create_column(
    sheet_id=sheet.sheet.id,
    name="自动版本",
    column_type="text"
)

# 方式2：手动指定版本
# 适用于需要精确控制的场景
version_info = await client.taples.get_sheet_version(sheet_id=sheet.sheet.id)
column = await client.taples.create_column(
    sheet_id=sheet.sheet.id,
    name="手动版本",
    column_type="text",
    sheet_version=version_info.version,
    client_id="my-client-123"
)

# 批量操作时的版本控制
operations = [...]  # 你的操作列表
batch_result = await client.taples.batch_edit_sheet(
    sheet_id=sheet.sheet.id,
    operations=operations,
    sheet_version=version_info.version,
    client_id="my-client-123"
)

# 检查冲突
if batch_result.conflict_info and batch_result.conflict_info.has_conflict:
    print(f"版本冲突: {batch_result.conflict_info.conflict_type}")
    print(f"服务器版本: {batch_result.conflict_info.server_version}")
```

#### 数据导入

Taple 支持从 CSV、Excel 等文件导入数据：

```python
import tempfile
import csv

# 创建测试 CSV 文件
def create_test_csv():
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    writer = csv.writer(temp_file)
    writer.writerow(['姓名', '年龄', '部门', '薪资'])
    writer.writerow(['张三', '28', '技术部', '15000'])
    writer.writerow(['李四', '32', '销售部', '12000'])
    temp_file.close()
    return temp_file.name

# 上传 CSV 文件
csv_file = create_test_csv()
upload_result = await client.blobs.upload(csv_file, folder_id=folder_id)

# 导入到表格
import_result = await client.taples.import_table_data(
    table_id=table.table.id,
    file_id=upload_result.file.id,
    import_mode="append",  # append 或 overwrite
    sheet_index=0,  # 导入到第几个工作表
    has_header=True,  # 第一行是否为表头
    idempotency_key="import-csv-001"
)

if import_result.success:
    print(f"导入成功！")
    print(f"导入了 {import_result.rows_imported} 行数据")
    print(f"创建了 {import_result.columns_created} 列")
else:
    print(f"导入失败: {import_result.error_message}")
```

#### 数据导出

Taple 支持导出为多种格式：

```python
from file_hub_client.enums import ExportFormat

# 导出为 Excel
export_result = await client.taples.export_table_data(
    table_id=table.table.id,
    format=ExportFormat.XLSX,
    options={
        "include_formulas": True,
        "include_styles": True,
        "include_hidden_sheets": False,
        "include_hidden_rows_cols": False
    },
    idempotency_key="export-excel-001"
)

if export_result.success:
    print(f"导出成功！")
    print(f"文件ID: {export_result.file_id}")
    print(f"文件名: {export_result.file_name}")
    print(f"下载链接: {export_result.download_url}")
    
    # 下载导出的文件
    await client.blobs.download(
        file_id=export_result.file_id,
        save_path=f"exports/{export_result.file_name}"
    )

# 支持的导出格式
# - ExportFormat.XLSX: Excel 格式
# - ExportFormat.CSV: CSV 格式（多工作表会生成 ZIP）
# - ExportFormat.JSON: JSON 格式
# - ExportFormat.HTML: HTML 表格
# - ExportFormat.MARKDOWN: Markdown 表格
```

#### 表格克隆操作

Taple 支持将表格数据克隆到另一个组织，包括所有工作表、列、行和单元格数据：

```python
from file_hub_client import AsyncTamarFileHubClient
import uuid

async def clone_table_example():
    async with AsyncTamarFileHubClient() as client:
        client.set_user_context(org_id="source-org-123", user_id="456")
        
        # 克隆表格到另一个组织
        clone_result = await client.taples.clone_table_data(
            source_table_id="table-123",
            target_org_id="target-org-456",
            target_user_id="target-user-789",
            target_folder_id="target-folder-001",  # 可选，目标文件夹
            new_table_name="克隆的员工表_2024",      # 可选，新表格名称
            include_views=False,                   # 是否包含视图数据
            idempotency_key=str(uuid.uuid4())      # 幂等性键
        )
        
        if clone_result.success:
            print(f"克隆成功！")
            print(f"新表格ID: {clone_result.new_table_id}")
            print(f"新文件ID: {clone_result.new_file_id}")
            print(f"克隆了 {clone_result.sheets_cloned} 个工作表")
            print(f"克隆了 {clone_result.cells_cloned} 个单元格")
            print(f"创建时间: {clone_result.created_at}")
        else:
            print(f"克隆失败: {clone_result.error_message}")

# 运行示例
import asyncio
asyncio.run(clone_table_example())
```

**同步客户端示例**：

```python
from file_hub_client import TamarFileHubClient
import uuid

with TamarFileHubClient() as client:
    client.set_user_context(org_id="source-org-123", user_id="456")
    
    # 克隆表格（最简示例）
    clone_result = client.taples.clone_table_data(
        source_table_id="table-123",
        target_org_id="target-org-456",
        target_user_id="target-user-789"
        # 其他参数都是可选的
    )
    
    print(f"克隆结果: {clone_result.success}")
    if clone_result.success:
        print(f"新表格ID: {clone_result.new_table_id}")
```

**克隆操作特点**：

- **跨组织克隆**：可以将表格从一个组织克隆到另一个组织
- **完整数据复制**：包括表格结构、工作表、列定义、行数据和单元格内容
- **可选视图数据**：通过 `include_views` 参数控制是否包含视图数据（默认不包含）
- **灵活命名**：可自定义新表格名称，不指定则自动使用原名称+Copy后缀
- **目标位置控制**：可指定目标文件夹，不指定则使用目标用户的默认文件夹
- **幂等性支持**：支持幂等性键，避免重复克隆

#### 完整示例：创建和填充数据表

```python
from file_hub_client import AsyncTamarFileHubClient
from datetime import datetime
import uuid

async def create_employee_table():
    async with AsyncTamarFileHubClient() as client:
        client.set_user_context(org_id="123", user_id="456")
        
        # 1. 创建表格
        table = await client.taples.create_table(
            name=f"员工信息_{datetime.now().strftime('%Y%m%d')}",
            description="员工基本信息管理表",
            idempotency_key=str(uuid.uuid4())
        )
        
        # 2. 创建工作表
        sheet = await client.taples.create_sheet(
            table_id=table.table.id,
            name="花名册",
            description="员工花名册"
        )
        
        # 3. 批量创建列
        column_operations = [
            {"create": {"name": "工号", "column_type": "text", "position": 0}},
            {"create": {"name": "姓名", "column_type": "text", "position": 1}},
            {"create": {"name": "部门", "column_type": "text", "position": 2}},
            {"create": {"name": "入职日期", "column_type": "date", "position": 3}},
            {"create": {"name": "薪资", "column_type": "number", "position": 4}}
        ]
        
        columns_result = await client.taples.batch_edit_columns(
            sheet_id=sheet.sheet.id,
            operations=column_operations
        )
        
        # 4. 批量创建行并填充数据
        employees = [
            {"工号": "E001", "姓名": "张三", "部门": "技术部", "入职日期": "2023-01-15", "薪资": "15000"},
            {"工号": "E002", "姓名": "李四", "部门": "销售部", "入职日期": "2023-03-20", "薪资": "12000"},
            {"工号": "E003", "姓名": "王五", "部门": "市场部", "入职日期": "2023-06-10", "薪资": "13000"}
        ]
        
        # 创建行
        row_operations = [{"create": {"position": i}} for i in range(len(employees))]
        rows_result = await client.taples.batch_edit_rows(
            sheet_id=sheet.sheet.id,
            operations=row_operations
        )
        
        # 填充数据
        cell_operations = []
        for i, (row, employee) in enumerate(zip(rows_result['results'], employees)):
            if row['success'] and row['row']:
                row_key = row['row'].row_key
                for j, (col, (field, value)) in enumerate(zip(columns_result['results'], employee.items())):
                    if col['success'] and col['column']:
                        cell_operations.append({
                            "edit": {
                                "column_key": col['column'].column_key,
                                "row_key": row_key,
                                "raw_value": value
                            }
                        })
        
        # 批量更新单元格
        await client.taples.batch_edit_cells(
            sheet_id=sheet.sheet.id,
            operations=cell_operations
        )
        
        print(f"表格创建成功！")
        print(f"表格ID: {table.table.id}")
        print(f"工作表ID: {sheet.sheet.id}")
        
        # 5. 读取数据验证
        sheet_data = await client.taples.get_sheet_data(sheet_id=sheet.sheet.id)
        print(f"数据行数: {len(sheet_data.rows)}")
        print(f"数据列数: {len(sheet_data.columns)}")

# 运行示例
import asyncio
asyncio.run(create_employee_table())
```

#### 高级功能：合并单元格

```python
# 合并单元格
merge_result = await client.taples.merge_cells(
    sheet_id=sheet.sheet.id,
    start_row_key="row_1",
    end_row_key="row_3",
    start_column_key="col_1",
    end_column_key="col_2",
    idempotency_key="merge-cells-001"
)

# 取消合并
unmerge_result = await client.taples.unmerge_cells(
    sheet_id=sheet.sheet.id,
    merged_cell_id=merge_result.merged_cell.id,
    idempotency_key="unmerge-cells-001"
)

# 获取合并单元格信息
merged_cells = await client.taples.list_merged_cells(sheet_id=sheet.sheet.id)
for cell in merged_cells.merged_cells:
    print(f"合并区域: {cell.start_row_key}-{cell.end_row_key}, {cell.start_column_key}-{cell.end_column_key}")
```

#### 高级功能：表格视图

```python
# 创建视图
view = await client.taples.create_table_view(
    table_id=table.table.id,
    name="销售部视图",
    description="只显示销售部数据",
    filter_config={
        "conditions": [
            {
                "column_key": "col_dept",
                "operator": "equals",
                "value": "销售部"
            }
        ]
    },
    sort_config={
        "rules": [
            {
                "column_key": "col_salary",
                "order": "desc"
            }
        ]
    },
    visible_columns=["col_name", "col_dept", "col_salary"],
    idempotency_key="create-view-001"
)

# 获取视图列表
views = await client.taples.list_table_views(table_id=table.table.id)
for v in views.views:
    print(f"视图: {v.name} - {v.description}")

# 使用视图获取数据
view_data = await client.taples.get_table_view_data(
    view_id=view.view.id,
    page_size=20,
    page=1
)
```

#### 同步客户端示例

所有异步操作都有对应的同步版本：

```python
from file_hub_client import TamarFileHubClient

with TamarFileHubClient() as client:
    client.set_user_context(org_id="123", user_id="456")
    
    # 创建表格
    table = client.taples.create_table(
        name="销售数据",
        description="2024年销售数据"
    )
    
    # 创建工作表
    sheet = client.taples.create_sheet(
        table_id=table.table.id,
        name="Q1数据"
    )
    
    # 创建列
    column = client.taples.create_column(
        sheet_id=sheet.sheet.id,
        name="产品名称",
        column_type="text"
    )
    
    print(f"创建成功: {table.table.id}")
```

### 最简单的使用方式（推荐）

File Hub Client 提供了预配置的单例客户端，可以直接导入使用：

```python
# 同步客户端
import os
from file_hub_client import tamar_client as client

# 直接使用，无需 with 语句
client.set_user_context(org_id="123", user_id="456")
file_path = os.path.abspath("1.jpg")
file_info = client.blobs.upload(file_path)
```

```python
# 异步客户端
import asyncio
import os
from file_hub_client import async_tamar_client as async_client


async def main():
    # 直接使用，无需 with 语句
    await async_client._ensure_connected()  # 需要手动连接
    async_client.set_user_context(org_id="123", user_id="456")
    file_path = os.path.abspath("1.jpg")
    file_info = await async_client.blobs.upload(file_path)
    print(f"上传成功: {file_info.file.id}")


asyncio.run(main())
```

### 自定义配置的单例

如果需要自定义配置，可以使用 `get_client()` 或 `get_async_client()`：

```python
from file_hub_client import get_client

# 获取自定义配置的客户端（单例）
client = get_client(
    host="custom-server.com",
    port=50051,
    secure=True
)
```

### 使用上下文管理器（可选）

如果您希望明确控制连接的生命周期，仍然可以使用上下文管理器：

```python
import os
from file_hub_client import TamarFileHubClient

# 使用 with 语句
with TamarFileHubClient(host="localhost", port=50051) as client:
    file_path = os.path.abspath("1.jpg")
    file_info = client.blobs.upload(file_path)
```

### 异步客户端示例

```python
import asyncio
import os
from file_hub_client import AsyncTamarFileHubClient


async def main():
    # 创建客户端
    async with AsyncTamarFileHubClient(host="localhost", port=50051) as client:
        # 上传文件
        file_path = os.path.abspath("1.jpg")
        file_info = await client.blobs.upload(file_path)
        print(f"上传成功: {file_info.file.id}")


asyncio.run(main())
```

### 同步客户端示例

```python
import os
from file_hub_client import TamarFileHubClient

# 创建客户端
with TamarFileHubClient(host="localhost", port=50051) as client:
    # 上传文件
    file_path = os.path.abspath("1.jpg")
    file_info = client.blobs.upload(file_path)
    print(f"上传成功: {file_info.file.id}")
```

### 使用用户上下文

File Hub Client 支持精细的用户上下文管理，区分资源所有权和实际操作者：

```python
import os
from file_hub_client import AsyncTamarFileHubClient, UserContext, RequestContext, Role

# 创建用户上下文
user_context = UserContext(
    org_id="org-123",  # 组织ID
    user_id="user-456",  # 用户ID（资源所有者）
    role=Role.ACCOUNT,  # 角色：ACCOUNT, AGENT, SYSTEM
    actor_id="agent-789"  # 实际操作者ID（可选，默认为user_id）
)

# 创建请求上下文（自动收集客户端信息）
request_context = RequestContext(
    client_ip="192.168.1.100",  # 客户端IP（可选）
    client_type="web",  # 客户端类型：web, mobile, desktop, cli
    client_version="2.0.0",  # 客户端版本
    extra={"session_id": "xyz"}  # 额外的元数据
)

# 使用上下文创建客户端
async with AsyncTamarFileHubClient(
        user_context=user_context,
        request_context=request_context
) as client:
    # 所有操作都会包含上下文信息
    file_path = os.path.abspath("1.jpg")
    await client.blobs.upload(file_path)
```

### 动态切换用户上下文

```python
from file_hub_client import tamar_client as client, Role

# 初始用户
client.set_user_context(
    org_id="123",
    user_id="456",
    role=Role.ACCOUNT
)
```

### 请求追踪

客户端会自动生成请求ID并收集环境信息：

```python
from file_hub_client import tamar_client as client

# 获取当前上下文信息
user_ctx = client.get_user_context()
request_ctx = client.get_request_context()

print(f"请求ID: {request_ctx.request_id}")
print(f"客户端信息: {request_ctx.client_type} v{request_ctx.client_version}")
print(f"操作者: {user_ctx.actor_id} (角色: {user_ctx.role})")
```

### 显式请求ID控制

所有服务方法都支持显式传入 `request_id` 参数，用于更精确的请求追踪和调试：

```python
from file_hub_client import AsyncTamarFileHubClient
import uuid

# 创建客户端
client = AsyncTamarFileHubClient(user_context=user_context)

# 方式1：不传入request_id，系统自动生成
table = await client.taples.create_table(name="auto_request_id_table")

# 方式2：传入自定义request_id
custom_request_id = f"create-table-{uuid.uuid4().hex}"
table = await client.taples.create_table(
    name="custom_request_id_table",
    request_id=custom_request_id
)

# 方式3：使用业务相关的request_id
business_request_id = "user-action-2025-0714-001"
folder = await client.folders.create_folder(
    folder_name="important_folder",
    request_id=business_request_id
)

# 同步客户端同样支持
sync_client = TamarFileHubClient(user_context=user_context)
response = sync_client.files.get_file(
    file_id="file-123",
    request_id="debug-get-file-001"
)
# response.file 包含文件基本信息
# response.upload_file 包含上传文件详细信息（可能为None）
```

#### 请求ID优先级

请求ID的使用优先级如下：

1. **显式传入的 request_id 参数**（最高优先级）
2. **RequestContext 中的 request_id**
3. **自动生成的 UUID**（默认行为）

```python
# 优先级示例
request_context = RequestContext(
    extra={"request_id": "context-request-id-123"}
)

client = AsyncTamarFileHubClient(
    user_context=user_context,
    request_context=request_context
)

# 使用显式传入的request_id（优先级最高）
await client.taples.create_table(
    name="explicit_priority", 
    request_id="explicit-request-id-456"
)
# 实际使用：explicit-request-id-456

# 使用RequestContext中的request_id
await client.taples.create_table(name="context_priority")
# 实际使用：context-request-id-123

# 如果都没有，自动生成UUID
minimal_client = AsyncTamarFileHubClient(user_context=user_context)
await minimal_client.taples.create_table(name="auto_generated")
# 实际使用：自动生成的UUID
```

#### 支持request_id的服务方法

所有服务方法都支持 `request_id` 参数：

**Taple 服务**：
- `create_table()`, `get_table()`, `delete_table()`
- `create_sheet()`, `get_sheet()`, `delete_sheet()`
- `create_column()`, `update_column()`, `delete_column()`
- `create_row()`, `update_row()`, `delete_row()`
- `edit_cell()`, `clear_cell()`, `get_cell_data()`
- `import_table_data()`, `export_table_data()`
- `clone_table_data()`
- 所有批量操作方法

**文件服务**：
- `get_file()` - 返回 `GetFileResponse` 对象，包含 `file` 和 `upload_file` 信息
- `rename_file()`, `delete_file()`, `list_files()`
- `generate_share_link()`, `visit_file()`

**文件夹服务**：
- `create_folder()`, `rename_folder()`, `move_folder()`, `delete_folder()`
- `list_folders()`

**Blob 服务**：
- `upload()`, `download()`, `generate_upload_url()`, `generate_download_url()`

#### 请求追踪最佳实践

1. **业务操作使用有意义的request_id**：
   ```python
   # 用户触发的操作
   request_id = f"user-{user_id}-create-table-{int(time.time())}"
   
   # 定时任务
   request_id = f"cron-export-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
   
   # 批量操作
   request_id = f"batch-import-{batch_id}"
   ```

2. **调试时使用描述性request_id**：
   ```python
   # 调试特定功能
   request_id = "debug-column-creation-issue"
   
   # 性能测试
   request_id = f"perf-test-{operation_name}-{iteration}"
   ```

3. **生产环境保持简洁**：
   ```python
   # 生产环境可以使用简短的标识符
   request_id = f"prod-{uuid.uuid4().hex[:8]}"
   ```

## 高级功能

### 幂等性支持

许多操作支持幂等性，通过 `idempotency_key` 参数防止重复操作：

```python
from file_hub_client import AsyncTamarFileHubClient, generate_idempotency_key

async with AsyncTamarFileHubClient() as client:
    # 自动生成幂等性键
    key = generate_idempotency_key("create", "table", "employee_2024")
    
    # 使用幂等性键创建表格
    # 即使多次调用，也只会创建一次
    table = await client.taples.create_table(
        name="员工表_2024",
        idempotency_key=key
    )
    
    # 使用 IdempotencyManager 管理多个操作
    from file_hub_client import IdempotencyManager
    
    manager = IdempotencyManager(prefix="import_batch_001")
    
    # 批量导入，每个操作都有唯一的幂等性键
    for i, file_id in enumerate(file_ids):
        await client.taples.import_table_data(
            table_id=table.table.id,
            file_id=file_id,
            idempotency_key=manager.generate_key("import", str(i))
        )
```

### 错误重试机制

SDK 内置了智能的错误重试机制：

```python
from file_hub_client import AsyncTamarFileHubClient

# 配置重试策略
client = AsyncTamarFileHubClient(
    retry_count=5,     # 最大重试次数
    retry_delay=1.0    # 初始重试延迟（秒）
)

# 使用装饰器自定义重试逻辑
from file_hub_client.utils.retry import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=0.5)
async def upload_with_retry(client, file_path):
    return await client.blobs.upload(file_path)
```

### 批量操作优化

对于大量数据操作，使用批量接口可以显著提高性能：

```python
# 批量操作示例
async def batch_import_data(client, sheet_id, data_rows):
    # 分批处理，每批100行
    batch_size = 100
    
    for i in range(0, len(data_rows), batch_size):
        batch = data_rows[i:i + batch_size]
        
        # 创建批量操作
        operations = []
        for row_data in batch:
            operations.append({
                "create": {"position": i}
            })
        
        # 执行批量创建
        result = await client.taples.batch_edit_rows(
            sheet_id=sheet_id,
            operations=operations
        )
        
        if not result.get('success'):
            print(f"批次 {i//batch_size + 1} 失败: {result.get('error_message')}")
            continue
            
        # 批量填充单元格数据
        cell_operations = []
        # ... 构建单元格操作
        
        await client.taples.batch_edit_cells(
            sheet_id=sheet_id,
            operations=cell_operations
        )
```

### 并发控制

使用异步客户端时，可以充分利用并发提高效率：

```python
import asyncio
from file_hub_client import AsyncTamarFileHubClient

async def concurrent_uploads(file_paths):
    async with AsyncTamarFileHubClient() as client:
        client.set_user_context(org_id="123", user_id="456")
        
        # 并发上传多个文件
        tasks = []
        for file_path in file_paths:
            task = client.blobs.upload(file_path)
            tasks.append(task)
        
        # 等待所有上传完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"文件 {file_paths[i]} 上传失败: {result}")
            else:
                print(f"文件 {file_paths[i]} 上传成功: {result.file.id}")

# 使用信号量限制并发数
async def controlled_concurrent_operations(items, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_item(item):
        async with semaphore:
            # 处理单个项目
            return await some_operation(item)
    
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)
```

### 流式处理大数据

对于大量数据的处理，使用流式API避免内存溢出：

```python
# 流式读取大型表格数据
async def stream_table_data(client, sheet_id):
    page = 1
    page_size = 1000
    
    while True:
        # 分页获取数据
        result = await client.taples.get_sheet_data(
            sheet_id=sheet_id,
            page=page,
            page_size=page_size
        )
        
        if not result.rows:
            break
            
        # 处理当前页数据
        for row in result.rows:
            yield row
            
        page += 1

# 使用示例
async def process_large_table():
    async with AsyncTamarFileHubClient() as client:
        async for row in stream_table_data(client, "sheet-123"):
            # 处理每一行数据
            process_row(row)
```

## 开发

### 生成 gRPC 代码

当 proto 文件更新后，需要重新生成代码：

```bash
# 使用命令行工具
file-hub-gen-proto

# 或直接运行脚本
cd file_hub_client/rpc
python generate_grpc.py
```

### 运行测试

```bash
# 运行所有测试
python tests/taple/run_all_tests.py

# 运行特定测试
python tests/taple/test_table_operations.py

# 设置测试环境变量
export TEST_SERVER_HOST=your-test-server.com
export TEST_SERVER_PORT=50051
export TEST_ORG_ID=test-org-123
export TEST_USER_ID=test-user-456
```

## 故障排除

### 常见问题

1. **连接超时**
   ```python
   # 增加超时时间
   client = AsyncTamarFileHubClient(
       retry_count=5,
       retry_delay=2.0
   )
   ```

2. **版本冲突**
   ```python
   # 自动重试版本冲突
   while True:
       try:
           result = await client.taples.create_column(...)
           break
       except VersionConflictError:
           # 重新获取版本并重试
           continue
   ```

3. **大文件上传失败**
   ```python
   # 使用断点续传模式
   file_info = await client.blobs.upload(
       "large_file.zip",
       mode=UploadMode.RESUMABLE
   )
   ```

### 调试技巧

1. **启用详细日志**
   ```python
   client = AsyncTamarFileHubClient(
       enable_logging=True,
       log_level="DEBUG"
   )
   ```

2. **使用请求ID追踪**
   ```python
   # 为每个操作设置唯一的请求ID
   request_id = f"debug-{operation}-{timestamp}"
   result = await client.taples.create_table(
       name="test",
       request_id=request_id
   )
   ```

3. **检查网络连接**
   ```python
   # 测试连接
   try:
       await client.connect()
       print("连接成功")
   except ConnectionError as e:
       print(f"连接失败: {e}")
   ```

## 最佳实践

1. **使用单例客户端**：避免频繁创建客户端实例
2. **设置合理的超时和重试**：根据网络环境调整
3. **使用幂等性键**：防止重复操作
4. **批量操作**：提高性能
5. **错误处理**：妥善处理各种异常
6. **资源清理**：使用 with 语句确保资源释放
7. **并发控制**：合理使用并发避免服务器过载

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.0.6 (2025-08)
- 新增媒体文件压缩服务功能
- 支持获取文件压缩状态 (get_compression_status)
- 支持获取压缩变体列表 (get_compressed_variants)
- 支持触发文件重新压缩 (trigger_recompression)
- 支持生成变体下载URL (generate_variant_download_url)
- 添加压缩相关数据模型 (CompressedVariant 等)
- 在所有文件服务类中实现压缩功能支持
- 更新文档包含压缩服务使用示例

### v0.0.5 (2025-01)
- 新增批量下载URL生成接口 (batch_generate_download_url)
- 新增GCS URL获取接口 (get_gcs_url, batch_get_gcs_url)
- **重要更新**: 批量下载URL接口 (BatchGenerateDownloadUrl) 现在返回MIME类型信息
- **重要更新**: DownloadUrlInfo 结构新增 mime_type 字段，便于文件类型识别
- GCS URL接口返回MIME类型信息，便于文件类型识别
- 新增 keep_original_filename 参数支持保留原始文件名
- 更新相关文档和测试用例

### v0.0.4 (2025-01)
- 新增从URL上传文件功能
- 支持自动下载URL内容并上传到GCS
- 支持自定义文件名
- 修复URL上传时的MIME类型检测问题
- 改进测试中对哈希去重的说明

### v0.0.3 (2025-07)
- 端口参数变为可选，支持直接使用域名连接
- 优化环境变量端口配置处理
- 改进连接地址构建逻辑

### v1.5.0 (2025-01)
- 添加 gRPC 请求自动日志记录
- 支持 JSON 格式日志输出
- 日志消息中文化并添加图标
- 优化 CSV 文件 MIME 类型检测
- 修复拦截器类型错误问题

### v1.4.0 (2024-12)
- 添加 Taple 表格导入导出功能
- 支持表格克隆操作
- 优化批量操作性能
- 增强幂等性支持

### v1.3.0 (2024-11)
- 添加完整的 Taple 电子表格支持
- 实现乐观锁版本控制
- 支持合并单元格和视图管理

### v1.2.0 (2024-10)
- 重构服务架构，实现分层设计
- 添加请求ID追踪功能
- 增强用户上下文管理

### v1.1.0 (2024-09)
- 添加 TLS/SSL 支持
- 实现自动重试机制
- 优化大文件上传下载

### v1.0.0 (2024-08)
- 初始版本发布
- 基础文件和文件夹操作
- 异步和同步双客户端支持