<template>
  <div class="merchant-auth-page">
    <div class="page-header">
      <h1 class="page-title">商家认证</h1>
    </div>
    <el-card class="placeholder-card">
      <el-empty description="商家认证功能即将上线，敬请期待" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.merchant-auth-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--brew-text);
  margin: 0;
}

.placeholder-card {
  border-radius: 12px;
}
</style>
