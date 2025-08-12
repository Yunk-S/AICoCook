# AI-Cook & AI-Meal-Coach: Full-Stack Dual-Backend Intelligent Cooking Application

[English](README.md) | [中文](README_zh.md)

---

This is a comprehensive full-stack web application that provides a powerful recipe search engine and intelligent AI meal assistant through a unified user interface. This project aims to become an AI cooking assistant application that integrates modern recipe exploration and personalized meal planning.

## ✨ Core Features

-   **Unified User Interface**: All features, including recipe search and the new AI meal assistant, are integrated into a single, responsive Vue.js frontend.
-   **Dual Backend Architecture**: The application runs two independent backend services to handle specialized tasks:
    -   **AI Backend (FastAPI)**: A high-performance service for personalized meal planning and conversational AI, listening on `http://localhost:8000`.
    -   **Search Backend (Flask)**: A hybrid search engine with integrated semantic understanding capabilities, listening on `http://localhost:5001`.
-   **Modern Project Management**:
    -   **Single Dependency Source**: Python dependencies for the entire project are unifiedly managed by the `pyproject.toml` file in the root directory, following modern Python standards (PEP 621), completely solving dependency conflict issues.
    -   **One-Click Startup Scripts**: `firststart.bat` and `aicook.bat` scripts simplify environment setup and daily development workflows.

## 📱 Application Page Overview

The application contains 8 main pages, each designed for specific recipe discovery and management functions:

### 🏠 Homepage (`/`)
The main landing page of the application, showcasing feature highlights and introduction. Key features:
- **Hero Section**: Eye-catching gradient titles and animated background introduction
- **Feature Cards**: Interactive glass-morphism cards highlighting core functions
- **Recipe Carousel**: Horizontal scrolling showcase of popular recipes
- **Usage Guide**: Step-by-step guidance on how to use the application
- **Responsive Design**: Adapts to all device sizes with smooth animations

### 🤖 AI Nutritionist (`/ai-coach`)
Intelligent nutrition coach providing personalized dietary advice through conversational AI. Key features:
- **Chat Interface**: Real-time streaming conversations with AI nutritionist
- **Health Analysis**: BMI calculation and personalized recommendations
- **Chat History**: Persistent conversation session management and search
- **Multi-Model Support**: Supports 5 mainstream AI service providers (Google Gemini, OpenAI, DouBao, ZhiPu, DeepSeek)
- **Intelligent RAG Vector Generation**: 🧠 Supports multiple embedding models for recipe knowledge vector generation
- **Dynamic Service Provider Switching**: Flexible switching between AI service providers as needed
- **Vector Data Management**: Visualized vector database status and management interface
- **Service Status Monitoring**: Real-time backend service health monitoring

### 💡 AI Recommendations (`/ai-recommend`)
Personalized recipe recommendations based on user health data and dietary preferences. Key features:
- **Health Profile**: Complete body metrics form (height, weight, age, activity level)
- **BMI & Calorie Calculator**: Automatic health metrics calculation and dietary advice
- **Dietary Preferences**: Ingredient preferences, restrictions, and dietary limitations
- **Smart Recommendations**: Recipe recommendations based on health profile
- **Filtering System**: Advanced filtering for vegetarian, vegan, low-sugar, etc.
- **Real-time Updates**: Dynamic recommendation updates when preferences change

### 🎲 Random Recipes (`/random-recipe`)
Generate random meal combinations for cooking exploration and meal planning. Key features:
- **Random Meal Generator**: Creates balanced multi-recipe meal combinations
- **Meal History**: Save and browse previously generated meal combinations
- **Quick Actions**: One-click meal generation and save to history
- **Carousel View**: Interactive history browsing and recipe preview
- **Nutrition Summary**: Comprehensive nutritional information for meal combinations
- **Export Options**: Save favorite meal combinations for future reference

