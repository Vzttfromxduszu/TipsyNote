<template>
  <div class="encyclopedia">
    <!-- 顶部超级搜索区 -->
    <section class="search-hero">
      <h1 class="search-title">精酿大全</h1>
      <p class="search-subtitle">探索精酿啤酒的风格、酒款与故事</p>
      <div class="search-box-wrapper">
        <el-autocomplete
          v-model="keyword"
          :fetch-suggestions="fetchSuggest"
          :placeholder="placeholder"
          :trigger-on-focus="false"
          :highlight-first-item="true"
          class="search-autocomplete"
          clearable
          @select="handleSelect"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #default="{ item }">
            <div class="suggest-item">
              <el-tag :type="item.type === 'beer' ? 'success' : 'primary'" size="small" effect="plain">
                {{ item.type === 'beer' ? '酒款' : '品类' }}
              </el-tag>
              <span class="suggest-name">{{ item.value }}</span>
              <span class="suggest-sub" v-if="item.subtitle">· {{ item.subtitle }}</span>
            </div>
          </template>
        </el-autocomplete>
        <el-button type="primary" size="large" @click="handleSearch">
          <el-icon><Search /></el-icon>
          探索
        </el-button>
      </div>
    </section>

    <!-- 搜索结果 -->
    <section v-if="searchResult" class="search-results section">
      <!-- 匹配到的品类 -->
      <div v-if="searchResult.styles.length" class="result-group">
        <h3 class="result-label">📚 品类百科</h3>
        <div class="style-cards">
          <div
            v-for="s in searchResult.styles"
            :key="'s-' + s.id"
            class="style-card"
            @click="$router.push(`/beer-wiki/style/${s.id}`)"
          >
            <span class="style-icon">{{ s.icon || '🍺' }}</span>
            <div class="style-info">
              <span class="style-name">{{ s.name }}</span>
              <span class="style-en">{{ s.name_en }}</span>
            </div>
            <el-tag size="small" effect="plain">{{ s.category }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 匹配到的酒款 -->
      <div v-if="searchResult.beers.length" class="result-group">
        <h3 class="result-label">🍻 经典酒款</h3>
        <div class="beer-cards">
          <div
            v-for="b in searchResult.beers"
            :key="'b-' + b.id"
            class="beer-card"
            @click="$router.push(`/beer-wiki/beer/${b.id}`)"
          >
            <div class="beer-card-img">
              <span class="beer-icon">🍺</span>
              <el-tag v-if="b.is_classic" size="small" type="warning" effect="dark" class="classic-badge">经典</el-tag>
            </div>
            <div class="beer-info">
              <span class="beer-name">{{ b.name }}</span>
              <span class="beer-meta">{{ b.brewery }} · {{ b.country }}</span>
              <div class="beer-tags">
                <el-tag v-if="b.style_name" size="small" effect="plain">{{ b.style_name }}</el-tag>
                <span v-if="b.abv" class="beer-stat">ABV {{ b.abv }}%</span>
                <span v-if="b.ibu" class="beer-stat">IBU {{ b.ibu }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-if="!searchResult.styles.length && !searchResult.beers.length" description="未找到相关内容" />
    </section>

    <!-- 品类金刚区 -->
    <section class="styles-section section">
      <h2 class="section-title">啤酒风格分类</h2>
      <p class="section-desc">按国际 BJCP 标准简化分类，助你快速入门</p>

      <!-- 按大类分组 -->
      <div v-for="group in styleGroups" :key="group.category" class="style-group">
        <h3 class="group-title">{{ group.category }}</h3>
        <div class="style-grid">
          <div
            v-for="s in group.styles"
            :key="s.id"
            class="style-tile"
            @click="$router.push(`/beer-wiki/style/${s.id}`)"
          >
            <span class="tile-icon">{{ s.icon || '🍺' }}</span>
            <span class="tile-name">{{ s.name }}</span>
            <span class="tile-en" v-if="s.name_en">{{ s.name_en }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 快速跳转酒款 -->
    <section class="classics-section section">
      <h2 class="section-title">全球经典酒款</h2>
      <p class="section-desc">精选风格代表作，点击了解详情</p>
      <div class="beer-grid">
        <div
          v-for="b in classicBeers"
          :key="b.id"
          class="beer-tile"
          @click="$router.push(`/beer-wiki/beer/${b.id}`)"
        >
          <span class="beer-tile-icon">🍺</span>
          <div class="beer-tile-info">
            <span class="beer-tile-name">{{ b.name }}</span>
            <span class="beer-tile-meta">{{ b.brewery }}</span>
            <div class="beer-tile-params">
              <el-tag v-if="b.style_name" size="small" effect="plain">{{ b.style_name }}</el-tag>
              <span v-if="b.abv" class="param">ABV {{ b.abv }}%</span>
              <span v-if="b.ibu" class="param">IBU {{ b.ibu }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { Search } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { fetchSuggestions, searchBeerWiki, fetchAllStyles, fetchClassicBeers } from "@/api/beerWiki";
import type { BeerStyleBrief, BeerItemBrief, BeerSearchResult, BeerSuggestItem } from "@/types/beerWiki";

const router = useRouter();
const keyword = ref("");
const searching = ref(false);
const searchResult = ref<BeerSearchResult | null>(null);
const allStyles = ref<BeerStyleBrief[]>([]);
const classicBeers = ref<BeerItemBrief[]>([]);

const placeholder = "输入酒名或品类，如：迷失海岸 / IPA / 世涛...";

// 搜索联想
const fetchSuggest = (queryString: string, cb: (results: any[]) => void) => {
  if (!queryString.trim()) {
    cb([]);
    return;
  }
  fetchSuggestions(queryString.trim(), 8)
    .then((items) => {
      cb(items.map((it: BeerSuggestItem) => ({
        value: it.name,
        type: it.type,
        id: it.id,
        subtitle: it.subtitle,
      })));
    })
    .catch(() => cb([]));
};

// 选中联想项
const handleSelect = (item: any) => {
  if (item.type === "style") {
    router.push(`/beer-wiki/style/${item.id}`);
  } else {
    router.push(`/beer-wiki/beer/${item.id}`);
  }
};

// 搜索
const handleSearch = async () => {
  const q = keyword.value.trim();
  if (!q) {
    ElMessage.warning("请输入搜索关键词");
    return;
  }
  searching.value = true;
  searchResult.value = null;
  try {
    searchResult.value = await searchBeerWiki(q);
  } catch {
    // 错误已由拦截器提示
  } finally {
    searching.value = false;
  }
};

// 按大类分组
const styleGroups = computed(() => {
  const map: Record<string, BeerStyleBrief[]> = {};
  for (const s of allStyles.value) {
    if (!map[s.category]) map[s.category] = [];
    map[s.category].push(s);
  }
  const order = ["艾尔", "拉格", "特色"];
  return order
    .filter((cat) => map[cat])
    .map((cat) => ({ category: cat, styles: map[cat] }));
});

onMounted(async () => {
  try {
    const [styles, classics] = await Promise.all([fetchAllStyles(), fetchClassicBeers()]);
    allStyles.value = styles;
    classicBeers.value = classics;
  } catch {
    // ignore
  }
});
</script>

<style scoped>
.encyclopedia {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 16px;
}

.section {
  margin-bottom: 48px;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--brew-text);
  margin-bottom: 6px;
}

.section-desc {
  font-size: 14px;
  color: var(--brew-secondary);
  margin-bottom: 20px;
}

/* ── 搜索区 ── */
.search-hero {
  text-align: center;
  padding: 48px 0 36px;
}

.search-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--brew-text);
  margin-bottom: 8px;
}

.search-subtitle {
  font-size: 15px;
  color: var(--brew-secondary);
  margin-bottom: 24px;
}

.search-box-wrapper {
  display: flex;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.search-autocomplete {
  flex: 1;
}

.suggest-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggest-name {
  font-weight: 600;
}

.suggest-sub {
  color: var(--brew-secondary);
  font-size: 13px;
}

/* ── 搜索结果 ── */
.search-results {
  margin-top: 0;
}

.result-label {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 12px;
}

.result-group {
  margin-bottom: 28px;
}

/* 品类卡片 */
.style-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.style-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 12px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.style-card:hover {
  border-color: var(--brew-primary, #7c3aed);
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.1);
}

.style-icon {
  font-size: 28px;
}

.style-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.style-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--brew-text);
}

