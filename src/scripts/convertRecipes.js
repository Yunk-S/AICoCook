/**
 * 转换recipes.csv为recipes.json
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseCSV } from '../utils/csvToJson.js';
import { DIFFICULTY_MAP } from '../utils/constants.js';

// 获取当前文件目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '../../');

// 定义文件路径
const csvPath = path.join(rootDir, 'src/data/recipes.csv');
const jsonOutputPath = path.join(rootDir, 'recipes.json');

/**
 * 解析 'cook' 列，保留原始分行和内容
 * @param {string} cookText - cook 列的原始文本
 * @returns {Array<object>} 步骤对象数组
 */
function parseCookSteps(cookText) {
    if (!cookText || !cookText.trim()) {
        return [];
    }
    // 按换行符分割，保留空行作为分隔
    const lines = cookText.split(/\r?\n/);
    
    // 移除每个步骤前的数字编号
    return lines.map(line => {
        const text = line.trim().replace(/^\s*\d+[.、\s]*\s*/, '');
        return { text };
    });
}

try {
  console.log('开始转换CSV文件...');
  
  // 读取CSV文件内容
  const csvContent = fs.readFileSync(csvPath, 'utf8');
  
  // 解析CSV为JSON对象数组
  const recipeData = parseCSV(csvContent);
  console.log(`CSV文件解析完成，共找到 ${recipeData.length} 行数据。`);
  
  // 扩展菜谱数据，添加更多字段
  const extendedRecipes = recipeData.map((recipe, index) => {
    const currentLine = index + 2; // +2 因为数组索引从0开始，且CSV有标题行
    try {
      // 打印进度
      if ((index + 1) % 50 === 0) {
        console.log(`正在处理第 ${index + 1} / ${recipeData.length} 道菜...`);
      }
    
    // 处理工具字段，将 "一口大锅" 替换为 "一口万能的大锅"
    const tools = (recipe.tools || '')
      .split(',')
      .map(tool => (tool.trim() === '一口大锅' ? '一口万能的大锅' : tool.trim()))
      .filter(Boolean);

    // 将 tags 和 stuff 字符串拆分为数组
    const tags = recipe.tags ? recipe.tags.split(';') : [];
    const stuff = recipe.stuff ? recipe.stuff.split(';') : [];
    
    // 解析 'cook' 列，生成统一的步骤列表
    const steps = parseCookSteps(recipe.cook);

    // 创建 Bilibili 链接
    const videoUrl = recipe.bv ? `https://www.bilibili.com/video/${recipe.bv}` : '';

    // 返回结构化的菜谱对象
    return {
      id: `recipe-${index + 1}`,
      name: recipe.name || `未命名菜谱 ${index + 1}`,
      stuff: stuff,
      tools: tools,
      tags: tags,
      difficulty: DIFFICULTY_MAP[recipe.difficulty] || 'medium',
      methods: recipe.methods, // 保留原始的 methods 字段
      videoUrl: videoUrl,
      steps: steps, // 使用新的统一个步骤列表
        image: recipe.image_filename ? `/images/${recipe.image_filename}.jpg` : '/images/recipe-placeholder.jpg',
      popularity: Math.floor(Math.random() * 100), // 生成随机人气值
      createdAt: new Date().toISOString() // 记录创建时间
    };
    } catch (e) {
      console.error(`处理CSV第 ${currentLine} 行（菜谱: ${recipe.name || '未知'}）时发生错误:`, e.message);
      return null; // 返回null以便后续过滤掉出错的行
    }
  }).filter(Boolean); // 过滤掉所有处理失败的null条目
  
  // 将扩展的菜谱数据写入JSON文件
  fs.writeFileSync(jsonOutputPath, JSON.stringify(extendedRecipes, null, 2), 'utf8');
  
  console.log(`转换完成！已成功生成 ${extendedRecipes.length} 条菜谱数据。`);
  console.log(`JSON文件已保存至: ${jsonOutputPath}`);

} catch (error) {
  console.error('CSV到JSON转换过程中发生错误:', error);
} 