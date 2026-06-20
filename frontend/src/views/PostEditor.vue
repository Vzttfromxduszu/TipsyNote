<template>
  <div class="page">
    <div class="back-row">
      <el-button text @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
    </div>

    <el-card class="editor-card">
      <template #header>
        <span class="editor-title">{{ isEdit ? '编辑帖子' : '发布帖子' }}</span>
      </template>

      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="给帖子起个标题吧…"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="分享你的品酒体验、酒馆见闻…"
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <div class="form-actions">
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '发布' }}
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { ArrowLeft } from "@element-plus/icons-vue";
import { createPost, updatePost, fetchPostDetail } from "@/api/posts";

const route = useRoute();
const router = useRouter();

const isEdit = ref(false);
const postId = ref<number | null>(null);
const submitting = ref(false);
const formRef = ref<FormInstance>();

const form = reactive({
  title: "",
  content: "",
});

const rules: FormRules = {
  title: [
    { required: true, message: "请输入标题", trigger: "blur" },
    { min: 2, max: 100, message: "标题 2-100 字", trigger: "blur" },
  ],
  content: [
    { required: true, message: "请输入内容", trigger: "blur" },
    { min: 10, message: "内容至少 10 字", trigger: "blur" },
  ],
};

const loadPost = async (id: number) => {
  try {
    const data = await fetchPostDetail(id);
    form.title = data.title;
    form.content = data.content;
  } catch {
    ElMessage.error("加载帖子失败");
    router.replace("/community");
  }
};

const handleSubmit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;
  submitting.value = true;
  try {
    if (isEdit.value && postId.value) {
      await updatePost(postId.value, {
        title: form.title,
        content: form.content,
      });
      ElMessage.success("修改成功");
      router.replace(`/community/${postId.value}`);
    } else {
      const data = await createPost({
        title: form.title,
        content: form.content,
      });
      ElMessage.success("发布成功");
      router.replace(`/community/${data.id}`);
    }
  } catch {
    ElMessage.error("操作失败，请重试");
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  const id = Number(route.params.id);
  if (route.name === "postEdit" && id) {
    isEdit.value = true;
    postId.value = id;
    loadPost(id);
  }
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.back-row {
  margin-bottom: -8px;
}

.editor-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 12px;
}

.editor-title {
  font-weight: 600;
  color: var(--brew-accent);
  font-size: 18px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--brew-border);
}
</style>
