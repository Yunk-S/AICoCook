/**
 * 全局数据缓存管理
 */

class DataCache {
  constructor() {
    this.cache = new Map();
    this.timestamps = new Map();
    this.defaultTTL = 5 * 60 * 1000; // 5分钟默认缓存时间
  }

  /**
   * 设置缓存
   * @param {string} key 缓存键
   * @param {any} data 缓存数据
   * @param {number} ttl 生存时间（毫秒）
   */
  set(key, data, ttl = this.defaultTTL) {
    this.cache.set(key, data);
    this.timestamps.set(key, Date.now() + ttl);
    console.log(`🗂️ DataCache: 缓存已设置 [${key}]`);
  }

  /**
   * 获取缓存
   * @param {string} key 缓存键
   * @returns {any|null} 缓存数据或null
   */
  get(key) {
    const timestamp = this.timestamps.get(key);
    if (!timestamp || Date.now() > timestamp) {
      // 缓存过期
      this.delete(key);
      return null;
    }
    
    const data = this.cache.get(key);
    if (data) {
      console.log(`✅ DataCache: 使用缓存 [${key}]`);
    }
    return data;
  }

  /**
   * 删除缓存
   * @param {string} key 缓存键
   */
  delete(key) {
    this.cache.delete(key);
    this.timestamps.delete(key);
    console.log(`🗑️ DataCache: 缓存已删除 [${key}]`);
  }

  /**
   * 清空所有缓存
   */
  clear() {
    this.cache.clear();
    this.timestamps.clear();
    console.log('🧹 DataCache: 所有缓存已清空');
  }

  /**
   * 检查缓存是否存在且有效
   * @param {string} key 缓存键
   * @returns {boolean}
   */
  has(key) {
    const timestamp = this.timestamps.get(key);
    return timestamp && Date.now() <= timestamp && this.cache.has(key);
  }

  /**
   * 获取缓存统计信息
   * @returns {Object}
   */
  getStats() {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      memory: this.estimateMemoryUsage()
    };
  }

  /**
   * 估算内存使用量（粗略估计）
   * @returns {string}
   */
  estimateMemoryUsage() {
    let size = 0;
    for (const [key, value] of this.cache) {
      size += JSON.stringify(key).length + JSON.stringify(value).length;
    }
    
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }

  /**
   * 清理过期缓存
   */
  cleanup() {
    const now = Date.now();
    let cleaned = 0;
    
    for (const [key, timestamp] of this.timestamps) {
      if (now > timestamp) {
        this.delete(key);
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      console.log(`🧹 DataCache: 清理了 ${cleaned} 个过期缓存`);
    }
  }
}

// 创建全局实例
const dataCache = new DataCache();

// 定期清理过期缓存
setInterval(() => {
  dataCache.cleanup();
}, 60 * 1000); // 每分钟清理一次

export default dataCache;

// 缓存键常量
export const CACHE_KEYS = {
  ALL_RECIPES: 'recipes:all',
  TRENDING_RECIPES: 'recipes:trending',
  ALL_INGREDIENTS: 'ingredients:all',
  ALL_COOKWARES: 'cookwares:all',
  SEARCH_RESULTS: 'search:results:',
  RECIPE_DETAILS: 'recipe:details:'
};