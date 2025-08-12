/**
 * 厨具数据
 * 从cook-dev项目中提取的数据
 */

// 厨具
export const cookwares = [
  {
    id: 'wok',
    name: '炒锅',
    name_en: 'Wok',
    emoji: '🍳',
    category: 'cookware'
  },
  {
    id: 'air_fryer',
    name: '空气炸锅',
    name_en: 'Air Fryer',
    emoji: '💨',
    category: 'cookware'
  },
  {
    id: 'rice_cooker',
    name: '电饭煲',
    name_en: 'Rice Cooker',
    emoji: '🍚',
    category: 'cookware'
  },
  {
    id: 'oven',
    name: '烤箱',
    name_en: 'Oven',
    emoji: '🔥',
    category: 'cookware'
  },
  {
    id: 'all_purpose_pot',
    name: '一口万能的大锅',
    name_en: 'All-Purpose Pot',
    emoji: '🍲',
    category: 'cookware'
  }
];

/**
 * 根据ID获取厨具
 * @param {string} id 厨具ID
 * @returns {Object|null} 厨具对象，如果未找到则返回null
 */
export function getCookwareById(id) {
  return cookwares.find(cookware => cookware.id === id) || null;
}

/**
 * 获取所有厨具
 * @returns {Array} 厨具数组
 */
export function getAllCookwares() {
  return cookwares;
} 