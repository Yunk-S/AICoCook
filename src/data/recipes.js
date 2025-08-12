/**
 * 菜谱数据服务
 */

let recipes = [];
let dataLoaded = false;

// 基础后备数据
const fallbackRecipes = [
  {
    id: "recipe-1",
    name: "红烧肉",
    stuff: ["五花肉", "生抽", "老抽", "冰糖", "料酒", "葱", "姜"],
    tools: ["炒锅"],
    tags: ["家常菜", "荤菜"],
    difficulty: "medium",
    methods: "红烧",
    image: "/images/1.jpg",
    steps: [
      { text: "五花肉切块，冷水下锅焯水" },
      { text: "热锅下糖炒糖色" },
      { text: "下肉块炒至上色" },
      { text: "加调料和热水炖煮40分钟" }
    ],
    popularity: 95
  },
  {
    id: "recipe-2", 
    name: "番茄炒蛋",
    stuff: ["鸡蛋", "番茄", "盐", "糖", "葱花"],
    tools: ["炒锅"],
    tags: ["家常菜", "素菜"],
    difficulty: "easy",
    methods: "炒",
    image: "/images/2.jpg",
    steps: [
      { text: "鸡蛋打散加盐" },
      { text: "番茄切块" },
      { text: "先炒蛋盛起" },
      { text: "炒番茄出汁后倒入鸡蛋炒匀" }
    ],
    popularity: 90
  },
  {
    id: "recipe-3",
    name: "宫保鸡丁",
    stuff: ["鸡胸肉", "花生米", "干辣椒", "花椒", "葱", "姜", "蒜"],
    tools: ["炒锅"],
    tags: ["川菜", "荤菜"],
    difficulty: "medium",
    methods: "炒",
    image: "/images/3.jpg",
    steps: [
      { text: "鸡肉切丁腌制" },
      { text: "花生米炸至酥脆" },
      { text: "爆炒干辣椒和花椒" },
      { text: "下鸡丁炒熟，最后加花生米" }
    ],
    popularity: 88
  }
];

// 同步导入菜谱数据的函数
async function loadRecipeData() {
  if (dataLoaded) return recipes;
  
  try {
    // 尝试加载JSON数据
    const response = await fetch('/recipes.json');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const recipeData = await response.json();
    
    // 确保数据是数组格式
    if (Array.isArray(recipeData) && recipeData.length > 0) {
      recipes = recipeData;
      console.log(`✅ 菜谱数据加载成功，共 ${recipes.length} 条记录`);
    } else {
      console.warn('⚠️ 菜谱数据不是数组格式或为空:', typeof recipeData);
      throw new Error('数据格式错误');
    }
  } catch (error) {
    console.error('❌ 菜谱数据加载失败，使用后备数据:', error.message);
    // 使用后备数据
    recipes = fallbackRecipes;
  }
  
  dataLoaded = true;
  return recipes;
}

// 立即初始化数据加载，确保数据可用
loadRecipeData().catch(error => {
  console.error('❌ 初始化数据加载失败:', error);
});

/**
 * 获取所有菜谱
 * @returns {Array} 菜谱列表
 */
export async function getAllRecipes() {
  await loadRecipeData();
  return recipes;
}

/**
 * 根据ID获取菜谱
 * @param {string} id 菜谱ID
 * @returns {Object|null} 菜谱对象或null
 */
export async function getRecipeById(id) {
  await loadRecipeData();
  return recipes.find(recipe => recipe.id === id) || null;
}

/**
 * 根据类别获取菜谱
 * @param {string} category 类别
 * @returns {Array} 菜谱列表
 */
export async function getRecipesByCategory(category) {
  await loadRecipeData();
  if (!category) return recipes;
  
  return recipes.filter(recipe => {
    // 如果 category 在 tags 数组中，则返回 true
    return recipe.tags && recipe.tags.includes(category);
  });
}

/**
 * 根据食材筛选菜谱
 * @param {Array} ingredients 食材数组
 * @param {string} mode 匹配模式 (fuzzy|strict|survival)
 * @returns {Array} 菜谱数组
 */
