<template>
  <div class="page">
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">精酿主题 · Nearby Craft</div>
        <h1>用酒款找到附近酒馆</h1>
        <p>从风格到距离，一步找到正在上头的那一杯。</p>
      </div>
      <div class="hero-panel">
        <div class="panel-title">热门风格</div>
        <div class="panel-tags">
          <el-tag v-for="item in quickTags" :key="item" effect="dark" @click="applyQuickTag(item)">
            {{ item }}
          </el-tag>
        </div>
        <div class="panel-meta">定位状态：{{ locationText }}</div>
      </div>
    </section>

    <el-card class="search-card">
      <div class="search-grid">
        <div class="search-form">
          <div class="search-title">酒款搜索</div>
          <el-form :model="form" inline class="form" @submit.prevent>
            <el-form-item label="酒款名称" class="form-grow">
              <el-input
                v-model="form.beerName"
                placeholder="例如：IPA"
                clearable
                @keyup.enter="handleSearch"
              />
            </el-form-item>
            <el-form-item label="排序" class="form-sort">
              <el-select v-model="form.sortBy" placeholder="请选择">
                <el-option label="默认" value="default" />
                <el-option label="价格从低到高" value="priceAsc" />
                <el-option label="价格从高到低" value="priceDesc" />
                <el-option label="距离从近到远" value="distanceAsc" />
              </el-select>
            </el-form-item>
            <el-form-item label="范围(公里)">
              <el-input-number v-model="form.radiusKm" :min="1" :max="50" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleSearch">搜索</el-button>
              <el-button @click="handleLocate">重新定位</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <div class="result-header">
        <div class="result-title">附近酒馆</div>
        <el-tag v-if="hasSearched" size="small">当前排序：{{ sortLabel }}</el-tag>
        <el-tag v-else size="small">默认排序：距离从近到远</el-tag>
      </div>
      <!-- 尚未搜索：展示附近 20km 全部酒馆 -->
      <template v-if="!hasSearched">
        <el-empty v-if="!nearbyPubs.length" description="正在获取附近酒馆…" />
        <el-row v-else :gutter="16">
          <el-col v-for="item in nearbyPubs" :key="item.pub.id" :span="8">
            <el-card class="pub-card" @click="$router.push(`/pubs/${item.pub.id}`)">
              <div class="pub-cover" :style="getCoverStyle(item.pub.cover_url)"></div>
              <div class="pub-title">{{ item.pub.pub_name }}</div>
              <el-text type="info">{{ item.pub.address || "暂无地址" }}</el-text>
              <div class="pub-info">
                <span>距离：{{ item.distance_km.toFixed(2) }} km</span>
                <span>营业：{{ item.pub.business_hours || "-" }}</span>
                <span>电话：{{ item.pub.contact_phone || "-" }}</span>
              </div>
              <div class="pub-actions">
                <el-button type="primary" size="small">查看详情</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </template>
      <!-- 已搜索酒款：按酒馆合并展示 -->
      <template v-else>
        <el-empty v-if="!groupedResults.length" description="暂无结果，请尝试其他酒款" />
        <div v-else class="grouped-list">
          <el-card
            v-for="group in groupedResults"
            :key="group.pub.id"
            class="grouped-card"
            shadow="hover"
          >
            <div class="grouped-layout">
              <div class="grouped-cover" :style="getCoverStyle(group.pub.cover_url)" @click="$router.push(`/pubs/${group.pub.id}`)"></div>
              <div class="grouped-body">
                <div class="grouped-head">
                  <span class="grouped-name" @click="$router.push(`/pubs/${group.pub.id}`)">{{ group.pub.pub_name }}</span>
                  <el-tag size="small" type="warning">{{ group.distance_km.toFixed(1) }} km</el-tag>
                </div>
                <el-text type="info" size="small">{{ group.pub.address || "暂无地址" }}</el-text>
                <div class="grouped-meta">
                  <span>营业：{{ group.pub.business_hours || "-" }}</span>
                  <span>电话：{{ group.pub.contact_phone || "-" }}</span>
                </div>
                <el-table :data="group.beers" size="small" class="beer-table" :show-header="true">
                  <el-table-column prop="beer_name" label="酒款" min-width="120" />
                  <el-table-column prop="brewery_name" label="酒厂" min-width="100">
                    <template #default="{ row }">{{ row.brewery_name || "-" }}</template>
                  </el-table-column>
                  <el-table-column prop="style" label="风格" min-width="80">
                    <template #default="{ row }">{{ row.style || "-" }}</template>
                  </el-table-column>
                  <el-table-column prop="price" label="价格" width="80" align="right">
                    <template #default="{ row }">{{ row.price != null ? `¥${row.price}` : "-" }}</template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-card>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { searchPubsByBeerNearby, fetchNearbyPubs } from "@/api/pubs";
