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
    back: { t: 'Спина и шея', who: 'Магомедов Муслим Абдулла-Гаджиевич', role: 'инструктор по лечебной физкультуре, мануальный терапевт', ini: 'ММ', price: 'от 2 000 ₽', pl: 'занятие', slug: 'spina' },
    knee: { t: 'Колено и тазобедренный сустав', who: 'Хаджалов Абузар Магомедович', role: 'травматолог-ортопед', ini: 'ХА', price: 'до 3 000 ₽', pl: 'приём', slug: 'koleno' },
    arm: { t: 'Плечо, локоть, кисть', who: 'Хаджалов Абузар Магомедович', role: 'травматолог-ортопед, кистевой реабилитолог', ini: 'ХА', price: 'до 3 000 ₽', pl: 'приём', slug: 'plecho' },
    foot: { t: 'Стопа и пятка', who: 'Хаджалов Абузар Магомедович', role: 'травматолог-ортопед', ini: 'ХА', price: 'до 3 000 ₽', pl: 'приём', slug: 'stopa' },
    kids: { t: 'Ребёнок: осанка, сколиоз', who: 'Мусаева Эльмира Ашурбеговна', role: 'инструктор по лечебной физкультуре и методике СИАС', ini: 'МЭ', price: 'от 2 000 ₽', pl: 'занятие', slug: 'detyam' },
    endo: { t: 'Желудок и кишечник', who: 'Нажмудинова Айшат Абдурахмановна', role: 'терапевт-гастроэнтеролог', ini: 'НА', price: 'до 3 000 ₽', pl: 'приём', slug: '' },
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
    const note = qa.why === 'surgery' ? 'После операции врач составит план реабилитации и передаст вас инструктору лечебной физкультуры.' : qa.why === 'trauma' ? 'Возьмите снимки после травмы — врач разберёт их на приёме.' : qa.when === 'long' ? 'Боль дольше полугода — врач найдёт причину и составит курс, а не просто снимет симптом.' : 'Чем раньше начать, тем короче обычно восстановление.'
    qb.innerHTML = `<div class="q-result"><div class="who"><span class="ava" style="width:52px;height:52px;border-radius:16px;font-size:17px;background:var(--lime);color:var(--graphite)">${a.ini}</span><div><b>${a.who}</b><small>${a.role}</small></div></div><p><b style="color:var(--deep)">${a.t}.</b> ${note}</p><div class="row"><strong>${a.price} <small style="font-size:14px;font-weight:500;color:var(--muted)">${a.pl}</small></strong><span style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn-ghost-d" href="${P}${a.slug ? `uslugi/${a.slug}/` : 'vrachi/'}">Об услуге</a><button class="btn-deep" type="button" style="margin:0"${a.guest ? ` data-lead="${a.guest}"` : ''}>${a.guest ? 'Узнать о приезде' : 'Записаться'}</button></span></div></div><button class="q-again" type="button">↺ Пройти заново</button>`
    qb.querySelector('.q-again').addEventListener('click', () => { qa = {}; qi = 0; render() })
  }
  render()
}

