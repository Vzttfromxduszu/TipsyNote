<template>
  <div class="my-pubs-page">
    <div class="page-header">
      <h1 class="page-title">我的酒馆</h1>
      <el-tag v-if="isAdmin" type="danger" effect="dark">管理员视图</el-tag>
      <el-tag v-else type="warning" effect="dark">商家视图</el-tag>
    </div>

    <!-- 加载中 -->
    <el-skeleton v-if="loading" :rows="5" animated />

    <!-- 无酒馆提示 -->
    <el-empty v-else-if="pubs.length === 0" description="暂无酒馆数据" />

    <!-- 酒馆列表 -->
    <div v-else class="pub-list">
      <div v-for="pub in pubs" :key="pub.id" class="pub-card">
        <div class="pub-header" @click="toggleExpand(pub.id)">
          <div class="pub-info">
            <span class="pub-name">{{ pub.pub_name }}</span>
            <span v-if="pub.address" class="pub-addr">{{ pub.address }}</span>
          </div>
          <el-icon :class="{ expanded: expandedPub === pub.id }">
            <ArrowDown />
          </el-icon>
        </div>

        <!-- 展开后的酒单区域 -->
        <div v-if="expandedPub === pub.id" class="pub-beers">
          <div class="beer-toolbar">
            <span class="beer-title">🍺 酒单</span>
            <el-button type="primary" size="small" @click="openBeerDialog(pub.id)">
              + 添加酒款
            </el-button>
          </div>

          <el-table :data="beerMap[pub.id] || []" v-loading="beerLoadingMap[pub.id]" stripe size="small">
            <el-table-column prop="beer_name" label="酒款名称" min-width="140" />
            <el-table-column prop="brewery_name" label="酒厂" min-width="120" />
            <el-table-column prop="style" label="风格" width="80" />
            <el-table-column prop="abv" label="ABV(%)" width="80">
              <template #default="{ row }">{{ row.abv ?? '-' }}</template>
            </el-table-column>
            <el-table-column prop="volume_ml" label="容量(ml)" width="90">
              <template #default="{ row }">{{ row.volume_ml ?? '-' }}</template>
            </el-table-column>
            <el-table-column prop="price" label="价格(¥)" width="90">
              <template #default="{ row }">{{ row.price != null ? `¥${row.price}` : '-' }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="70">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
                  {{ row.status === 1 ? '在售' : '停售' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openBeerDialog(pub.id, row)">
                  编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDeleteBeer(pub.id, row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 酒款编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingBeer ? '编辑酒款' : '添加酒款'"
      width="480px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="beerForm"
        label-width="80px"
        :rules="beerRules"
      >
        <el-form-item label="酒款名称" prop="beer_name">
          <el-input v-model="beerForm.beer_name" placeholder="例：IPA" />
        </el-form-item>
        <el-form-item label="酒厂" prop="brewery_name">
          <el-input v-model="beerForm.brewery_name" placeholder="例：京A精酿" />
        </el-form-item>
        <el-form-item label="风格" prop="style">
          <el-input v-model="beerForm.style" placeholder="可选" />
        </el-form-item>
        <el-form-item label="ABV(%)">
          <el-input-number v-model="beerForm.abv" :min="0" :max="67.5" :precision="1" placeholder="可选" style="width:100%" />
        </el-form-item>
        <el-form-item label="容量(ml)">
          <el-input-number v-model="beerForm.volume_ml" :min="0" :step="10" placeholder="可选" style="width:100%" />
        </el-form-item>
        <el-form-item label="价格(¥)">
          <el-input-number v-model="beerForm.price" :min="0" :precision="0" placeholder="可选" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="beerForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="在售"
            inactive-text="停售"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitBeer">
          {{ editingBeer ? '保存修改' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { BeerItem } from '@/types/beer'
import type { PubInfo } from '@/types/pubs'
import { fetchBeersByPub, createBeer, updateBeer, deleteBeer } from '@/api/beer'
import { fetchAllPubs } from '@/api/pubs'

const store = useUserStore()
const isAdmin = computed(() => store.profile?.role === 2)

const loading = ref(false)
const pubs = ref<PubInfo[]>([])
const expandedPub = ref<number | null>(null)

/** 酒单缓存：pub_id → beers[] */
const beerMap = reactive<Record<number, BeerItem[]>>({})
const beerLoadingMap = reactive<Record<number, boolean>>({})

/** 加载酒馆列表 */
onMounted(async () => {
  loading.value = true
  try {
    if (isAdmin.value) {
      // 管理员：拉取全部酒馆
      const res = await fetchAllPubs()
      pubs.value = res.items
    } else {
      // 商家：使用个人资料中的 managed_pubs
      if (store.profile?.managed_pubs) {
        pubs.value = store.profile.managed_pubs
      }
    }
  } finally {
    loading.value = false
  }
})

/** 展开/折叠某个酒馆，同时加载酒单 */
function toggleExpand(pubId: number) {
  if (expandedPub.value === pubId) {
    expandedPub.value = null
    return
  }
  expandedPub.value = pubId
  if (!beerMap[pubId]) {
    loadBeers(pubId)
  }
}

async function loadBeers(pubId: number) {
  beerLoadingMap[pubId] = true
  try {
    const res = await fetchBeersByPub(pubId)
    beerMap[pubId] = res.items
  } finally {
    beerLoadingMap[pubId] = false
  }
}

// ─── 酒款弹窗 ───

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const currentPubId = ref(0)
const editingBeer = ref<BeerItem | null>(null)

const beerForm = reactive({
  beer_name: '',
  brewery_name: '',
  style: '',
  abv: undefined as number | undefined,
  volume_ml: undefined as number | undefined,
  price: undefined as number | undefined,
  status: 1 as 0 | 1,
})

const beerRules: FormRules = {
  beer_name: [{ required: true, message: '请输入酒款名称', trigger: 'blur' }],
  brewery_name: [{ required: true, message: '请输入酒厂名称', trigger: 'blur' }],
}

function resetBeerForm() {
  beerForm.beer_name = ''
  beerForm.brewery_name = ''
  beerForm.style = ''
  beerForm.abv = undefined
  beerForm.volume_ml = undefined
  beerForm.price = undefined
  beerForm.status = 1
}

function openBeerDialog(pubId: number, beer?: BeerItem) {
  currentPubId.value = pubId
  editingBeer.value = beer || null
  if (beer) {
    beerForm.beer_name = beer.beer_name
    beerForm.brewery_name = beer.brewery_name
    beerForm.style = beer.style || ''
    beerForm.abv = beer.abv ?? undefined
    beerForm.volume_ml = beer.volume_ml ?? undefined
    beerForm.price = beer.price ?? undefined
    beerForm.status = beer.status as 0 | 1
  } else {
    resetBeerForm()
  }
  dialogVisible.value = true
}

async function handleSubmitBeer() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      pub_id: currentPubId.value,
      beer_name: beerForm.beer_name.trim(),
      brewery_name: beerForm.brewery_name.trim(),
      style: beerForm.style.trim() || undefined,
      abv: beerForm.abv,
      volume_ml: beerForm.volume_ml,
      price: beerForm.price,
      status: beerForm.status,
    }

    if (editingBeer.value) {
      // 更新：pub_id 不可修改
      const { pub_id, ...updatePayload } = payload
      await updateBeer(editingBeer.value.id, updatePayload)
      ElMessage.success('酒款已更新')
    } else {
      await createBeer(payload)
      ElMessage.success('已添加酒款')
    }

    dialogVisible.value = false
    loadBeers(currentPubId.value)
  } finally {
    submitting.value = false
  }
}

async function handleDeleteBeer(pubId: number, beerId: number) {
  try {
    await ElMessageBox.confirm('确定删除该酒款？', '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteBeer(beerId)
  ElMessage.success('已删除')
  loadBeers(pubId)
}
</script>

<style scoped>
.my-pubs-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--brew-text);
  margin: 0;
}

/* ── 酒馆卡片 ── */
.pub-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pub-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  overflow: hidden;
}

.pub-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  transition: background .2s;
}
.pub-header:hover {
  background: var(--brew-bg);
}

.pub-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.pub-name {
  font-weight: 600;
  font-size: 16px;
  color: var(--brew-text);
}
.pub-addr {
  font-size: 13px;
  color: var(--brew-text-muted);
}

.pub-header .el-icon {
  transition: transform .25s;
  color: var(--brew-text-muted);
}
.pub-header .el-icon.expanded {
  transform: rotate(180deg);
}

/* ── 酒单 ── */
.pub-beers {
  padding: 0 20px 20px;
  border-top: 1px solid var(--brew-border);
}

.beer-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}
.beer-title {
  font-weight: 600;
  color: var(--brew-text);
}
</style>
