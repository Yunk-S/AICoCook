#!/usr/bin/env python3
"""
简单可靠的搜索引擎
专注于稳定性和高召回率
"""
import json
import jieba
import logging
from typing import List, Dict, Any
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSearchEngine:
    def __init__(self):
        self.recipes = {}
        self.total_recipes = 0
        
    def load_recipes(self, recipes_data: List[Dict[str, Any]]) -> bool:
        """加载菜谱数据"""
        try:
            self.recipes = {}
            for i, recipe in enumerate(recipes_data):
                if isinstance(recipe, dict) and 'name' in recipe:
                    self.recipes[str(i)] = recipe
            
            self.total_recipes = len(self.recipes)
            logger.info(f"✅ 成功加载 {self.total_recipes} 个菜谱")
            return True
            
        except Exception as e:
            logger.error(f"❌ 加载菜谱失败: {e}")
            return False
    
    def search(self, query: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        简单直接的搜索方法
        """
        if not query or not query.strip():
            return []
        
        query = query.strip().lower()
        logger.info(f"🔍 搜索: '{query}' (限制: {limit})")
        
        results = []
        
        try:
            for doc_id, recipe in self.recipes.items():
                score = 0.0
                
                try:
                    # 检查菜名
                    name = str(recipe.get('name', '')).lower()
                    if query in name:
                        if query == name:
                            score += 10.0  # 完全匹配
                        else:
                            score += 5.0   # 部分匹配
                    
                    # 检查标签
                    tags = recipe.get('tags', [])
                    if isinstance(tags, list):
                        for tag in tags:
                            if query in str(tag).lower():
                                score += 3.0
                                break
                    
                    # 检查食材
                    stuff = recipe.get('stuff', [])
                    if isinstance(stuff, list):
                        for item in stuff:
                            if query in str(item).lower():
                                score += 2.0
                                break
                    
                    # 检查厨具
                    tools = recipe.get('tools', [])
                    if isinstance(tools, list):
                        for tool in tools:
                            if query in str(tool).lower():
                                score += 1.5
                                break
                    
                    # 检查做法
                    methods = str(recipe.get('methods', '')).lower()
                    if query in methods:
                        score += 1.0
                    
                    # 分词搜索 (提高召回率) - 不管是否已有分数都进行
                    try:
                        tokens = jieba.lcut(query)
                        for token in tokens:
                            if len(token.strip()) > 1:  # 忽略单字符
                                token_lower = token.lower()
                                
                                # 在所有字段中搜索token
                                all_text = name + ' '
                                
                                if isinstance(tags, list):
                                    all_text += ' '.join(str(tag) for tag in tags) + ' '
                                
                                if isinstance(stuff, list):
                                    all_text += ' '.join(str(item) for item in stuff) + ' '
                                
                                if isinstance(tools, list):
                                    all_text += ' '.join(str(tool) for tool in tools) + ' '
                                
                                all_text += methods
                                
                                # 分词匹配加分
                                if token_lower in all_text:
                                    # 如果原本没分数，给基础分数
                                    if score == 0:
                                        score += 1.0
                                    else:
                                        score += 0.3  # 额外加分
                    except:
                        pass
                    
                    # 模糊匹配 - 进一步提高召回率
                    if score == 0:
                        # 单字符匹配（中文常用）
                        if len(query) == 1:
                            all_content = f"{name} {' '.join(str(tag) for tag in tags if isinstance(tags, list))} {' '.join(str(item) for item in stuff if isinstance(stuff, list))}"
                            if query in all_content:
                                score += 0.8
                    
                    # 如果有匹配，添加到结果
                    if score > 0:
                        result_recipe = recipe.copy()
                        # 确保methods字段不为None
                        if result_recipe.get('methods') is None:
                            result_recipe['methods'] = ""
                        result_recipe['match_score'] = round(score, 4)
                        results.append(result_recipe)
                        
                except Exception as e:
                    logger.error(f"处理菜谱 {doc_id} 时出错: {e}")
                    continue
            
            # 按分数排序
            results.sort(key=lambda x: x['match_score'], reverse=True)
            
            # 限制结果数量
            final_results = results[:limit]
            
            logger.info(f"✅ 找到 {len(final_results)} 个结果")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ 搜索过程出错: {e}")
            return []

def load_recipes_from_file() -> List[Dict[str, Any]]:
    """从文件加载菜谱数据"""
    try:
        # 尝试多个可能的路径
        possible_paths = [
            Path(__file__).parent.parent / "src" / "data" / "recipes.json",
            Path(__file__).parent.parent / "recipes.json",
            Path("src/data/recipes.json"),
            Path("recipes.json")
        ]
        
        recipes_path = None
        for path in possible_paths:
            if path.exists():
                recipes_path = path
                break
        
        if not recipes_path:
            logger.error(f"❌ 菜谱文件不存在，尝试过的路径: {[str(p) for p in possible_paths]}")
            return []
        
        logger.info(f"✅ 找到菜谱文件: {recipes_path}")
        
        with open(recipes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            logger.info(f"✅ 从文件加载了 {len(data)} 个菜谱")
            return data
        else:
            logger.error("❌ 菜谱数据格式错误，应该是数组")
            return []
            
    except Exception as e:
        logger.error(f"❌ 加载菜谱文件失败: {e}")
        return []