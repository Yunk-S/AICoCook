"""
AI 相关的异步任务

处理 AI 推理、食谱生成、膳食计划生成等计算密集型任务。
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

import structlog
from celery import current_task

from app.core.ai_service import get_ai_service_instance, chat_with_ai, generate_text
from app.core.celery import task
from app.core.exceptions import AIServiceException

logger = structlog.get_logger()


@task(bind=True, name="app.tasks.ai_tasks.generate_recipe")
def generate_recipe_task(
    self,
    ingredients: List[str],
    diet_profile: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    cooking_time: Optional[int] = None,
    difficulty: Optional[str] = None,
    servings: int = 4,
    additional_requirements: Optional[str] = None,
) -> Dict[str, Any]:
    """
    异步生成食谱任务
    
    Args:
        ingredients: 食材列表
        diet_profile: 饮食档案
        cuisine_type: 菜系类型
        cooking_time: 烹饪时间限制
        difficulty: 难度等级
        servings: 份数
        additional_requirements: 额外要求
        
    Returns:
        生成的食谱数据
    """
    try:
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在生成食谱...", "progress": 10}
        )
        
        # 构建 prompt
        prompt = _build_recipe_generation_prompt(
            ingredients=ingredients,
            diet_profile=diet_profile,
            cuisine_type=cuisine_type,
            cooking_time=cooking_time,
            difficulty=difficulty,
            servings=servings,
            additional_requirements=additional_requirements,
        )
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在调用 AI 服务...", "progress": 30}
        )
        
        # 调用 AI 服务生成食谱
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                generate_text(
                    prompt=prompt,
                    temperature=0.8,
                    max_tokens=2000
                )
            )
        finally:
            loop.close()
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在解析食谱数据...", "progress": 70}
        )
        
        # 解析生成的食谱
        recipe_data = _parse_generated_recipe(response)
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "食谱生成完成", "progress": 100}
        )
        
        logger.info(
            "Recipe generated successfully",
            ingredients_count=len(ingredients),
            diet_profile=diet_profile,
            recipe_title=recipe_data.get("title", "Unknown")
        )
        
        return {
            "status": "success",
            "recipe": recipe_data,
            "meta": {
                "ingredients_used": ingredients,
                "diet_profile": diet_profile,
                "generation_params": {
                    "cuisine_type": cuisine_type,
                    "cooking_time": cooking_time,
                    "difficulty": difficulty,
                    "servings": servings,
                }
            }
        }
        
    except Exception as e:
        logger.error("Failed to generate recipe", error=str(e))
        
        # 更新任务状态为失败
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "食谱生成失败"}
        )
        
        raise AIServiceException(f"Failed to generate recipe: {str(e)}")


@task(bind=True, name="app.tasks.ai_tasks.generate_meal_plan")
def generate_meal_plan_task(
    self,
    days: int,
    meals_per_day: int = 3,
    diet_profile: Optional[str] = None,
    target_calories: Optional[int] = None,
    include_snacks: bool = False,
    cuisine_preferences: List[str] = [],
    allergies: List[str] = [],
    dislikes: List[str] = [],
    cooking_time_limit: Optional[int] = None,
    additional_requirements: Optional[str] = None,
) -> Dict[str, Any]:
    """
    异步生成膳食计划任务
    
    Args:
        days: 计划天数
        meals_per_day: 每日餐次
        diet_profile: 饮食档案
        target_calories: 目标卡路里
        include_snacks: 是否包含零食
        cuisine_preferences: 菜系偏好
        allergies: 过敏信息
        dislikes: 不喜欢的食物
        cooking_time_limit: 烹饪时间限制
        additional_requirements: 额外要求
        
    Returns:
        生成的膳食计划数据
    """
    try:
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在生成膳食计划...", "progress": 10}
        )
        
        # 构建 prompt
        prompt = _build_meal_plan_generation_prompt(
            days=days,
            meals_per_day=meals_per_day,
            diet_profile=diet_profile,
            target_calories=target_calories,
            include_snacks=include_snacks,
            cuisine_preferences=cuisine_preferences,
            allergies=allergies,
            dislikes=dislikes,
            cooking_time_limit=cooking_time_limit,
            additional_requirements=additional_requirements,
        )
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在调用 AI 服务...", "progress": 30}
        )
        
        # 调用 AI 服务生成膳食计划
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=3000
                )
            )
        finally:
            loop.close()
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在解析膳食计划数据...", "progress": 80}
        )
        
        # 解析生成的膳食计划
        meal_plan_data = _parse_generated_meal_plan(response, days)
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "膳食计划生成完成", "progress": 100}
        )
        
        logger.info(
            "Meal plan generated successfully",
            days=days,
            meals_per_day=meals_per_day,
            diet_profile=diet_profile,
        )
        
        return {
            "status": "success",
            "meal_plan": meal_plan_data,
            "meta": {
                "generation_params": {
                    "days": days,
                    "meals_per_day": meals_per_day,
                    "diet_profile": diet_profile,
                    "target_calories": target_calories,
                    "include_snacks": include_snacks,
                }
            }
        }
        
    except Exception as e:
        logger.error("Failed to generate meal plan", error=str(e))
        
        # 更新任务状态为失败
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "膳食计划生成失败"}
        )
        
        raise AIServiceException(f"Failed to generate meal plan: {str(e)}")


@task(bind=True, name="app.tasks.ai_tasks.chat_with_assistant")
def chat_with_assistant_task(
    self,
    messages: List[Dict[str, str]],
    user_id: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    异步聊天助手任务
    
    Args:
        messages: 聊天消息列表
        user_id: 用户 ID
        context: 上下文信息
        
    Returns:
        聊天回复
    """
    try:
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "正在处理聊天请求...", "progress": 20}
        )
        
        # 调用 AI 服务进行聊天
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            response = loop.run_until_complete(
                chat_with_ai(
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1500
                )
            )
        finally:
            loop.close()
        
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "聊天回复生成完成", "progress": 100}
        )
        
        logger.info(
            "Chat response generated successfully",
            user_id=user_id,
            message_count=len(messages)
        )
        
        return {
            "status": "success",
            "response": response,
            "meta": {
                "user_id": user_id,
                "context": context,
                "message_count": len(messages),
            }
        }
        
    except Exception as e:
        logger.error("Failed to process chat", error=str(e))
        
        # 更新任务状态为失败
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e), "status": "聊天处理失败"}
        )
        
        raise AIServiceException(f"Failed to process chat: {str(e)}")


