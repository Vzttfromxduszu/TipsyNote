<template>
  <div class="page">
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">AI 侍酒师 · Sommelier AI</div>
        <h1>让 AI 为你推荐精酿</h1>
        <p>描述你的心境和口味偏好，AI 侍酒师将为你精选最适合的精酿啤酒。</p>
      </div>
      <div class="hero-panel">
        <div class="panel-title">🤖 AI 推荐</div>
        <div class="panel-desc">基于你的心情、品味与场景，使用先进的 AI 模型推荐专属于你的精酿酒款。</div>
        <div class="panel-meta">智能匹配 · 个性定制 · 即时推荐</div>
      </div>
    </section>

    <el-card class="sommelier-card">
      <div class="sommelier-container">
        <!-- 左侧表单 -->
        <div class="form-section">
          <div class="form-title">
            <span class="title-icon">✨</span>
            <span>描述你的需求</span>
          </div>

          <div class="form-box">
            <el-form :model="form" class="sommelier-form">
              <!-- 心情 -->
              <div class="form-group">
                <label class="form-label">当前心情</label>
                <div class="mood-selector">
                  <el-button
                    v-for="mood in moodOptions"
                    :key="mood.value"
                    :type="form.mood === mood.value ? 'primary' : ''"
                    :plain="form.mood !== mood.value"
                    class="mood-btn"
                    @click="form.mood = mood.value"
                  >
                    <span class="mood-icon">{{ mood.icon }}</span>
                    <span>{{ mood.label }}</span>
                  </el-button>
                </div>
              </div>

              <!-- 口味偏好 -->
              <div class="form-group">
                <label class="form-label">口味偏好</label>
                <el-checkbox-group v-model="form.tastes" class="taste-group">
                  <div class="taste-row" v-for="row in tasteRows" :key="row[0]?.value">
                    <el-checkbox v-for="taste in row" :key="taste.value" :label="taste.value">
                      {{ taste.label }}
                    </el-checkbox>
                  </div>
                </el-checkbox-group>
              </div>

              <!-- 场景 -->
              <div class="form-group">
                <label class="form-label">饮酒场景</label>
                <el-radio-group v-model="form.scene" class="scene-group">
                  <el-radio v-for="scene in sceneOptions" :key="scene.value" :label="scene.value">
                    {{ scene.label }}
                  </el-radio>
                </el-radio-group>
              </div>

              <!-- 风格偏好 -->
              <div class="form-group">
                <label class="form-label">风格偏好</label>
                <div class="style-selector">
                  <el-button
                    v-for="style in styleOptions"
                    :key="style.value"
                    :type="form.style === style.value ? 'primary' : ''"
                    :plain="form.style !== style.value"
                    class="style-btn"
                    @click="form.style = style.value"
                  >
                    {{ style.label }}
                  </el-button>
                </div>
              </div>

              <!-- 提交按钮 -->
              <div class="form-actions">
                <el-button type="primary" :loading="loading" size="large" class="btn-recommend" @click="handleRecommend">
                  <span class="action-icon">🎯</span>
                  获取 AI 推荐
                </el-button>
                <el-button class="btn-reset" @click="resetForm">重置</el-button>
              </div>
            </el-form>
          </div>
        </div>

        <!-- 右侧结果 -->
        <div class="result-section">
          <div class="form-title">
            <span class="title-icon">🍺</span>
            <span>AI 推荐结果</span>
          </div>

          <div class="result-box">
            <el-empty v-if="!hasRecommended" description="暂无推荐，请先提交" class="empty-state" />

            <div v-else class="recommendation-list">
              <transition-group name="list" tag="div" class="list-container">
                <div
                  v-for="(item, index) in results"
                  :key="index"
                  class="recommendation-card"
                  :style="{ animationDelay: `${index * 0.1}s` }"
                >
                  <div class="card-header">
                    <div class="card-rank">
                      <span class="rank-icon">{{ getRankIcon(index) }}</span>
                    </div>
                    <div class="card-info">
                      <div class="beer-name">{{ item.beer_name }}</div>
                      <div class="brewery-name">{{ item.brewery_name }}</div>
                    </div>
                  </div>

                  <div class="card-reason">
                    <div class="reason-label">为什么推荐？</div>
                    <p class="reason-text">{{ item.reason }}</p>
                  </div>

                  <div class="card-actions">
                    <el-button type="primary" size="small" @click="searchBeer(item.beer_name)">
                      在附近寻找
                    </el-button>
                  </div>
                </div>
              </transition-group>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { fetchAIRecommend } from "@/api/ai";
