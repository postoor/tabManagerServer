<template>
  <div class="collection-card">
    <!-- Collection header -->
    <div class="collection-header">
      <div class="collection-title-wrapper" @dblclick="startEditTitle">
        <input
          v-if="editingTitle"
          v-model="editTitle"
          ref="titleInputRef"
          class="title-input"
          @blur="saveTitle"
          @keydown.enter="saveTitle"
          @keydown.esc="editingTitle = false"
        />
        <h3 v-else class="collection-title" :title="collection.title">{{ collection.title }}</h3>
      </div>
      <div class="collection-actions">
        <span class="count-badge">{{ collection.bookmarks.length }}</span>
        <button class="btn btn-ghost btn-sm icon-btn" @click="$emit('add-bookmark')" title="Add bookmark">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
        <button class="btn btn-ghost btn-sm icon-btn danger-btn" @click="$emit('delete-collection')" title="Delete collection">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Bookmarks list -->
    <div
      class="bookmarks-list"
      @dragover.prevent
      @drop="onDrop($event)"
    >
      <BookmarkCard
        v-for="bookmark in sortedBookmarks"
        :key="bookmark.id"
        :bookmark="bookmark"
        draggable="true"
        @dragstart="onDragStart($event, bookmark.id)"
        @delete="$emit('delete-bookmark', bookmark.id)"
        @update="(data) => $emit('update-bookmark', bookmark.id, data)"
      />
      <div v-if="collection.bookmarks.length === 0" class="empty-bookmarks">
        <p>No bookmarks yet</p>
        <button class="btn btn-ghost btn-sm" @click="$emit('add-bookmark')">
          + Add first bookmark
        </button>
      </div>
    </div>

    <!-- Add bookmark button -->
    <button class="add-bookmark-btn" @click="$emit('add-bookmark')">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      Add bookmark
    </button>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import BookmarkCard from './BookmarkCard.vue'

const props = defineProps({
  collection: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits([
  'add-bookmark',
  'delete-collection',
  'update-title',
  'delete-bookmark',
  'update-bookmark',
])

const editingTitle = ref(false)
const editTitle = ref('')
const titleInputRef = ref(null)
const draggedId = ref(null)

const sortedBookmarks = computed(() =>
  [...props.collection.bookmarks].sort((a, b) => a.position - b.position)
)

async function startEditTitle() {
  editTitle.value = props.collection.title
  editingTitle.value = true
  await nextTick()
  titleInputRef.value?.focus()
  titleInputRef.value?.select()
}

function saveTitle() {
  const title = editTitle.value.trim()
  if (title && title !== props.collection.title) {
    emit('update-title', title)
  }
  editingTitle.value = false
}

function onDragStart(event, bookmarkId) {
  draggedId.value = bookmarkId
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', bookmarkId)
}

function onDrop(event) {
  const droppedId = event.dataTransfer.getData('text/plain')
  if (!droppedId || droppedId === draggedId.value) return
  // Reorder within collection — find drop target
  const target = event.target.closest('[data-bookmark-id]')
  if (target) {
    const targetId = target.dataset.bookmarkId
    const bookmarks = [...sortedBookmarks.value]
    const fromIdx = bookmarks.findIndex((b) => b.id === droppedId)
    const toIdx = bookmarks.findIndex((b) => b.id === targetId)
    if (fromIdx !== -1 && toIdx !== -1) {
      const [moved] = bookmarks.splice(fromIdx, 1)
      bookmarks.splice(toIdx, 0, moved)
      bookmarks.forEach((b, i) => {
        emit('update-bookmark', b.id, { position: i })
      })
    }
  }
}
</script>

<style scoped>
.collection-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow var(--transition);
}

.collection-card:hover {
  box-shadow: var(--shadow-md);
}

.collection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  border-bottom: 1px solid var(--color-border);
  gap: 8px;
}

.collection-title-wrapper {
  flex: 1;
  min-width: 0;
  cursor: text;
}

.collection-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title-input {
  width: 100%;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  padding: 2px 6px;
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.collection-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.count-badge {
  background: var(--color-primary-50);
  color: var(--color-primary);
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 600;
}

.icon-btn {
  padding: 5px;
  border-radius: var(--radius-sm);
  color: var(--color-text-3);
}

.icon-btn:hover { color: var(--color-text); }
.danger-btn:hover { color: var(--color-danger) !important; background: var(--color-danger-light); }

.bookmarks-list {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 60px;
}

.empty-bookmarks {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  gap: 8px;
  color: var(--color-text-3);
  font-size: 13px;
}

.add-bookmark-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-top: 1px solid var(--color-border);
  font-size: 12px;
  color: var(--color-text-3);
  width: 100%;
  transition: all var(--transition);
}

.add-bookmark-btn:hover {
  background: var(--color-surface-3);
  color: var(--color-primary);
}
</style>
