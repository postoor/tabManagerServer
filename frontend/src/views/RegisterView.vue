<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
          <rect width="36" height="36" rx="10" fill="#4f46e5"/>
          <path d="M10 13h16M10 18h12M10 23h8" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <span>Tab Manager</span>
      </div>
      <h1 class="auth-title">Create your account</h1>
      <p class="auth-subtitle">Start organizing your bookmarks across devices</p>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            required
            autocomplete="email"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <div class="input-wrapper">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              placeholder="At least 8 characters"
              required
              minlength="8"
              autocomplete="new-password"
            />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Confirm Password</label>
          <input
            v-model="confirmPassword"
            :type="showPassword ? 'text' : 'password'"
            class="input"
            :class="{ 'input-error': confirmPassword && password !== confirmPassword }"
            placeholder="Repeat your password"
            required
            autocomplete="new-password"
          />
          <span v-if="confirmPassword && password !== confirmPassword" class="error-msg">
            Passwords do not match
          </span>
        </div>

        <transition name="fade">
          <div v-if="authStore.error" class="alert alert-error">{{ authStore.error }}</div>
        </transition>

        <button
          type="submit"
          class="btn btn-primary btn-block"
          :disabled="authStore.loading || (confirmPassword && password !== confirmPassword)"
        >
          <span v-if="authStore.loading" class="spinner spinner-sm"></span>
          <span v-else>Create Account</span>
        </button>
      </form>

      <p class="auth-footer">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)

async function handleRegister() {
  if (password.value !== confirmPassword.value) return
  const ok = await authStore.register(email.value, password.value)
  if (ok) {
    router.push('/')
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 60%, #e0e7ff 100%);
  padding: 24px;
}

.auth-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.auth-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

.auth-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 6px;
}

.auth-subtitle {
  color: var(--color-text-2);
  margin-bottom: 28px;
  font-size: 14px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-weight: 500;
  font-size: 13px;
  color: var(--color-text-2);
}

.input-wrapper {
  position: relative;
}
.input-wrapper .input { padding-right: 40px; }

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-3);
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 4px;
  transition: color var(--transition);
}
.toggle-password:hover { color: var(--color-text-2); }

.input-error {
  border-color: var(--color-danger) !important;
}

.alert {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
}
.alert-error {
  background: var(--color-danger-light);
  color: var(--color-danger);
  border: 1px solid #fca5a5;
}

.btn-block {
  width: 100%;
  justify-content: center;
  padding: 11px;
  font-size: 14px;
  margin-top: 4px;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  color: var(--color-text-2);
  font-size: 13px;
}
.auth-footer a { font-weight: 500; }
</style>
