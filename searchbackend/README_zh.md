# AI Cook 搜索引擎后端

此目录包含为 AI Cook 项目构建的基于 FastAPI 的后端搜索引擎。它被设计成一个简单、高效、独立的服务，为菜谱提供搜索功能。

## 功能特性

-   **FastAPI**: 构建于一个现代、高性能的 Python Web 框架之上。
-   **加权搜索**: 实现了一套自定义的手写搜索逻辑，针对不同字段（名称、食材、标签等）进行加权评分。
-   **中文支持**: 使用 `jieba` 库进行精确的中文分词，提升了中文查询的搜索相关性。
-   **简洁的 API**: 提供两个主要端点：
    -   `/health`: 用于健康检查。
    -   `/search`: 用于执行搜索。
-   **CORS 已启用**: 已预先配置，以接受来自前端的直连请求 (`http://localhost:3001`)。
-   **直连模式**: 前端绕过 Vite 代理，实现更快、更可靠的连接。

## 快速上手

### 环境要求

-   Python 3.9+
-   pip 用于依赖管理（Poetry 可选）。
-   项目的数据文件 (`recipes.json`) 必须位于 `src/data/` 目录下。

### 安装

1.  **安装依赖**:
    依赖项列在项目根目录的 `pyproject.toml` 文件中。请导航到项目根目录并运行：

    ```bash
    pip install fastapi uvicorn jieba
    ```

    或者使用 Poetry：
    ```bash
    poetry install
    ```

    该命令将安装所有必要的包，包括 `fastapi`, `uvicorn`, 和 `jieba`。

### 运行服务

1.  **激活虚拟环境**:
    激活 Poetry shell 以使用项目的虚拟环境。

    ```bash
    poetry shell
    ```

2.  **启动服务**:
    可以使用在 `pyproject.toml` 中定义的脚本启动服务，或直接运行 `uvicorn`。

    使用 Poetry 脚本：
    ```bash
    poetry run start-backend
    ```

    或者直接运行 uvicorn（请确保您位于项目根目录）：
    ```bash
    uvicorn searchbackend.main:app --host 0.0.0.0 --port 8080 --reload
    ```

服务将运行在 `http://0.0.0.0:8080`。

## API 端点

### 健康检查

-   **URL**: `/health`
-   **Method**: `GET`
-   **描述**: 返回服务的运行状态。
-   **成功响应**:
    ```json
    {
      "status": "healthy",
      "recipe_count": 605
    }
    ```

### 菜谱搜索

-   **URL**: `/search`
-   **Method**: `POST`
-   **描述**: 基于 JSON 载荷搜索菜谱。
-   **请求体**:
    ```json
    {
      "query": "土豆 牛肉",
      "limit": 10
    }
    ```
-   **成功响应**:
    返回一个匹配查询的菜谱对象列表，按相关性分数排序。
    ```json
    {
      "results": [
        {
          "id": "recipe-123",
          "name": "土豆烧牛肉",
          "stuff": ["土豆", "牛肉", ...],
          "match_score": 25.0,
          ...
        }
      ],
      "total": 1,
      "query": "土豆 牛肉"
    }
    ```
