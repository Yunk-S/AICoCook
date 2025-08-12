/**
 * 工具函数库
 */

/**
 * 计算BMI指数
 * @param {number} weight - 体重(kg)
 * @param {number} height - 身高(cm)
 * @returns {number} BMI指数
 */
export function calculateBMI(weight, height) {
  if (!weight || !height || height <= 0) return 0;
  
  // BMI = 体重(kg) / (身高(m) * 身高(m))
  const heightInMeter = height / 100;
  return weight / (heightInMeter * heightInMeter);
}

/**
 * 获取BMI状态
 * @param {number} bmi - BMI指数
 * @returns {string} BMI状态
 */
export function getBMIStatus(bmi) {
  if (bmi < 18.5) return 'underweight';  // 体重过轻
  if (bmi < 24.9) return 'normal';       // 体重正常
  if (bmi < 29.9) return 'overweight';   // 超重
  return 'obese';                        // 肥胖
}

/**
 * 计算每日卡路里需求
 * @param {number} weight - 体重(kg)
 * @param {number} height - 身高(cm)
 * @param {number} age - 年龄
 * @param {string} gender - 性别('male'或'female')
 * @param {string} activityLevel - 活动水平
 * @returns {number} 每日卡路里需求
 */
export function calculateDailyCalories(weight, height, age, gender, activityLevel) {
  if (!weight || !height || !age) return 0;
  
  // 基础代谢率(BMR)计算 - Harris-Benedict公式
  let bmr;
  if (gender === 'male') {
    bmr = 66 + (13.7 * weight) + (5 * height) - (6.8 * age);
  } else {
    bmr = 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age);
  }
  
  // 根据活动水平调整
  const activityMultipliers = {
    'sedentary': 1.2,           // 久坐不动
    'lightly_active': 1.375,    // 轻度活动
    'moderately_active': 1.55,  // 中度活动
    'very_active': 1.725,       // 非常活跃
    'extra_active': 1.9         // 极度活跃
  };
  
  const multiplier = activityMultipliers[activityLevel] || 1.2;
  return bmr * multiplier;
}

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期对象、日期字符串或时间戳
 * @param {string} format - 格式化模板，默认为'YYYY-MM-DD'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  const d = date instanceof Date ? date : new Date(date);
  
  if (isNaN(d.getTime())) {
    return '无效日期';
  }
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 格式化烹饪时间
 * @param {number} minutes - 分钟数
 * @returns {string} 格式化后的时间字符串
 */
export function formatCookingTime(minutes) {
  if (!minutes || minutes <= 0) return '未知';
  
  if (minutes < 60) {
    return `${minutes}分钟`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `${hours}小时`;
  }
  
  return `${hours}小时${remainingMinutes}分钟`;
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间(ms)
 * @returns {Function} 防抖处理后的函数
 */
export function debounce(func, wait = 300) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

/**
 * 深拷贝对象
 * @param {*} obj - 要拷贝的对象
 * @returns {*} 拷贝后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj);
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item));
  }
  
  if (obj instanceof Object) {
    const copy = {};
    Object.keys(obj).forEach(key => {
      copy[key] = deepClone(obj[key]);
    });
    return copy;
  }
  
  return obj;
}

/**
 * 生成唯一ID
 * @returns {string} 唯一ID
 */
export function generateUniqueId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
} 