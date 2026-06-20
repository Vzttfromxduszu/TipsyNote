<template>
  <div class="page">
    <!-- 顶栏操作区 -->
    <section class="community-hero">
      <div class="hero-left">
        <div class="hero-badge">精酿社区 · Craft Talk</div>
        <h1>精酿社区</h1>
        <p>分享你的品酒体验，发现同好。</p>
      </div>
      <div class="hero-right">
        <el-button type="primary" size="large" @click="goCreate">
          <el-icon style="margin-right:6px"><EditPen /></el-icon>
          发布帖子
        </el-button>
      </div>
    </section>

    <!-- 搜索栏 -->
    <el-card v-if="activeTab === 'all'" class="search-card">
      <el-form :model="searchForm" inline class="search-form" @submit.prevent="handleSearch">
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索帖子标题或内容…"
            clearable
            @keyup.enter="handleSearch"
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSearch">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" @tab-change="onTabChange" class="community-tabs">
      <el-tab-pane label="全部帖子" name="all" />
      <el-tab-pane label="我的帖子" name="mine" />
      <el-tab-pane label="我赞过的" name="liked" />
    </el-tabs>

    <!-- 帖子列表 -->
    <el-empty v-if="!posts.length && !loading" :description="emptyText" />
    <div v-else class="post-list">
      <el-card
        v-for="post in posts"
        :key="post.id"
        class="post-card"
        shadow="hover"
        @click="goDetail(post.id)"
      >
        <div class="post-header">
          <div class="post-author">
            <el-avatar :size="40" :src="post.user_avatar || undefined">
              {{ (post.user_nickname || '用')[0] }}
            </el-avatar>
            <div class="author-info">
              <span class="author-name">{{ post.user_nickname || '匿名用户' }}</span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
        </div>
        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-content">{{ truncate(post.content, 150) }}</p>
        <div class="post-footer">
          <div class="post-stats">
            <span class="stat-item" :class="{ active: post.liked }">
              <el-icon><StarFilled v-if="post.liked" /><Star v-else /></el-icon>
              {{ post.like_count || 0 }}
            </span>
            <span class="stat-item">
              <el-icon><ChatDotRound /></el-icon>
              {{ post.comment_count || 0 }}
            </span>
          </div>
          <el-tag size="small" type="info">{{ post.comment_count ? '已讨论' : '新帖' }}</el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { EditPen, Search, Star, StarFilled, ChatDotRound } from "@element-plus/icons-vue";
import { fetchPosts, fetchLikedPosts } from "@/api/posts";
import { useUserStore } from "@/stores/user";
import type { PostItem } from "@/types/posts";

const router = useRouter();
const userStore = useUserStore();
const posts = ref<PostItem[]>([]);
const loading = ref(false);
const activeTab = ref("all");

const searchForm = reactive({
  keyword: "",
});

const emptyText = computed(() => {
  switch (activeTab.value) {
    case "mine": return "你还没有发布过帖子";
    case "liked": return "你还没有点赞过帖子";
    default: return "暂无帖子，快来发布第一条吧";
  }
});

const loadPosts = async () => {
  loading.value = true;
  try {
    const params: Record<string, unknown> = {
      offset: 0,
      limit: 50,
    };
    if (activeTab.value === "all") {
      params.keyword = searchForm.keyword || undefined;
    }
    if (activeTab.value === "mine") {
      params.user_id = userStore.profile?.id;
    }
    const data = await fetchPosts(params);
    posts.value = data.items;
  } catch {
    ElMessage.error("加载帖子失败");
  } finally {
    loading.value = false;
  }
};

const loadLikedPosts = async () => {
  loading.value = true;
  try {
    const data = await fetchLikedPosts({ offset: 0, limit: 50 });
    posts.value = data.items;
  } catch {
    ElMessage.error("加载点赞列表失败");
  } finally {
    loading.value = false;
  }
};

const requireAuth = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning("请先登录");
    router.push({ path: "/login", query: { redirect: "/community" } });
    return false;
  }
  return true;
};

const onTabChange = (tab: string) => {
  if ((tab === "mine" || tab === "liked") && !requireAuth()) {
    activeTab.value = "all";
    return;
  }
  if (tab === "liked") {
    loadLikedPosts();
  } else {
    loadPosts();
  }
};

const handleSearch = () => {
  loadPosts();
};

const goCreate = () => {
  router.push("/community/create");
};

const goDetail = (id: number) => {
  router.push(`/community/${id}`);
};

const formatTime = (iso: string) => {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins} 分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} 小时前`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} 天前`;
  return d.toLocaleDateString("zh-CN");
};

const truncate = (text: string, max: number) => {
  if (!text) return "";
  return text.length > max ? text.slice(0, max) + "..." : text;
};

onMounted(() => {
  loadPosts();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.community-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.hero-left h1 {
  margin: 8px 0 4px;
  font-size: 26px;
  color: var(--brew-text);
}

.hero-left p {
  margin: 0;
  color: var(--brew-text-muted);
}

.hero-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(194, 168, 122, 0.15);
  color: var(--brew-accent);
  font-size: 12px;
}

.search-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 360px;
}

.community-tabs {
  margin-bottom: -8px;
}

:deep(.community-tabs .el-tabs__header) {
  margin-bottom: 8px;
}

.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-card {
  cursor: pointer;
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.post-card:hover {
  border-color: var(--brew-accent);
  box-shadow: 0 4px 16px rgba(194, 168, 122, 0.12);
}

.post-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-weight: 600;
  color: var(--brew-text);
  font-size: 14px;
}

.post-time {
  font-size: 12px;
  color: var(--brew-text-muted);
}

.post-title {
  margin: 0 0 8px;
  font-size: 17px;
  color: var(--brew-text);
}

.post-content {
  margin: 0 0 12px;
  color: var(--brew-text-muted);
  font-size: 14px;
  line-height: 1.6;
}

.post-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--brew-border);
}

.post-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--brew-text-muted);
}

.stat-item.active {
  color: var(--brew-accent);
}

:deep(.el-card__body) {
  padding: 18px 20px;
}

@media (max-width: 768px) {
  .community-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .search-input {
    width: 100%;
  }
}
</style>
