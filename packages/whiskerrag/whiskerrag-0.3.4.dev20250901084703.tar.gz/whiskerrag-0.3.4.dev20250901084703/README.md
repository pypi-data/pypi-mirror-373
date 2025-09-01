# WhiskerRAG

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/pypi/pyversions/whiskerrag)](https://pypi.org/project/whiskerrag/)
[![PyPI version](https://badge.fury.io/py/whiskerrag.svg)](https://badge.fury.io/py/whiskerrag)
[![codecov](https://codecov.io/gh/petercat-ai/whiskerrag_toolkit/branch/main/graph/badge.svg)](https://codecov.io/gh/petercat-ai/whiskerrag_toolkit)

WhiskerRAG 是为 PeterCat 和 Whisker 项目开发的 RAG（Retrieval-Augmented Generation）工具包，提供完整的 RAG 相关类型定义和方法实现。

## 特性

- 针对通用 RAG 的领域建模类型, 包括任务（Task）、知识（Knowledge）、分段(Chunk)、租户(Tenant)、知识库空间(Space)。
- Whisker rag 插件接口描述。
- Github 仓库、S3 资源管理器。

## 安装

使用 pip 安装：

```bash
pip install whiskerrag
```

## 快速开始

whiskerrag 包含三个子模块，分别是 whiskerrag_utils、whiskerrag_client、whiskerrag_types。它们分别有不同的用途：

### whiskerrag_utils

包含了构建 RAG 系统的常用方法：

```python
from whiskerrag_utils import loader,embedding,retriever
```

### whiskerrag_client

将 RAG 系统服务通过 python sdk 的形式向外暴露。

```python
from whiskerrag_client import APIClient

api_client = APIClient(
    base_url="https://api.example.com",
    token="your_token_here"
)

knowledge_chunks = await api_client.retrieval.retrieve_knowledge_content(
    RetrievalByKnowledgeRequest(knowledge_id="your knowledge uuid here")
)

space_chunks = await api_client.retrieval.retrieve_space_content(
    RetrievalBySpaceRequest(space_id="your space id here ")
)

chunk_list = await api_client.chunk.get_chunk_list(
    page=1,
    size=10,
    filters={"status": "active"}
)

task_list = await api_client.task.get_task_list(
    page=1,
    size=10
)

task_detail = await api_client.task.get_task_detail("task_id_here")
```

### whiskerrag_types

一些辅助开发的类型提示，接口；

```python
from whiskerrag_types.interface import DBPluginInterface, TaskEngineInterface
from whiskerrag_types.model import Knowledge, Task, Tenant, PageParams, PageResponse
```

## 开发者指南

### 环境初始化

1. 克隆项目

```bash
git clone https://github.com/petercat-ai/whiskerrag_toolkit.git
cd whiskerrag_toolkit
```

2. 创建并激活虚拟环境

```bash
# 查看poetry配置
poetry config --list

# 修改 poetry 配置
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true

poetry env use python3.10

# 激活虚拟环境
source .venv/bin/activate
```

3. 安装依赖

```bash
# 安装项目依赖
poetry install
# 安装 pre-commit 工具
pre-commit install
```

4. 运行测试

```bash
# 运行所有测试
poetry run pytest
# 运行指定测试文件
poetry run pytest tests/test_loader.py
```

4. poetry 常用命令

```bash
# 安装依赖
poetry install

# 添加新依赖
poetry add package_name

# 添加新 dev 依赖
poetry add --dev package_name

# 更新依赖
poetry update

# 查看环境信息
poetry env info

# 查看已安装的包
poetry show
```

### 开发工作流

1. 创建新分支
2. 开发新功能，补充单元测试，确保代码质量。注意，请确保单元测试覆盖率不低于 80%。
3. 提交代码，并创建 Pull Request。
4. 等待代码审查，并根据反馈进行修改。
5. 合并 Pull Request。

## 项目结构

```
whiskerRAG-toolkit/
├── src/
│   ├── whiskerrag_utils/
│   └── whiskerrag_types/
│   └── whiskerrag_client/
└── pyproject.toml
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`make branch name=feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

项目维护者 - [@petercat-ai](https://github.com/petercat-ai)

项目链接：[https://github.com/petercat-ai/whiskerrag_toolkit](https://github.com/your-username/whiskerrag_toolkit)
