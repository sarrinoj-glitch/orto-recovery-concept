// Общий скрипт всех страниц концепции. Каждый блок проверяет, есть ли он на странице.
const P = document.body.dataset.p || ''
const ALL = location.hash === '#all'
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
const $ = (s) => document.querySelector(s)
const $$ = (s) => [...document.querySelectorAll(s)]

// Мобильное меню
const burger = $('.burger'), mnav = $('.mnav')
if (burger && mnav) burger.addEventListener('click', () => {
  const open = mnav.hidden
  mnav.hidden = !open
  burger.setAttribute('aria-expanded', String(open))
  burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню')
})

// Подсказки заполняют поиск
const q = $('#q')
if (q) $$('.chip').forEach((c) => c.addEventListener('click', () => { q.value = c.textContent; q.focus() }))

// Стрелки каруселей
const scroller = (list, gap) => (dir) => list.scrollBy({ left: dir * (list.firstElementChild.offsetWidth + gap), behavior: 'smooth' })
const cards = $('#cards')
if (cards) { const go = scroller(cards, 20); $$('[data-dir]').forEach((b) => b.addEventListener('click', () => go(Number(b.dataset.dir)))) }
const tour = $('#tourList')
if (tour) { const go = scroller(tour, 16); $$('[data-tour]').forEach((b) => b.addEventListener('click', () => go(Number(b.dataset.tour)))) }

// Появление при прокрутке
const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } }), { threshold: 0.15 })
$$('.rv').forEach((el) => (ALL ? el.classList.add('in') : io.observe(el)))

// 121 точка = 121 оценка в 2ГИС
const g = $('#g121')
if (g) {
  for (let i = 0; i < 121; i++) g.appendChild(document.createElement('i'))
  const dots = [...g.children]
  if (ALL || reduce) dots.forEach((d) => d.classList.add('on'))
  else new IntersectionObserver((es, o) => es.forEach((e) => { if (e.isIntersecting) { dots.forEach((d, i) => setTimeout(() => d.classList.add('on'), i * 12)); o.disconnect() } })).observe(g)
}

// Вкладки «С чем работаем»
$$('.conds').forEach((box) => {
  const tabs = [...box.querySelectorAll('.tab')], lists = [...box.querySelectorAll('.cond-list')]
  tabs.forEach((t) => t.addEventListener('click', () => {
    tabs.forEach((x) => x.setAttribute('aria-selected', String(x === t)))
    lists.forEach((l) => { l.hidden = l.dataset.panel !== t.dataset.tab })
  }))
})

// Двери «С чего начать»: якорь на странице или переход на страницу услуги
$$('.door').forEach((d) => d.addEventListener('click', () => {
  const go = d.dataset.go
  const el = go.startsWith('#') && $(go)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  else location.href = go
}))

