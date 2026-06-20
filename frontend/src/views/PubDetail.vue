<template>
  <div class="page">
    <el-card v-loading="loading" class="pub-card">
      <div class="pub-hero">
        <div class="pub-cover" :style="getCoverStyle(pub?.cover_url || null)"></div>
        <div class="pub-main">
          <div class="title">{{ pub?.pub_name || "酒馆详情" }}</div>
          <el-text type="info">{{ pub?.address || "暂无地址" }}</el-text>
          <div class="pub-meta">
            <el-tag v-if="pub" :type="pub.status === 1 ? 'success' : 'info'">
              {{ pub.status === 1 ? "营业中" : "暂停营业" }}
            </el-tag>
            <el-tag effect="plain">电话：{{ pub?.contact_phone || "-" }}</el-tag>
            <el-tag effect="plain">营业：{{ pub?.business_hours || "-" }}</el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="route-card" v-loading="routeLoading">
      <template #header>
        <div class="header">
          <span>到店路径</span>
        </div>
      </template>
      <div class="route-box">
        <el-text v-if="routeText">{{ routeText }}</el-text>
        <el-text v-else type="info">请允许定位以获取到店时间</el-text>
      </div>
    </el-card>

    <el-card class="beer-card" v-loading="beerLoading">
      <template #header>
        <div class="header">
          <span>当前酒单</span>
          <el-text type="info">共 {{ beers.length }} 款</el-text>
        </div>
      </template>
      <el-table :data="beers" style="width: 100%">
        <el-table-column prop="beer_name" label="酒名" min-width="160" />
        <el-table-column prop="brewery_name" label="酒厂" min-width="140" />
        <el-table-column prop="style" label="风格" min-width="120" />
        <el-table-column prop="abv" label="酒精度" min-width="100" />
        <el-table-column prop="volume_ml" label="容量(ml)" min-width="110" />
        <el-table-column prop="price" label="价格" min-width="100" />
        <el-table-column label="状态" min-width="90">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
              {{ scope.row.status === 1 ? "在售" : "售罄" }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!beers.length" description="暂无酒单" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { fetchPubDetail, fetchPubRoute } from "@/api/pubs";
import { fetchBeersByPub } from "@/api/beers";
import type { PubInfo } from "@/types/pubs";
import type { BeerItem } from "@/types/beers";

const route = useRoute();
const pub = ref<PubInfo | null>(null);
const beers = ref<BeerItem[]>([]);
const loading = ref(false);
const beerLoading = ref(false);
const routeLoading = ref(false);
const routeInfo = ref<{ mode: "walking" | "driving"; distance_m: number; duration_min: number } | null>(null);

const routeText = computed(() => {
  if (!routeInfo.value) return "";
  const distanceKm = routeInfo.value.distance_m / 1000;
  const minutes = Math.ceil(routeInfo.value.duration_min);
  const modeText = routeInfo.value.mode === "walking" ? "步行" : "驾车";
  return `${modeText}${distanceKm.toFixed(1)}公里，需要${minutes}分钟`;
});

const getCoverStyle = (coverUrl: string | null) => {
  if (!coverUrl) {
    return { backgroundImage: "linear-gradient(135deg, #EBE8E3 0%, #DCD8CF 100%)" };
  }
  return { backgroundImage: `url(${coverUrl})` };
};


const loadPub = async () => {
  const id = Number(route.params.id);
  if (!id) {
    ElMessage.error("酒馆ID无效");
    return;
  }
  loading.value = true;
  try {
    pub.value = await fetchPubDetail(id);
  } finally {
    loading.value = false;
  }
};

const loadBeers = async () => {
  const id = Number(route.params.id);
  if (!id) {
    return;
  }
  beerLoading.value = true;
  try {
    const data = await fetchBeersByPub(id);
    beers.value = data.items;
  } finally {
    beerLoading.value = false;
  }
};

const loadRoute = async () => {
  const id = Number(route.params.id);
  if (!id) return;
  if (!navigator.geolocation) {
    return;
  }
  routeLoading.value = true;
  try {
    const position = await new Promise<GeolocationPosition>((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject);
    });
    const data = await fetchPubRoute(id, position.coords.longitude, position.coords.latitude);
    routeInfo.value = {
      mode: data.mode,
      distance_m: data.distance_m,
      duration_min: data.duration_min,
    };
  } catch {
    // 保持静默提示
  } finally {
    routeLoading.value = false;
  }
};

onMounted(async () => {
  await loadPub();
  await loadBeers();
  await loadRoute();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pub-card,
.route-card,
.beer-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 600;
  font-size: 18px;
  color: var(--brew-accent);
}

.pub-hero {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
}

.pub-cover {
  height: 160px;
  border-radius: 12px;
  background-size: cover;
  background-position: center;
}

.pub-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pub-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.route-box {
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--brew-surface-2);
  border: 1px dashed var(--brew-border);
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--brew-border);
}

@media (max-width: 900px) {
  .pub-hero {
    grid-template-columns: 1fr;
  }
}
</style>