import type { AIRecommendItem } from "@/types/ai";

const router = useRouter();
const loading = ref(false);
const results = ref<AIRecommendItem[]>([]);
const hasRecommended = ref(false);

// 选项配置
const moodOptions = [
  { value: "happy", label: "愉快", icon: "😄" },
  { value: "relaxed", label: "放松", icon: "😌" },
  { value: "excited", label: "兴奋", icon: "🤩" },
  { value: "thoughtful", label: "深思", icon: "🤔" },
  { value: "melancholic", label: "忧伤", icon: "😔" },
];

const tasteOptions = [
  { value: "hoppy", label: "苦味浓" },
  { value: "fruity", label: "果香" },
  { value: "floral", label: "花香" },
  { value: "malty", label: "麦芽香" },
  { value: "citrus", label: "柑橘" },
  { value: "spicy", label: "辛辣" },
];

const tasteRows = computed(() => {
  const rows = [];
  for (let i = 0; i < tasteOptions.length; i += 2) {
    rows.push(tasteOptions.slice(i, i + 2));
  }
  return rows;
});

const sceneOptions = [
  { value: "solo", label: "独自享受" },
  { value: "friends", label: "与朋友" },
  { value: "date", label: "约会聚餐" },
  { value: "celebration", label: "庆祝活动" },
  { value: "work", label: "工作休闲" },
];

const styleOptions = [
  { value: "light", label: "清淡" },
  { value: "balanced", label: "平衡" },
  { value: "intense", label: "浓烈" },
  { value: "experimental", label: "特色" },
];

const form = reactive({
  mood: "relaxed",
  tastes: [],
  scene: "friends",
  style: "balanced",
});

// 处理推荐
const handleRecommend = async () => {
  if (!form.mood) {
    ElMessage.warning("请选择心情");
    return;
  }
  if (!form.scene) {
    ElMessage.warning("请选择场景");
    return;
  }
  if (!form.style) {
    ElMessage.warning("请选择风格");
    return;
  }

  loading.value = true;
  try {
    const data = await fetchAIRecommend({
      mood: form.mood,
      tastes: form.tastes.length > 0 ? form.tastes : ["balanced"],
      scene: form.scene,
      style: form.style,
    });
    results.value = data.items;
    hasRecommended.value = true;
    ElMessage.success("推荐完成！");
  } catch (error) {
    ElMessage.error("推荐失败，请稍后重试");
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  form.mood = "relaxed";
  form.tastes = [];
  form.scene = "friends";
  form.style = "balanced";
  results.value = [];
  hasRecommended.value = false;
};

// 获取排名图标
const getRankIcon = (index: number) => {
  if (index === 0) return "🥇";
  if (index === 1) return "🥈";
  if (index === 2) return "🥉";
  return `${index + 1}`;
};

// 搜索啤酒
const searchBeer = (beerName: string) => {
  router.push({
    path: "/",
    query: { beerName },
  });
};
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

.hero-content h1 {
  margin: 12px 0 8px;
  font-size: 28px;
  color: var(--brew-text);
  font-weight: 600;
}

.hero-content p {
  margin: 0 0 16px;
  color: var(--brew-text-muted);
  font-size: 14px;
  line-height: 1.5;
}

.hero-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(194, 168, 122, 0.15);
  color: var(--brew-accent);
  font-size: 12px;
  font-weight: 500;
}

.hero-panel {
  background: var(--brew-surface-2);
  border: 1px solid var(--brew-border);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-title {
  font-weight: 600;
  font-size: 13px;
  color: var(--brew-text);
}

.panel-desc {
  color: var(--brew-text);
  font-size: 12px;
  line-height: 1.5;
}

.panel-meta {
  color: var(--brew-text-muted);
  font-size: 11px;
  padding-top: 8px;
  border-top: 1px solid var(--brew-border);
}

.sommelier-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02);
}

:deep(.sommelier-card .el-card__body) {
  padding: 16px;
}

.sommelier-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-section,
.result-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--brew-text);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  height: 32px;
}

.title-icon {
  font-size: 16px;
}