### 🔍 Limited Conditions (`/limited-conditions`)
Find recipes based on available ingredients and kitchen equipment. Key features:
- **Ingredient Selection**: Browse and select categorized ingredient database
- **Equipment Matching**: Select available kitchen tools and cookware
- **Smart Search**: Fuzzy, strict, or survival mode matching algorithms
- **Real-time Filtering**: Instant recipe updates as selections change
- **Match Analysis**: Detailed matching scores and missing ingredient analysis
- **Category Filtering**: Organize ingredients by type (vegetables, meat, seafood)
- **Progress Indicators**: Visual feedback for recipe compatibility

### 🍽️ Food Gallery (`/food-gallery`)
Comprehensive recipe browser with advanced search capabilities. Key features:
- **AI Smart Search**: Natural language recipe discovery and semantic understanding
- **Search Analysis**: Detailed breakdown of search intent and extracted features
- **Recipe Grid**: Responsive waterfall layout and infinite scrolling
- **Filtering System**: Advanced filtering by cuisine, difficulty, cooking time
- **Particle Animations**: Dynamic particle effects enhancing visual appeal
- **Search Suggestions**: AI-generated query recommendations
- **Batch Operations**: Multi-select recipe batch management

### ⭐ My Recipes (`/my-recipes`)
Personal recipe collection management, including favorites and browsing history. Key features:
- **Favorites Management**: Curated preferred recipe collections
- **Browsing History**: Chronological record of recipe interactions
- **Tab Interface**: Easy switching between favorites and history
- **Batch Operations**: Clear history and efficient collection management
- **Search Integration**: Quick access to add more recipes from gallery
- **Statistics Dashboard**: Usage analytics and preference insights
- **Data Export**: Backup and share personal recipe collections

### 📖 Recipe Details (`/recipe/:id`)
Comprehensive recipe information with interactive features. Key features:
- **Complete Recipe Information**: Ingredients, preparation steps, nutritional content
- **Visual Media**: High-quality images and optional video links
- **Interactive Elements**: Favorite toggle, portion adjustment
- **Nutrition Breakdown**: Detailed macro and micronutrient information
- **Related Recipes**: AI-curated recommendations based on current recipe
- **Kitchen Tools**: Required equipment and cookware list
- **Responsive Layout**: Cross-device optimized reading experience
- **Social Features**: Share recipes and track cooking progress

## 🧠 Multi-Model RAG Vector Generation Features

### 🎯 Core Features

Our AI backend now supports vector embedding generation from **3 mainstream AI service providers**, providing powerful semantic search capabilities for your recipe knowledge base:

| AI Service Provider | Chat Function | Vector Generation | Embedding Model | Features | Recommended Scenarios |
|---|---|---|---|---|---|
| **🌟 Google Gemini** | ✅ | ✅ | models/embedding-001 | High quality, excellent stability | Primary recommendation |
| **🔥 OpenAI** | ✅ | ✅ | text-embedding-3-small | Good compatibility, excellent results | Preferred for international users |
| **🎓 ZhiPu** | ✅ | ✅ | embedding-2 | Strong Chinese understanding, academic background | Optimized for Chinese content |
| **🇨🇳 DouBao** | ✅ | ❌ | Not supported | Fast domestic access, low cost | Recommended for domestic users |
| **💰 DeepSeek** | ✅ | ❌ | Not supported | Extremely low cost, strong reasoning | Large-scale processing |

> **⚠️ Note**: DeepSeek R1 focuses on reasoning capabilities and does not support vector generation.

### 🔧 Intelligent Configuration System

#### Environment Variable Configuration
```bash
# Select default embedding service provider
EMBEDDING_PROVIDER=google  # google, openai, doubao, zhipu, deepseek

# API keys for each service provider
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key  
DOUBAO_API_KEY=your_doubao_api_key
ZHIPU_API_KEY=your_zhipu_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Or use universal default key
DEFAULT_AI_API_KEY=your_default_key
```

