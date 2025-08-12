/**
 * 食材或厨具项目
 * @typedef {Object} StuffItem
 * @property {string} name - 名称
 * @property {string} emoji - emoji图标
 * @property {string} [image] - 图片链接
 * @property {string} [alias] - 别名
 * @property {string} [icon] - 图标名称
 * @property {string} [label] - 显示标签
 */

/**
 * 食谱项目
 * @typedef {Object} RecipeItem
 * @property {string} id - 唯一ID
 * @property {string} name - 菜名
 * @property {string} [link] - 链接
 * @property {string} [bv] - BiliBili视频ID
 * @property {string[]} stuff - 材料
 * @property {string[]} [emojis] - 根据材料生成的emoji
 * @property {string} [difficulty] - 难度 (简单|普通|困难)
 * @property {string[]} [tags] - 标签
 * @property {string[]} [methods] - 烹饪方法 (炒|煎|烘|炸|etc)
 * @property {string[]} tools - 烹饪工具
 * @property {string} [category] - 菜品类别
 * @property {string} [cuisine] - 菜系
 * @property {Object} [nutrition] - 营养信息
 * @property {number} [nutrition.calories] - 卡路里
 * @property {number} [nutrition.protein] - 蛋白质(g)
 * @property {number} [nutrition.fat] - 脂肪(g)
 * @property {number} [nutrition.carbs] - 碳水化合物(g)
 * @property {string} [image] - 图片URL
 * @property {string} [videoUrl] - 视频URL
 */ 