# Media Agent MCP

一个基于 Model Context Protocol (MCP) 的媒体处理服务器，提供强大的AI驱动的媒体处理工具。

## 🚀 功能特性

### 核心工具 (9个)

1. **TOS存储** - 将内容保存为URL
2. **视频拼接** - 拼接多个视频文件
3. **视频帧提取** - 提取视频的最后一帧
4. **Seedream图像生成** - 使用AI模型生成图像
5. **Seedance视频生成** - 使用AI模型生成视频（支持lite和pro版本）
6. **Seededit角色维持** - 保持主要角色的一致性
7. **Seed1.6视觉语言模型** - 执行视觉任务工作流
8. **图像选择器** - 从多个图像中选择最佳的一个
9. **视频选择器** - 从多个视频中选择最佳的一个

### AI模型支持

- **Seedream**: 高质量图像生成
- **Seedance**: 视频生成（支持文本生成视频、首帧生成视频、首尾帧生成视频）
- **Seededit**: 图像编辑和角色一致性维护
- **Seed1.6**: 多模态视觉语言理解

## 📋 系统要求

- Python >= 3.12
- 支持的操作系统：macOS, Linux, Windows

## 🛠️ 安装

### 方法一：使用 UVX（推荐）

```bash
uvx media-agent-mcp
```

### 方法二：本地开发安装

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd media-agent-mcp
```

#### 2. 安装依赖

使用 uv（推荐）：

```bash
uv sync
```

或使用 pip：

```bash
pip install -e .
```

#### 3. 配置环境变量

复制环境变量模板并填写配置：

```bash
cp .env.template .env
```

编辑 `.env` 文件，填写以下必要配置：

```env
# TOS存储配置
TOS_ACCESS_KEY=your_tos_access_key_here
TOS_SECRET_KEY=your_tos_secret_key_here
TOS_BUCKET_NAME=your_bucket_name_here
TOS_ENDPOINT=tos-ap-southeast-1.bytepluses.com
TOS_REGION=ap-southeast-1

# 火山引擎视觉智能SDK配置
VOLC_ACCESS_KEY=your_volcengine_access_key_here
VOLC_SECRET_KEY=your_volcengine_secret_key_here

# BytePlus ModelArk API配置
ARK_API_KEY=your_ark_api_key_here
ARK_BASE_URL=https://ark.ap-southeast.bytepluses.com

# AI模型端点配置
SEEDANCE_EP=seedance-1-0-lite
SEEDREAM_EP=seedream-1-0
SEEDEDIT_EP=seededit-3-0
VLM_EP=seed-1-6-chat
```

## 🚀 使用方法

### 启动MCP服务器

#### 使用 UVX

```bash
uvx media-agent-mcp
```

#### 使用 UV（本地开发）

```bash
uv run media-agent-mcp
```

#### 使用stdio传输（默认）

```bash
media-agent-mcp
```

#### 使用SSE传输

```bash
media-agent-mcp --transport sse --host 127.0.0.1 --port 8000
```

#### 直接运行服务器文件

```bash
cd src
python -m media_agent_mcp.server
```

### 命令行选项

```bash
media-agent-mcp --help
```

可用选项：
- `--transport`: 传输方式 (sse 或 stdio，默认: stdio)
- `--host`: SSE传输的主机地址 (默认: 127.0.0.1)
- `--port`: SSE传输的端口 (默认: 8000)
- `--version`: 显示版本信息

### 与MCP客户端集成

#### Claude Desktop配置

在Claude Desktop的配置文件中添加：

```json
{
  "mcpServers": {
    "media-agent": {
      "command": "uvx",
      "args": ["media-agent-mcp"]
    }
  }
}
```

#### VS Code MCP扩展配置

```json
{
  "mcp.servers": {
    "media-agent": {
      "command": "uvx",
      "args": ["media-agent-mcp"]
    }
  }
}
```

## 🔧 API工具详细说明

### 1. 视频拼接工具

```python
video_concat_tool(video_urls: list[str]) -> str
```

拼接多个视频URL并上传到TOS。

**参数：**
- `video_urls`: 要按顺序拼接的视频URL列表

**返回：** JSON字符串，包含状态、数据和消息

**示例：**
```python
result = video_concat_tool([
    "https://example.com/video1.mp4",
    "https://example.com/video2.mp4"
])
```

### 2. 视频帧提取工具

```python
video_last_frame_tool(video_path: str) -> str
```

从视频文件中提取最后一帧并上传到TOS。

**参数：**
- `video_path`: 视频文件路径或URL

**返回：** JSON字符串，包含状态、数据和消息

### 3. Seedream图像生成工具

```python
seedream_generate_image_tool(
    prompt: str, 
    style: str = "realistic", 
    size: str = "1024x1024"
) -> str
```

使用Seedream AI模型生成图像。

**参数：**
- `prompt`: 图像描述文本
- `style`: 图像风格（realistic, artistic, cartoon等）
- `size`: 图像尺寸（如"1024x1024"）

**示例：**
```python
result = seedream_generate_image_tool(
    prompt="一只可爱的小猫坐在花园里",
    style="realistic",
    size="1024x1024"
)
```

### 4. Seedance视频生成工具

```python
seedance_generate_video_tool(
    prompt: str = "", 
    first_frame_image: str = None,
    last_frame_image: str = None, 
    duration: int = 5,
    resolution: str = "720p", 
    ratio: str = "16:9"
) -> str
```

使用Seedance AI模型生成视频。

**参数：**
- `prompt`: 视频描述文本（图像转视频时可选）
- `first_frame_image`: 首帧图像的URL或base64
- `last_frame_image`: 尾帧图像的URL或base64（可选）
- `duration`: 视频时长（5或10秒）
- `resolution`: 视频分辨率（480p, 720p, 1080p）
- `ratio`: 宽高比（16:9, 4:3, 1:1, 3:4, 9:16, adaptive等）

**示例：**
```python
# 文本生成视频
result = seedance_generate_video_tool(
    prompt="一只鸟在天空中飞翔",
    duration=5,
    resolution="720p"
)

