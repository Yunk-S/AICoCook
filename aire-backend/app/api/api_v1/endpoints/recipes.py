"""
食谱管理 API 端点

提供食谱的CRUD操作、搜索、推荐等功能。
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_superuser
from app.models.user import User
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse, 
    RecipeSearch, RecipeSearchResult, RecipeFilter
)
from app.services.recipe_service import RecipeService

router = APIRouter()


@router.get("/", response_model=RecipeSearchResult, summary="获取食谱列表")
async def get_recipes(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(600, ge=1, le=1000, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    cuisine: Optional[str] = Query(None, description="菜系"),
    difficulty: Optional[str] = Query(None, description="难度等级"),
    max_time: Optional[int] = Query(None, ge=0, description="最大制作时间(分钟)"),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取食谱列表
    
    支持搜索和筛选功能。
    """
    recipe_service = RecipeService(db)
    
    # 构建搜索条件
    search_params = RecipeSearch(
        query=search,
        cuisine=cuisine,
        difficulty=difficulty,
        max_total_time=max_time,
        page=skip // limit + 1,
        size=limit
    )
    
    result = recipe_service.search_recipes(search_params)
    return result


@router.post("/", response_model=RecipeResponse, summary="创建食谱")
async def create_recipe(
    recipe_create: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    创建新食谱
    
    需要登录用户权限。
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.create_recipe(recipe_create)
    return recipe


@router.get("/search", response_model=RecipeSearchResult, summary="搜索食谱")
async def search_recipes(
    search_params: RecipeSearch = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    搜索食谱
    
    支持复杂的搜索条件和筛选。
    """
    recipe_service = RecipeService(db)
    result = recipe_service.search_recipes(search_params)
    return result


@router.get("/recommend", response_model=List[RecipeResponse], summary="推荐食谱")
async def recommend_recipes(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    ingredients: Optional[str] = Query(None, description="现有食材，用逗号分隔"),
    exclude_ingredients: Optional[str] = Query(None, description="排除食材，用逗号分隔"),
    cuisine: Optional[str] = Query(None, description="偏好菜系"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    智能推荐食谱
    
    基于用户偏好、现有食材等条件推荐合适的食谱。
    """
    recipe_service = RecipeService(db)
    
    # 解析食材列表
    ingredients_list = ingredients.split(',') if ingredients else []
    exclude_list = exclude_ingredients.split(',') if exclude_ingredients else []
    
    # 构建推荐参数
    filter_params = RecipeFilter(
        available_ingredients=ingredients_list,
        dietary_restrictions=exclude_list,
        cuisine=[cuisine] if cuisine else None
    )
    
    recipes = recipe_service.recommend_recipes(
        filter_params=filter_params,
        user=current_user,
        limit=limit
    )
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse, summary="获取食谱详情")
async def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    获取指定食谱的详细信息
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.get_recipe(recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食谱不存在"
        )
    
    # 更新查看次数
    recipe_service.increment_view_count(recipe_id)
    
    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse, summary="更新食谱")
async def update_recipe(
    recipe_id: int,
    recipe_update: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    更新食谱信息
    
    只有创建者或超级用户可以更新。
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.get_recipe(recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食谱不存在"
        )
    
    # 检查权限（在实际实现中，需要检查食谱的创建者）
    # 这里暂时只允许超级用户更新
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限更新此食谱"
        )
    
    updated_recipe = recipe_service.update_recipe(recipe_id, recipe_update)
    return updated_recipe


@router.delete("/{recipe_id}", summary="删除食谱")
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    删除食谱
    
    需要超级用户权限。
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.get_recipe(recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食谱不存在"
        )
    
    recipe_service.delete_recipe(recipe_id)
    return {"message": "食谱已删除"}


@router.post("/{recipe_id}/rate", summary="评价食谱")
async def rate_recipe(
    recipe_id: int,
    rating: float = Query(..., ge=1, le=5, description="评分 (1-5)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    为食谱评分
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.get_recipe(recipe_id)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食谱不存在"
        )
    
    # 添加评分逻辑（在实际实现中需要创建评分表）
    recipe_service.rate_recipe(recipe_id, current_user.id, rating)
    
    return {"message": "评分已提交", "rating": rating}


@router.get("/cuisines/list", response_model=List[str], summary="获取菜系列表")
async def get_cuisines(
    db: Session = Depends(get_db)
) -> Any:
    """
    获取所有可用的菜系列表
    """
    recipe_service = RecipeService(db)
    cuisines = recipe_service.get_available_cuisines()
    return cuisines


@router.get("/tags/list", response_model=List[str], summary="获取标签列表")
async def get_tags(
    db: Session = Depends(get_db)
) -> Any:
    """
    获取所有可用的标签列表
    """
    recipe_service = RecipeService(db)
    tags = recipe_service.get_available_tags()
    return tags


@router.post("/import", summary="批量导入食谱")
async def import_recipes(
    file_path: str = Query(..., description="CSV文件路径"),
    overwrite: bool = Query(False, description="是否覆盖现有食谱"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    从CSV文件批量导入食谱
    
    需要超级用户权限。
    """
    recipe_service = RecipeService(db)
    
    try:
        result = recipe_service.import_recipes_from_csv(file_path, overwrite)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"导入失败: {str(e)}"
        )