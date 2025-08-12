/**
 * CSV转JSON工具函数
 */
import Papa from 'papaparse';

/**
 * 解析CSV文件内容为JSON数据
 * @param {string} csvContent - CSV文件内容
 * @returns {Array} 解析后的JSON数组
 */
export function parseCSV(csvContent) {
  if (!csvContent) return [];

  try {
    const result = Papa.parse(csvContent.trim(), {
      header: true,       // 将第一行作为对象的键
      skipEmptyLines: true, // 跳过空行
      dynamicTyping: true,  // 自动转换数字和布尔值
    });

    if (result.errors.length > 0) {
      console.warn('CSV解析过程中发现错误:', result.errors);
  }
  
    return result.data;
  } catch (error) {
    console.error('使用papaparse解析CSV时发生严重错误:', error);
    return [];
  }
} 