export async function getRecipesByIngredients(ingredients, mode = 'fuzzy') {
  await loadRecipeData();
  const ingredientNames = ingredients.map(ing => typeof ing === 'string' ? ing : ing.name);
  
  switch(mode) {
    case 'fuzzy':
      // 只要有任何一种食材符合即可
      return recipes.filter(recipe => 
        recipe.stuff && recipe.stuff.some(stuff => 
          ingredientNames.some(name => stuff === name || stuff.includes(name) || name.includes(stuff))
        )
      );
    
    case 'strict':
      // 必须拥有菜谱所需的所有必要食材
      return recipes.filter(recipe => {
        const requiredStuff = recipe.stuff ? recipe.stuff.filter(s => !s.includes('可选')) : [];
        return requiredStuff.every(stuff => 
          ingredientNames.some(name => stuff === name || stuff.includes(name) || name.includes(stuff))
        );
      });
    
    case 'survival':
      // 只能使用所选食材，尽可能多地匹配
      return recipes.filter(recipe => {
        // 菜谱中的所有食材必须在所选食材中找到
        return recipe.stuff && recipe.stuff.every(stuff => 
          ingredientNames.some(name => stuff === name || stuff.includes(name) || name.includes(stuff))
        );
      });
    
    default:
      return [];
  }
}

/**
 * 根据厨具筛选菜谱
 * @param {Array} cookwareList 厨具数组
 * @returns {Array} 菜谱数组
 */
export async function getRecipesByCookwares(cookwareList) {
  await loadRecipeData();
  const cookwareNames = cookwareList.map(cw => typeof cw === 'string' ? cw : cw.name);
  
  return recipes.filter(recipe => 
    recipe.tools && recipe.tools.some(tool => 
      cookwareNames.some(name => tool === name || tool.includes(name) || name.includes(tool))
    )
  );
}

/**
 * 获取随机菜谱组合（一荤一素一汤一主食）
 * @returns {Object} 随机菜谱组合
 */
export async function getRandomMealCombination() {
  await loadRecipeData();
  // 按类别分类菜谱
  const categorizeRecipe = (recipe) => {
    if (recipe.category) return recipe.category;
    
    const hasMeat = recipe.stuff && recipe.stuff.some(s => 
      ['猪肉', '牛肉', '鸡肉', '午餐肉', '香肠', '腊肠', '虾', '鱼'].includes(s));
    
    if (hasMeat) return 'meat_dish';
    if (recipe.name && (recipe.name.includes('汤') || recipe.name.includes('羹'))) return 'soup';
    if (recipe.stuff && recipe.stuff.some(s => ['米', '面食', '面包', '方便面'].includes(s)) && 
        recipe.name && (recipe.name.includes('饭') || recipe.name.includes('面') || recipe.name.includes('粥'))) {
      return 'staple_food';
    }
    
    return 'vegetable_dish';
  };
  
  const allRecipes = recipes.slice();
  const meatDishes = allRecipes.filter(recipe => categorizeRecipe(recipe) === 'meat_dish');
  const vegetableDishes = allRecipes.filter(recipe => categorizeRecipe(recipe) === 'vegetable_dish');
  const soups = allRecipes.filter(recipe => categorizeRecipe(recipe) === 'soup');
  const stapleFood = allRecipes.filter(recipe => categorizeRecipe(recipe) === 'staple_food');
  
  const getRandomRecipe = (categoryRecipes) => {
    if (categoryRecipes.length > 0) {
      return categoryRecipes[Math.floor(Math.random() * categoryRecipes.length)];
    }
    return allRecipes.length > 0 ? allRecipes[Math.floor(Math.random() * allRecipes.length)] : null;
  };
  
  const randomMeat = getRandomRecipe(meatDishes);
  const randomVegetable = getRandomRecipe(vegetableDishes);
  const randomSoup = getRandomRecipe(soups);
  const randomStaple = getRandomRecipe(stapleFood);
  
  const uniqueRecipes = [];
  [randomMeat, randomVegetable, randomSoup, randomStaple].forEach(recipe => {
    if (recipe && !uniqueRecipes.some(r => r.id === recipe.id)) {
      uniqueRecipes.push(recipe);
    }
  });
  
  return {
    id: `meal-${Date.now()}`,
    recipes: uniqueRecipes,
    timestamp: new Date()
  };
}

/**
 * 根据关键词搜索菜谱
 * @param {string} keyword 关键词
 * @returns {Array} 匹配的菜谱数组
 */
export async function searchRecipes(keyword) {
  await loadRecipeData();
  if (!keyword) return [];
  const lowerKeyword = keyword.toLowerCase();
  
  return recipes.filter(recipe => {
    // 搜索菜名
    if (recipe.name && recipe.name.toLowerCase().includes(lowerKeyword)) {
      return true;
    }
    
    // 搜索食材
    if (recipe.stuff && recipe.stuff.some(stuff => stuff.toLowerCase().includes(lowerKeyword))) {
      return true;
    }
    
    // 搜索标签
    if (recipe.tags && recipe.tags.some(tag => tag.toLowerCase().includes(lowerKeyword))) {
      return true;
    }
    
    return false;
  });
}

export default recipes; 