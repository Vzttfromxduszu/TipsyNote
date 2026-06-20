<template>
  <el-card>
    <template #header>
      <div class="card-header">文件上传测试</div>
    </template>
    <el-upload
      drag
      :show-file-list="false"
      :before-upload="beforeUpload"
      :http-request="handleUpload"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">当前示例使用头像上传接口</div>
      </template>
    </el-upload>
  </el-card>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import type { UploadRequestOptions } from "element-plus";
import { uploadAvatar } from "@/api/user";

const beforeUpload = (file: File) => {
  const isImage = ["image/jpeg", "image/png"].includes(file.type);
  if (!isImage) {
    ElMessage.error("仅支持 JPG/PNG");
  }
  return isImage;
};

const handleUpload = async (options: UploadRequestOptions) => {
  const file = options.file as File;
  await uploadAvatar(file);
  ElMessage.success("上传成功");
};
</script>

<style scoped>
.card-header {
  font-weight: 600;
}
</style>