// Опрос «подобрать врача»
const qb = $('#quizBody')
if (qb) {
  const AREAS = {
    back: { t: 'Спина и шея', who: 'Куделя Павел Александрович', role: 'невролог, мануальный терапевт', ini: 'КП', price: '8 000 ₽', pl: 'полный приём', slug: 'spina' },
    knee: { t: 'Колено и тазобедренный сустав', who: 'Хаджалов Абузар Магомедович', role: 'травматолог-ортопед', ini: 'ХА', price: '3 000 ₽', pl: 'приём', slug: 'ortopediya' },
    arm: { t: 'Плечо, локоть, кисть', who: 'Хаджалов Абузар Магомедович', role: 'травматолог-ортопед, кистевой реабилитолог', ini: 'ХА', price: '3 000 ₽', pl: 'приём', slug: 'ortopediya' },
    foot: { t: 'Стопа и пятка', who: 'Хаджалов Абузар Магомедович', role: 'травматолог-ортопед', ini: 'ХА', price: '3 000 ₽', pl: 'приём', slug: 'ortopediya' },
    kids: { t: 'Ребёнок: осанка, сколиоз', who: 'Мусаева Эльмира Ашурбеговна', role: 'инструктор ЛФК, методика СИАС', ini: 'МЭ', price: '2 500 ₽', pl: 'занятие', slug: 'detyam' },
    endo: { t: 'Желудок и кишечник', who: 'Нажмудинова Айшат Абдурахмановна', role: 'терапевт-гастроэнтеролог', ini: 'НА', price: '3 000 ₽', pl: 'приём', slug: 'endoskopiya' },
  }
  const Q = [
    { q: 'Где беспокоит?', k: 'area', o: [['back', 'Спина или шея'], ['knee', 'Колено или таз'], ['arm', 'Плечо или кисть'], ['foot', 'Стопа или пятка'], ['kids', 'Осанка у ребёнка'], ['endo', 'Желудок, кишечник']] },
    { q: 'Как давно?', k: 'when', o: [['new', 'До двух недель'], ['mid', 'От месяца до полугода'], ['long', 'Больше полугода']] },
    { q: 'Была травма или операция?', k: 'why', o: [['trauma', 'Да, травма'], ['surgery', 'Да, операция'], ['no', 'Нет']] },
  ]
  const steps = $$('.quiz-steps i')
  let qa = {}, qi = 0
  const render = () => {
    steps.forEach((el, i) => el.classList.toggle('on', i <= qi))
    if (qi < Q.length) {
      const c = Q[qi]
      qb.innerHTML = `<p class="q-title">${c.q}</p><div class="q-opts">${c.o.map(([v, l]) => `<button type="button" data-v="${v}">${l}</button>`).join('')}</div>`
      qb.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => { qa[c.k] = b.dataset.v; qi++; render() }))
      return
    }
    const a = AREAS[qa.area]
    const note = qa.why === 'surgery' ? 'После операции врач составит план реабилитации и передаст вас инструктору ЛФК.' : qa.why === 'trauma' ? 'Возьмите снимки после травмы — врач разберёт их на приёме.' : qa.when === 'long' ? 'Боль дольше полугода — врач найдёт причину и составит курс, а не просто снимет симптом.' : 'Чем раньше начать, тем короче обычно восстановление.'
    qb.innerHTML = `<div class="q-result"><div class="who"><span class="ava" style="width:52px;height:52px;border-radius:16px;font-size:17px;background:var(--lime);color:var(--graphite)">${a.ini}</span><div><b>${a.who}</b><small>${a.role}</small></div></div><p><b style="color:var(--deep)">${a.t}.</b> ${note}</p><div class="row"><strong>${a.price} <small style="font-size:14px;font-weight:500;color:var(--muted)">${a.pl}</small></strong><span style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn-ghost-d" href="${P}uslugi/${a.slug}/">Об услуге</a><button class="btn-deep" type="button" style="margin:0">Записаться</button></span></div></div><button class="q-again" type="button">↺ Пройти заново</button>`
    qb.querySelector('.q-again').addEventListener('click', () => { qa = {}; qi = 0; render() })
  }
  render()
}

