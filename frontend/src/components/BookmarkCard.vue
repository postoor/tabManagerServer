<template>
  <div
    class="bookmark-card"
    :data-bookmark-id="bookmark.id"
    :class="{ editing: isEditing }"
  >
    <!-- View mode -->
    <template v-if="!isEditing">
      <div class="card-favicon">
        <img
          v-if="faviconUrl"
          :src="faviconUrl"
          :alt="displayTitle"
          @error="faviconError = true"
          width="16"
          height="16"
        />
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
          <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
        </svg>
      </div>

      <div class="card-content" @click="openUrl">
        <div class="card-title">{{ displayTitle }}</div>
        <div class="card-url">{{ displayUrl }}</div>
        <div v-if="bookmark.custom_description" class="card-desc">{{ bookmark.custom_description }}</div>
      </div>

      <div class="card-actions">
        <button class="card-btn" @click.stop="startEdit" title="Edit">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="card-btn danger" @click.stop="$emit('delete', bookmark.id)" title="Delete">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </template>

    <!-- Edit mode -->
    <template v-else>
      <div class="edit-form">
        <input v-model="editData.title" class="input input-sm" placeholder="Title" />
        <input v-model="editData.url" class="input input-sm" placeholder="URL" type="url" />
        <input v-model="editData.custom_title" class="input input-sm" placeholder="Custom title (optional)" />
        <textarea
          v-model="editData.custom_description"
          class="input input-sm textarea-sm"
          placeholder="Description (optional)"
          rows="2"
        ></textarea>
        <div class="edit-actions">
          <button class="btn btn-primary btn-sm" @click="saveEdit">Save</button>
          <button class="btn btn-secondary btn-sm" @click="isEditing = false">Cancel</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  bookmark: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['delete', 'update'])

const isEditing = ref(false)
const faviconError = ref(false)
const editData = ref({})

const faviconUrl = computed(() => {
  if (faviconError.value) return null
  if (props.bookmark.favicon_url) return props.bookmark.favicon_url
  try {
    const url = new URL(props.bookmark.url)
    return `https://www.google.com/s2/favicons?domain=${url.hostname}&sz=32`
  } catch {
    return null
  }
})

const displayTitle = computed(() =>
  props.bookmark.custom_title || props.bookmark.title || props.bookmark.url
)

const displayUrl = computed(() => {
  try {
    const url = new URL(props.bookmark.url)
    return url.hostname + (url.pathname !== '/' ? url.pathname : '')
  } catch {
    return props.bookmark.url
  }
})

function openUrl() {
  window.open(props.bookmark.url, '_blank', 'noopener,noreferrer')
}

function startEdit() {
  editData.value = {
    title: props.bookmark.title,
    url: props.bookmark.url,
    custom_title: props.bookmark.custom_title || '',
    custom_description: props.bookmark.custom_description || '',
  }
  isEditing.value = true
}

function saveEdit() {
  if (!editData.value.url?.trim()) return
  emit('update', {
    title: editData.value.title,
    url: editData.value.url,
    custom_title: editData.value.custom_title,
    custom_description: editData.value.custom_description,
  })
  isEditing.value = false
}
</script>

<style scoped>
.bookmark-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 9px 10px;
  border-radius: var(--radius-sm);
  transition: background var(--transition);
  cursor: grab;
  border: 1px solid transparent;
}

.bookmark-card:hover {
  background: var(--color-surface-3);
  border-color: var(--color-border);
}

.bookmark-card:active { cursor: grabbing; }

.bookmark-card.editing {
  background: var(--color-surface-3);
  border-color: var(--color-primary);
  border-radius: var(--radius-md);
  cursor: default;
}

.card-favicon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  color: var(--color-text-3);
}

.card-favicon img {
  border-radius: 3px;
  object-fit: contain;
}

.card-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-url {
  font-size: 11px;
  color: var(--color-text-3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 2px;
}

.card-desc {
  font-size: 11px;
  color: var(--color-text-2);
  margin-top: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity var(--transition);
  flex-shrink: 0;
}

.bookmark-card:hover .card-actions {
  opacity: 1;
}

.card-btn {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: var(--color-text-3);
  transition: all var(--transition);
}

.card-btn:hover {
  background: var(--color-border);
  color: var(--color-text);
}

.card-btn.danger:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

/* Edit form */
.edit-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}

.input-sm {
  padding: 6px 10px;
  font-size: 12px;
}

.textarea-sm {
  resize: vertical;
  min-height: 48px;
}

.edit-actions {
  display: flex;
  gap: 8px;
}
</style>
