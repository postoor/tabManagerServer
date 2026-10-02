<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-header">
        <div class="logo">
          <svg width="28" height="28" viewBox="0 0 36 36" fill="none">
            <rect width="36" height="36" rx="10" fill="#4f46e5"/>
            <path d="M10 13h16M10 18h12M10 23h8" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
          <span>Tab Manager</span>
        </div>
        <button class="btn btn-ghost btn-sm sidebar-close" @click="sidebarOpen = false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="col in bookmarksStore.collections"
          :key="col.id"
          class="nav-item"
          :class="{
            active: activeCollectionId === col.id,
            'drop-before': navDrop?.id === col.id && navDrop.mode === 'before',
            'drop-after': navDrop?.id === col.id && navDrop.mode === 'after',
            'drop-into': navDrop?.id === col.id && navDrop.mode === 'into',
          }"
          draggable="true"
          @click="activeCollectionId = col.id; sidebarOpen = false"
          @dragstart="onNavDragStart($event, col.id)"
          @dragover="onNavDragOver($event, col.id)"
          @dragleave="onNavDragLeave($event)"
          @drop="onNavDrop($event, col.id)"
          @dragend="navDrop = null"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 7h18M3 12h18M3 17h18"/>
          </svg>
          <span class="nav-item-title">{{ col.title }}</span>
          <span class="nav-badge">{{ col.bookmarks.length }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <button class="btn btn-secondary btn-sm btn-block" @click="addCollection">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          New Collection
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="main-wrapper">
      <!-- Header -->
      <header class="app-header">
        <div class="header-left">
          <button class="btn btn-ghost btn-sm menu-btn" @click="sidebarOpen = true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <h2 class="header-title">{{ activeCollection?.title || 'All Collections' }}</h2>
        </div>

        <div class="header-right">
          <button
            v-if="displayedCollections.length > 0"
            class="btn btn-secondary btn-sm"
            @click="toggleCollapseAll"
            :title="allCollapsed ? 'Expand all collections' : 'Collapse all collections'"
          >
            <svg v-if="allCollapsed" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="7 13 12 18 17 13"/><polyline points="7 6 12 11 17 6"/>
            </svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="17 11 12 6 7 11"/><polyline points="17 18 12 13 7 18"/>
            </svg>
            {{ allCollapsed ? 'Expand all' : 'Collapse all' }}
          </button>
          <div class="sync-info" v-if="syncStatus">
            <span class="sync-label">{{ bookmarksStore.collections.length }} lists &middot; {{ totalBookmarks }} bookmarks</span>
          </div>
          <button class="btn btn-secondary btn-sm" @click="handleSyncPull" :disabled="syncing">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ spinning: syncing }">
              <path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
            </svg>
            Pull
          </button>
          <button class="btn btn-primary btn-sm" @click="handleSyncPush" :disabled="syncing">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
            </svg>
            Push
          </button>
          <div class="user-menu" @click="showUserMenu = !showUserMenu" ref="userMenuRef">
            <div class="avatar">{{ userInitial }}</div>
            <transition name="fade">
              <div v-if="showUserMenu" class="dropdown">
                <div class="dropdown-header">{{ authStore.user?.email }}</div>
                <button class="dropdown-item" @click="handleLogout">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
                  </svg>
                  Sign Out
                </button>
              </div>
            </transition>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="main-content">
        <div v-if="bookmarksStore.loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading your bookmarks...</p>
        </div>

        <div v-else-if="bookmarksStore.collections.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-3)" stroke-width="1">
            <path d="M4 6h16M4 12h16M4 18h7"/>
          </svg>
          <h3>No collections yet</h3>
          <p>Create your first collection to start organizing bookmarks</p>
          <button class="btn btn-primary" @click="addCollection">Create Collection</button>
        </div>

        <div v-else class="collections-grid">
          <BookmarkList
            v-for="col in displayedCollections"
            :key="col.id"
            :collection="col"
            :collapsed="collapsedIds.has(col.id)"
            @toggle-collapse="toggleCollapse(col.id)"
            @add-bookmark="openAddModal(col.id)"
            @delete-collection="deleteCollection(col.id)"
            @update-title="(title) => updateCollectionTitle(col.id, title)"
            @delete-bookmark="deleteBookmark"
            @update-bookmark="updateBookmark"
            @move-bookmark="moveBookmark"
            @move-collection="moveCollection"
          />
        </div>
      </main>
    </div>

    <!-- Add Bookmark Modal -->
    <AddBookmarkModal
      v-if="showAddModal"
      :collection-id="addToCollectionId"
      @close="showAddModal = false"
      @add="handleAddBookmark"
    />

    <!-- Toast notifications -->
    <transition name="fade">
      <div v-if="toast" class="toast" :class="`toast-${toast.type}`">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useBookmarksStore } from '../stores/bookmarks.js'