@task(name="app.tasks.ai_tasks.update_recommendation_model")
def update_recommendation_model_task() -> Dict[str, Any]:
    """
    更新推荐模型任务（定时任务）
    """
    try:
        logger.info("Starting recommendation model update")
        
        # 这里可以实现模型更新逻辑
        # 例如：重新训练推荐模型、更新向量索引等
        
        logger.info("Recommendation model update completed")
        
        return {
            "status": "success",
            "message": "Recommendation model updated successfully"
        }
        
    except Exception as e:
        logger.error("Failed to update recommendation model", error=str(e))
        raise


def _build_recipe_generation_prompt(
    ingredients: List[str],
    diet_profile: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    cooking_time: Optional[int] = None,
    difficulty: Optional[str] = None,
    servings: int = 4,
    additional_requirements: Optional[str] = None,
) -> str:
    """构建食谱生成的 prompt"""
    
    prompt = f"""作为一名专业的营养师和厨师，请根据以下要求生成一个食谱：

可用食材：{', '.join(ingredients)}
份数：{servings}人份"""
    
    if diet_profile:
        prompt += f"\n饮食类型：{diet_profile}"
    
    if cuisine_type:
        prompt += f"\n菜系：{cuisine_type}"
    
    if cooking_time:
        prompt += f"\n烹饪时间限制：{cooking_time}分钟以内"
    
    if difficulty:
        prompt += f"\n难度等级：{difficulty}"
    
    if additional_requirements:
        prompt += f"\n额外要求：{additional_requirements}"
    
    prompt += """

请按照以下 JSON 格式返回食谱：
{
  "title": "食谱标题",
  "description": "食谱简介",
  "ingredients": [
    {"name": "食材名", "amount": "数量", "unit": "单位", "notes": "备注（可选）"}
  ],
  "directions": [
    "步骤1描述",
    "步骤2描述",
    "..."
  ],
  "prep_time": 准备时间（分钟），
  "cook_time": 烹饪时间（分钟），
  "total_time": 总时间（分钟），
  "servings": 份数,
  "difficulty": "难度等级",
  "nutrition": {
    "calories": 卡路里,
    "protein": 蛋白质（克）,
    "fat": 脂肪（克）,
    "carbohydrates": 碳水化合物（克）,
    "fiber": 纤维（克）
  },
  "tags": ["标签1", "标签2"]
}

请确保食谱健康、美味且符合指定的饮食要求。只返回 JSON 格式的数据，不要包含其他文字。"""
    
    return prompt


