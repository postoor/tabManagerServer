// Touch fallback for HTML5 drag-and-drop: mobile browsers don't start native
// drags from touch, so touch gestures are tracked here and routed to drop zones
// that share their drop logic with the native dragover/drop handlers.

const LONG_PRESS_MS = 350
const MOVE_TOLERANCE = 8 // px a finger may drift before a pending long-press becomes a scroll
const EDGE = 60 // px from the scroller edge where auto-scroll kicks in
const MAX_SCROLL_SPEED = 14 // px per frame

const zones = new Map() // element -> { over(type, x, y, target), leave(), drop(type, id) }

let lastPointerType = 'mouse'
document.addEventListener('pointerdown', (e) => { lastPointerType = e.pointerType }, true)

// iOS can start a native drag on long-press; touch drags go through startTouchDrag instead
export function isTouchPointer() {
  return lastPointerType === 'touch'
}

export function registerDropZone(el, handlers) {
  zones.set(el, handlers)
  return () => zones.delete(el)
}

function findScroller(el) {
  for (let node = el.parentElement; node; node = node.parentElement) {
    const { overflowY } = getComputedStyle(node)
    if ((overflowY === 'auto' || overflowY === 'scroll') && node.scrollHeight > node.clientHeight) return node
  }
  return document.scrollingElement
}

function createGhost(el) {
  const rect = el.getBoundingClientRect()
  const ghost = el.cloneNode(true)
  Object.assign(ghost.style, {
    position: 'fixed',
    left: `${rect.left}px`,
    top: `${rect.top}px`,
    width: `${rect.width}px`,
    maxHeight: '160px',
    overflow: 'hidden',
    margin: '0',
    pointerEvents: 'none',
    opacity: '0.85',
    zIndex: '1000',
    background: 'var(--color-surface)',
    boxShadow: 'var(--shadow-lg)',
    borderRadius: 'var(--radius-md)',
  })
  document.body.appendChild(ghost)
  return ghost
}

/**
 * Start tracking a touch drag from a touchstart event.
 * longPress: require the finger to rest LONG_PRESS_MS first, so plain swipes still scroll.
 */
export function startTouchDrag(event, { type, id, el, longPress = false, onStart, onEnd }) {
  if (event.touches.length !== 1) return
  const start = { x: event.touches[0].clientX, y: event.touches[0].clientY }
  let last = start
  let active = false
  let timer = null
  let ghost = null
  let zone = null
  let scroller = null
  let frame = null

  function activate() {
    active = true
    scroller = findScroller(el)
    ghost = createGhost(el)
    onStart?.()
    navigator.vibrate?.(20)
    frame = requestAnimationFrame(autoScroll)
  }

  function updateZone() {
    const target = document.elementFromPoint(last.x, last.y)
    let next = null
    if (target) {
      for (const [zoneEl, handlers] of zones) {
        if (zoneEl.contains(target)) { next = handlers; break }
      }
    }
    if (zone && zone !== next) zone.leave()
    zone = next
    zone?.over(type, last.x, last.y, target)
  }

  function autoScroll() {
    if (!active) return
    const rect = scroller === document.scrollingElement
      ? { top: 0, bottom: window.innerHeight }
      : scroller.getBoundingClientRect()
    let delta = 0
    if (last.y < rect.top + EDGE) delta = -MAX_SCROLL_SPEED * (1 - (last.y - rect.top) / EDGE)
    else if (last.y > rect.bottom - EDGE) delta = MAX_SCROLL_SPEED * (1 - (rect.bottom - last.y) / EDGE)
    if (delta) {
      scroller.scrollTop += Math.max(-MAX_SCROLL_SPEED, Math.min(MAX_SCROLL_SPEED, delta))
      updateZone()
    }
    frame = requestAnimationFrame(autoScroll)
  }

  function onMove(e) {
    const t = e.touches[0]
    last = { x: t.clientX, y: t.clientY }
    if (!active) {
      if (Math.hypot(last.x - start.x, last.y - start.y) > MOVE_TOLERANCE) cleanup()
      return
    }
    e.preventDefault()
    ghost.style.transform = `translate(${last.x - start.x}px, ${last.y - start.y}px)`
    updateZone()
  }

  function onTouchEnd(e) {
    if (active) {
      e.preventDefault() // suppress the click that would otherwise open the bookmark
      if (zone) zone.drop(type, id)
    }
    cleanup()
  }

  function onContextMenu(e) {
    e.preventDefault()
  }

  function cleanup() {
    clearTimeout(timer)
    cancelAnimationFrame(frame)
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', onTouchEnd)
    document.removeEventListener('touchcancel', cleanup)
    document.removeEventListener('contextmenu', onContextMenu)
    if (active) {
      zone?.leave()
      ghost.remove()
      onEnd?.()
    }
    active = false
  }

  document.addEventListener('touchmove', onMove, { passive: false })
  document.addEventListener('touchend', onTouchEnd)
  document.addEventListener('touchcancel', cleanup)
  document.addEventListener('contextmenu', onContextMenu)

  if (longPress) timer = setTimeout(activate, LONG_PRESS_MS)
  else activate()
}