#### Intelligent Fallback Mechanism
- 🔄 **Automatic Service Provider Failover**: Automatically uses Google as fallback when primary provider fails
- 🔐 **Key Validation**: Automatically detects API key validity and provides configuration suggestions
- 📊 **Performance Monitoring**: Real-time monitoring of response times and success rates for each service provider

### 🎛️ Frontend Configuration Interface

In the AI Nutritionist page, click the settings button to:

1. **Select AI Service Provider**: Freely choose from 5 service providers
2. **Enter API Key**: Secure sessionStorage storage
3. **View Vector Status**: Real-time display of vector database status
4. **One-Click Vector Generation**: Support Google/OpenAI one-click generation of 17,000+ recipe vectors
5. **Switch Service Providers**: Switch between different embedding models anytime

### 🚀 Usage Methods

#### Method 1: Frontend Interface Operation
1. Open AI Nutritionist page → Settings
2. Select service provider supporting vector generation (Google/OpenAI/DouBao/ZhiPu)
3. Enter corresponding API key
4. Click "Generate Vector Data" button

#### Method 2: API Interface Operation
```bash
# View supported service providers
GET /api/v1/rag/providers

# Rebuild vectors using specified service provider
POST /api/v1/rag/rebuild-embeddings?provider=doubao&batch_size=100
```

#### Method 3: Command Line Operation
```bash
# Rebuild vectors using ZhiPu (requires API key configuration)
python aire-backend/scripts/import_data.py rebuild --embedding-provider zhipu
```

---

## 🚀 Getting Started

### Prerequisites

-   **Python 3.9+**: Recommended to use Python 3.9 or higher.
-   **Node.js & npm**: Required for frontend build and run (recommended v18+).

### Running the Application

#### First Run: Patience is Key

⚠️ **Important Note**: **The first run process takes a long time to prepare, expected to take 5-15 minutes**, depending on your network conditions and computer performance. Please ensure stable network connection and be patient. This is **only needed once**, subsequent startups will be very fast.

The first run takes time mainly in this stages:
1.  **Dependency Package Download**: `firststart.bat` will automatically download all required Python and Node.js dependency packages, with potentially large total volume.


**Operation Steps:**

1.  **Ensure Clean Environment** (optional but recommended): If you've run old versions before, please manually delete the `.venv` folder in the project root directory.
2.  **Start Installation and Launch**:
    -   Find and double-click `firststart.bat` in the project root directory.
    -   The script will automatically complete all preparation work: create virtual environment, install dependencies, initialize database, and finally launch three service windows in parallel.
3.  **Wait for Completion**:
    -   Please patiently wait for all tasks in command line windows to complete, especially the model download in the **AI-Cook Search API** window.
    -   Upon success, the script will automatically open `http://localhost:3001` in your default browser.

#### Daily Startup: One-Click Instant Launch

-   After you've successfully run `firststart.bat` once, for daily development you only need to double-click and run `aicook.bat` in the root directory.
-   This script will skip all time-consuming installation steps, directly activate the virtual environment and launch all services, completing in a few seconds.

## 🏗️ Design Philosophy and Technical Principles

### 1. High-Level Architecture: Unified Dependencies, Dual Backend Separation

This project adopts a **dual backend** architecture, aiming to achieve separation of concerns and technology stack optimization, while ensuring consistency and stability of the entire project environment through a **single `pyproject.toml`** file.

-   **AI Backend (FastAPI)**: Responsible for handling computation-intensive and I/O-intensive AI-related tasks, such as interactions with Large Language Models (LLM), complex queries of user personalized data, etc. FastAPI's asynchronous features make it an ideal choice for handling concurrent AI requests.
-   **Search Backend (Flask)**: Specifically designed for high-performance local recipe search. Flask's lightweight nature enables fast startup and focuses on text indexing and retrieval.
-   **Unified Dependency Management**: The `pyproject.toml` in the root directory is the project's **only** dependency source, integrating all requirements from both backends and following PEP 621 standards. This fundamentally solves dependency conflict issues, making the environment creation and maintenance process highly reliable.

