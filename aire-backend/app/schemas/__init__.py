"""
Pydantic 数据模式

定义 API 请求和响应的数据结构。
"""

from .user import (
    UserCreate, UserUpdate, UserInDB, UserResponse,
    UserLogin, UserRegister, Token, TokenData
)
from .recipe import (
    RecipeCreate, RecipeUpdate, RecipeInDB, RecipeResponse,
    RecipeSearch, RecipeSearchResult, RecipeFilter
)
from .meal_plan import (
    MealPlanCreate, MealPlanUpdate, MealPlanInDB, MealPlanResponse,
    MealPlanRecipeCreate, MealPlanRecipeUpdate, MealPlanRecipeResponse,
    MealPlanDetail, MealPlanGenerateRequest
)
from .diet_profile import (
    DietProfileCreate, DietProfileUpdate, DietProfileInDB, DietProfileResponse,
    UserDietProfileCreate, UserDietProfileUpdate, UserDietProfileResponse
)
from .ai import (
    ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse,
    RecipeGenerationRequest, RecipeGenerationResponse,
    MealPlanGenerationRequest, MealPlanGenerationResponse
)

__all__ = [
    # User schemas
    "UserCreate", "UserUpdate", "UserInDB", "UserResponse",
    "UserLogin", "UserRegister", "Token", "TokenData",
    
    # Recipe schemas
    "RecipeCreate", "RecipeUpdate", "RecipeInDB", "RecipeResponse",
    "RecipeSearch", "RecipeSearchResult", "RecipeFilter",
    
    # Meal plan schemas
    "MealPlanCreate", "MealPlanUpdate", "MealPlanInDB", "MealPlanResponse",
    "MealPlanRecipeCreate", "MealPlanRecipeUpdate", "MealPlanRecipeResponse",
    "MealPlanDetail", "MealPlanGenerateRequest",
    
    # Diet profile schemas
    "DietProfileCreate", "DietProfileUpdate", "DietProfileInDB", "DietProfileResponse",
    "UserDietProfileCreate", "UserDietProfileUpdate", "UserDietProfileResponse",
    
    # AI schemas
    "ChatRequest", "ChatResponse", "EmbeddingRequest", "EmbeddingResponse",
    "RecipeGenerationRequest", "RecipeGenerationResponse",
    "MealPlanGenerationRequest", "MealPlanGenerationResponse",
]