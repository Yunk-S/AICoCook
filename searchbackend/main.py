"""
FastAPI Backend for AI Cook Search Engine

This module provides the main API endpoints for the search service.
"""
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import uvicorn
import os

from .simple_search import (
    load_recipes_from_file,
    SimpleSearchEngine
)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Cook Search Engine",
    description="A high-performance search engine for recipes, supporting keyword, ingredient, and cookware search.",
    version="1.0.0"
)

# --- CORS Configuration ---
# Allows the frontend (e.g., running on localhost:3001) to communicate with this backend.
origins = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # 允许所有源支持直连
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Data Loading ---
# Determine the correct path to the project root to find data files.
# This assumes the backend is run from the project root directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RECIPES_PATH = os.path.join(PROJECT_ROOT, 'src', 'data', 'recipes.json')
USER_DICT_PATH = os.path.join(PROJECT_ROOT, 'user_dict.txt')

try:
    logger.info(f"Project root identified as: {PROJECT_ROOT}")
    logger.info(f"Attempting to load recipes from: {RECIPES_PATH}")
    recipes_data = load_recipes_from_file()
    logger.info(f"Successfully loaded {len(recipes_data)} recipes.")
    
    logger.info("Initializing Simple Search Engine...")
    search_indexer = SimpleSearchEngine()
    search_indexer.load_recipes(recipes_data)
    logger.info("Simple Search Engine initialized successfully.")
    
except FileNotFoundError as e:
    logger.error(f"FATAL: A required data file was not found. {e}")
    recipes_data = []
    search_indexer = SimpleSearchEngine()
except Exception as e:
    logger.error(f"An unexpected error occurred during data loading or indexing: {e}")
    recipes_data = []
    search_indexer = SimpleSearchEngine()


# --- Pydantic Models for API ---
class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query string.", min_length=1)
    limit: int = Field(1000, gt=0, le=10000, description="The maximum number of results to return.")

class Recipe(BaseModel):
    # This model reflects the actual structure of recipe objects in recipes.json
    id: str
    name: str
    stuff: List[str]
    tools: List[str]
    tags: List[str]
    difficulty: str
    methods: Optional[str] = ""  # 允许None值，默认为空字符串
    videoUrl: Optional[str] = None
    steps: List[dict]
    image: Optional[str] = None
    popularity: Optional[int] = None
    match_score: Optional[float] = 0.0

class SearchResponse(BaseModel):
    results: List[Recipe]
    total: int
    query: str


# --- API Endpoints ---
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Checks if the search engine service is running.
    """
    logger.info("Health check endpoint was called.")
    return {"status": "healthy", "recipe_count": len(recipes_data)}

@app.post("/search", tags=["Search"])
def perform_search(request: SearchRequest = Body(...)):
    """
    Performs a search for recipes based on a query.

    This endpoint takes a search query and returns a list of matching recipes,
    ranked by relevance.
    """
    logger.info(f"Received search request for query: '{request.query}' with limit: {request.limit}")
    if not search_indexer:
        logger.error("Search attempted but the search indexer is not available.")
        raise HTTPException(status_code=500, detail="Search index not loaded. Cannot perform search.")

    try:
        matched_recipes = search_indexer.search(
            query=request.query,
            limit=request.limit
        )
        logger.info(f"Found {len(matched_recipes)} results for query: '{request.query}'")
        
        response = {
            "results": matched_recipes,
            "total": len(matched_recipes),
            "query": request.query
        }
        return response
    except Exception as e:
        logger.exception(f"An error occurred during search for query '{request.query}': {e}")
        # 返回详细错误信息用于调试
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full error traceback: {error_details}")
        
        return {
            "results": [],
            "total": 0,
            "query": request.query,
            "error": str(e),
            "traceback": error_details
        }

# --- Main execution ---
def start():
    """
    Starts the Uvicorn server for the FastAPI application.
    This function is intended to be called when running the module directly.
    """
    logger.info("Starting Search Engine Backend Server...")
    uvicorn.run("searchbackend.main:app", host="0.0.0.0", port=8080, reload=True, workers=1)

if __name__ == "__main__":
    start()
