# Dify SDK

一个用于与 Dify AI 平台交互的 Python SDK，提供应用管理、对话管理、数据集管理等功能。

## 功能特点

- 完整支持 Dify API，包括应用管理、对话、数据集等功能
- 支持异步操作，提高性能和响应速度
- 内置类型提示支持，基于 Pydantic 的数据模型
- 详细的文档和丰富的示例代码
- 完整的测试覆盖
- 健壮的错误处理和日志记录
- 支持事件处理，包括聊天消息、Agent消息等多种事件类型
- 支持停止消息生成功能，可以中断正在进行的AI响应

## 安装

使用pip安装：

```bash
pip install dify_sdk
```

## 使用方法

### 基本用法

```python
import asyncio
from dify import AdminClient, Dify

async def main():
    # 初始化客户端
    admin_client = AdminClient("https://api.dify.ai/v1", "your-api-key")
    dify = Dify(admin_client)

    # 获取应用列表
    apps = await dify.app.find_list()
    print(f"应用总数: {apps.total}")

    # 创建新应用
    new_app = await dify.app.create(
        name="我的聊天应用",
        mode="chat",
        description="这是一个简单的聊天应用"
    )
    print(f"创建应用成功: {new_app.name} (ID: {new_app.id})")

if __name__ == "__main__":
    asyncio.run(main())
```

### 应用管理

```python
import asyncio
from dify import AdminClient, Dify

async def app_management_example():
    admin_client = AdminClient("https://api.dify.ai/v1", "your-api-key")
    dify = Dify(admin_client)

    # 创建应用
    app = await dify.app.create(
        name="我的AI助手",
        mode="chat",  # 或 "completion"
        description="这是一个AI助手应用"
    )

    # 获取应用详情
    app_detail = await dify.app.find_by_id(app.id)
    print(f"应用名称: {app_detail.name}")

    # 更新应用模型配置
    await dify.app.update_model_config(
        app_id=app.id,
        model_config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    )

    # 删除应用
    await dify.app.delete(app.id)

# 运行示例
asyncio.run(app_management_example())
```

### 对话管理

```python
import asyncio
from dify import AdminClient, Dify, ApiClient

async def conversation_example():
    # 管理端API
    admin_client = AdminClient("https://api.dify.ai/v1", "your-api-key")
    dify = Dify(admin_client)

    # 获取对话列表
    conversations = await dify.app.conversation.find_list(
        app_id="your-app-id",
        user_id="user-123",
        page=1,
        limit=10
    )

    # 获取对话消息
    if conversations.data:
        messages = await dify.app.conversation.get_messages(
            app_id="your-app-id",
            conversation_id=conversations.data[0].id,
            user_id="user-123"
        )
        print(f"消息数量: {len(messages.data)}")

    # 应用端API (聊天)
    api_client = ApiClient("https://api.dify.ai/v1", "your-api-key")

    # 发送聊天消息
    response = await api_client.chat(
        inputs={},
        query="你好，请介绍一下自己",
        user="user-123",
        stream=True
    )

    async for chunk in response:
        if chunk.event == "message":
            print(f"收到消息: {chunk.answer}")

# 运行示例
asyncio.run(conversation_example())
```

### 事件处理

```python
from dify.app.schemas import ConversationEventType, parse_event

# 解析事件
json_data = {
    "event": "message",
    "message_id": "msg_123",
    "conversation_id": "conv_456",
    "answer": "这是一个消息回复",
    "created_at": 1646035200
}

# 自动解析为对应的事件类型
event = parse_event(json_data)

# 根据事件类型处理
if event.event == ConversationEventType.MESSAGE:
    print(f"收到消息: {event.answer}")
elif event.event == ConversationEventType.ERROR:
    print(f"发生错误: {event.message}")
```

更详细的示例请参考 `examples/stop_message_example.py`。

## 开发

### 环境设置

1. 克隆仓库
2. 创建并激活虚拟环境
3. 安装开发依赖

```bash
git clone https://github.com/cruldra/dify_sdk.git
cd dify_sdk
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 发布到PyPI

本项目使用Hatch作为构建和发布工具。以下是发布到PyPI的步骤：

#### 1. 安装Hatch

```bash
pip install hatch
# 或使用uv
uv pip install hatch
```

#### 2. 配置PyPI凭证

有两种方式配置PyPI凭证：

**方式一：使用API令牌（推荐）**

1. 在[PyPI官网](https://pypi.org/manage/account/)注册并登录账号
2. 在账号设置中创建API令牌
3. 创建`~/.pypirc`文件：

```
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**方式二：使用环境变量**

```bash
# Windows (PowerShell)
$env:HATCH_INDEX_USER="__token__"
$env:HATCH_INDEX_AUTH="pypi-AgEIcHlwaS5vcmcCJDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Linux/Mac
export HATCH_INDEX_USER=__token__
export HATCH_INDEX_AUTH=pypi-AgEIcHlwaS5vcmcCJDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 3. 构建分发包

```bash
hatch build
```

这将在`dist/`目录下创建源代码分发包（.tar.gz）和轮子分发包（.whl）。

#### 4. 发布到PyPI

```bash
hatch publish
```

如果您想先在测试环境（TestPyPI）上发布：

```bash
hatch publish -r test
```

#### 5. 验证发布

发布成功后，您可以通过pip安装您的包来验证：

```bash
pip install dify_sdk
```

## 许可证

MIT

## 项目结构

```
dify_sdk/
├── dify/                    # 主库目录
│   ├── __init__.py          # 导出公共API
│   ├── app/                 # 应用相关功能
│   │   ├── conversation/    # 对话管理
│   │   ├── workflow/        # 工作流管理
│   │   ├── schemas.py       # 数据模型定义
│   │   └── utils.py         # 工具函数
│   ├── dataset/             # 数据集管理
│   ├── file/                # 文件管理
│   ├── llm/                 # LLM模型管理
│   ├── tag/                 # 标签管理
│   ├── http.py              # HTTP客户端
│   ├── exceptions.py        # 异常定义
│   └── schemas.py           # 通用数据模型
├── tests/                   # 测试目录
│   ├── app/                 # 应用测试
│   ├── test_app.py          # 应用测试
│   ├── test_dataset_*.py    # 数据集测试
│   ├── test_file_*.py       # 文件测试
│   ├── test_llm.py          # LLM测试
│   └── test_tag_*.py        # 标签测试
└── examples/                # 示例目录
    ├── app/                 # 应用示例
    │   ├── chat.py          # 聊天示例
    │   ├── completion.py    # 补全示例
    │   ├── conversation/    # 对话示例
    │   └── workflow_*.py    # 工作流示例
    ├── dataset/             # 数据集示例
    ├── file/                # 文件示例
    ├── llm/                 # LLM示例
    ├── tag/                 # 标签示例
    ├── event_example.py     # 事件处理示例
    └── stop_message_example.py # 停止消息生成示例
```

## 功能模块

- **应用管理 (app)**: 创建、查询、更新和删除应用，管理应用配置
- **对话管理 (conversation)**: 管理对话历史、消息和反馈
- **数据集管理 (dataset)**: 创建和管理知识库数据集
- **文件管理 (file)**: 上传和管理文件资源
- **LLM管理 (llm)**: 查询和管理可用的LLM模型
- **标签管理 (tag)**: 创建、查询、更新和删除标签，绑定标签到应用

## 最近更新

### 0.1.9

- 完善了对Dify API的支持
- 优化了异步操作的性能
- 增强了错误处理和日志记录
- 添加了更多示例代码和测试用例