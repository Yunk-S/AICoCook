/**
 * 食材数据
 * 从cook-dev项目中提取的数据
 */

// 素菜
export const vegetables = [
  {
    id: 'potato',
    name: '土豆',
    name_en: 'Potato',
    emoji: '🥔',
    category: 'vegetable'
  },
  {
    id: 'carrot',
    name: '胡萝卜',
    name_en: 'Carrot',
    emoji: '🥕',
    category: 'vegetable'
  },
  {
    id: 'cauliflower',
    name: '花菜',
    name_en: 'Cauliflower',
    emoji: '🥦',
    category: 'vegetable'
  },
  {
    id: 'radish',
    name: '白萝卜',
    name_en: 'Radish',
    emoji: '🥕',
    category: 'vegetable'
  },
  {
    id: 'zucchini',
    name: '西葫芦',
    name_en: 'Zucchini',
    emoji: '🥒',
    category: 'vegetable'
  },
  {
    id: 'tomato',
    name: '番茄',
    name_en: 'Tomato',
    emoji: '🍅',
    alias: '西红柿',
    category: 'vegetable'
  },
  {
    id: 'celery',
    name: '芹菜',
    name_en: 'Celery',
    emoji: '🥬',
    category: 'vegetable'
  },
  {
    id: 'cucumber',
    name: '黄瓜',
    name_en: 'Cucumber',
    emoji: '🥒',
    category: 'vegetable'
  },
  {
    id: 'onion',
    name: '洋葱',
    name_en: 'Onion',
    emoji: '🧅',
    category: 'vegetable'
  },
  {
    id: 'lettuce',
    name: '莴笋',
    name_en: 'Lettuce',
    emoji: '🎋',
    category: 'vegetable'
  },
  {
    id: 'mushroom',
    name: '菌菇',
    name_en: 'Mushroom',
    emoji: '🍄',
    category: 'vegetable'
  },
  {
    id: 'eggplant',
    name: '茄子',
    name_en: 'Eggplant',
    emoji: '🍆',
    category: 'vegetable'
  },
  {
    id: 'tofu',
    name: '豆腐',
    name_en: 'Tofu',
    emoji: '⬜',
    category: 'vegetable'
  },
  {
    id: 'cabbage',
    name: '包菜',
    name_en: 'Cabbage',
    emoji: '🥗',
    category: 'vegetable'
  },
  {
    id: 'chinese_cabbage',
    name: '白菜',
    name_en: 'Chinese Cabbage',
    emoji: '🥬',
    category: 'vegetable'
  }
];

// 荤菜
export const meats = [
  {
    id: 'luncheon_meat',
    name: '午餐肉',
    name_en: 'Luncheon Meat',
    emoji: '🍖',
    category: 'meat'
  },
  {
    id: 'sausage',
    name: '香肠',
    name_en: 'Sausage',
    emoji: '🌭',
    category: 'meat'
  },
  {
    id: 'chinese_sausage',
    name: '腊肠',
    name_en: 'Chinese Sausage',
    emoji: '🥓',
    category: 'meat'
  },
  {
    id: 'chicken',
    name: '鸡肉',
    name_en: 'Chicken',
    emoji: '🍗',
    category: 'meat'
  },
  {
    id: 'pork',
    name: '猪肉',
    name_en: 'Pork',
    emoji: '🐷',
    category: 'meat'
  },
  {
    id: 'egg',
    name: '鸡蛋',
    name_en: 'Egg',
    emoji: '🥚',
    category: 'meat'
  },
  {
    id: 'beef',
    name: '牛肉',
    name_en: 'Beef',
    emoji: '🐮',
    category: 'meat'
  },
  {
    id: 'bone',
    name: '骨头',
    name_en: 'Bone',
    emoji: '🦴',
    category: 'meat'
  }
];

// 主食
export const staples = [
  {
    id: 'noodle',
    name: '面食',
    name_en: 'Noodles',
    emoji: '🍝',
    category: 'staple'
  },
  {
    id: 'bread',
    name: '面包',
    name_en: 'Bread',
    emoji: '🍞',
    category: 'staple'
  },
  {
    id: 'rice',
    name: '米',
    name_en: 'Rice',
    emoji: '🍚',
    category: 'staple'
  },
  {
    id: 'instant_noodle',
    name: '方便面',
    name_en: 'Instant Noodle',
    emoji: '🍜',
    category: 'staple'
  }
];

// 海鲜
export const seafood = [
  {
    id: 'fish',
    name: '鱼',
    name_en: 'Fish',
    emoji: '🐟',
    category: 'seafood'
  },
  {
    id: 'shrimp',
    name: '虾',
    name_en: 'Shrimp',
    emoji: '🦐',
    category: 'seafood'
  }
];

// 汇总所有食材
export const allIngredients = [...vegetables, ...meats, ...staples, ...seafood];

/**
 * 根据ID获取食材
 * @param {string} id 食材ID
 * @returns {Object|null} 食材对象，如果未找到则返回null
 */
export function getIngredientById(id) {
  return allIngredients.find(ingredient => ingredient.id === id) || null;
}

/**
 * 根据类别筛选食材
 * @param {string} category 类别
 * @returns {Array} 食材数组
 */
export function getIngredientsByCategory(category) {
  return allIngredients.filter(ingredient => ingredient.category === category);
} 