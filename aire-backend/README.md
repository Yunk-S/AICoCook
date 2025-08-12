# AI-Cook: FastAPI Backend

[English](README.md) | [中文](README_zh.md)

---

This is the high-performance AI backend for the AI-Cook project, built with FastAPI. It handles all core business logic, including AI-powered conversations, recipe data management, user interactions, and advanced RAG (Retrieval-Augmented Generation) capabilities.

## 🏆 Core Features

-   **Multi-Provider AI Support**: Unified interface for 6+ major AI providers (Google Gemini, OpenAI, ZhiPu, etc.).
-   **Advanced RAG Pipeline**: Integrates multi-model vector embeddings (Google, OpenAI, ZhiPu) with a FAISS vector database for intelligent, context-aware responses.
-   **Dynamic Configuration**: Easily switch between AI providers and configure API keys via API headers or environment variables.
-   **High-Performance Asynchronous API**: Built on FastAPI and Starlette for high-throughput, non-blocking I/O, perfect for streaming AI responses.
-   **Automated Data Management**: Automatic import of recipe data and on-demand generation of vector embeddings.
-   **Secure by Design**: Stateless API key handling and robust data validation with Pydantic.

## 🛠️ Technology Stack

-   **Framework**: FastAPI, Pydantic, SQLAlchemy
-   **AI & RAG**: Google Generative AI, OpenAI SDK, FAISS
-   **Database**: SQLite (default), PostgreSQL (production-ready)
-   **Deployment**: Uvicorn, Gunicorn, Docker

## 📁 Directory Structure

The backend follows a clean, layered architecture for maintainability and scalability.

```
aire-backend/
└── app/
    ├── api/                # API Routing Layer (Endpoints)
    ├── core/               # Core Components (Config, Security, AI Services)
    ├── models/             # SQLAlchemy Database Models
    ├── schemas/            # Pydantic Data Validation Models
    ├── services/           # Business Logic Service Layer (RAG, User)
    └── main.py             # Main application entry point
```

## 🚀 Quick Start & RAG Configuration

The AI backend is started automatically using the `aicook.bat` or `firststart.bat` scripts in the project root. It runs on `http://localhost:8000`.

### How to Enable RAG

1.  **Navigate to the AI Coach Page**: Open the application and go to the "AI Coach" section.
2.  **Open Settings**: Click the settings (⚙️) icon.
3.  **Select a Provider**: Choose a provider that supports vector generation (**Google**, **OpenAI**, or **ZhiPu**).
4.  **Enter API Key**: Provide a valid API key for the selected service.
5.  **Generate Vectors**: Click the "Generate Vector Data" button. The system will then process and index all recipe data, which may take a few minutes.

Once completed, the RAG functionality will be fully enabled, providing significantly enhanced search and conversational capabilities.