// Один диагноз — две программы
if ($('#twPlan')) {
  const TW = {
    a: { who: 'Офисный сотрудник, 45 лет', why: 'Сидячая работа, боль усиливается к вечеру. Цель — работать без боли.', load: 30, plan: [['1–2 неделя', 'Снять острую боль: щадящие процедуры по назначению невролога'], ['3–4 неделя', 'ЛФК с минимальной нагрузкой: упражнения на стабилизацию спины'], ['5–8 неделя', 'Постепенно укрепляем мышцы корпуса'], ['Дальше', 'План домашних занятий и контрольный осмотр']] },
    b: { who: 'Борец, 24 года', why: 'Тренируется 6 раз в неделю, боль после схватки. Цель — вернуться на ковёр.', load: 75, plan: [['1–2 неделя', 'Работа с болью и мышечным спазмом: физиотерапия, массаж'], ['3–6 неделя', 'Силовая ЛФК: возвращаем нагрузку под контролем врача'], ['7–10 неделя', 'Специальные упражнения под технику борьбы'], ['Дальше', 'Поэтапный возврат к тренировкам на ковре']] },
  }
  const render = (k) => {
    const t = TW[k]
    $('#twWho').textContent = t.who; $('#twWhy').textContent = t.why
    $('#twLoad').style.width = t.load + '%'
    $('#twPlan').innerHTML = t.plan.map(([w, x]) => `<li><em>${w}</em><span>${x}</span></li>`).join('')
    $$('.twin-sw button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.p === k)))
  }
  $$('.twin-sw button').forEach((b) => b.addEventListener('click', () => render(b.dataset.p)))
  render('a')
}

// Словарь методик: описание лежит в data-text у кнопки
const dictT = $('#dictT'), dictP = $('#dictP')
if (dictT) $$('.all-methods button').forEach((b) => b.addEventListener('click', () => {
  $$('.all-methods button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)))
  dictT.textContent = b.textContent; dictP.textContent = b.dataset.text
}))

// Чат WhatsApp печатается по одному сообщению
const wa = $('#waChat')
if (wa) {
  const bubs = [...wa.querySelectorAll('.bub')]
  if (ALL || reduce) bubs.forEach((b) => b.classList.add('show'))
  else new IntersectionObserver((es, o) => es.forEach((e) => { if (e.isIntersecting) { bubs.forEach((b, i) => setTimeout(() => b.classList.add('show'), i * 700)); o.disconnect() } }), { threshold: 0.3 }).observe(wa)
}

// Чек-лист запоминается в браузере
const boxes = $$('.checklist input')
if (boxes.length) {
  try { const saved = JSON.parse(localStorage.getItem('orto-prep') || '[]'); boxes.forEach((b, i) => { b.checked = !!saved[i] }) } catch (e) { /* нет хранилища */ }
  boxes.forEach((b) => b.addEventListener('change', () => { try { localStorage.setItem('orto-prep', JSON.stringify(boxes.map((x) => x.checked))) } catch (e) { /* нет хранилища */ } }))
}

// Памятка: проверяем номер, в концепции ничего не отправляем
const mf = $('#magnetForm'), mp = $('#magnetPhone'), me = $('#magnetErr')
if (mf) {
  mp.addEventListener('input', () => { me.hidden = true })
  mf.addEventListener('submit', (e) => {
    e.preventDefault()
    if (mp.value.replace(/\D/g, '').replace(/^[78]/, '').length !== 10) { me.hidden = false; return }
    mf.outerHTML = '<div class="ok"><b>Готово!</b> Памятка придёт в WhatsApp в течение минуты. <small style="display:block;color:var(--muted);margin-top:4px">В концепции номер никуда не отправляется.</small></div>'
  })
}

// Шаги «Как лечим» подсвечиваются по очереди
const stepsList = $$('.steps li')
if (stepsList.length && !reduce) {
  let s = 0
  setInterval(() => { stepsList[s].classList.remove('on'); s = (s + 1) % stepsList.length; stepsList[s].classList.add('on') }, 2600)
}

// ===== Анимации второго круга (как в React-версиях), на чистом JS. Подключается после основного скрипта. =====
;(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
  const fine = matchMedia('(pointer: fine)').matches
  const $ = (s, r = document) => r.querySelector(s)
  const $$ = (s, r = document) => [...r.querySelectorAll(s)]
  const ease = (t) => 1 - Math.pow(1 - t, 4)

  // Полоска прогресса чтения
  const bar = document.createElement('div')
  bar.className = 'sprog'
  document.body.appendChild(bar)
  const onScroll = () => {
    const h = document.documentElement.scrollHeight - innerHeight
    bar.style.transform = `scaleX(${h > 0 ? scrollY / h : 0})`
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll()

  // Слово в заголовке сменяется по кругу
  $$('.flip[data-words]').forEach((el) => {
    const words = el.dataset.words.split('|')
    const longest = words.reduce((a, b) => (b.length > a.length ? b : a))
    el.innerHTML = `<span class="sizer" aria-hidden="true">${longest}</span><span>${words[0]}</span>`
    if (reduce) return
    let i = 0
    setInterval(() => {
      const old = el.lastElementChild
      i = (i + 1) % words.length
      const next = document.createElement('span')
      next.className = 'in-start'
      next.textContent = words[i]
      el.appendChild(next)
      old.classList.add('out')
      requestAnimationFrame(() => requestAnimationFrame(() => next.classList.remove('in-start')))
      setTimeout(() => old.remove(), 460)
    }, 2400)
  })

  // Кнопки чуть тянутся к курсору
  if (fine && !reduce) $$('.btn-main, .btn-coral').forEach((b) => {
    b.classList.add('magnetic')
    b.addEventListener('pointermove', (e) => {
      const r = b.getBoundingClientRect()
      b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.3}px, ${(e.clientY - r.top - r.height / 2) * 0.3}px)`
    })
    b.addEventListener('pointerleave', () => { b.style.transform = '' })
  })

  // 3D-наклон карточек + блик под курсором
  if (fine && !reduce) $$('.card, .door, .svc-cards a').forEach((c) => {
    c.classList.add('tilt')
    const glow = document.createElement('span')
    glow.className = 'tilt-glow'
    c.appendChild(glow)
    c.addEventListener('pointermove', (e) => {
      const r = c.getBoundingClientRect()
      const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height
      c.classList.add('tilting')
      c.style.transform = `perspective(900px) rotateX(${(0.5 - y) * 14}deg) rotateY(${(x - 0.5) * 14}deg)`
      c.style.setProperty('--gx', `${x * 100}%`); c.style.setProperty('--gy', `${y * 100}%`)
    })
    c.addEventListener('pointerleave', () => { c.classList.remove('tilting'); c.style.transform = '' })
  })

  // Свет за курсором в шапках и слова заголовка из размытия
  $$('.phead, .hero').forEach((h) => {
    const spot = document.createElement('span')
    spot.className = 'ph-spot'
    h.prepend(spot)
    if (fine) h.addEventListener('pointermove', (e) => {
      const r = h.getBoundingClientRect()
      spot.style.setProperty('--mx', `${e.clientX - r.left}px`); spot.style.setProperty('--my', `${e.clientY - r.top}px`)
    })
  })
  if (!reduce) $$('.phead h1').forEach((h1) => {
    if (h1.children.length) return
    h1.innerHTML = h1.textContent.trim().split(/\s+/).map((w, i) => `<span class="blur-w" style="--i:${i}">${w}</span>`).join(' ')
  })

  // Скользящая подложка у вкладок и переключателя
  const pill = (box, sel) => {
    const p = document.createElement('span')
    p.className = 'tab-pill'
    box.prepend(p); box.classList.add('has-pill')
    const place = () => {
      const a = $(sel, box)
      if (!a) return
      Object.assign(p.style, { left: a.offsetLeft + 'px', top: a.offsetTop + 'px', width: a.offsetWidth + 'px', height: a.offsetHeight + 'px' })
    }
    box.addEventListener('click', () => setTimeout(place, 0))
    addEventListener('resize', place)
    place()
  }
  $$('.tabs').forEach((t) => pill(t, '.tab[aria-selected="true"]'))
  $$('.twin-sw').forEach((t) => pill(t, 'button[aria-pressed="true"]'))

  // Шаги опроса перелистываются
  const qb = $('#quizBody')
  if (qb && !reduce) new MutationObserver(() => { const f = qb.firstElementChild; if (f) f.classList.add('q-anim') }).observe(qb, { childList: true })
  const quiz = $('.quiz'); if (quiz) quiz.classList.add('beam-border')

  // Цифры досчитываются при появлении
  const fmt = (v, d) => v.toLocaleString('ru-RU', { minimumFractionDigits: d, maximumFractionDigits: d })
  const ticker = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return
    ticker.unobserve(e.target)
    const el = e.target, to = Number(el.dataset.count), d = Number(el.dataset.dec || 0)
    if (reduce) { el.firstChild.textContent = fmt(to, d); return }
    const t0 = performance.now()
    const step = (t) => { const k = Math.min((t - t0) / 1600, 1); el.firstChild.textContent = fmt(to * ease(k), d); if (k < 1) requestAnimationFrame(step) }
    requestAnimationFrame(step)
  }), { threshold: 0.4 })
  $$('[data-count]').forEach((el) => ticker.observe(el))

  // Шаги приёма: активный шаг подсвечивается, фото справа меняется
  $$('.steps2').forEach((box) => {
    const steps = $$('.st-step', box), imgs = $$('.st-media img', box), dots = $$('.st-dots i', box)
    const cap = $('.st-cap b', box), line = $('.st-line', box)
    const set = (i) => {
      steps.forEach((s, k) => s.classList.toggle('on', k === i))
      imgs.forEach((s, k) => s.classList.toggle('on', k === i))
      dots.forEach((s, k) => s.classList.toggle('on', k === i))
      if (cap) cap.textContent = `Шаг ${i + 1} из ${steps.length}`
      if (line) line.style.transform = `scaleY(${(i + 1) / steps.length})`
    }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) set(steps.indexOf(e.target)) }), { rootMargin: '-45% 0px -45% 0px' })
    steps.forEach((s) => io.observe(s))
    set(0)
  })

  // Принцип центра: слова проявляются, пока текст прокручивается
  $$('.reveal-words').forEach((p) => {
    const words = p.textContent.trim().split(/\s+/)
    p.innerHTML = words.map((w) => `<span>${w}</span>`).join(' ')
    const spans = [...p.children]
    if (reduce) return
    const upd = () => {
      const r = p.getBoundingClientRect()
      const prog = Math.min(Math.max((innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.4), 0), 1)
      spans.forEach((s, i) => { s.style.opacity = Math.min(Math.max((prog * words.length - i), 0.15), 1) })
    }
    addEventListener('scroll', upd, { passive: true }); upd()
  })

  // Схема записи: лучи между узлами (идея Animated Beam из 21st.dev)
  $$('.flow-box').forEach((box) => {
    const svg = $('.beams', box)
    const node = (n) => $(`[data-node="${n}"] i`, box)
    const pairs = [['a', 'hub', -60, 4.2, 0], ['b', 'hub', 0, 3.6, 0.4], ['c', 'hub', 60, 4.6, 0.8], ['hub', 'x', -60, 4.2, 1.2], ['hub', 'y', 0, 3.8, 1.6], ['hub', 'z', 60, 4.4, 2]]
    const draw = () => {
      const br = box.getBoundingClientRect()
      svg.setAttribute('viewBox', `0 0 ${br.width} ${br.height}`)
      let html = ''
      pairs.forEach(([f, t, curve], k) => {
        const a = node(f).getBoundingClientRect(), b = node(t).getBoundingClientRect()
        const sx = a.left - br.left + a.width / 2, sy = a.top - br.top + a.height / 2
        const ex = b.left - br.left + b.width / 2, ey = b.top - br.top + b.height / 2
        const d = `M ${sx},${sy} Q ${(sx + ex) / 2},${sy - curve} ${ex},${ey}`
        html += `<defs><linearGradient id="bg${k}" gradientUnits="userSpaceOnUse" x1="${sx}" y1="${sy}" x2="${ex}" y2="${ey}"><stop offset="0" stop-color="#48F6FF"/><stop offset="1" stop-color="#F2FF59"/></linearGradient></defs><path class="base" d="${d}"/><path class="pulse" d="${d}" stroke="url(#bg${k})"/>`
      })
      svg.innerHTML = html
      if (reduce) return
      $$('.pulse', svg).forEach((p, k) => {
        const len = p.getTotalLength(), seg = Math.max(len * 0.22, 40)
        p.style.strokeDasharray = `${seg} ${len + seg}`
        p.animate([{ strokeDashoffset: seg }, { strokeDashoffset: -len }], { duration: pairs[k][3] * 1000, delay: pairs[k][4] * 1000, iterations: Infinity, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' })
      })
    }
    draw()
    new ResizeObserver(draw).observe(box)
  })

  // Врачи: карточка раскрывается в окно с биографией (Morphing Dialog)
  const BIO = {
    'Куделя Александр Павлович': ['Дагестанский государственный медицинский институт, лечебное дело (1979)', 'Переподготовка по эндоскопии — ГНЦ колопроктологии, Москва (1984)', 'Высшая квалификационная категория по эндоскопии (2004)', 'Повышение квалификации: РМАПО (1999, 2018), СПбМАПО (2009), ГНЦ колопроктологии (2014)'],
    'Нажмудинова Айшат Абдурахмановна': ['Первый МГМУ им. Сеченова, лечебное дело (2013)', 'Специализация по гастроэнтерологии — МГМСУ им. Евдокимова (2019)', 'Повышение квалификации по гастроэнтерологии и гепатологии — РНИМУ им. Пирогова (2023–2024)'],
    'Мусаева Эльмира Ашурбеговна': ['Лечебная гимнастика по методике SEAS (СИАС)', 'Ашхабадское медицинское училище (1994)', 'Северо-Кавказский государственный институт (2012)'],
    'Куделя Павел Александрович': ['Проводит авторские семинары по сухим иглам для специалистов'],
  }
  $$('.doc').forEach((card) => card.addEventListener('click', (e) => {
    if (e.target.closest('button')) return
    const name = $('b', card).textContent
    const ava = $('.ava', card).cloneNode(true)
    const overlay = document.createElement('div')
    overlay.className = 'dm-overlay'
    overlay.innerHTML = `<div class="dm-card" role="dialog" aria-modal="true" aria-label="${name}">
      <button class="dm-close" type="button" aria-label="Закрыть">×</button>
      <div class="dm-top"><span class="dm-ava"></span><div><b>${name}</b><div class="role">${$('.role', card).textContent}</div><p>${$('p', card).textContent}</p></div></div>
      <div class="dm-fade">${BIO[name] ? `<ul class="dm-bio">${BIO[name].map((l) => `<li>${l}</li>`).join('')}</ul>` : ''}
      <div class="dm-bot"><strong>${$('.doc-bot strong', card).innerHTML}</strong><button class="btn-deep" type="button" style="margin:0">Записаться к врачу</button></div></div></div>`
    $('.dm-ava', overlay).replaceWith(ava)
    document.body.appendChild(overlay)
    document.body.style.overflow = 'hidden'
    const dlg = $('.dm-card', overlay)
    const from = card.getBoundingClientRect(), to = dlg.getBoundingClientRect()
    const anim = (rev) => reduce ? null : dlg.animate([
      { transform: `translate(${from.left - to.left}px, ${from.top - to.top}px) scale(${from.width / to.width}, ${from.height / to.height})`, borderRadius: '26px', opacity: 0.6 },
      { transform: 'none', borderRadius: '32px', opacity: 1 },
    ], { duration: 420, easing: 'cubic-bezier(.22,1,.36,1)', direction: rev ? 'reverse' : 'normal', fill: 'both' })
    requestAnimationFrame(() => overlay.classList.add('on'))
    anim(false)
    $('.dm-close', overlay).focus()
    const close = () => {
      overlay.classList.remove('on')
      const a = anim(true)
      const done = () => { overlay.remove(); document.body.style.overflow = ''; removeEventListener('keydown', onKey) }
      a ? (a.onfinish = done) : done()
    }
    const onKey = (ev) => { if (ev.key === 'Escape') close() }
    addEventListener('keydown', onKey)
    overlay.addEventListener('click', (ev) => { if (ev.target === overlay || ev.target.closest('.dm-close')) close() })
  }))

  // Каталог услуг: картинка плывёт за курсором над строкой
  $$('.hlist').forEach((list) => {
    const wrap = list.parentElement, float = $('.hl-float', wrap), img = $('img', float)
    let tx = 0, ty = 0, x = 0, y = 0, raf = 0
    const loop = () => { x += (tx - x) * 0.18; y += (ty - y) * 0.18; float.style.left = x + 'px'; float.style.top = y + 'px'; raf = requestAnimationFrame(loop) }
    wrap.addEventListener('pointermove', (e) => { const r = wrap.getBoundingClientRect(); tx = e.clientX - r.left; ty = e.clientY - r.top })
    $$('li', list).forEach((li) => li.addEventListener('pointerenter', () => {
      img.src = li.dataset.img
      if (!float.classList.contains('on')) { x = tx; y = ty; float.classList.add('on'); list.classList.add('dim'); raf = requestAnimationFrame(loop) }
    }))
    list.addEventListener('pointerleave', () => { float.classList.remove('on'); list.classList.remove('dim'); cancelAnimationFrame(raf) })
  })

  // Мобильная панель записи появляется после первого экрана
  const dock = $('.dock')
  if (dock) { const upd = () => dock.classList.toggle('on', scrollY > 280); addEventListener('scroll', upd, { passive: true }); upd() }
})()