# 首帧生成视频
result = seedance_generate_video_tool(
    first_frame_image="https://example.com/first_frame.jpg",
    duration=5
)
```

### 5. 其他工具

- **Seededit角色维持工具**: 保持图像中主要角色的一致性
- **Seed1.6 VLM工具**: 执行视觉语言任务
- **图像选择器**: 从多个图像中选择最佳的一个
- **视频选择器**: 从多个视频中选择最佳的一个
- **TOS保存工具**: 将内容保存到TOS并返回URL

## 📁 项目结构

```
media-agent-mcp/
├── src/
│   └── media_agent_mcp/
│       ├── __init__.py
│       ├── server.py              # MCP服务器主文件
│       ├── ai_models/             # AI模型模块
│       │   ├── __init__.py
│       │   ├── seedream.py        # 图像生成
│       │   ├── seedance.py        # 视频生成
│       │   ├── seededit.py        # 图像编辑
│       │   └── seed16.py          # 视觉语言模型
│       ├── video/                 # 视频处理模块
│       │   ├── __init__.py
│       │   └── processor.py       # 视频处理功能
│       ├── storage/               # 存储模块
│       │   ├── __init__.py
│       │   └── tos_client.py      # TOS客户端
│       └── media_selectors/       # 媒体选择器
│           ├── __init__.py
│           ├── image_selector.py  # 图像选择
│           └── video_selector.py  # 视频选择
├── .env.template                  # 环境变量模板
├── .gitignore                     # Git忽略文件
├── pyproject.toml                 # 项目配置
├── uv.lock                        # 依赖锁定文件
└── README.md                      # 项目文档
```

## 🔑 API密钥获取

### TOS存储
1. 访问 [BytePlus TOS控制台](https://console.byteplus.com/tos)
2. 创建存储桶并获取访问密钥
3. 记录访问密钥、秘密密钥和存储桶名称

### ModelArk API
1. 访问 [BytePlus ModelArk控制台](https://console.byteplus.com/)
2. 获取API密钥
3. 选择合适的模型端点

### 火山引擎视觉智能
1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通视觉智能服务
3. 获取访问密钥和秘密密钥

## 🐛 故障排除

### 常见问题

1. **相对导入错误**
   ```
   ImportError: attempted relative import with no known parent package
   ```
   **解决方案**: 使用模块方式运行：
   ```bash
   cd src
   python -m media_agent_mcp.server
   ```

2. **环境变量未设置**
   确保 `.env` 文件已正确配置所有必要的API密钥。
   
3. **依赖安装问题**
   ```bash
   pip install --upgrade pip
   pip install -e .
   ```
   
   或使用uv：
   ```bash
   uv sync --reinstall
   ```

4. **TOS上传失败**
   - 检查TOS配置是否正确
   - 确认存储桶权限设置
   - 验证网络连接

5. **AI模型调用失败**
   - 检查API密钥是否有效
   - 确认模型端点配置
   - 查看API配额和限制

## 📝 开发

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd media-agent-mcp

# 使用uv创建虚拟环境并安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 运行测试

```bash
# 运行测试套件
uv run test_server.py

# 运行特定测试
python -m pytest tests/
```

### 构建和发布

```bash
# 构建包
uv build

# 发布到PyPI
uv publish
```

### 添加新工具

1. 在相应模块中实现功能
2. 在 `server.py` 中添加 `@mcp.tool()` 装饰器
3. 添加类型注解和文档字符串
4. 更新README文档
5. 添加测试用例

### 代码规范

- 使用类型注解
- 遵循PEP 8代码风格
- 添加详细的文档字符串
- 包含错误处理
- 返回统一的JSON格式

## 📊 性能优化

- 使用异步处理提高并发性能
- 实现缓存机制减少重复计算
- 优化文件上传和下载流程
- 合理设置超时和重试机制

## 🔒 安全考虑

- 不要在代码中硬编码API密钥
- 使用环境变量管理敏感信息
- 验证输入参数防止注入攻击
- 限制文件上传大小和类型
- 定期更新依赖包

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献流程

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 添加测试
5. 提交Pull Request

## 📞 支持

如有问题，请：

1. 查看本文档的故障排除部分
2. 搜索已有的Issues
3. 提交新的Issue
4. 联系开发团队

## 📈 版本历史

- **v0.1.0** (Alpha) - 初始版本，包含9个核心工具
- **v2.2.0** add subtitle and description to tools
- **v2.3.0** add audio and video merge
- **v2.4.0** omni human, tts, stack video