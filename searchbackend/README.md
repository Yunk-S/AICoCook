# AI Cook Search Backend

This directory contains the FastAPI-based backend search engine for the AI Cook project. It is designed to be a simple, efficient, and standalone service that provides search functionality for recipes.

## Features

-   **FastAPI**: Built on a modern, high-performance Python web framework.
-   **Weighted Search**: Implements a custom, hand-written search logic with weighted scoring for different fields (name, ingredients, tags, etc.).
-   **Chinese Language Support**: Uses the `jieba` library for accurate Chinese word segmentation, improving search relevance for Chinese queries.
-   **Simple API**: Provides two main endpoints:
    -   `/health`: For health checks.
    -   `/search`: To perform searches.
-   **CORS Enabled**: Pre-configured to accept direct requests from the frontend (`http://localhost:3001`).
-   **Direct Connection**: Frontend bypasses Vite proxy for faster, more reliable connections.

## Getting Started

### Prerequisites

-   Python 3.9+
-   pip for dependency management (Poetry optional).
-   The project's data files (`recipes.json`) must be present in the `src/data/` directory.

### Installation

1.  **Install Dependencies**:
    Dependencies are listed in the `pyproject.toml` file in the project root. Navigate to the project root directory and run:

    ```bash
    pip install fastapi uvicorn jieba
    ```

    Or if using Poetry:
    ```bash
    poetry install
    ```

    This will install all necessary packages, including `fastapi`, `uvicorn`, and `jieba`.

### Running the Server

1.  **Activate the Virtual Environment**:
    Activate the Poetry shell to use the project's virtual environment.

    ```bash
    poetry shell
    ```

2.  **Start the Server**:
    The server can be started using the script defined in `pyproject.toml` or by running `uvicorn` directly.

    Using the poetry script:
    ```bash
    poetry run start-backend
    ```

    Or by running uvicorn directly (make sure you are in the project root):
    ```bash
    uvicorn searchbackend.main:app --host 0.0.0.0 --port 8080 --reload
    ```

The server will be running at `http://0.0.0.0:8080`.

## API Endpoints

### Health Check

-   **URL**: `/health`
-   **Method**: `GET`
-   **Description**: Returns the operational status of the service.
-   **Success Response**:
    ```json
    {
      "status": "healthy",
      "recipe_count": 605
    }
    ```

### Recipe Search

-   **URL**: `/search`
-   **Method**: `POST`
-   **Description**: Searches for recipes based on a JSON payload.
-   **Request Body**:
    ```json
    {
      "query": "土豆 牛肉",
      "limit": 10
    }
    ```
-   **Success Response**:
    Returns a list of recipe objects that match the query, sorted by relevance score.
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