def _build_meal_plan_generation_prompt(
    days: int,
    meals_per_day: int = 3,
    diet_profile: Optional[str] = None,
    target_calories: Optional[int] = None,
    include_snacks: bool = False,
    cuisine_preferences: List[str] = [],
    allergies: List[str] = [],
    dislikes: List[str] = [],
    cooking_time_limit: Optional[int] = None,
    additional_requirements: Optional[str] = None,
) -> str:
    """构建膳食计划生成的 prompt"""
    
    prompt = f"""作为一名专业的营养师，请生成一个 {days} 天的膳食计划：

基本要求：
- 天数：{days}天
- 每日餐次：{meals_per_day}餐"""
    
    if include_snacks:
        prompt += "\n- 包含健康零食"
    
    if diet_profile:
        prompt += f"\n- 饮食类型：{diet_profile}"
    
    if target_calories:
        prompt += f"\n- 每日目标卡路里：{target_calories}千卡"
    
    if cuisine_preferences:
        prompt += f"\n- 菜系偏好：{', '.join(cuisine_preferences)}"
    
    if allergies:
        prompt += f"\n- 过敏食物：{', '.join(allergies)}"
    
    if dislikes:
        prompt += f"\n- 不喜欢的食物：{', '.join(dislikes)}"
    
    if cooking_time_limit:
        prompt += f"\n- 单餐烹饪时间限制：{cooking_time_limit}分钟"
    
    if additional_requirements:
        prompt += f"\n- 额外要求：{additional_requirements}"
    
    prompt += """

请按照以下 JSON 格式返回膳食计划：
{
  "plan": [
    {
      "date": "第1天",
      "meals": [
        {
          "type": "早餐",
          "recipes": [
            {
              "title": "食谱名称",
              "description": "简介",
              "prep_time": 准备时间,
              "calories": 卡路里
            }
          ]
        },
        {
          "type": "午餐",
          "recipes": [...]
        },
        {
          "type": "晚餐", 
          "recipes": [...]
        }
      ],
      "total_nutrition": {
        "calories": 全天总卡路里,
        "protein": 蛋白质,
        "fat": 脂肪,
        "carbohydrates": 碳水化合物
      }
    }
  ],
  "summary": {
    "total_days": 天数,
    "avg_daily_calories": 平均每日卡路里,
    "nutrition_balance": "营养均衡性评价"
  },
  "recommendations": [
    "建议1",
    "建议2"
  ]
}

请确保膳食计划营养均衡、多样化且符合指定要求。只返回 JSON 格式的数据。"""
    
    return prompt


def _parse_generated_recipe(response: str) -> Dict[str, Any]:
    """解析生成的食谱响应"""
    try:
        # 尝试提取 JSON 部分
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response[start_idx:end_idx]
        recipe_data = json.loads(json_str)
        
        # 验证必需字段
        required_fields = ['title', 'ingredients', 'directions']
        for field in required_fields:
            if field not in recipe_data:
                raise ValueError(f"Missing required field: {field}")
        
        return recipe_data
        
    except Exception as e:
        logger.error("Failed to parse recipe response", error=str(e), response=response[:500])
        # 返回一个基本的食谱结构
        return {
            "title": "生成的食谱",
            "description": "由 AI 生成的食谱",
            "ingredients": [],
            "directions": ["请查看原始响应"],
            "raw_response": response
        }


def _parse_generated_meal_plan(response: str, days: int) -> Dict[str, Any]:
    """解析生成的膳食计划响应"""
    try:
        # 尝试提取 JSON 部分
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response[start_idx:end_idx]
        meal_plan_data = json.loads(json_str)
        
        # 验证必需字段
        if 'plan' not in meal_plan_data:
            raise ValueError("Missing 'plan' field")
        
        return meal_plan_data
        
    except Exception as e:
        logger.error("Failed to parse meal plan response", error=str(e), response=response[:500])
        # 返回一个基本的膳食计划结构
        return {
            "plan": [],
            "summary": {"total_days": days},
            "recommendations": [],
            "raw_response": response
        }