import type { BeerPubItem, PubNearbyItem, PubInfo } from "@/types/pubs";

interface GroupedPubItem {
  pub: PubInfo;
  distance_km: number;
  beers: { beer_name: string; brewery_name: string | null; style: string | null; price: number | null }[];
}
import { reverseGeocode } from "@/api/location";
import { useRoute } from "vue-router";
const route = useRoute();
const form = reactive({
  beerName: "",
  radiusKm: 5,
  sortBy: "default" as "default" | "priceAsc" | "priceDesc" | "distanceAsc",
});

const loading = ref(false);
const results = ref<BeerPubItem[]>([]);
const nearbyPubs = ref<PubNearbyItem[]>([]);
const hasSearched = ref(false);
const location = ref<{ lat: number; lng: number; address?: string } | null>(null);
const quickTags = ["IPA", "世涛", "拉格", "皮尔森", "野菌"];

const locationText = computed(() => {
  if (!location.value) return "未定位";
  if (location.value.address) return location.value.address;
  return `${location.value.lat.toFixed(2)}, ${location.value.lng.toFixed(2)}`;
});

const sortLabel = computed(() => {
  if (form.sortBy === "priceAsc") return "价格从低到高";
  if (form.sortBy === "priceDesc") return "价格从高到低";
  if (form.sortBy === "distanceAsc") return "距离从近到远";
  return "默认";
});

const groupedResults = computed(() => {
  const data = [...results.value];
  // 1. 先按原始排序（后端已按距离排序）
  // 2. 按 pub.id 分组
  const map = new Map<number, GroupedPubItem>();
  const order: number[] = [];
  for (const item of data) {
    const pid = item.pub.id;
    if (!map.has(pid)) {
      map.set(pid, {
        pub: item.pub,
        distance_km: item.distance_km ?? 0,
        beers: [],
      });
      order.push(pid);
    }
    map.get(pid)!.beers.push({
      beer_name: item.beer_name,
      brewery_name: item.brewery_name,
      style: item.style ?? null,
      price: item.price,
    });
  }
  const groups = order.map((id) => map.get(id)!);
  // 3. 按用户选择的排序方式排序
  if (form.sortBy === "priceAsc") {
    groups.sort((a, b) => {
      const minA = Math.min(...a.beers.map((b) => b.price ?? Infinity));
      const minB = Math.min(...b.beers.map((b) => b.price ?? Infinity));
      return minA - minB;
    });
  } else if (form.sortBy === "priceDesc") {
    groups.sort((a, b) => {
      const maxA = Math.max(...a.beers.map((b) => b.price ?? -1));
      const maxB = Math.max(...b.beers.map((b) => b.price ?? -1));
      return maxB - maxA;
    });
  } else if (form.sortBy === "distanceAsc") {
    groups.sort((a, b) => a.distance_km - b.distance_km);
  }
  return groups;
});

// const fetchAddress = async (
//   lat: number,
//   lng: number
// ): Promise<string | undefined> => {
//   try {
//     const response = await fetch(
//       `/api/location/reverse-geocode?lng=${lng}&lat=${lat}`
//     );

//     if (!response.ok) {
//       return undefined;
//     }

//     const data = await response.json();

//     return data.address;
//   } catch (e) {
//     return undefined;
//   }
// };
const fetchAddress = async (
  lat: number,
  lng: number
): Promise<string | undefined> => {
  try {
    const data = await reverseGeocode(lng, lat);

    return data.address;
  } catch {
    return undefined;
  }
};

const handleLocate = () => {
  if (!navigator.geolocation) {
    ElMessage.error("当前浏览器不支持定位");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = Number(pos.coords.latitude.toFixed(6));
      const lng = Number(pos.coords.longitude.toFixed(6));
      const address = await fetchAddress(lat, lng);
      location.value = { lat, lng, address };
      ElMessage.success("已获取定位");
    },
    () => {
      ElMessage.error("定位失败，请手动填写经纬度");
    }
  );
};

