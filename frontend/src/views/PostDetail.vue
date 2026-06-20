<template>
  <div class="page">
    <!-- 返回按钮 -->
    <div class="back-row">
      <el-button text @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回社区
      </el-button>
    </div>

    <!-- 帖子主体 -->
    <el-card v-if="post" class="post-card" v-loading="pageLoading">
      <div class="post-header">
        <div class="post-author">
          <el-avatar :size="44" :src="post.user_avatar || undefined">
            {{ (post.user_nickname || '用')[0] }}
          </el-avatar>
          <div class="author-info">
            <span class="author-name">{{ post.user_nickname || '匿名用户' }}</span>
            <span class="post-time">{{ formatTime(post.created_at) }}</span>
          </div>
        </div>
        <div v-if="isOwner" class="owner-actions">
          <el-button text size="small" @click="goEdit">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <el-popconfirm title="确定删除该帖子吗？" @confirm="handleDelete">
            <template #reference>
              <el-button text size="small" type="danger">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-body">{{ post.content }}</div>

      <div class="post-actions">
        <el-button
          :type="post.liked ? 'primary' : 'default'"
          :icon="post.liked ? StarFilled : Star"
          @click="handleLike"
          :loading="likeLoading"
        >
          {{ post.liked ? '已赞' : '点赞' }} {{ post.like_count || 0 }}
        </el-button>
        <el-button text>
          <el-icon><ChatDotRound /></el-icon> {{ comments.length }} 条评论
        </el-button>
      </div>
    </el-card>

    <!-- 评论区域 -->
    <el-card v-if="post" class="comments-card">
      <template #header>
        <span class="comments-title">评论 ({{ comments.length }})</span>
      </template>

      <!-- 发表评论 -->
      <div class="comment-input-row">
        <el-input
          v-model="commentForm.content"
          type="textarea"
          :rows="3"
          placeholder="写下你的想法…"
          maxlength="500"
          show-word-limit
        />
        <el-button
          type="primary"
          :loading="commentLoading"
          :disabled="!commentForm.content.trim()"
          @click="handleComment"
          class="comment-submit"
        >
          发表评论
        </el-button>
      </div>

      <el-divider v-if="comments.length" />

      <!-- 评论列表 -->
      <div v-if="comments.length" class="comment-list">
        <div v-for="c in comments" :key="c.id" class="comment-item">
          <div class="comment-meta">
            <div class="comment-user">
              <el-avatar :size="28" :src="c.user_avatar || undefined">
                {{ (c.user_nickname || '用')[0] }}
              </el-avatar>
              <span>{{ c.user_nickname || '匿名用户' }}</span>
            </div>
            <span class="comment-time">{{ formatTime(c.created_at) }}</span>
          </div>
          <p class="comment-content">{{ c.content }}</p>
        </div>
      </div>
      <el-empty v-else description="暂无评论，来说两句吧" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  ArrowLeft, Edit, Delete, Star, StarFilled, ChatDotRound,
} from "@element-plus/icons-vue";
import { useUserStore } from "@/stores/user";
import {
  fetchPostDetail, deletePost, toggleLike,
  fetchComments, createComment,
} from "@/api/posts";
import type { PostItem, CommentItem } from "@/types/posts";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const post = ref<PostItem | null>(null);
const comments = ref<CommentItem[]>([]);
const pageLoading = ref(false);
const likeLoading = ref(false);
const commentLoading = ref(false);

const commentForm = reactive({ content: "" });

const isOwner = ref(false);

const loadPost = async () => {
  const id = Number(route.params.id);
  if (!id) return;
  pageLoading.value = true;
  try {
    const data = await fetchPostDetail(id);
    post.value = data;
    isOwner.value = userStore.profile?.id === data.user_id;
  } catch {
    ElMessage.error("加载帖子失败");
  } finally {
    pageLoading.value = false;
  }
};

const loadComments = async () => {
  const id = Number(route.params.id);
  if (!id) return;
  try {
    const data = await fetchComments(id);
    comments.value = data.items;
  } catch {
    // silent
  }
};

const handleLike = async () => {
  if (!post.value || likeLoading.value) return;
  likeLoading.value = true;
  try {
    const result = await toggleLike(post.value.id);
    post.value.liked = result.liked;
    post.value.like_count = result.like_count;
  } catch {
    ElMessage.error("操作失败");
  } finally {
    likeLoading.value = false;
  }
};

const handleComment = async () => {
  if (!commentForm.content.trim() || !post.value) return;
  commentLoading.value = true;
  try {
    await createComment(post.value.id, { content: commentForm.content.trim() });
    commentForm.content = "";
    ElMessage.success("评论成功");
    await loadComments();
    if (post.value) post.value.comment_count += 1;
  } catch {
    ElMessage.error("评论失败");
  } finally {
    commentLoading.value = false;
  }
};

const goEdit = () => {
  router.push(`/community/${post.value!.id}/edit`);
};

const handleDelete = async () => {
  if (!post.value) return;
  try {
    await deletePost(post.value.id);
    ElMessage.success("已删除");
    router.replace("/community");
  } catch {
    ElMessage.error("删除失败");
  }
};

const formatTime = (iso: string) => {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "刚刚";
  if (mins < 60) return `${mins} 分钟前`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} 小时前`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} 天前`;
  return d.toLocaleDateString("zh-CN");
};

onMounted(async () => {
  await loadPost();
  await loadComments();
});
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.back-row {
  margin-bottom: -8px;
}

.post-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 12px;
}

.post-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-weight: 600;
  color: var(--brew-text);
  font-size: 15px;
}

.post-time {
  font-size: 12px;
  color: var(--brew-text-muted);
}

.owner-actions {
  display: flex;
  gap: 4px;
}

.post-title {
  margin: 0 0 16px;
  font-size: 22px;
  color: var(--brew-text);
}

.post-body {
  color: var(--brew-text);
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.post-actions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--brew-border);
  display: flex;
  gap: 12px;
  align-items: center;
}

.comments-card {
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  border-radius: 12px;
}

.comments-title {
  font-weight: 600;
  color: var(--brew-text);
}

.comment-input-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-submit {
  align-self: flex-end;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-item {
  padding: 12px;
  background: var(--brew-surface-2);
  border-radius: 8px;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 13px;
  color: var(--brew-accent);
}

.comment-time {
  font-size: 12px;
  color: var(--brew-text-muted);
}

.comment-content {
  margin: 0;
  font-size: 14px;
  color: var(--brew-text);
  line-height: 1.6;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--brew-border);
}
</style>
