<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户信息</span>
          <el-button type="primary" plain @click="refresh">刷新</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ profile?.id }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ profile?.phone }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ profile?.nickname || "-" }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ roleText }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ profile?.status }}</el-descriptions-item>
        <el-descriptions-item label="头像">
          <el-avatar :size="56" :src="profile?.avatar_url || undefined">{{ profile?.nickname?.[0] }}</el-avatar>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card v-if="managedPubs.length">
      <template #header>
        <div class="card-header">
          <span>管理的酒馆（{{ managedPubs.length }} 家）</span>
        </div>
      </template>
      <el-table :data="managedPubs" size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="pub_name" label="名称" min-width="140" />
        <el-table-column prop="address" label="地址" min-width="160">
          <template #default="{ row }">{{ row.address || "-" }}</template>
        </el-table-column>
        <el-table-column prop="contact_phone" label="电话" width="120">
          <template #default="{ row }">{{ row.contact_phone || "-" }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? "营业" : "歇业" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑酒馆弹窗 -->
    <el-dialog v-model="editVisible" title="编辑酒馆" width="520px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="editForm.pub_name" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editForm.address" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="editForm.contact_phone" />
        </el-form-item>
        <el-form-item label="营业时间">
          <el-input v-model="editForm.business_hours" placeholder="例如：18:00-02:00" />
        </el-form-item>
        <el-form-item label="封面">
          <div class="cover-upload-row">
            <el-upload
              class="cover-upload"
              :show-file-list="false"
              :before-upload="beforeCoverUpload"
              :http-request="handleCoverUpload"
            >
              <el-button size="small">上传封面</el-button>
            </el-upload>
            <span v-if="editForm.cover_url" class="cover-hint">已上传</span>
            <span v-else class="cover-hint">未上传</span>
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="editForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="营业"
            inactive-text="歇业"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEditSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>上传头像</span>
        </div>
      </template>
      <el-upload
        class="upload"
        :show-file-list="false"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
      >
        <el-button type="primary">选择图片</el-button>
        <template #tip>
          <div class="el-upload__tip">仅支持 JPG/PNG，大小不超过 2MB</div>
        </template>
      </el-upload>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import type { UploadRequestOptions, FormInstance } from "element-plus";
import { useUserStore } from "@/stores/user";
import { uploadAvatar } from "@/api/user";
import { updatePub, uploadPubCover } from "@/api/pubs";
import type { PubInfo } from "@/types/pubs";

const store = useUserStore();
const profile = computed(() => store.profile);
const managedPubs = computed(() => profile.value?.managed_pubs ?? []);

// ── 编辑酒馆弹窗 ──
const editVisible = ref(false);
const editLoading = ref(false);
const editFormRef = ref<FormInstance>();
const editingPubId = ref(0);
const editForm = reactive({
  pub_name: "",
  address: "",
  contact_phone: "",
  business_hours: "",
  cover_url: "",
  status: 1 as number,
});

const openEditDialog = (pub: PubInfo) => {
  editingPubId.value = pub.id;
  editForm.pub_name = pub.pub_name;
  editForm.address = pub.address ?? "";
  editForm.contact_phone = pub.contact_phone ?? "";
  editForm.business_hours = pub.business_hours ?? "";
  editForm.cover_url = pub.cover_url ?? "";
  editForm.status = pub.status;
  editVisible.value = true;
};

// ── 封面上传 ──
const beforeCoverUpload = (file: File) => {
  const isImage = ["image/jpeg", "image/png"].includes(file.type);
  if (!isImage) {
    ElMessage.error("仅支持 JPG/PNG");
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    ElMessage.error("图片需小于 2MB");
  }
  return isImage && isLt2M;
};

const handleCoverUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File;
  try {
    const data = await uploadPubCover(editingPubId.value, file);
    editForm.cover_url = data.cover_url;
    ElMessage.success("封面上传成功");
  } catch {
    ElMessage.error("封面上传失败");
  }
};

const handleEditSubmit = async () => {
  editLoading.value = true;
  try {
    await updatePub(editingPubId.value, { ...editForm });
    ElMessage.success("酒馆信息已更新");
    editVisible.value = false;
    await store.fetchProfile();
  } catch {
    ElMessage.error("更新失败，请重试");
  } finally {
    editLoading.value = false;
  }
};

const roleText = computed(() => {
  const role = profile.value?.role;
  if (role === 2) return "管理员";
  if (role === 1) return "商家";
  return "普通用户";
});

const refresh = async () => {
  await store.fetchProfile();
  ElMessage.success("已刷新");
};

const beforeUpload = (file: File) => {
  const isImage = ["image/jpeg", "image/png"].includes(file.type);
  if (!isImage) {
    ElMessage.error("仅支持 JPG/PNG");
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    ElMessage.error("图片需小于 2MB");
  }
  return isImage && isLt2M;
};

const handleUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File;
  const data = await uploadAvatar(file);
  await store.fetchProfile();
  ElMessage.success("上传成功");
  if (data.avatar_url) {
    // 可在此处理头像地址展示
  }
};
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