import { useRouter } from 'vue-router'
import BookmarkList from '../components/BookmarkList.vue'
import AddBookmarkModal from '../components/AddBookmarkModal.vue'

const authStore = useAuthStore()
const bookmarksStore = useBookmarksStore()
const router = useRouter()

const sidebarOpen = ref(false)
const activeCollectionId = ref(null)
const showUserMenu = ref(false)
const showAddModal = ref(false)
const addToCollectionId = ref(null)
const syncing = ref(false)
const syncStatus = ref(null)
const toast = ref(null)
const userMenuRef = ref(null)

const userInitial = computed(() => {
  const email = authStore.user?.email || ''
  return email.charAt(0).toUpperCase() || 'U'
})

const totalBookmarks = computed(() =>
  bookmarksStore.collections.reduce((sum, c) => sum + c.bookmarks.length, 0)
)

const displayedCollections = computed(() => {
  if (activeCollectionId.value) {
    return bookmarksStore.collections.filter((c) => c.id === activeCollectionId.value)
  }
  return bookmarksStore.collections
})

const activeCollection = computed(() =>
  bookmarksStore.collections.find((c) => c.id === activeCollectionId.value)
)

function showToast(message, type = 'success') {
  toast.value = { message, type }
  setTimeout(() => { toast.value = null }, 3000)
}

async function handleSyncPull() {
  syncing.value = true
  try {
    await bookmarksStore.syncPull()
    await bookmarksStore.fetchSyncStatus()
    syncStatus.value = bookmarksStore.syncStatus
    showToast('Synced from server')
  } catch {
    showToast('Sync failed', 'error')
  } finally {
    syncing.value = false
  }
}

async function handleSyncPush() {
  syncing.value = true
  try {
    await bookmarksStore.syncPush()
    showToast('Pushed to server')
  } catch {
    showToast('Push failed', 'error')
  } finally {
    syncing.value = false
  }
}

async function addCollection() {
  const col = await bookmarksStore.createCollection({ title: 'New Collection' })
  activeCollectionId.value = col.id
  sidebarOpen.value = false
}

async function deleteCollection(id) {
  if (!confirm('Delete this collection and all its bookmarks?')) return
  await bookmarksStore.deleteCollection(id)
  if (activeCollectionId.value === id) {
    activeCollectionId.value = null
  }
  showToast('Collection deleted')
}

async function updateCollectionTitle(id, title) {
  await bookmarksStore.updateCollection(id, { title })
}

function openAddModal(collectionId) {
  addToCollectionId.value = collectionId
  showAddModal.value = true
}

async function handleAddBookmark(data) {
  await bookmarksStore.addBookmark(addToCollectionId.value, data)
  showAddModal.value = false
  showToast('Bookmark added')
}

async function deleteBookmark(id) {
  await bookmarksStore.deleteBookmark(id)
  showToast('Bookmark deleted')
}

async function updateBookmark(id, data) {
  await bookmarksStore.updateBookmark(id, data)
}

async function moveBookmark(bookmarkId, collectionId, targetBookmarkId, after) {
  try {
    await bookmarksStore.moveBookmark(bookmarkId, collectionId, targetBookmarkId, after)
  } catch {
    showToast('Move failed', 'error')
  }
}

async function moveCollection(collectionId, targetCollectionId, after) {
  try {
    await bookmarksStore.moveCollection(collectionId, targetCollectionId, after)
  } catch {
    showToast('Move failed', 'error')
  }
}

// Collapsed state is a per-browser view preference, kept in localStorage
const COLLAPSED_KEY = 'collapsedCollections'

function loadCollapsed() {
  try {
    return new Set(JSON.parse(localStorage.getItem(COLLAPSED_KEY)) || [])
  } catch {
    return new Set()
  }
}

const collapsedIds = ref(loadCollapsed())

watch(collapsedIds, (ids) => {
  try {
    localStorage.setItem(COLLAPSED_KEY, JSON.stringify([...ids]))
  } catch {
    // storage unavailable (private mode / quota) → state just won't persist
  }
}, { deep: true })

const allCollapsed = computed(() =>
  displayedCollections.value.length > 0 &&
  displayedCollections.value.every((c) => collapsedIds.value.has(c.id))
)

function toggleCollapse(id) {
  if (collapsedIds.value.has(id)) collapsedIds.value.delete(id)
  else collapsedIds.value.add(id)
}

