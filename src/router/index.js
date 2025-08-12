import { createRouter, createWebHistory } from "vue-router"

// 路由懒加载
const Home = () => import("../views/Home.vue")
const AiRecommend = () => import("../views/AiRecommend.vue")
const RandomRecipe = () => import("../views/RandomRecipe.vue")
const LimitedConditions = () => import("../views/LimitedConditions.vue")
const FoodGallery = () => import("../views/FoodGallery.vue")
const MyRecipes = () => import("../views/MyRecipes.vue")
const RecipeDetail = () => import("../views/RecipeDetail.vue")
const AiCoach = () => import("../views/AiCoach.vue") // 新增 AI Coach 路由

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home
  },
  {
    path: "/ai-coach", // 新增 AI Coach 页面路由
    name: "AiCoach",
    component: AiCoach
  },
  {
    path: "/ai-recommend",
    name: "AiRecommend",
    component: AiRecommend
  },
  {
    path: "/random-recipe",
    name: "RandomRecipe",
    component: RandomRecipe
  },
  {
    path: "/limited-conditions",
    name: "LimitedConditions",
    component: LimitedConditions
  },
  {
    path: "/food-gallery",
    name: "FoodGallery",
    component: FoodGallery
  },
  {
    path: "/my-recipes",
    name: "MyRecipes",
    component: MyRecipes
  },
  {
    path: "/recipe/:id",
    name: "RecipeDetail",
    component: RecipeDetail,
    props: true
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/"
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 生产环境下移除路由守卫的日志，提高性能
if (import.meta.env.DEV) {
  router.beforeEach((to, from, next) => {
    console.log(`[Router Guard] Navigating from ${from.path} to ${to.path}`);
    next();
  });
}

export default router