### 2. Intelligent Search Backend (Flask) and Hybrid Search Principles

The search function design adopts the **Hybrid Search** concept, combining the precision of traditional keyword search with the intelligence of modern semantic search to provide search results far exceeding single methods.

#### a. Retrieval Stage: Multi-Channel Recall

This is the first step of search, aiming to quickly and accurately recall the most relevant candidate set from massive recipe data. We adopt a **Multi-Channel Recall** strategy:

1.  **Keyword Matching (BM25)**: A classic probabilistic retrieval model that considers term frequency and inverse document frequency, giving high scores to recipes containing search keywords.
2.  **Fuzzy Matching (FuzzyWuzzy)**: Uses the `fuzzywuzzy` library to handle user spelling errors or synonym queries, improving fault tolerance.
3.  **Multi-Model Semantic Vector Retrieval (Multi-Model Embeddings)**:
    -   **🧠 Core Technology Upgrade**: The system now supports embedding models from 5 AI service providers, no longer limited to a single model. Can choose embedding services from Google Gemini, OpenAI, DouBao, ZhiPu, or DeepSeek as needed.
    -   **🔧 Flexible Index Construction**: All recipes (recipe names, tags, ingredients, preparation steps) are converted to high-dimensional **vectors (Embeddings)** by the selected AI model. Each vector is a precise mathematical representation of recipe content in mathematical space.
    -   **🎯 Intelligent Similarity Calculation**: Queries are converted to vectors through the same embedding model, using **FAISS vector database** for efficient similarity search. Supports dynamic switching of embedding models for optimal search results.
    -   **🔄 Fallback Mechanism**: If the primary service provider is unavailable, the system intelligently switches to fallback providers, ensuring continuous availability of search functionality.

#### b. Ranking and Fusion

Multi-channel recall produces several different candidate result sets. The system uses a weighted fusion algorithm, comprehensively considering multiple dimensions such as keyword matching scores, semantic similarity scores, etc., to calculate a final comprehensive score for each candidate recipe, then ranks them to present the most relevant results to users.

This hybrid search design effectively combines the efficiency and precision of traditional search engines with the powerful semantic understanding capabilities of AI language models.

### 3. Project Structure (After Modernization)

```
/
├── .venv/                  # ➤ Global Python virtual environment
├── firststart.bat          # ➤ Script for first-time installation and launching all services
├── aicook.bat              # ➤ Script for daily quick launch of all services
├── pyproject.toml          # ➤ [Core] Project's only Python dependency and configuration source
│
├── aire-backend/           # │
│   └── app/                # │─ AI backend core application (FastAPI)
│
├── src/                    # 
│   ├── components/         # │─ Vue reusable components
│   ├── views/              # │─ Vue page-level components
│   └── backend/            # │
│       └── recipe_search_engine.py # │─ Search backend core application (Flask)
│
├── recipes.json            # │─ Core recipe data file
├── package.json            # │─ Frontend project metadata and dependencies
└── README_zh.md            # └─ This Chinese documentation file
```

## Acknowledgments

The initial inspiration, design philosophy, and partial recipe data for this project come from Bilibili UP creator **YunYouJun**'s open-source project [**Let's Cook!**](https://cook.yunyoujun.cn).

Building on this foundation, this project has undergone comprehensive technology stack upgrades, architectural refactoring, and feature expansion, including but not limited to:
-   Introduced AI API self-service filling, unified dependencies, updated recipes and images.
-   Integrated intelligent search engine based on **hybrid search** philosophy, combining keyword and semantic vector retrieval.
-   Refactored and simplified local development and deployment workflows.

Sincere thanks to YunYouJun for the open-source sharing!

## Contact Us:
[yunkun.syk@gmail.com](mailto:yunkun.syk@gmail.com)、[1411434312@qq.com](mailto:1411434312@qq.com)
