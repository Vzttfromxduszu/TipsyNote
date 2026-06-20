import { createRouter, createWebHistory, type RouteLocationNormalized } from "vue-router";
import { useUserStore } from "@/stores/user";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/Login.vue"),
      meta: { public: true, title: "登录" },
    },
    {
      path: "/register",
      name: "register",
      component: () => import("@/views/Register.vue"),
      meta: { public: true, title: "注册" },
    },
    {
      path: "/",
      component: () => import("@/layouts/MainLayout.vue"),
      children: [
        {
          path: "",
          redirect: "/login",
        },
        {
          path: "search",
          name: "home",
          component: () => import("@/views/Home.vue"),
          meta: { requiresAuth: true, title: "酒款搜索", keepAlive: true },
        },
        {
          path: "profile",
          name: "profile",
          component: () => import("@/views/UserProfile.vue"),
          meta: { requiresAuth: true, title: "我的信息" },
        },
        {
          path: "my-pubs",
          name: "myPubs",
          component: () => import("@/views/MyPubs.vue"),
          meta: { requiresAuth: true, title: "我的酒馆" },
        },
        {
          path: "merchant-auth",
          name: "merchantAuth",
          component: () => import("@/views/MerchantAuth.vue"),
          meta: { requiresAuth: true, title: "商家认证" },
        },
        {
          path: "pubs/:id",
          name: "pubDetail",
          component: () => import("@/views/PubDetail.vue"),
          meta: { requiresAuth: true, title: "酒馆详情" },
        },
        {
          path: "beer-style",
          name: "beerStyle",
          component: () => import("@/views/BeerStyleSearch.vue"),
          meta: { requiresAuth: true, title: "风格搜索" },
        },
        {
          path: "ai-sommelier",
          name: "aiSommelier",
          component: () => import("@/views/AISommelier.vue"),
          meta: { requiresAuth: true, title: "AI 侍酒师", keepAlive: true },
        },
        {
          path: "community",
          name: "community",
          component: () => import("@/views/Community.vue"),
          meta: { requiresAuth: true, title: "精酿社区" },
        },
        {
          path: "community/create",
          name: "postCreate",
          component: () => import("@/views/PostEditor.vue"),
          meta: { requiresAuth: true, title: "发布帖子" },
        },
        {
          path: "community/:id",
          name: "postDetail",
          component: () => import("@/views/PostDetail.vue"),
          meta: { requiresAuth: true, title: "帖子详情" },
        },
        {
          path: "community/:id/edit",
          name: "postEdit",
          component: () => import("@/views/PostEditor.vue"),
          meta: { requiresAuth: true, title: "编辑帖子" },
        },
        // ── 精酿大全（暂时下架）──
        // {
        //   path: "beer-wiki",
        //   name: "encyclopedia",
        //   component: () => import("@/views/Encyclopedia.vue"),
        //   meta: { requiresAuth: true, title: "精酿大全" },
        // },
        // {
        //   path: "beer-wiki/style/:id",
        //   name: "beerStyleDetail",
        //   component: () => import("@/views/BeerStyleDetail.vue"),
        //   meta: { requiresAuth: true, title: "品类百科" },
        // },
        // {
        //   path: "beer-wiki/beer/:id",
        //   name: "beerItemDetail",
        //   component: () => import("@/views/BeerItemDetail.vue"),
        //   meta: { requiresAuth: true, title: "酒款详情" },
        // },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/login" },
  ],
});

router.beforeEach(async (to: RouteLocationNormalized) => {
  const store = useUserStore();
  if (to.meta?.title) {
    document.title = `酒款找酒 - ${String(to.meta.title)}`;
  }
  const isPublic = Boolean(to.meta?.public);
  if (!isPublic) {
    if (!store.isLoggedIn) {
      return { path: "/login", query: { redirect: to.fullPath } };
    }
    if (!store.profile) {
      await store.fetchProfile();
    }
  }
  // 已登录用户访问登录/注册页时，重定向到社区页
  if (isPublic && store.isLoggedIn && !to.query.redirect) {
    return { path: "/community" };
  }
  return true;
});

export default router;