.form-box,
.result-box {
  background: var(--brew-surface-2);
  border: 1px solid var(--brew-border);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.result-box {
  flex: 1;
  min-height: 400px;
}

.sommelier-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 500;
  font-size: 13px;
  color: var(--brew-text);
  line-height: 1;
}

.mood-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.mood-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 12px;
  height: 32px;
  margin: 0 !important;
}

.mood-icon {
  font-size: 14px;
}

.taste-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.taste-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.scene-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.style-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.style-btn {
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 12px;
  height: 32px;
  margin: 0 !important;
}

.form-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--brew-border);
}

.btn-recommend {
  flex: 1;
  height: 36px;
}

.btn-reset {
  width: 80px;
  height: 36px;
}

.action-icon {
  font-size: 14px;
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 600px;
  overflow-y: auto;
  padding: 4px;
}

.list-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommendation-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.3s ease;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.recommendation-card:hover {
  border-color: var(--brew-accent);
  box-shadow: 0 2px 8px rgba(194, 168, 122, 0.08);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.card-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  flex-shrink: 0;
  font-size: 12px;
}

.rank-icon {
  font-size: 18px;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.beer-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--brew-text);
}

.brewery-name {
  color: var(--brew-text-muted);
  font-size: 11px;
  margin-top: 2px;
}

.card-reason {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reason-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--brew-accent);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.reason-text {
  font-size: 12px;
  color: var(--brew-text);
  line-height: 1.4;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 6px;
  padding-top: 4px;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .sommelier-container {
    grid-template-columns: 1fr;
  }

  .hero {
    grid-template-columns: 1fr;
  }

  .recommendation-list {
    max-height: none;
  }

  .mood-selector,
  .taste-row,
  .scene-group,
  .style-selector {
    grid-template-columns: 1fr;
  }

  .form-actions {
    gap: 6px;
  }

  .btn-recommend,
  .btn-reset {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 16px;
    gap: 16px;
  }

  .sommelier-card {
    border-radius: 8px;
  }

  :deep(.sommelier-card .el-card__body) {
    padding: 12px;
  }

  .form-box,
  .result-box {
    padding: 12px;
  }

  .form-title {
    padding: 0 8px;
    font-size: 14px;
  }

  .mood-btn,
  .style-btn {
    font-size: 11px;
    height: 28px;
  }

  .recommendation-card {
    padding: 10px;
    gap: 8px;
  }

  .beer-name {
    font-size: 12px;
  }

  .reason-text {
    font-size: 11px;
  }
}

/* Element Plus 组件样式覆盖 */
:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
}

:deep(.el-button.is-plain) {
  height: 32px;
}

:deep(.el-button--small) {
  height: 28px;
  padding: 0 12px;
  font-size: 12px;
}

:deep(.el-button--primary--plain) {
  border-color: var(--brew-accent);
  color: var(--brew-accent);
}

:deep(.el-button--primary--plain:hover) {
  background-color: rgba(194, 168, 122, 0.1);
  border-color: var(--brew-accent);
  color: var(--brew-accent);
}

:deep(.el-input__wrapper) {
  background-color: var(--brew-surface);
  border-color: var(--brew-border);
}

:deep(.el-input__input) {
  color: var(--brew-text);
  font-size: 13px;
}

:deep(.el-checkbox) {
  color: var(--brew-text);
  --el-checkbox-input-height: 16px;
  --el-checkbox-input-width: 16px;
}

:deep(.el-checkbox__label) {
  font-size: 12px;
  padding-left: 4px;
}

:deep(.el-radio) {
  color: var(--brew-text);
  --el-radio-input-height: 16px;
  --el-radio-input-width: 16px;
}

:deep(.el-radio__label) {
  font-size: 12px;
  padding-left: 4px;
}

:deep(.el-empty) {
  --el-empty-padding: 24px;
}

:deep(.el-empty__description) {
  color: var(--brew-text-muted);
  font-size: 12px;
  margin-top: 8px;
}

/* 列表过渡效果 */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 滚动条样式 */
:deep(.recommendation-list::-webkit-scrollbar) {
  width: 6px;
}

:deep(.recommendation-list::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.recommendation-list::-webkit-scrollbar-thumb) {
  background: var(--brew-border);
  border-radius: 3px;
}

:deep(.recommendation-list::-webkit-scrollbar-thumb:hover) {
  background: var(--brew-text-muted);
}
</style>