.style-en {
  font-size: 12px;
  color: var(--brew-secondary);
}

/* 酒款卡片（搜索结果） */
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
}

.beer-card-img {
  position: relative;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f3e8ff, #fce7f3);
  border-radius: 10px;
  font-size: 24px;
}

.classic-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  transform: scale(0.75);
}

.beer-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.beer-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--brew-text);
}

.beer-meta {
  font-size: 13px;
  color: var(--brew-secondary);
}

.beer-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.beer-stat {
  font-size: 12px;
  color: var(--brew-secondary);
}

/* ── 金刚区 ── */
.style-group {
  margin-bottom: 24px;
}

.group-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--brew-primary, #7c3aed);
  margin-bottom: 10px;
  padding-left: 4px;
  border-left: 3px solid var(--brew-primary, #7c3aed);
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
}

.style-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 14px;
  padding: 20px 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.style-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border-color: var(--brew-primary, #7c3aed);
}

.tile-icon {
  font-size: 32px;
}

.tile-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--brew-text);
}

.tile-en {
  font-size: 11px;
  color: var(--brew-secondary);
  text-align: center;
}

/* ── 经典酒款 ── */
.beer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.beer-tile {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid var(--brew-border);
  border-radius: 14px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.beer-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border-color: var(--brew-primary, #7c3aed);
}

.beer-tile-icon {
  font-size: 36px;
}

.beer-tile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.beer-tile-name {
  font-weight: 700;
  font-size: 14px;
  color: var(--brew-text);
}

.beer-tile-meta {
  font-size: 12px;
  color: var(--brew-secondary);
}

.beer-tile-params {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.param {
  font-size: 12px;
  color: var(--brew-secondary);
}
</style>
