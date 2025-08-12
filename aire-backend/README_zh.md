# AI-Cook: FastAPI 后端

[English](README.md) | [中文](README_zh.md)

---

这是 AI-Cook 项目的高性能 AI 后端，使用 FastAPI 构建。它负责处理所有核心业务逻辑，包括 AI 对话、菜谱数据管理、用户交互以及先进的 RAG（检索增强生成）功能。

## 🏆 核心功能

-   **多AI服务商支持**: 为超过6个主流AI服务商（Google Gemini、OpenAI、智谱等）提供了统一的接口。
-   **先进的RAG流程**: 集成了多模型向量嵌入（Google、OpenAI、智谱）和 FAISS 向量数据库，以实现智能的、具备上下文感知能力的应答。
-   **动态配置**: 通过 API 请求头或环境变量，轻松切换AI服务商和配置API密钥。
-   **高性能异步API**: 基于 FastAPI 和 Starlette 构建，适用于高吞吐量、非阻塞I/O，完美支持流式AI响应。
-   **自动化数据管理**: 自动导入菜谱数据，并按需生成向量嵌入。
-   **安全设计**: 无状态的 API 密钥处理和基于 Pydantic 的稳健数据验证。

## 🛠️ 技术栈

-   **核心框架**: FastAPI, Pydantic, SQLAlchemy
-   **AI & RAG**: Google Generative AI, OpenAI SDK, FAISS
-   **数据库**: SQLite (默认), PostgreSQL (生产环境适用)
-   **部署**: Uvicorn, Gunicorn, Docker

## 📁 目录结构

后端遵循清晰、分层的架构，以实现可维护性和可扩展性。

```
aire-backend/
└── app/
    ├── api/                # API 路由层 (接口)
    ├── core/               # 核心组件 (配置, 安全, AI服务)
    ├── models/             # SQLAlchemy 数据库模型
    ├── schemas/            # Pydantic 数据校验模型
    ├── services/           # 业务逻辑服务层 (RAG, 用户)
    └── main.py             # 应用主入口
```

## 🚀 快速启动与RAG配置

AI 后端通过项目根目录下的 `aicook.bat` 或 `firststart.bat` 脚本自动启动。它运行在 `http://localhost:8000`。

### 如何启用 RAG 功能

1.  **访问AI营养师页面**: 打开应用并进入“AI营养师”部分。
2.  **打开设置**: 点击设置 (⚙️) 图标。
3.  **选择服务商**: 选择一个支持向量生成的技术提供方（**Google**、**OpenAI** 或 **智谱**）。
4.  **输入API密钥**: 为所选服务提供一个有效的API密钥。
5.  **生成向量**: 点击“生成向量数据”按钮。系统将处理并索引所有菜谱数据，这可能需要几分钟时间。

完成后，RAG功能将完全启用，提供显著增强的搜索和对话能力。
