
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

// ===== Виджет отзывов ПроДокторов: только по кнопке (ч. 3 ст. 24 38-ФЗ, cookie площадки) =====
;(() => {
  const PAGE = 'https://prodoctorov.ru/mahachkala/lpu/90155-orto-rekaveri/#otzivi'
  document.querySelectorAll('[data-pd]').forEach((b) => b.addEventListener('click', () => {
    const slot = b.closest('.pd-slot')
    const el = document.createElement('div')
    el.id = 'pd_widget_big'; el.dataset.lpu = b.dataset.pd; el.hidden = true
    // скрипт берёт домен API из первой ссылки внутри блока
    el.innerHTML = '<a target="_blank" rel="noreferrer" href="' + PAGE + '">Отзывы о клинике «Орто-Рекавери»</a>'
    const wait = document.createElement('div'); wait.className = 'pd-wait'; wait.setAttribute('aria-label', 'Загружаем отзывы')
    const fail = () => { if (el.hidden) wait.outerHTML = '<p class="pd-fail">Не удалось загрузить виджет. <a href="' + PAGE + '" target="_blank" rel="noreferrer">Открыть отзывы на ПроДокторов</a></p>' }
    slot.replaceChildren(el, wait)
    new MutationObserver((m, o) => { if (!el.hidden) { wait.remove(); o.disconnect() } }).observe(el, { attributes: true, attributeFilter: ['hidden'] })
    setTimeout(fail, 10000)
    const s = document.createElement('script')
    s.src = 'https://prodoctorov.ru/static/js/widget_big.js?v07'; s.async = true; s.onerror = fail
    document.body.appendChild(s)
  }))
})()