// Один диагноз — две программы
if ($('#twPlan')) {
  const TW = {
    a: { who: 'Офисный сотрудник, 45 лет', why: 'Сидячая работа, боль усиливается к вечеру. Цель — работать без боли.', load: 30, plan: [['1–2 неделя', 'Снять острую боль: щадящие процедуры по назначению невролога'], ['3–4 неделя', 'Лечебная физкультура с минимальной нагрузкой: упражнения на стабилизацию спины'], ['5–8 неделя', 'Постепенно укрепляем мышцы корпуса'], ['Дальше', 'План домашних занятий и контрольный осмотр']] },
    b: { who: 'Борец, 24 года', why: 'Тренируется 6 раз в неделю, боль после схватки. Цель — вернуться на ковёр.', load: 75, plan: [['1–2 неделя', 'Работа с болью и мышечным спазмом: физиотерапия, массаж'], ['3–6 неделя', 'Силовая лечебная физкультура: возвращаем нагрузку под контролем врача'], ['7–10 неделя', 'Специальные упражнения под технику борьбы'], ['Дальше', 'Поэтапный возврат к тренировкам на ковре']] },
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

// Заявка на приём: любая кнопка «Записаться…» открывает форму.
// Заявка уходит на orto-lead-api (Vercel) → WhatsApp администратора через API;
// если сервер недоступен — кнопка «Отправить через WhatsApp» с готовым текстом.
const WA = 'https://wa.me/79883011805'
const LEAD_API = 'https://orto-lead-api.vercel.app/api/lead'
const leadBox = document.createElement('div')
leadBox.className = 'lead-ov'
leadBox.hidden = true
leadBox.innerHTML = `<div class="lead" role="dialog" aria-modal="true" aria-labelledby="leadTitle">
  <button type="button" class="lead-x" aria-label="Закрыть">✕</button>
  <form class="lead-form" novalidate>
    <h2 id="leadTitle">Запись на приём</h2>
    <p class="lead-sub">Администратор перезвонит, подберёт врача и удобное время.</p>
    <label>Имя<input name="name" autocomplete="name"></label><div class="err" data-err="name" hidden>Как к вам обращаться?</div>
    <label>Номер телефона<input name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__"></label><div class="err" data-err="phone" hidden>Проверьте номер — нужно 10–11 цифр</div>
    <label>Что беспокоит?<textarea name="what" rows="3" placeholder="Например: болит колено при ходьбе"></textarea></label>
    <fieldset><legend>Как давно?</legend><div class="lead-chips" data-name="when"><button type="button">До двух недель</button><button type="button">От месяца до полугода</button><button type="button">Больше полугода</button></div></fieldset>
    <fieldset><legend>Была травма или операция?</legend><div class="lead-chips" data-name="why"><button type="button">Да, травма</button><button type="button">Да, операция</button><button type="button">Нет</button></div></fieldset>
    <label class="pd-consent"><input type="checkbox" name="pd"><span>Даю <a href="${P}dokumenty/soglasie/" target="_blank">согласие на обработку персональных данных</a>, ознакомлен(а) с <a href="${P}dokumenty/politika/" target="_blank">Политикой</a></span></label><div class="err" data-err="pd" hidden>Отметьте согласие, чтобы отправить заявку</div>
    <input name="company" tabindex="-1" autocomplete="off" aria-hidden="true" class="lead-trap">
    <button type="submit" class="lead-go">Отправить заявку</button>
  </form>
  <div class="lead-done" hidden><h2>Заявка отправлена</h2><p>Администратор свяжется с вами, чтобы подобрать врача и время. Если срочно — позвоните: <a href="tel:+78722522333">+7 (8722) 52-23-33</a></p><button type="button" class="lead-go lead-close">Готово</button></div>
  <div class="lead-fb" hidden><h2>Отправьте заявку в WhatsApp</h2><p>Не получилось отправить заявку напрямую. Нажмите кнопку — откроется WhatsApp центра с готовым текстом, останется нажать «Отправить».</p><a class="lead-go lead-wa" target="_blank" rel="noreferrer">Отправить через WhatsApp</a><p>Или позвоните: <a href="tel:+78722522333">+7 (8722) 52-23-33</a></p></div>
</div>`
document.body.appendChild(leadBox)
const lf = leadBox.querySelector('.lead-form'), ld = leadBox.querySelector('.lead-done'), lfb = leadBox.querySelector('.lead-fb')
const F = (n) => lf.querySelector(`[name=${n}]`)
const leadClose = () => { leadBox.hidden = true; document.body.style.overflow = '' }
function openLead(ctx, phone) {
  lf.hidden = false; ld.hidden = true; lfb.hidden = true
  if (ctx && !F('what').value) F('what').value = ctx
  if (phone && !F('phone').value) F('phone').value = phone
  leadBox.querySelectorAll('.err').forEach((e) => { e.hidden = true })
  leadBox.hidden = false; document.body.style.overflow = 'hidden'
  setTimeout(() => F('name').focus(), 50)
}
leadBox.addEventListener('click', (e) => { if (e.target === leadBox || e.target.closest('.lead-x, .lead-close')) leadClose() })
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !leadBox.hidden) leadClose() })
leadBox.querySelectorAll('.lead-chips button').forEach((b) => b.addEventListener('click', () => {
  const on = b.getAttribute('aria-pressed') === 'true'
  b.parentElement.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', 'false'))
  b.setAttribute('aria-pressed', on ? 'false' : 'true')
}))
lf.addEventListener('submit', async (e) => {
  e.preventDefault()
  const name = F('name').value.trim(), phone = F('phone').value.trim(), digits = phone.replace(/\D/g, '')
  const bad = { name: name.length < 2, phone: digits.length < 10 || digits.length > 12, pd: !F('pd').checked }
  Object.entries(bad).forEach(([k, v]) => { leadBox.querySelector(`[data-err="${k}"]`).hidden = !v })
  if (bad.name || bad.phone || bad.pd) return
  const pick = (n) => { const b = leadBox.querySelector(`[data-name="${n}"] [aria-pressed="true"]`); return b ? b.textContent : '' }
  const text = ['Заявка на приём с сайта', `Имя: ${name}`, `Телефон: ${phone}`,
    F('what').value.trim() && `Что беспокоит: ${F('what').value.trim()}`, pick('when') && `Как давно: ${pick('when')}`, pick('why') && `Травма или операция: ${pick('why')}`].filter(Boolean).join('\n')
  const go = lf.querySelector('.lead-go')
  if (go.disabled) return
  go.disabled = true; go.textContent = 'Отправляем…'
  let ok = false
  try {
    // text/plain — без предварительного CORS-запроса
    const r = await fetch(LEAD_API, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, signal: AbortSignal.timeout(10000),
      body: JSON.stringify({ name, phone, what: F('what').value.trim(), when: pick('when'), why: pick('why'), consent: true, company: F('company').value, page: location.pathname }) })
    ok = r.ok
  } catch { ok = false }
  go.disabled = false; go.textContent = 'Отправить заявку'
  lf.hidden = true
  if (ok) ld.hidden = false
  else { lfb.querySelector('.lead-wa').href = `${WA}?text=${encodeURIComponent(text)}`; lfb.hidden = false }
})
// Все CTA: кнопки со словом «запис…» и ссылки с data-lead
document.addEventListener('click', (e) => {
  const el = e.target.closest('button, a[data-lead]')
  if (!el || el.closest('.lead-ov') || !(el.matches('[data-lead]') || /запис/i.test(el.textContent))) return
  e.preventDefault(); e.stopPropagation()
  const doc = el.closest('.doc, .dm-card')
  openLead(el.dataset.lead || (doc ? `Хочу записаться к врачу: ${doc.querySelector('b').textContent}` : ''))
}, true)

// Памятка: номер переносим в форму заявки
const mf = $('#magnetForm')
if (mf) mf.addEventListener('submit', (e) => { e.preventDefault(); openLead('Хочу памятку «5 правил, чтобы спина не болела»', $('#magnetPhone').value.trim()) })

// Шаги «Как лечим» подсвечиваются по очереди
const stepsList = $$('.steps li')
if (stepsList.length && !reduce) {
  let s = 0
  setInterval(() => { stepsList[s].classList.remove('on'); s = (s + 1) % stepsList.length; stepsList[s].classList.add('on') }, 2600)
}

// ===== Блог: фильтр по темам =====
;(() => {
  const chips = $$('.bl-chips button')
  if (!chips.length) return
  const cards = $$('.bl-grid .bl-card')
  chips.forEach((c) => c.addEventListener('click', () => {
    chips.forEach((x) => x.classList.toggle('on', x === c))
    cards.forEach((card, i) => {
      card.hidden = !!c.dataset.cat && card.dataset.cat !== c.dataset.cat
      card.classList.toggle('big', !c.dataset.cat && i === 0)
    })
  }))
})()
