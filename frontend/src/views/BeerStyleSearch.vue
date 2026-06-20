<template>
  <div class="page">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <span>风格搜索</span>
          <el-text type="info">输入风格（如 IPA），查看对应酒款与酒馆</el-text>
        </div>
      </template>
      <el-form :model="form" inline class="form" @submit.prevent>
        <el-form-item label="风格">
          <el-input v-model="form.style" placeholder="例如：IPA" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSearch">搜索</el-button>
        </el-form-item>
      </el-form>
      <el-empty v-if="!items.length" description="暂无结果" />
      <el-table v-else :data="items" style="width: 100%">
        <el-table-column prop="beer.beer_name" label="酒名" min-width="160" />
        <el-table-column prop="beer.brewery_name" label="酒厂" min-width="140" />
        <el-table-column prop="beer.style" label="风格" min-width="120" />
        <el-table-column prop="beer.price" label="价格" min-width="90" />
        <el-table-column prop="pub.pub_name" label="酒馆" min-width="160" />
        <el-table-column prop="pub.address" label="地址" min-width="220" />
        <el-table-column label="操作" min-width="90">
          <template #default="scope">
            <el-button type="primary" size="small" @click="$router.push(`/pubs/${scope.row.pub.id}`)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { searchBeersByStyle } from "@/api/beerStyle";
import type { BeerStyleItem } from "@/types/beerStyle";

const form = reactive({ style: "" });
const loading = ref(false);
const items = ref<BeerStyleItem[]>([]);

const handleSearch = async () => {
  if (!form.style) {
    ElMessage.warning("请输入风格关键词");
    return;
  }
  loading.value = true;
  try {
    const data = await searchBeersByStyle({ style: form.style, offset: 0, limit: 50 });
    items.value = data.items;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-card {
  background: #ffffff;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
