<template>
  <div class="style-detail" v-loading="loading">
    <div v-if="detail" class="style-content">
      <!-- 顶部导航 -->
      <div class="breadcrumb">
        <el-button link @click="$router.push('/beer-wiki')">
          <el-icon><ArrowLeft /></el-icon> 精酿大全
        </el-button>
      </div>

      <!-- 风格名片 -->
      <section class="hero-card">
        <div class="hero-top">
          <span class="hero-icon">{{ detail.icon || '🍺' }}</span>
          <div class="hero-info">
            <h1 class="hero-name">{{ detail.name }}</h1>
            <p class="hero-en" v-if="detail.name_en">{{ detail.name_en }}</p>
            <el-tag effect="plain" class="hero-cat">{{ detail.category }}</el-tag>
          </div>
        </div>
        <p class="hero-desc" v-if="detail.description">{{ detail.description }}</p>
      </section>

      <!-- 风味雷达图 + 参数 -->
      <section class="radar-section">
        <h2 class="section-title">风味特征</h2>
        <div class="radar-wrap">
          <!-- 雷达图 -->
          <div class="radar-chart">
            <canvas ref="radarCanvas"></canvas>
          </div>
          <!-- 参数卡片 -->
          <div class="param-cards">
            <div class="param-item">
              <span class="param-label">苦度 IBU</span>
              <span class="param-value">{{ detail.ibu_min }}–{{ detail.ibu_max }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">色度 SRM</span>
              <span class="param-value">{{ detail.srm_min }}–{{ detail.srm_max }}</span>
            </div>
            <div class="param-item">
              <span class="param-label">酒精度 ABV</span>
              <span class="param-value">{{ detail.abv_min }}%–{{ detail.abv_max }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 起源工艺 -->
      <section v-if="detail.origin_story" class="info-section">
        <h2 class="section-title">📖 起源 & 工艺</h2>
        <p class="info-text">{{ detail.origin_story }}</p>
      </section>

      <!-- 品鉴指南 -->
      <section v-if="detail.tasting_notes" class="info-section">
        <h2 class="section-title">🍷 品鉴指南</h2>
        <p class="info-text">{{ detail.tasting_notes }}</p>
      </section>

      <!-- 经典代表作 -->
      <section v-if="classicBeers.length" class="beers-section">
        <h2 class="section-title">⭐ 经典代表作</h2>
        <div class="beer-cards">
          <div
            v-for="b in classicBeers"
            :key="b.id"
            class="beer-card"
            @click="$router.push(`/beer-wiki/beer/${b.id}`)"
          >
            <div class="beer-card-icon">🍺</div>
            <div class="beer-card-info">
              <span class="beer-card-name">{{ b.name }}</span>
              <span class="beer-card-meta">{{ b.brewery }} · {{ b.country }}</span>
              <div class="beer-card-params">
                <span v-if="b.abv">ABV {{ b.abv }}%</span>
                <span v-if="b.ibu">IBU {{ b.ibu }}</span>
              </div>
            </div>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </section>

      <!-- 全部酒款 -->
      <section v-if="allBeers.length" class="beers-section">
        <h2 class="section-title">🍻 该品类全部酒款</h2>
        <div class="beer-cards">
          <div
            v-for="b in allBeers"
            :key="b.id"
            class="beer-card"
            @click="$router.push(`/beer-wiki/beer/${b.id}`)"
          >
            <div class="beer-card-icon">🍺</div>
            <div class="beer-card-info">
              <span class="beer-card-name">{{ b.name }}</span>
              <span class="beer-card-meta">{{ b.brewery }} · {{ b.country }}</span>
              <div class="beer-card-params">
                <span v-if="b.abv">ABV {{ b.abv }}%</span>
                <span v-if="b.ibu">IBU {{ b.ibu }}</span>
              </div>
            </div>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue";
import { fetchStyleDetailFull, fetchStyleDetail, fetchAllStyles } from "@/api/beerWiki";
import type { BeerStyleDetail, BeerItemBrief } from "@/types/beerWiki";

const route = useRoute();
const loading = ref(false);
const detail = ref<BeerStyleDetail | null>(null);
const classicBeers = ref<BeerItemBrief[]>([]);
const allBeers = ref<BeerItemBrief[]>([]);
const radarCanvas = ref<HTMLCanvasElement | null>(null);

const styleId = computed(() => Number(route.params.id));

// 绘制简易雷达图
const drawRadar = () => {
  if (!radarCanvas.value || !detail.value) return;
  const canvas = radarCanvas.value;
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const d = detail.value;
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const r = Math.min(cx, cy) - 28;  // 留出标签空间

  const labels = ["苦度", "色度", "酒精度", "麦芽香", "果香"];
  // 归一化值（将各类参数映射到0-50再归一化到0-1）
  const ibuVal = d.ibu_max ? Math.min((d.ibu_max / 80), 1) : 0.3;
  const srmVal = d.srm_max ? Math.min((d.srm_max / 40), 1) : 0.3;
  const abvVal = d.abv_max ? Math.min((d.abv_max / 14), 1) : 0.3;
  const maltVal = 0.5;  // 默认中等麦芽香
  const fruitVal = ibuVal > 0.5 ? ibuVal * 0.7 : 0.4; // IPA类果香高

  const values: number[] = [ibuVal, srmVal, abvVal, maltVal, fruitVal];
  const angleStep = (Math.PI * 2) / labels.length;

  // 背景网格
  ctx.strokeStyle = "#e5e7eb";
  ctx.fillStyle = "transparent";
  for (let level = 0.2; level <= 1; level += 0.2) {
    ctx.beginPath();
    for (let i = 0; i < labels.length; i++) {
      const angle = angleStep * i - Math.PI / 2;
      const x = cx + r * level * Math.cos(angle);
      const y = cy + r * level * Math.sin(angle);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  // 轴线
  ctx.strokeStyle = "#d1d5db";
  for (let i = 0; i < labels.length; i++) {
    const angle = angleStep * i - Math.PI / 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * Math.cos(angle), cy + r * Math.sin(angle));
    ctx.stroke();
  }

  // 数据区域
  ctx.beginPath();
  ctx.fillStyle = "rgba(124, 58, 237, 0.15)";
  ctx.strokeStyle = "#7c3aed";
  ctx.lineWidth = 2;
  for (let i = 0; i < values.length; i++) {
    const angle = angleStep * i - Math.PI / 2;
    const x = cx + r * values[i] * Math.cos(angle);
    const y = cy + r * values[i] * Math.sin(angle);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // 标签
  ctx.fillStyle = "#374151";
  ctx.font = "12px sans-serif";
  ctx.textAlign = "center";
  for (let i = 0; i < labels.length; i++) {
    const angle = angleStep * i - Math.PI / 2;
    const x = cx + (r + 12) * Math.cos(angle);
    const y = cy + (r + 12) * Math.sin(angle) + 4;
    ctx.fillText(labels[i], x, y);
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    const [detailData, styleData] = await Promise.all([
      fetchStyleDetailFull(styleId.value),
      fetchStyleDetail(styleId.value),
    ]);
    detail.value = detailData;
    classicBeers.value = styleData.classic_beers;
    allBeers.value = styleData.beers;
    await nextTick();
    drawRadar();
  } catch {
    // handled
  } finally {
    loading.value = false;
  }
});

// 监听窗口大小变化重绘雷达
watch(() => radarCanvas.value, drawRadar);
</script>

<style scoped>
.style-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}

.breadcrumb {
  margin: 16px 0;
}

/* 英雄卡片 */
.hero-card {
  background: linear-gradient(135deg, #faf5ff, #fdf2f8);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}

.hero-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
}

.hero-icon {
  font-size: 48px;
}

.hero-name {
  font-size: 26px;
  font-weight: 800;
  color: var(--brew-text);
  margin: 0;
}

.hero-en {
  font-size: 14px;
  color: var(--brew-secondary);
  margin: 2px 0 6px;
}

.hero-desc {
  font-size: 15px;
  color: var(--brew-secondary);
  line-height: 1.7;
  margin: 0;
}

/* 雷达区 */
.radar-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 19px;
  font-weight: 700;
  color: var(--brew-text);
  margin-bottom: 14px;
}

.radar-wrap {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.radar-chart {
  width: 220px;
  height: 220px;
  flex-shrink: 0;
}

.radar-chart canvas {
  width: 100%;
  height: 100%;
}

.param-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-item {
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 10px;
  padding: 12px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  min-width: 180px;
}

.param-label {
  font-size: 14px;
  color: var(--brew-secondary);
}

.param-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--brew-text);
}

/* 信息区 */
.info-section {
  margin-bottom: 32px;
}

.info-text {
  font-size: 15px;
  color: var(--brew-secondary);
  line-height: 1.8;
  margin: 0;
  white-space: pre-line;
}

/* 酒款列表 */
.beers-section {
  margin-bottom: 32px;
}

.beer-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.beer-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.beer-card:hover {
  border-color: var(--brew-primary, #7c3aed);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.08);
}

.beer-card-icon {
  font-size: 28px;
}

.beer-card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.beer-card-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--brew-text);
}

.beer-card-meta {
  font-size: 13px;
  color: var(--brew-secondary);
}

.beer-card-params {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--brew-secondary);
}
</style>
