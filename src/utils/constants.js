/**
 * 应用常量
 */

// 食材分类
export const INGREDIENT_CATEGORIES = {
  MEAT: '肉类',
  VEGETABLE: '蔬菜类',
  SEAFOOD: '海鲜类',
  FRUIT: '水果类',
  GRAIN: '谷物类',
  DAIRY: '乳制品',
  SPICE: '调料香料',
  OTHER: '其他'
};

// 厨具分类
export const COOKWARE_CATEGORIES = {
  POT: '锅具',
  KNIFE: '刀具',
  BOARD: '砧板',
  UTENSIL: '厨具',
  APPLIANCE: '电器',
  BAKEWARE: '烘焙器具',
  OTHER: '其他'
};

// 菜谱类别
export const RECIPE_CATEGORIES = {
  MEAT_DISH: '荤菜',
  VEGETABLE_DISH: '素菜',
  SOUP: '汤',
  STAPLE_FOOD: '主食',
  DESSERT: '甜点',
  BEVERAGE: '饮品',
  APPETIZER: '开胃菜',
  SALAD: '沙拉'
};

// 料理难度
export const DIFFICULTIES = {
  EASY: 'easy',      // 简单
  MEDIUM: 'medium',  // 中等
  HARD: 'hard'       // 困难
};

export const DIFFICULTY_MAP = {
  '简单': 'easy',
  '普通': 'medium',
  '中等': 'medium',
  '复杂': 'hard',
  '困难': 'hard'
};

// 为了兼容性，添加DIFFICULTY_LEVELS作为DIFFICULTIES的别名
export const DIFFICULTY_LEVELS = DIFFICULTIES;

// 匹配方法
export const MATCHING_METHODS = {
  FUZZY: 'fuzzy',     // 模糊匹配（任何食材匹配即可）
  STRICT: 'strict',   // 严格匹配（必须包含所有必需食材）
  SURVIVAL: 'survival' // 极限生存（只使用选择的食材）
};

// 默认分页大小
export const DEFAULT_PAGE_SIZE = 12;

// 本地存储键名
export const STORAGE_KEYS = {
  THEME: 'theme',
  LOCALE: 'locale',
  FAVORITE_RECIPES: 'favoriteRecipes',
  HISTORY_RECIPES: 'historyRecipes',
  USER_PREFERENCES: 'userPreferences',
  USER_HEALTH_DATA: 'userHealthData',
  SAVED_SEARCHES: 'savedSearches',
  MEAL_HISTORY: 'mealHistory'
}; 