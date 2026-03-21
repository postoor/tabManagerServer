import { defineStore } from 'pinia'
import { ref } from 'vue'
import { bookmarksApi, syncApi } from '../api/index.js'

export const useBookmarksStore = defineStore('bookmarks', () => {
  const collections = ref([])
  const loading = ref(false)
  const error = ref(null)
  const syncStatus = ref(null)

  async function fetchCollections() {
    loading.value = true
    error.value = null
    try {
      const res = await bookmarksApi.getCollections()
      collections.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch collections'
    } finally {
      loading.value = false
    }
  }

  async function createCollection(data = {}) {
    try {
      const res = await bookmarksApi.createCollection({
        title: data.title || 'New Collection',
        labels: data.labels || [],
        position: collections.value.length,
      })
      collections.value.push(res.data)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create collection'
      throw err
    }
  }

  async function updateCollection(id, data) {
    try {
      const res = await bookmarksApi.updateCollection(id, data)
      const idx = collections.value.findIndex((c) => c.id === id)
      if (idx !== -1) {
        collections.value[idx] = { ...collections.value[idx], ...res.data }
      }
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update collection'
      throw err
    }
  }

  async function deleteCollection(id) {
    try {
      await bookmarksApi.deleteCollection(id)
      collections.value = collections.value.filter((c) => c.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete collection'
      throw err
    }
  }

  async function addBookmark(collectionId, data) {
    try {
      const collection = collections.value.find((c) => c.id === collectionId)
      const position = collection ? collection.bookmarks.length : 0
      const res = await bookmarksApi.addBookmark(collectionId, { ...data, position })
      if (collection) {
        collection.bookmarks.push(res.data)
      }
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to add bookmark'
      throw err
    }
  }

  async function updateBookmark(id, data) {
    try {
      const res = await bookmarksApi.updateBookmark(id, data)
      for (const col of collections.value) {
        const idx = col.bookmarks.findIndex((b) => b.id === id)
        if (idx !== -1) {
          col.bookmarks[idx] = { ...col.bookmarks[idx], ...res.data }
          break
        }
      }
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update bookmark'
      throw err
    }
  }

  async function deleteBookmark(id) {
    try {
      await bookmarksApi.deleteBookmark(id)
      for (const col of collections.value) {
        const idx = col.bookmarks.findIndex((b) => b.id === id)
        if (idx !== -1) {
          col.bookmarks.splice(idx, 1)
          break
        }
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete bookmark'
      throw err
    }
  }

  async function reorder(type, items) {
    try {
      await bookmarksApi.reorder(type, items)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to reorder'
      throw err
    }
  }

  async function syncPush() {
    try {
      const payload = {
        version: 3,
        lists: collections.value.map((col) => ({
          id: col.id,
          title: col.title,
          labels: col.labels || [],
          cards: col.bookmarks.map((bk) => ({
            id: bk.id,
            title: bk.title,
            url: bk.url,
            customTitle: bk.custom_title || '',
            customDescription: bk.custom_description || '',
          })),
        })),
      }
      const res = await syncApi.push(payload)
      // Refresh from response
      collections.value = _tobyToCollections(res.data)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sync push failed'
      throw err
    }
  }

  async function syncPull() {
    try {
      const res = await syncApi.pull()
      collections.value = _tobyToCollections(res.data)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Sync pull failed'
      throw err
    }
  }

  async function fetchSyncStatus() {
    try {
      const res = await syncApi.status()
      syncStatus.value = res.data
    } catch {
      syncStatus.value = null
    }
  }

  function _tobyToCollections(data) {
    return (data.lists || []).map((lst, idx) => ({
      id: lst.id,
      title: lst.title,
      labels: lst.labels || [],
      position: idx,
      bookmarks: (lst.cards || []).map((card, cardIdx) => ({
        id: card.id,
        collection_id: lst.id,
        title: card.title,
        url: card.url,
        custom_title: card.customTitle || '',
        custom_description: card.customDescription || '',
        favicon_url: null,
        position: cardIdx,
      })),
    }))
  }

  return {
    collections,
    loading,
    error,
    syncStatus,
    fetchCollections,
    createCollection,
    updateCollection,
    deleteCollection,
    addBookmark,
    updateBookmark,
    deleteBookmark,
    reorder,
    syncPush,
    syncPull,
    fetchSyncStatus,
  }
})
