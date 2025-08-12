"""
数据库模型

定义所有的 SQLAlchemy 模型类。
"""

# 导入所有模型以确保它们被注册到 Base.metadata
from .user import User
from .diet_profile import DietProfile, UserDietProfile
from .recipe import Recipe, RecipeIngredient, RecipeCategory, UserRecipe
from .meal_plan import MealPlan, MealPlanRecipe

__all__ = [
    "User",
    "DietProfile",
    "UserDietProfile", 
    "Recipe",
    "RecipeIngredient",
    "RecipeCategory",
    "UserRecipe",
    "MealPlan",
    "MealPlanRecipe",
]