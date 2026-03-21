<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div class="modal-header">
        <h3 id="modal-title">Add Bookmark</h3>
        <button class="btn btn-ghost btn-sm close-btn" @click="$emit('close')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <!-- URL -->
          <div class="form-group">
            <label class="form-label">URL <span class="required">*</span></label>
            <div class="url-input-wrapper">
              <input
                v-model="form.url"
                ref="urlInputRef"
                type="url"
                class="input"
                placeholder="https://example.com"
                required
                @blur="tryFetchTitle"
              />
              <button
                v-if="form.url"
                type="button"
                class="btn btn-secondary btn-sm fetch-btn"
                @click="tryFetchTitle"
                :disabled="fetchingTitle"
              >
                <span v-if="fetchingTitle" class="spinner spinner-sm"></span>
                <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
                </svg>
                Fetch
              </button>
            </div>
          </div>

          <!-- Title (auto-fetched or manual) -->
          <div class="form-group">
            <label class="form-label">Title</label>
            <input
              v-model="form.title"
              type="text"
              class="input"
              placeholder="Page title (auto-filled from URL)"
            />
          </div>

          <!-- Custom title -->
          <div class="form-group">
            <label class="form-label">Custom Title <span class="optional">(optional)</span></label>
            <input
              v-model="form.custom_title"
              type="text"
              class="input"
              placeholder="Override display name"
            />
          </div>

          <!-- Description -->
          <div class="form-group">
            <label class="form-label">Description <span class="optional">(optional)</span></label>
            <textarea
              v-model="form.custom_description"
              class="input"
              placeholder="Add a note about this bookmark"
              rows="3"
              style="resize: vertical"
            ></textarea>
          </div>

          <transition name="fade">
            <div v-if="error" class="alert alert-error">{{ error }}</div>
          </transition>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!form.url || submitting">
              <span v-if="submitting" class="spinner spinner-sm"></span>
              <span v-else>Add Bookmark</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  collectionId: String,
})

const emit = defineEmits(['close', 'add'])

const urlInputRef = ref(null)
const fetchingTitle = ref(false)
const submitting = ref(false)
const error = ref(null)

const form = ref({
  url: '',
  title: '',
  custom_title: '',
  custom_description: '',
})

onMounted(() => {
  urlInputRef.value?.focus()
  // Listen for escape key
  window.addEventListener('keydown', handleKeydown)
})

function handleKeydown(e) {
  if (e.key === 'Escape') emit('close')
}

// Try to infer domain from URL as fallback title
async function tryFetchTitle() {
  if (!form.value.url || form.value.title) return
  fetchingTitle.value = true
  try {
    const url = new URL(form.value.url)
    // Use hostname as fallback title since fetching external URLs from browser is blocked by CORS
    form.value.title = url.hostname.replace('www.', '')
  } catch {
    // Invalid URL, ignore
  } finally {
    fetchingTitle.value = false
  }
}

async function handleSubmit() {
  if (!form.value.url?.trim()) return
  submitting.value = true
  error.value = null
  try {
    // Auto-fill title from URL if empty
    if (!form.value.title) {
      try {
        const url = new URL(form.value.url)
        form.value.title = url.hostname.replace('www.', '')
      } catch {
        form.value.title = form.value.url
      }
    }
    emit('add', {
      url: form.value.url.trim(),
      title: form.value.title.trim(),
      custom_title: form.value.custom_title.trim(),
      custom_description: form.value.custom_description.trim(),
    })
  } catch (err) {
    error.value = 'Failed to add bookmark. Please try again.'
  } finally {
    submitting.value = false
    window.removeEventListener('keydown', handleKeydown)
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
  padding: 24px;
  backdrop-filter: blur(2px);
}

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
}

.close-btn { color: var(--color-text-3); }
.close-btn:hover { color: var(--color-text); }

.modal-body {
  padding: 20px 24px 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-2);
}

.required { color: var(--color-danger); }
.optional { color: var(--color-text-3); font-weight: 400; }

.url-input-wrapper {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

.url-input-wrapper .input { flex: 1; }

.fetch-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

.alert {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  margin-bottom: 16px;
}
.alert-error {
  background: var(--color-danger-light);
  color: var(--color-danger);
  border: 1px solid #fca5a5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 4px;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border-width: 2px;
}
</style>
