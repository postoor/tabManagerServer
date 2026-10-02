<template>
  <div
    ref="rootRef"
    class="collection-card"
    :class="{
      dragging: isDragging,
      horizontal: dropHorizontal,
      'drop-before': collectionDrop === 'before',
      'drop-after': collectionDrop === 'after',
      'drag-over-collection': bookmarkDrop !== null,
      collapsed,
    }"
    :draggable="collectionDraggable"
    @dragstart="onCollectionDragStart"
    @dragend="onCollectionDragEnd"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <!-- Collection header -->
    <div class="collection-header">
      <button class="drag-handle" title="Drag to reorder" @pointerdown="onHandlePointerDown">
        <svg width="10" height="14" viewBox="0 0 10 14" fill="currentColor">
          <circle cx="3" cy="2" r="1.2"/><circle cx="7" cy="2" r="1.2"/><circle cx="3" cy="7" r="1.2"/>
          <circle cx="7" cy="7" r="1.2"/><circle cx="3" cy="12" r="1.2"/><circle cx="7" cy="12" r="1.2"/>
        </svg>
      </button>
      <button
        class="collapse-btn"
        :title="collapsed ? 'Expand' : 'Collapse'"
        :aria-expanded="!collapsed"
        @click="$emit('toggle-collapse')"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
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
    <div v-show="!collapsed" class="bookmarks-list">
      <BookmarkCard
        v-for="bookmark in sortedBookmarks"
        :key="bookmark.id"
        :bookmark="bookmark"
        :class="{
          'drop-before': bookmarkDrop?.id === bookmark.id && !bookmarkDrop.after,
          'drop-after': bookmarkDrop?.id === bookmark.id && bookmarkDrop.after,
        }"
        draggable="true"
        @dragstart="onBookmarkDragStart($event, bookmark.id)"
        @dragend="onBookmarkDragEnd"
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
    <button v-show="!collapsed" class="add-bookmark-btn" @click="$emit('add-bookmark')">
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
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'add-bookmark',
  'delete-collection',
  'update-title',
  'delete-bookmark',
  'update-bookmark',
  'move-bookmark',
  'move-collection',
  'toggle-collapse',
])

const editingTitle = ref(false)
const editTitle = ref('')
const titleInputRef = ref(null)
const rootRef = ref(null)
const collectionDraggable = ref(false)
const isDragging = ref(false)
const collectionDrop = ref(null) // 'before' | 'after' | null
const dropHorizontal = ref(false)
const bookmarkDrop = ref(null) // { id, after } | { id: null } | null

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

const BOOKMARK_TYPE = 'text/x-bookmark'
const COLLECTION_TYPE = 'text/x-collection'

function onBookmarkDragStart(event, bookmarkId) {
  event.stopPropagation()
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData(BOOKMARK_TYPE, bookmarkId)
  const el = event.currentTarget
  setTimeout(() => el.classList.add('bookmark-dragging'), 0)
}

function onBookmarkDragEnd(event) {
  event.currentTarget.classList.remove('bookmark-dragging')
}

// Only the handle makes the whole card draggable, so text/inputs stay usable
function onHandlePointerDown() {
  collectionDraggable.value = true
  document.addEventListener('pointerup', () => { collectionDraggable.value = false }, { once: true })
}

function onCollectionDragStart(event) {
  if (event.target !== rootRef.value) return
  if (!collectionDraggable.value) { event.preventDefault(); return }
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData(COLLECTION_TYPE, props.collection.id)
  setTimeout(() => { isDragging.value = true }, 0)
}

function onCollectionDragEnd(event) {
  if (event.target !== rootRef.value) return
  collectionDraggable.value = false
  isDragging.value = false
  clearDropState()
}

function clearDropState() {
  collectionDrop.value = null
  bookmarkDrop.value = null
}

// Grid shows several columns side by side → split left/right, otherwise top/bottom
function isGridHorizontal() {
  const grid = rootRef.value?.parentElement
  if (!grid) return false
  return getComputedStyle(grid).gridTemplateColumns.split(' ').length > 1
}

function onDragOver(event) {
  const types = event.dataTransfer.types
  if (types.includes(COLLECTION_TYPE)) {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    const rect = rootRef.value.getBoundingClientRect()
    dropHorizontal.value = isGridHorizontal()
    const before = dropHorizontal.value
      ? event.clientX < rect.left + rect.width / 2
      : event.clientY < rect.top + rect.height / 2
    collectionDrop.value = before ? 'before' : 'after'
  } else if (types.includes(BOOKMARK_TYPE)) {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
    const card = event.target.closest('[data-bookmark-id]')
    if (card && rootRef.value.contains(card)) {
      const rect = card.getBoundingClientRect()
      bookmarkDrop.value = {
        id: card.dataset.bookmarkId,
        after: event.clientY >= rect.top + rect.height / 2,
      }
    } else {
      bookmarkDrop.value = { id: null }
    }
  }
}

function onDragLeave(event) {
  if (!rootRef.value.contains(event.relatedTarget)) clearDropState()
}

function onDrop(event) {
  const types = event.dataTransfer.types
  if (types.includes(COLLECTION_TYPE)) {
    event.preventDefault()
    const draggedId = event.dataTransfer.getData(COLLECTION_TYPE)
    const after = collectionDrop.value === 'after'
    if (draggedId && draggedId !== props.collection.id) {
      emit('move-collection', draggedId, props.collection.id, after)
    }
  } else if (types.includes(BOOKMARK_TYPE)) {
    event.preventDefault()
    const draggedId = event.dataTransfer.getData(BOOKMARK_TYPE)
    const target = bookmarkDrop.value
    if (draggedId && draggedId !== target?.id) {
      emit('move-bookmark', draggedId, props.collection.id, target?.id || null, !!target?.after)
    }
  }
  clearDropState()
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

.collection-card.dragging { opacity: 0.4; }
.collection-card.drop-before { box-shadow: 0 -3px 0 var(--color-primary); }
.collection-card.drop-after { box-shadow: 0 3px 0 var(--color-primary); }
.collection-card.horizontal.drop-before { box-shadow: -3px 0 0 var(--color-primary); }
.collection-card.horizontal.drop-after { box-shadow: 3px 0 0 var(--color-primary); }
.collection-card.drag-over-collection {
  outline: 2px dashed var(--color-primary);
  outline-offset: 2px;
}

.drag-handle {
  display: flex;
  align-items: center;
  padding: 4px 2px;
  color: var(--color-text-3);
  cursor: grab;
  flex-shrink: 0;
}
.drag-handle:hover { color: var(--color-text); }
.drag-handle:active { cursor: grabbing; }

.bookmark-card.bookmark-dragging { opacity: 0.35; }
.bookmark-card.drop-before { box-shadow: 0 -2px 0 var(--color-primary); }
.bookmark-card.drop-after { box-shadow: 0 2px 0 var(--color-primary); }

.collection-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  border-bottom: 1px solid var(--color-border);
  gap: 8px;
}

.collapse-btn {
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: var(--radius-sm);
  color: var(--color-text-3);
  flex-shrink: 0;
  transition: transform var(--transition);
}
.collapse-btn:hover { color: var(--color-text); background: var(--color-surface-3); }
.collection-card.collapsed .collapse-btn { transform: rotate(-90deg); }
.collection-card.collapsed .collection-header { border-bottom: none; }

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
