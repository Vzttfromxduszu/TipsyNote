<template>
  <div class="login-page">
    <div class="login-shell">
      <div class="login-hero">
        <div class="hero-badge">精酿主题 · Member</div>
        <h1>欢迎回到 TipsyNote</h1>
        <p>记录每一次微醺，发现附近好喝的那一杯。</p>
        <ul>
          <li>精准定位附近酒馆</li>
          <li>按风格探索精酿口味</li>
          <li>收藏你的常去酒馆</li>
        </ul>
      </div>
      <el-card class="login-card">
        <template #header>
          <div class="login-title">用户登录</div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="密码" prop="secret">
            <el-input v-model="form.secret" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
          <el-button type="primary" class="login-button" :loading="store.loading" @click="handleSubmit">
            登录
          </el-button>
          <el-button class="register-button" @click="handleRegister">注册</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const route = useRoute();
const store = useUserStore();

const formRef = ref<FormInstance>();
const form = reactive({
  phone: "",
  secret: "",
});

const rules: FormRules = {
  phone: [{ required: true, message: "请输入手机号", trigger: "blur" }],
  secret: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const handleSubmit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;
  try {
    await store.login(form);
    ElMessage.success("登录成功");
    const redirect = (route.query.redirect as string) || "/community";
    router.replace(redirect);
  } catch {
    // 错误已由拦截器提示
  }
};

const handleRegister = () => {
  router.push("/register");
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top, #FFFFFF 0%, #F8F7F4 60%);
  padding: 24px;
}

.login-shell {
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 24px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid var(--brew-border);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--brew-shadow);
}

.login-hero {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px 8px;
}

.login-hero h1 {
  margin: 0;
  font-size: 28px;
  color: var(--brew-text);
}

.login-hero p {
  margin: 0;
  color: var(--brew-text-muted);
}

.login-hero ul {
  margin: 8px 0 0;
  padding-left: 18px;
  color: var(--brew-text-muted);
}

.hero-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(194, 168, 122, 0.15);
  color: var(--brew-accent);
  font-size: 12px;
  align-self: flex-start;
}

.login-card {
  width: 100%;
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.login-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--brew-accent);
}

.login-button {
  width: 100%;
}

.register-button {
  width: 100%;
  margin-top: 10px;
  margin-left: 0 !important;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--brew-border);
}

@media (max-width: 900px) {
  .login-shell {
    grid-template-columns: 1fr;
  }
}
</style>
