"""
AI 服务相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """聊天消息模式"""
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str = Field(..., min_length=1, max_length=8000)
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    """聊天请求模式"""
    messages: List[ChatMessage] = Field(..., min_items=1)
    model: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    stream: bool = False
    context: Optional[Dict[str, Any]] = {}
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('At least one message is required')
        
        # 确保最后一条消息是用户消息
        if v[-1].role != 'user':
            raise ValueError('Last message must be from user')
        
        return v


class ChatResponse(BaseModel):
    """聊天响应模式"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddingRequest(BaseModel):
    """文本嵌入请求模式"""
    text: Union[str, List[str]] = Field(..., description="Text(s) to embed")
    model: Optional[str] = None
    encoding_format: str = Field("float", pattern="^(float|base64)$")
    
    @validator('text')
    def validate_text(cls, v):
        if isinstance(v, str):
            if len(v.strip()) == 0:
                raise ValueError('Text cannot be empty')
            if len(v) > 8000:
                raise ValueError('Text too long (max 8000 characters)')
        elif isinstance(v, list):
            if len(v) == 0:
                raise ValueError('Text list cannot be empty')
            if len(v) > 100:
                raise ValueError('Too many texts (max 100)')
            for text in v:
                if len(text.strip()) == 0:
                    raise ValueError('Text cannot be empty')
                if len(text) > 8000:
                    raise ValueError('Text too long (max 8000 characters)')
        return v


class EmbeddingData(BaseModel):
    """嵌入数据模式"""
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    """文本嵌入响应模式"""
    data: List[EmbeddingData]
    model: str
    usage: Optional[Dict[str, Any]] = {}


class RecipeGenerationRequest(BaseModel):
    """食谱生成请求模式"""
    ingredients: List[str] = Field(..., min_items=1, max_items=20)
    diet_profile: Optional[str] = None
    cuisine_type: Optional[str] = None
    cooking_time: Optional[int] = Field(None, ge=5, le=300)  # 分钟
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    servings: int = Field(4, ge=1, le=12)
    additional_requirements: Optional[str] = Field(None, max_length=500)
    
    @validator('ingredients')
    def validate_ingredients(cls, v):
        if not v:
            raise ValueError('At least one ingredient is required')
        
        # 清理和验证食材
        cleaned_ingredients = []
        for ingredient in v:
            ingredient = ingredient.strip()
            if len(ingredient) == 0:
                continue
            if len(ingredient) > 100:
                raise ValueError('Ingredient name too long (max 100 characters)')
            cleaned_ingredients.append(ingredient)
        
        if len(cleaned_ingredients) == 0:
            raise ValueError('At least one valid ingredient is required')
        
        return cleaned_ingredients


class GeneratedRecipe(BaseModel):
    """生成的食谱模式"""
    title: str
    description: str
    ingredients: List[Dict[str, Any]]  # {"name": str, "amount": str, "unit": str}
    directions: List[str]
    prep_time: Optional[int]  # 分钟
    cook_time: Optional[int]  # 分钟
    total_time: Optional[int]  # 分钟
    servings: int
    difficulty: Optional[str]
    nutrition: Optional[Dict[str, float]]  # {"calories": float, "protein": float, ...}
    tags: List[str] = []


class RecipeGenerationResponse(BaseModel):
    """食谱生成响应模式"""
    recipe: GeneratedRecipe
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    model: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MealPlanGenerationRequest(BaseModel):
    """膳食计划生成请求模式"""
    days: int = Field(..., ge=1, le=30)
    meals_per_day: int = Field(3, ge=1, le=6)
    diet_profile: Optional[str] = None
    target_calories: Optional[int] = Field(None, ge=1000, le=5000)
    include_snacks: bool = False
    cuisine_preferences: List[str] = []
    allergies: List[str] = []
    dislikes: List[str] = []
    cooking_time_limit: Optional[int] = Field(None, ge=10, le=180)  # 分钟
    budget_range: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    additional_requirements: Optional[str] = Field(None, max_length=500)


class MealPlanDay(BaseModel):
    """膳食计划一天的模式"""
    date: str  # YYYY-MM-DD 格式
    meals: List[Dict[str, Any]]  # {"type": str, "recipes": List[GeneratedRecipe]}
    total_nutrition: Dict[str, float]


class MealPlanGenerationResponse(BaseModel):
    """膳食计划生成响应模式"""
    plan: List[MealPlanDay]
    summary: Dict[str, Any]  # 计划总结
    recommendations: List[str]  # 建议
    model: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RecipeSearchRequest(BaseModel):
    """食谱搜索请求模式"""
    query: str = Field(..., min_length=1, max_length=200)
    diet_profile: Optional[str] = None
    ingredients: Optional[List[str]] = []
    excluded_ingredients: Optional[List[str]] = []
    cuisine_type: Optional[str] = None
    max_cooking_time: Optional[int] = Field(None, ge=5, le=300)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    limit: int = Field(10, ge=1, le=50)
    
    @validator('query')
    def validate_query(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError('Search query cannot be empty')
        return v


class SearchedRecipe(BaseModel):
    """搜索到的食谱模式"""
    id: int
    title: str
    description: Optional[str]
    image_url: Optional[str]
    rating: Optional[float]
    prep_time: Optional[int]
    cook_time: Optional[int]
    difficulty: Optional[str]
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class RecipeSearchResponse(BaseModel):
    """食谱搜索响应模式"""
    recipes: List[SearchedRecipe]
    total: int
    query: str
    filters_applied: Dict[str, Any]
    search_time_ms: float


class RecipeAdaptationRequest(BaseModel):
    """食谱适配请求模式"""
    recipe_id: int
    target_diet: str
    custom_requirements: Optional[str] = Field(None, max_length=500)
    servings: Optional[int] = Field(None, ge=1, le=12)


class RecipeAdaptationResponse(BaseModel):
    """食谱适配响应模式"""
    adapted_recipe: GeneratedRecipe
    changes_made: List[str]  # 修改说明
    explanation: str
    original_recipe_id: int
    model: str
    adapted_at: datetime = Field(default_factory=datetime.utcnow)


class DietCompatibilityRequest(BaseModel):
    """饮食兼容性检查请求模式"""
    recipe_id: int
    diet_profile: str


class DietCompatibilityResponse(BaseModel):
    """饮食兼容性检查响应模式"""
    compatible: bool
    compatibility_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[str] = []  # 不兼容的问题
    suggestions: List[str] = []  # 改进建议
    explanation: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)