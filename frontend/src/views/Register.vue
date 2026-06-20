<template>
  <div class="register-page">
    <div class="register-shell">
      <div class="register-hero">
        <div class="hero-badge">精酿主题 · New Member</div>
        <h1>加入 TipsyNote</h1>
        <p>收藏你的第一杯精酿，解锁附近酒馆。</p>
      </div>
      <el-card class="register-card">
        <template #header>
          <div class="register-title">用户注册</div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="密码" prop="secret">
            <el-input v-model="form.secret" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
          <el-form-item label="验证码" prop="code">
            <div class="code-row">
              <el-input v-model="form.code" placeholder="请输入验证码" maxlength="6" />
              <el-button
                class="send-code-button"
                :disabled="codeCountdown > 0 || !phoneValid"
                :loading="sendingCode"
                @click="handleSendCode"
              >
                {{ codeCountdown > 0 ? `${codeCountdown}s` : "发送验证码" }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="可选" />
          </el-form-item>
          <el-button type="primary" class="register-button" :loading="loading" @click="handleSubmit">
            注册
          </el-button>
          <el-button class="login-button" @click="handleGoLogin">返回登录</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { registerUser, sendCode } from "@/api/user";

const router = useRouter();
const loading = ref(false);
const sendingCode = ref(false);
const codeCountdown = ref(0);
let countdownTimer: ReturnType<typeof setInterval> | null = null;

const formRef = ref<FormInstance>();
const form = reactive({
  phone: "",
  secret: "",
  code: "",
  nickname: "",
});

const phoneValid = computed(() => /^1\d{10}$/.test(form.phone));

const rules: FormRules = {
  phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    { pattern: /^1\d{10}$/, message: "手机号格式不正确", trigger: "blur" },
  ],
  secret: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 位", trigger: "blur" },
  ],
  code: [
    { required: true, message: "请输入验证码", trigger: "blur" },
    { len: 6, message: "验证码为 6 位数字", trigger: "blur" },
  ],
};

const handleSendCode = async () => {
  if (!phoneValid.value) {
    ElMessage.warning("请先输入正确的手机号");
    return;
  }
  sendingCode.value = true;
  try {
    await sendCode({ phone: form.phone });
    ElMessage.success("验证码已发送");
    codeCountdown.value = 60;
    countdownTimer = setInterval(() => {
      codeCountdown.value--;
      if (codeCountdown.value <= 0) {
        if (countdownTimer) {
          clearInterval(countdownTimer);
          countdownTimer = null;
        }
      }
    }, 1000);
  } catch (error: any) {
    const message = error?.response?.data?.detail || "发送失败，请稍后重试";
    ElMessage.error(message);
  } finally {
    sendingCode.value = false;
  }
};

const handleSubmit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;
  loading.value = true;
  try {
    await registerUser({
      phone: form.phone,
      secret: form.secret,
      code: form.code,
      nickname: form.nickname || undefined,
    });
    ElMessage.success("注册成功，请登录");
    router.replace("/login");
  } catch (error: any) {
    const message = error?.response?.data?.detail || "注册失败，请稍后重试";
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};

const handleGoLogin = () => {
  router.push("/login");
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top, #FFFFFF 0%, #F8F7F4 60%);
  padding: 24px;
}

.register-shell {
  width: min(900px, 100%);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid var(--brew-border);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--brew-shadow);
}

.register-hero {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px 8px;
}

.register-hero h1 {
  margin: 0;
  font-size: 26px;
  color: var(--brew-text);
}

.register-hero p {
  margin: 0;
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

.register-card {
  width: 100%;
  background: var(--brew-surface);
  border: 1px solid var(--brew-border);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.register-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--brew-accent);
}

.code-row {
  display: flex;
  gap: 8px;
}

.send-code-button {
  flex-shrink: 0;
  min-width: 110px;
}

.register-button,
.login-button {
  width: 100%;
}

.login-button {
  margin-top: 10px;
  margin-left: 0 !important;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--brew-border);
}

@media (max-width: 900px) {
  .register-shell {
    grid-template-columns: 1fr;
  }
}
</style>
