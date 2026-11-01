
// ===== Согласие на cookie: сторонние виджеты (Яндекс Карты) — только после согласия или по кнопке =====
;(() => {
  const KEY = 'orto-cookie'
  const get = () => { try { return localStorage.getItem(KEY) } catch (e) { return null } }
  const loadFrame = (box) => {
    const f = document.createElement('iframe')
    f.src = box.dataset.src; f.title = box.dataset.title || ''; f.loading = 'lazy'
    box.replaceWith(f)
  }
  const loadAll = () => document.querySelectorAll('.consent-frame').forEach(loadFrame)
  document.querySelectorAll('.consent-frame button').forEach((b) => b.addEventListener('click', () => loadFrame(b.closest('.consent-frame'))))
  if (get() === 'all') loadAll()
  const banner = document.querySelector('.cookie')
  if (!banner) return
  if (!get()) banner.hidden = false
  banner.querySelectorAll('[data-cookie]').forEach((b) => b.addEventListener('click', () => {
    try { localStorage.setItem(KEY, b.dataset.cookie) } catch (e) { /* без хранилища спросим снова */ }
    banner.hidden = true
    if (b.dataset.cookie === 'all') loadAll()
  }))
})()
