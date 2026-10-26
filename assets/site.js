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