const handleSearch = async () => {
  if (!form.beerName) {
    ElMessage.warning("请输入酒款名称");
    return;
  }
  if (!location.value) {
    await new Promise<void>((resolve) => {
      if (!navigator.geolocation) {
        ElMessage.error("当前浏览器不支持定位");
        resolve();
        return;
      }
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          const lat = Number(pos.coords.latitude.toFixed(6));
          const lng = Number(pos.coords.longitude.toFixed(6));
          const address = await fetchAddress(lat, lng);
          location.value = { lat, lng, address };
          resolve();
        },
        () => {
          ElMessage.error("定位失败，请检查定位权限");
          resolve();
        }
      );
    });
  }
  if (!location.value) {
    return;
  }
  loading.value = true;
  hasSearched.value = true;
  try {
    const data = await searchPubsByBeerNearby({
      beer_name: form.beerName,
      lat: location.value.lat,
      lng: location.value.lng,
      radius_km: form.radiusKm,
      offset: 0,
      limit: 20,
    });
    results.value = data.items;
  } finally {
    loading.value = false;
  }
};

const applyQuickTag = (tag: string) => {
  form.beerName = tag;
  handleSearch();
};

const getCoverStyle = (coverUrl: string | null) => {
  if (!coverUrl) {
    return { backgroundImage: "linear-gradient(135deg, #EBE8E3 0%, #DCD8CF 100%)" };
  }
  return { backgroundImage: `url(${coverUrl})` };
};

const applyBeerNameFromQuery = (value: unknown) => {
  if (typeof value !== "string") return;
  const nextValue = value.trim();
  if (!nextValue) return;
  if (form.beerName === nextValue) return;
  form.beerName = nextValue;
};

const loadNearbyPubs = async () => {
  if (!location.value) return;
  try {
    const data = await fetchNearbyPubs({
      lat: location.value.lat,
      lng: location.value.lng,
      radius_km: 20,
    });
    nearbyPubs.value = data.items;
  } catch {
    // 加载失败不阻塞
  }
};

onMounted(() => {
  handleLocate();
  applyBeerNameFromQuery(route.query.beerName);
  // 延时等待定位回调后加载附近所有酒馆
  setTimeout(async () => {
    await loadNearbyPubs();
  }, 1500);
});

watch(
  () => route.query.beerName,
  (value) => {
    applyBeerNameFromQuery(value);
  }
);
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.hero-content h1 {
  margin: 12px 0 8px;
  font-size: 28px;
  color: var(--brew-text);
}

.hero-content p {
  margin: 0 0 16px;
  color: var(--brew-text-muted);
}

.hero-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(194, 168, 122, 0.15);
  color: var(--brew-accent);
  font-size: 12px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.hero-panel {
  background: var(--brew-surface-2);
  border: 1px solid var(--brew-border);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-title {
  font-weight: 600;
}

.panel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.panel-meta {
  color: var(--brew-text-muted);
  font-size: 12px;
}

.search-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.search-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 12px;
}

.search-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.search-extra {
  background: var(--brew-surface-2);
  border: 1px solid var(--brew-border);
  border-radius: 10px;
  padding: 16px;
}

.extra-title {
  font-weight: 600;
  margin-bottom: 8px;
}


.extra-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form {
  flex-wrap: wrap;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.form-grow {
  flex: 1;
  min-width: 240px;
}

.form-sort {
  margin-left: auto;
}

.result-header {
  margin: 12px 0 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.result-title {
  font-weight: 600;
}


.pub-card {
  margin-bottom: 16px;
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.pub-cover {
  height: 120px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  margin-bottom: 10px;
}

.pub-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.pub-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}

.pub-actions {
  margin-top: 10px;
}

/* ── 合并展示卡片 ── */
.grouped-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.grouped-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
}

.grouped-layout {
  display: flex;
  gap: 16px;
}

.grouped-cover {
  flex: 0 0 140px;
  height: 140px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  cursor: pointer;
}

.grouped-body {
  flex: 1;
  min-width: 0;
}

.grouped-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.grouped-name {
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
}

.grouped-name:hover {
  color: var(--brew-accent);
}

.grouped-meta {
  display: flex;
  gap: 16px;
  color: var(--brew-text-muted);
  font-size: 12px;
  margin: 6px 0 10px;
}

.beer-table {
  margin-top: 4px;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--brew-border);
}

@media (max-width: 960px) {
  .hero,
  .search-grid {
    grid-template-columns: 1fr;
  }

  .grouped-layout {
    flex-direction: column;
  }

  .grouped-cover {
    flex: 0 0 120px;
    height: 120px;
  }
}
</style>
