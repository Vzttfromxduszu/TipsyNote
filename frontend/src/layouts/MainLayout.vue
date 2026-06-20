<template>
  <el-container class="layout">
    <el-header class="layout-header">
      <div class="header-inner">
        <div class="header-left">
          <div class="logo">
            <span class="logo-mark">TN</span>
            <span class="logo-text">TipsyNote</span>
          </div>
          <el-menu :default-active="activeMenu" router mode="horizontal" :ellipsis="false" class="menu">
            <el-menu-item index="/search">找酒</el-menu-item>
            <el-menu-item index="/community">社区</el-menu-item>
            <!-- 精酿大全暂时下架 -->
            <!-- <el-menu-item index="/beer-wiki">精酿大全</el-menu-item> -->
            <el-menu-item index="/ai-sommelier">侍酒师</el-menu-item>
          </el-menu>
        </div>
        <div class="header-right">
          <template v-if="store.isLoggedIn">
            <el-dropdown trigger="click" class="more-dropdown">
              <span class="more-trigger">
                <span class="more-icon">···</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <span @click="$router.push('/profile')">我的信息</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="merchant-auth">
                    <span @click="$router.push('/merchant-auth')">商家认证</span>
                  </el-dropdown-item>
                  <el-dropdown-item v-if="canManagePubs" command="pubs">
                    <span @click="$router.push('/my-pubs')">我的酒馆</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-text class="user-name">{{ nickname }}</el-text>
            <el-button type="primary" link @click="handleLogout">退出</el-button>
          </template>
          <el-button v-else type="primary" @click="handleLogin">登录</el-button>
        </div>
      </div>
    </el-header>
    <el-main class="layout-main">
      <div class="content-wrap">
        <router-view v-slot="{ Component, route }">
          <template v-if="route.meta?.keepAlive">
            <keep-alive>
              <component :is="Component" />
            </keep-alive>
          </template>
          <template v-else>
            <component :is="Component" />
          </template>
        </router-view>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const route = useRoute();
const router = useRouter();
const store = useUserStore();

const activeMenu = computed(() => {
  const p = route.path;
  if (p.startsWith("/beer-wiki")) return "/beer-wiki";
  if (p.startsWith("/community")) return "/community";
  return p;
});
const nickname = computed(() => store.profile?.nickname || store.profile?.phone || "用户");

/** 是否显示「我的酒馆」入口：角色为商家(1)或管理员(2) */
const canManagePubs = computed(() => {
  const role = store.profile?.role;
  return role === 1 || role === 2;
});

const handleLogout = () => {
  store.logout();
  router.replace("/login");
};

const handleLogin = () => {
  router.push("/login");
};
</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: var(--brew-bg);
}

.layout-header {
  background: rgba(255, 255, 255, 0.85);
  border-bottom: 1px solid var(--brew-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(12px);
}

.header-inner {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 18px;
  color: var(--brew-text);
}

.logo-mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--brew-accent);
  color: #FFFFFF;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 12px;
}

.logo-text {
  letter-spacing: 0.5px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  color: var(--brew-text-muted);
}

.layout-main {
  padding: 24px;
}

.content-wrap {
  width: min(1200px, 100%);
  margin: 0 auto;
}

.menu {
  border-right: none;
  border-bottom: none;
  background: transparent;
}

:deep(.el-menu--horizontal) {
  background-color: transparent;
  border-bottom: none;
}

:deep(.el-menu--horizontal .el-menu-item) {
  color: var(--brew-text-muted);
}

:deep(.el-menu--horizontal .el-menu-item.is-active) {
  color: var(--brew-accent);
}

/* ── 三点下拉菜单 ── */
.more-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.more-trigger:hover {
  background: var(--brew-bg);
}
.more-icon {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--brew-text-muted);
  line-height: 1;
  user-select: none;
}


</style>
