<template>
  <div class="beer-detail" v-loading="loading">
    <div v-if="detail" class="beer-content">
      <!-- 顶部导航 -->
      <div class="breadcrumb">
        <el-button link @click="$router.push('/beer-wiki')">
          <el-icon><ArrowLeft /></el-icon> 精酿大全
        </el-button>
      </div>

      <!-- 酒款基本信息 -->
      <section class="hero-card">
        <div class="hero-top">
          <div class="beer-avatar">
            <span class="avatar-icon">🍺</span>
          </div>
          <div class="hero-info">
            <h1 class="beer-name">{{ detail.name }}</h1>
            <p class="beer-en" v-if="detail.name_en">{{ detail.name_en }}</p>
            <div class="hero-tags">
              <el-tag v-if="detail.style_name" type="primary" effect="plain" @click.stop="goToStyle" class="clickable-tag">
                {{ detail.style_name }}
              </el-tag>
              <el-tag v-if="detail.is_classic" size="small" type="warning" effect="dark">经典代表作</el-tag>
            </div>
          </div>
        </div>
      </section>

      <!-- 专业参数 -->
      <section class="params-section">
        <h2 class="section-title">专业参数</h2>
        <div class="param-grid">
          <div class="param-card">
            <span class="param-label">原麦汁浓度</span>
            <span class="param-value">{{ detail.og ? detail.og + '°P' : '暂无数据' }}</span>
          </div>
          <div class="param-card">
            <span class="param-label">酒精度 ABV</span>
            <span class="param-value">{{ detail.abv ? detail.abv + '%' : '暂无数据' }}</span>
          </div>
          <div class="param-card">
            <span class="param-label">苦度 IBU</span>
            <span class="param-value">{{ detail.ibu ?? '暂无数据' }}</span>
          </div>
          <div class="param-card">
            <span class="param-label">酒厂/品牌</span>
            <span class="param-value">{{ detail.brewery || '暂无数据' }}</span>
          </div>
          <div class="param-card">
            <span class="param-label">产地</span>
            <span class="param-value">{{ detail.country || '暂无数据' }}</span>
          </div>
          <div class="param-card" v-if="detail.style_name">
            <span class="param-label">所属品类</span>
            <span class="param-value link" @click="goToStyle">{{ detail.style_name }}</span>
          </div>
        </div>
      </section>

      <!-- 风味描述 -->
      <section v-if="detail.description || detail.flavor_tags" class="desc-section">
        <h2 class="section-title">风味描述</h2>
        <p v-if="detail.description" class="desc-text">{{ detail.description }}</p>
        <div v-if="detail.flavor_tags" class="flavor-tags">
          <el-tag
            v-for="tag in flavorTags"
            :key="tag"
            size="small"
            effect="plain"
            class="flavor-tag"
          >{{ tag }}</el-tag>
        </div>
      </section>

      <!-- 社区联动：相关酒评 -->
      <section v-if="relatedPosts.length" class="community-section">
        <h2 class="section-title">
          💬 社区里的相关讨论
          <el-button link type="primary" size="small" @click="goToCommunity" class="view-all">
            查看更多 →
          </el-button>
        </h2>
        <div class="related-posts">
          <div
            v-for="p in relatedPosts"
            :key="p.id"
            class="related-post"
            @click="$router.push(`/community/${p.id}`)"
          >
            <div class="post-header">
              <el-avatar :size="32" :src="p.user_avatar" class="post-avatar" />
              <span class="post-nickname">{{ p.user_nickname || '匿名用户' }}</span>
              <span class="post-time">{{ formatTime(p.created_at) }}</span>
            </div>
            <h4 class="post-title">{{ p.title }}</h4>
            <p class="post-content">{{ p.content || '' }}</p>
            <div class="post-footer">
              <span><el-icon><StarFilled /></el-icon> {{ p.like_count }}</span>
              <span><el-icon><ChatDotRound /></el-icon> {{ p.comment_count }}</span>
            </div>
          </div>
        </div>
      </section>

      <el-empty v-else description="暂无相关讨论，快去社区发帖聊聊吧！" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, StarFilled, ChatDotRound } from "@element-plus/icons-vue";
import { fetchBeerDetail } from "@/api/beerWiki";
import type { BeerItemDetail, RelatedPost } from "@/types/beerWiki";

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const detail = ref<BeerItemDetail | null>(null);
const relatedPosts = ref<RelatedPost[]>([]);
const beerId = computed(() => Number(route.params.id));

const flavorTags = computed(() => {
  if (!detail.value?.flavor_tags) return [];
  return detail.value.flavor_tags.split(",").map((t) => t.trim()).filter(Boolean);
});

const goToStyle = () => {
  if (detail.value?.style_id) {
    router.push(`/beer-wiki/style/${detail.value.style_id}`);
  }
};

const goToCommunity = () => {
  router.push("/community");
};

const formatTime = (t: string | null) => {
  if (!t) return "";
  const d = new Date(t);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  return d.toLocaleDateString("zh-CN");
};

onMounted(async () => {
  loading.value = true;
  try {
    const data = await fetchBeerDetail(beerId.value);
    detail.value = data.beer;
    relatedPosts.value = data.related_posts;
  } catch {
    // handled
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.beer-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}

.breadcrumb {
  margin: 16px 0;
}

/* 英雄卡片 */
.hero-card {
  background: linear-gradient(135deg, #faf5ff, #eef2ff);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.hero-top {
  display: flex;
  align-items: center;
  gap: 18px;
}

.beer-avatar {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f3e8ff, #fce7f3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 36px;
}

.beer-name {
  font-size: 24px;
  font-weight: 800;
  color: var(--brew-text);
  margin: 0;
}

.beer-en {
  font-size: 14px;
  color: var(--brew-secondary);
  margin: 4px 0 8px;
}

.hero-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.clickable-tag {
  cursor: pointer;
}

/* 参数卡片 */
.params-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 19px;
  font-weight: 700;
  color: var(--brew-text);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.param-card {
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-label {
  font-size: 12px;
  color: var(--brew-secondary);
}

.param-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--brew-text);
}

.param-value.link {
  color: var(--brew-primary, #7c3aed);
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* 风味描述 */
.desc-section {
  margin-bottom: 32px;
}

.desc-text {
  font-size: 15px;
  color: var(--brew-secondary);
  line-height: 1.8;
  margin: 0 0 12px;
  white-space: pre-line;
}

.flavor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.flavor-tag {
  border-radius: 20px;
}

/* 社区联动 */
.community-section {
  margin-bottom: 32px;
}

.view-all {
  font-size: 13px;
}

.related-posts {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-post {
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.related-post:hover {
  border-color: var(--brew-primary, #7c3aed);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.08);
}

.post-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.post-avatar {
  flex-shrink: 0;
}

.post-nickname {
  font-size: 13px;
  font-weight: 600;
  color: var(--brew-text);
}

.post-time {
  font-size: 12px;
  color: var(--brew-secondary);
  margin-left: auto;
}

.post-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--brew-text);
  margin: 0 0 6px;
}

.post-content {
  font-size: 13px;
  color: var(--brew-secondary);
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-footer {
  display: flex;
  gap: 16px;
  margin-top: 10px;
  font-size: 13px;
  color: var(--brew-secondary);
}

.post-footer span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