function toggleCollapseAll() {
  const collapse = !allCollapsed.value
  for (const c of displayedCollections.value) {
    if (collapse) collapsedIds.value.add(c.id)
    else collapsedIds.value.delete(c.id)
  }
}

// Sidebar: reorder collections, or drop a bookmark into a collection
const navDrop = ref(null) // { id, mode: 'before' | 'after' | 'into' }

function onNavDragStart(event, collectionId) {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/x-collection', collectionId)
}

function onNavDragOver(event, collectionId) {
  const types = event.dataTransfer.types
  if (types.includes('text/x-collection')) {
    event.preventDefault()
    const rect = event.currentTarget.getBoundingClientRect()
    const mode = event.clientY < rect.top + rect.height / 2 ? 'before' : 'after'
    navDrop.value = { id: collectionId, mode }
  } else if (types.includes('text/x-bookmark')) {
    event.preventDefault()
    navDrop.value = { id: collectionId, mode: 'into' }
  }
}

function onNavDragLeave(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) navDrop.value = null
}

function onNavDrop(event, collectionId) {
  const drop = navDrop.value
  navDrop.value = null
  const types = event.dataTransfer.types
  if (types.includes('text/x-collection')) {
    event.preventDefault()
    const draggedId = event.dataTransfer.getData('text/x-collection')
    if (draggedId) moveCollection(draggedId, collectionId, drop?.mode === 'after')
  } else if (types.includes('text/x-bookmark')) {
    event.preventDefault()
    const bookmarkId = event.dataTransfer.getData('text/x-bookmark')
    if (bookmarkId) moveBookmark(bookmarkId, collectionId, null, false)
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function handleOutsideClick(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    showUserMenu.value = false
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchMe()
  }
  await bookmarksStore.fetchCollections()
  await bookmarksStore.fetchSyncStatus()
  syncStatus.value = bookmarksStore.syncStatus
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform var(--transition);
  z-index: 100;
}

.sidebar-header {
  padding: 20px 16px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 15px;
  color: var(--color-text);
}

.sidebar-close { display: none; }

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  color: var(--color-text-2);
  font-size: 13px;
  text-align: left;
  transition: all var(--transition);
  width: 100%;
}

.nav-item:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary-50);
  color: var(--color-primary);
  font-weight: 500;
}

.nav-item.drop-before { box-shadow: 0 -2px 0 var(--color-primary); }
.nav-item.drop-after { box-shadow: 0 2px 0 var(--color-primary); }
.nav-item.drop-into {
  background: var(--color-primary-50);
  outline: 2px dashed var(--color-primary);
  outline-offset: -2px;
}

.nav-item-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-badge {
  background: var(--color-surface-3);
  color: var(--color-text-3);
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 11px;
  flex-shrink: 0;
}

.nav-item.active .nav-badge {
  background: var(--color-primary-100);
  color: var(--color-primary);
}

.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid var(--color-border);
}

.btn-block { width: 100%; justify-content: center; }

/* Main wrapper */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* Header */
.app-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.menu-btn { display: none; }

.header-title {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.sync-info {
  font-size: 12px;
  color: var(--color-text-3);
  white-space: nowrap;
}

.spinning {
  animation: spin 1s linear infinite;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  user-select: none;
}

.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  min-width: 200px;
  z-index: 200;
  overflow: hidden;
}

.dropdown-header {
  padding: 12px 16px;
  font-size: 12px;
  color: var(--color-text-3);
  border-bottom: 1px solid var(--color-border);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 13px;
  color: var(--color-text);
  width: 100%;
  transition: background var(--transition);
}
.dropdown-item:hover { background: var(--color-surface-3); }

/* Main content */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 16px;
  color: var(--color-text-3);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  gap: 16px;
  color: var(--color-text-3);
  text-align: center;
}

.empty-state h3 {
  font-size: 18px;
  color: var(--color-text);
  margin: 0;
}

.empty-state p {
  color: var(--color-text-2);
  max-width: 300px;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  align-items: start;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  box-shadow: var(--shadow-md);
  z-index: 1000;
}

.toast-success {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
}

.toast-error {
  background: var(--color-danger-light);
  color: var(--color-danger);
  border: 1px solid #fca5a5;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    transform: translateX(-100%);
    box-shadow: var(--shadow-lg);
  }
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  .sidebar-close { display: flex; }
  .menu-btn { display: flex; }
  .sync-info { display: none; }
  .collections-grid { grid-template-columns: 1fr; }
  .main-content { padding: 16px; }
  .app-header { padding: 0 16px; }
}
</style>
