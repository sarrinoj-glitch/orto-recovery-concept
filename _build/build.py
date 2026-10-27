"""Сборка многостраничной концепции из блоков одностраничной (_build/source.html).

Запуск из папки hero-v3:  python3 _build/build.py
Пишет index.html и папки страниц рядом, общие assets/site.css и assets/site.js.
Данные услуг, цен и заболеваний берутся из многостраничного Next.js-сайта (orto-recovery-site), чтобы версии не расходились.
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(ROOT), 'orto-recovery-site', 'src', 'lib')
SRC = open(os.path.join(HERE, 'source.html'), encoding='utf-8').read()

# ---------- данные из Next.js-версии ----------
def ts(name):
    return open(os.path.join(SITE, name), encoding='utf-8').read()

def q(s):
    return s.replace('\\\'', "'")

CONDITIONS = []
for m in re.finditer(r"id: '(\w+)',\s*label: '([^']+)',\s*items: \[(.*?)\]", ts('content.ts'), re.S):
    CONDITIONS.append((m.group(1), m.group(2), re.findall(r"'([^']+)'", m.group(3))))

SERVICES = []
nav_ts = ts('nav.ts')
nav_ts = nav_ts[nav_ts.index('export const SERVICES'):]
for block in re.findall(r"\{\s*slug: .*?chat: '[^']*',\s*\}", nav_ts, re.S):
    g = lambda k: re.search(k + r": '([^']*)'", block).group(1)
    SERVICES.append({
        'slug': g('slug'), 'menu': g('menu'), 'kicker': g('kicker'), 'title': g('title'), 'lead': g('lead'),
        'photo': g('photo').replace('/photos/', 'assets/'), 'alt': g('photoAlt'),
        'doctors': re.findall(r"'([^']+)'", re.search(r"doctors: \[(.*?)\]", block).group(1)),
        'prices': re.findall(r"\['([^']+)', '([^']+)'\]", re.search(r"prices: \[(.*?)\],\n", block, re.S).group(1)),
        'conditions': re.findall(r"'(\w+)'", re.search(r"conditions: \[(.*?)\]", block).group(1)),
        'extras': re.findall(r"'(\w+)'", re.search(r"extras: \[(.*?)\]", block).group(1)),
    })

PRICE_GROUPS = []
clinic = ts('clinic.ts')
pg = clinic[clinic.index('export const PRICE_GROUPS'):clinic.index('// Экскурсия')]
for m in re.finditer(r"title: '([^']+)',\s*items: \[(.*?)\],\s*\}", pg, re.S):
    PRICE_GROUPS.append((m.group(1), re.findall(r"name: '([^']+)', price: '([^']+)'", m.group(2))))

assert len(SERVICES) == 8 and len(CONDITIONS) == 5 and len(PRICE_GROUPS) == 4, (len(SERVICES), len(CONDITIONS), len(PRICE_GROUPS))

# ---------- блоки исходной страницы ----------
def section(sid):
    m = re.search(r'<section[^>]*id="%s"[^>]*>.*?</section>' % sid, SRC, re.S)
    return m.group(0)

HERO = re.search(r'<header class="hero">.*?</header>', SRC, re.S).group(0)
FINDER = re.search(r'<section class="finder">.*?</section>', SRC, re.S).group(0)
FINAL = re.search(r'<footer class="final".*?</footer>', SRC, re.S).group(0)
NOTE = re.search(r'<p class="note".*?</p>', SRC, re.S).group(0)
DICT = json.loads(re.search(r'const NEW = (\{.*?\})\n', SRC).group(1))['dict']
DOCS = {m.group(1): m.group(0) for m in re.finditer(r'<article class="doc[^"]*"[^>]*>.*?<b>([^<]+)</b>.*?</article>', section('doctors'), re.S)}

CARD_LINKS = ['spina', 'ortopediya', 'ortopediya', 'ortopediya', 'reabilitaciya']

def cards_section():
    s = section('where')
    for slug in CARD_LINKS:
        s = s.replace('<article class="card rv"', '<a class="card rv" href="{P}uslugi/%s/"' % slug, 1)
    s = s.replace('</article>', '</a>')
    s = s.replace('<button class="plus" type="button" aria-label="Подробнее">+</button>', '<span class="plus" aria-hidden="true">+</span>')
    s = s.replace('<div class="arrows">', '<div style="display:flex;gap:18px;align-items:center"><a class="sec-link" href="{P}uslugi/">Все услуги →</a><div class="arrows">', 1)
    s = s.replace('</button></div>\n    </div>\n    <div class="cards"', '</button></div></div>\n    </div>\n    <div class="cards"', 1)
    return s

def methods_section():
    s = section('methods')
    return re.sub(r'<button type="button" aria-pressed="false">([^<]+)</button>',
                  lambda m: '<button type="button" aria-pressed="false" data-text="%s">%s</button>' % (DICT[m.group(1)], m.group(1)), s)

def fix(html, P):
    html = html.replace('{P}', P)
    html = html.replace('src="assets/', 'src="%sassets/' % P)
    html = html.replace('href="#where"', 'href="%suslugi/"' % P)
    html = html.replace('href="#doctors"', 'href="%svrachi/"' % P)
    html = html.replace('box-shadow:0 8px 20px -10px rgba(11,61,74,.4)" href="#"', 'box-shadow:0 8px 20px -10px rgba(11,61,74,.4)" href="%svrachi/"' % P)
    html = html.replace('data-go="#conditions"', 'data-go="%suslugi/reabilitaciya/"' % P)
    html = html.replace('data-go="#sport"', 'data-go="%suslugi/reabilitaciya/#sport"' % P)
    return html

# ---------- общая шапка ----------
NAV = [('', 'Главная'), ('o-centre/', 'О центре'), ('uslugi/', 'Услуги'), ('vrachi/', 'Врачи'), ('ceny/', 'Цены'), ('pacientam/', 'Пациентам'), ('kontakty/', 'Контакты')]
CHEV = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
BURGER = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

def nav(P, active):
    links = []
    for href, label in NAV:
        on = ' class="on"' if href == active else ''
        if href == 'uslugi/':
            panel = ''.join('<a href="%suslugi/%s/">%s<span>%s</span></a>' % (P, s['slug'], s['menu'], s['prices'][0][1]) for s in SERVICES)
            links.append('<div class="mm"><a href="%suslugi/"%s>Услуги %s</a><div class="mm-panel svc">%s</div></div>' % (P, on, CHEV, panel))
        else:
            links.append('<a href="%s%s"%s>%s</a>' % (P, href, on, label))
    mob = ''.join('<a href="%s%s"%s>%s</a>' % (P, h, ' class="on"' if h == active else '', l) for h, l in NAV if h != 'uslugi/')
    mob_svc = ''.join('<a href="%suslugi/%s/">%s<span>%s</span></a>' % (P, s['slug'], s['menu'], s['prices'][0][1]) for s in SERVICES)
    return '''<nav class="nav" aria-label="Основное меню">
      <a class="logo" href="%(P)s"><img src="%(P)sassets/logo-dark.png" alt="Орто-Рекавери"></a>
      <div class="nav-links">%(links)s</div>
      <div class="nav-right">
        <a class="phone" href="tel:+78722522333">+7 (8722) 52-23-33<small>пн–пт 9–18, сб 9–16</small></a>
        <button class="btn-white" type="button">Записаться</button>
        <button class="burger" type="button" aria-expanded="false" aria-label="Открыть меню">%(burger)s</button>
      </div>
    </nav>
    <div class="mnav" hidden>%(mob)s<p>Услуги</p><div class="sub">%(mob_svc)s</div><button type="button">Записаться</button></div>''' % {
        'P': P, 'links': ''.join(links), 'burger': BURGER, 'mob': mob, 'mob_svc': mob_svc}

def page_head(P, active, kicker, title, lead, crumbs=None):
    cr = ''
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Хлебные крошки"><a href="%s">Главная</a>%s</nav>' % (P, ''.join(
            '<span><a href="%s%s">%s</a></span>' % (P, h, l) if h is not None else '<span>%s</span>' % l for h, l in crumbs))
    return '''<header class="phead"><div class="wrap">
    %s
    <div class="phead-in">%s<p class="kicker">%s</p><h1>%s</h1>%s</div>
  </div></header>''' % (nav(P, active), cr, kicker, title, '<p class="lead">%s</p>' % lead if lead else '')

def doc_html(P, title, desc, body):
    return '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s</title>
<meta name="description" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700;800&family=Unbounded:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%sassets/site.css">
</head>
<body data-p="%s">
%s
%s
%s
%s
<script src="%sassets/site.js"></script>
</body>
</html>
''' % (title, desc, P, P, fix(body, P), fix(FINAL, P), NOTE, dock(P), P)

def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(html)

# ---------- общие блоки ----------
def conds_block(ids, title='С чем к нам приходят'):
    items = [c for c in CONDITIONS if c[0] in ids] if ids else CONDITIONS
    tabs = ''.join('<button class="tab" role="tab" aria-selected="%s" data-tab="%s">%s</button>' % ('true' if i == 0 else 'false', c[0], c[1]) for i, c in enumerate(items))
    lists = ''.join('<ul class="cond-list" data-panel="%s"%s>%s</ul>' % (c[0], '' if i == 0 else ' hidden', ''.join('<li>%s</li>' % x for x in c[2])) for i, c in enumerate(items))
    return '''<section class="sec"><div class="wrap">
    <div class="sec-head rv"><div><p class="kicker">С чем работаем</p><h2>%s</h2></div></div>
    <div class="conds rv">%s%s
      <div class="cond-foot"><span>Не нашли свой диагноз? Напишите — администратор подскажет, к какому врачу идти.</span><button class="btn-deep" type="button" style="margin:0">Спросить администратора</button></div>
    </div></div></section>''' % (title, '<div class="tabs" role="tablist">%s</div>' % tabs if len(items) > 1 else '', lists)

def prices_teaser():
    top = [('Травматолог-ортопед', '3 000 ₽'), ('Невролог, полный приём', '8 000 ₽'), ('Ударно-волновая терапия', '3 000 ₽'), ('PRP-терапия', '10 500 ₽'), ('ЛФК, 60 минут', '2 500 ₽'), ('Гастроскопия во сне', '6 000 ₽')]
    return '''<section><div class="wrap"><div class="tease rv">
    <div><p class="kicker">Цены</p><h2>Цену вы знаете до начала лечения</h2><p>Прайс центра на ПроДокторов от 19.10.2026. Есть рассрочка без переплат и справка для налогового вычета.</p><a class="btn-lime" href="{P}ceny/">Весь прайс →</a></div>
    <ul>%s</ul></div></div></section>''' % ''.join('<li><span>%s</span><b>%s</b></li>' % x for x in top)

EXTRA = {
    'second': lambda: section('second'), 'twin': lambda: section('twin'), 'glossary': methods_section, 'procedures': methods_section,
    'prp': lambda: section('prp'), 'sport': lambda: section('sport'), 'after': lambda: section('after'), 'home': lambda: section('perks'),
    'endoscopy': lambda: section('sleep'), 'family': lambda: section('perks'), 'whole': lambda: section('whole'),
}


# ---------- новые блоки второго круга (как в React-версиях) ----------
ICON = {
    'globe': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#177E96" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
    'chat': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#25D366" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8.5 8.5 0 0 1-12.6 7.4L3 21l1.6-5.2A8.5 8.5 0 1 1 21 12z"/></svg>',
    'phone': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#177E96" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    'steth': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0B3D4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3v6a5 5 0 0 0 10 0V3M10 14v2a5 5 0 0 0 10 0v-2"/><circle cx="20" cy="12" r="2"/></svg>',
    'cal': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0B3D4A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18M9 16l2 2 4-4"/></svg>',
    'bell': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#C2563A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>',
}

def stats_html():
    items = [(5, 1, '', 'рейтинг в 2ГИС'), (121, 0, '', 'оценка пациентов'), (4.9, 1, '', 'на Яндекс Картах'), (30, 0, ' лет', 'стаж эндоскописта высшей категории'), (23, 0, '', 'методики восстановления'), (8, 0, '', 'направлений в одном центре')]
    li = ''.join('<li><b data-count="%s" data-dec="%d">0%s</b><span>%s</span></li>' % (v, d, '<small>%s</small>' % suf if suf else '', lab) for v, d, suf, lab in items)
    return '<section><div class="wrap"><div class="cstats beam-border rv"><ul>%s</ul></div></div></section>' % li

STEPS2 = [('Расскажите, что беспокоит', 'Врач собирает жалобы и историю: когда началось, что усиливает боль, были ли травмы и операции.', 'g-ortho.jpg'),
          ('Осмотр и простой тест', 'Врач смотрит, как двигается сустав или спина, и проводит несложный физический тест.', 'g-explain.jpg'),
          ('Разбираем снимки', 'МРТ, рентген, заключения — врач объяснит простыми словами, что на них видно.', 'g-mri.jpg'),
          ('План лечения и цена', 'Вы получаете курс процедур и знаете, сколько он стоит, до начала лечения.', 'c-shoulder.jpg')]

def steps_html():
    li = ''.join('<li class="st-step"><span class="n">%d</span><h3>%s</h3><p>%s</p><img src="assets/%s" alt="" loading="lazy"></li>' % (i + 1, t, d, img) for i, (t, d, img) in enumerate(STEPS2))
    imgs = ''.join('<img src="assets/%s" alt="%s"%s>' % (img, t, ' class="on"' if i == 0 else '') for i, (t, d, img) in enumerate(STEPS2))
    dots = ''.join('<i%s></i>' % (' class="on"' if i == 0 else '') for i in range(len(STEPS2)))
    return ('<section class="sec"><div class="wrap">'
            '<div class="sec-head rv"><div><p class="kicker">Как проходит приём</p><h2>Четыре шага до плана лечения</h2></div></div>'
            '<div class="steps2"><ol class="st-list"><span class="st-line" aria-hidden="true"></span>%s</ol>'
            '<div><div class="st-media">%s<div class="st-cap"><b>Шаг 1 из 4</b><span class="st-dots">%s</span></div></div></div></div>'
            '</div></section>') % (li, imgs, dots)

def manifesto_html():
    return ('<section class="manifesto"><div class="wrap"><p class="kicker">Принцип центра</p>'
            '<p class="reveal-words">Для двух пациентов с одинаковым диагнозом нельзя использовать одну и ту же программу: для одного она будет слишком лёгкой, для другого — невыполнимой. Поэтому план лечения мы составляем под вас.</p></div></section>')

def flow_html():
    n = lambda key, icon, label, hub=False: '<div class="fnode%s" data-node="%s"><i>%s</i><span>%s</span></div>' % (' hub' if hub else '', key, icon, label)
    return ('<section class="sec"><div class="wrap"><div class="flow">'
            '<div class="rv"><p class="kicker">Запись без ожидания на линии</p><h2>Пишете куда удобно — администратор сделает остальное</h2>'
            '<p class="lead" style="color:var(--muted)">Сайт, WhatsApp или звонок: администратор подберёт врача, запишет на свободное время и напомнит о визите накануне.</p>'
            '<small>Пример того, как работает ИИ-администратор центра.</small>'
            '<button class="btn-deep" type="button">Попробовать — написать</button></div>'
            '<div class="flow-box rv"><svg class="beams" aria-hidden="true"></svg>'
            '<div class="flow-col">%s%s%s</div>%s<div class="flow-col">%s%s%s</div></div>'
            '</div></div></section>') % (n('a', ICON['globe'], 'Сайт'), n('b', ICON['chat'], 'WhatsApp'), n('c', ICON['phone'], 'Звонок'),
                                         n('hub', '<img src="assets/logo-dark.png" alt="">', 'Администратор', True),
                                         n('x', ICON['steth'], 'Подбор врача'), n('y', ICON['cal'], 'Запись на время'), n('z', ICON['bell'], 'Напоминание накануне'))

def marquee_html():
    names = list(DICT.keys()); half = (len(names) + 1) // 2
    row = lambda ns, rev, dur: '<div class="mq%s" style="--dur:%ds">%s</div>' % (' rev' if rev else '', dur, ''.join('<div class="mq-track"%s>%s</div>' % (' aria-hidden="true"' if k else '', ''.join('<span>%s</span>' % x for x in ns)) for k in range(2)))
    return ('<section class="mq-sec"><div class="wrap"><div class="sec-head rv"><div><p class="kicker">Методы</p><h2>23 методики восстановления в одном центре</h2></div>'
            '<a class="sec-link" href="{P}uslugi/fizioterapiya/">Что это за методики →</a></div></div>%s%s</section>') % (row(names[:half], False, 55), row(names[half:], True, 60))

def hover_list_html():
    li = ''.join('<li data-img="{P}%s"><a href="{P}uslugi/%s/"><span style="display:flex;align-items:baseline;gap:24px"><span class="num">%02d</span><span class="t">%s</span></span>'
                 '<span style="display:flex;align-items:center;gap:20px"><span class="k">%s</span><span class="p">%s</span></span></a></li>' % (s['photo'], s['slug'], i + 1, s['menu'], s['kicker'], s['prices'][0][1]) for i, s in enumerate(SERVICES))
    return '<section><div class="wrap"><div style="position:relative"><ul class="hlist">%s</ul><div class="hl-float" aria-hidden="true"><img alt="" src="{P}%s"></div></div></div></section>' % (li, SERVICES[0]['photo'])

def dock(P):
    small = lambda k: ICON[k].replace('width="24" height="24"', 'width="18" height="18"')
    return ('<nav class="dock" aria-label="Быстрая запись"><a href="tel:+78722522333">%s Позвонить</a>'
            '<a href="https://wa.me/79883011805" target="_blank" rel="noreferrer">%s WhatsApp</a><a class="main" href="%s#quiz">Записаться</a></nav>') % (small('phone'), small('chat'), P)


# ---------- страницы ----------
def build():
    css = re.search(r'<style>(.*?)</style>', SRC, re.S).group(1) + open(os.path.join(HERE, 'motion.css'), encoding='utf-8').read()
    open(os.path.join(ROOT, 'assets', 'site.css'), 'w', encoding='utf-8').write(css + open(os.path.join(HERE, 'pages.css'), encoding='utf-8').read())
    open(os.path.join(ROOT, 'assets', 'site.js'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'site.js'), encoding='utf-8').read() + open(os.path.join(HERE, 'motion.js'), encoding='utf-8').read())

    # главная
    hero = re.sub(r'<nav class="nav".*?</nav>', lambda m: nav('', ''), HERO, flags=re.S)
    home = '\n'.join([hero, FINDER, section('start'), stats_html(), cards_section(), steps_html(), manifesto_html(), section('second'), section('doctors'), flow_html(), marquee_html(), section('trust'), prices_teaser()])
    write('index.html', doc_html('', 'Орто-Рекавери — центр восстановительной медицины в Махачкале', 'Лечим боль в спине и суставах без операции: ортопед, невролог, реабилитация и ЛФК, физиотерапия, PRP, эндоскопия во сне.', home))

    # услуги
    cards = ''.join('<a href="{P}uslugi/%s/"><img src="assets/%s" alt="%s"><span><b>%s</b><em>%s</em><i>%s →</i></span></a>' % (s['slug'], s['photo'][7:], s['alt'], s['menu'], s['lead'], s['prices'][0][1]) for s in SERVICES)
    body = page_head('../', 'uslugi/', 'Услуги', 'Что мы лечим', 'Восемь направлений в одном центре: от консультации ортопеда до обследования во сне. Выберите своё или подберите врача за три вопроса.', [(None, 'Услуги')])
    body += hover_list_html() + '<section class="mob-only"><div class="wrap"><div class="svc-cards">%s</div></div></section>' % cards + section('start') + marquee_html()
    write('uslugi/index.html', doc_html('../', 'Услуги — Орто-Рекавери', 'Ортопедия, лечение спины, реабилитация и ЛФК, физиотерапия, PRP, эндоскопия во сне, детская реабилитация.', body))

    for s in SERVICES:
        P = '../../'
        docs = ''.join(DOCS[n] for n in s['doctors'] if n in DOCS)
        top = '''<header class="phead"><div class="wrap">%s
      <div class="svc-top"><div class="phead-in">
        <nav class="crumbs" aria-label="Хлебные крошки"><a href="%s">Главная</a><span><a href="%suslugi/">Услуги</a></span><span>%s</span></nav>
        <p class="kicker">%s</p><h1>%s</h1><p class="lead">%s</p>
        <div class="svc-cta"><button class="btn-main" type="button">Записаться</button><span>%s — <b>%s</b></span></div>
      </div><img src="%s" alt="%s"></div>
    </div></header>''' % (nav(P, 'uslugi/'), P, P, s['menu'], s['kicker'], s['title'], s['lead'], s['prices'][0][0], s['prices'][0][1], s['photo'], s['alt'])
        grid = '''<section><div class="wrap"><div class="svc-grid">
      <div class="pcard rv"><h2>Цены</h2><ul class="plist2">%s</ul><small>Прайс центра на ПроДокторов от 19.10.2026. <a href="%sceny/">Все цены</a></small></div>
      <div class="dcard rv"><h2>%s</h2>%s</div>
    </div></div></section>''' % (''.join('<li><span>%s</span><b>%s</b></li>' % p for p in s['prices']), P, 'Ведут приём' if len(s['doctors']) > 1 else 'Ведёт приём', docs)
        seen, extras = set(), []
        for e in s['extras']:
            html = EXTRA[e]()
            if html not in seen:
                seen.add(html); extras.append(html)
        others = ''.join('<a href="%suslugi/%s/">%s</a>' % (P, o['slug'], o['menu']) for o in SERVICES if o['slug'] != s['slug'])
        body = top + grid + (conds_block(s['conditions']) if s['conditions'] else '') + '\n'.join(extras)
        body += '<section class="sec"><div class="wrap"><h2 style="font-size:28px">Другие направления</h2><div class="others">%s</div></div></section>' % others
        write('uslugi/%s/index.html' % s['slug'], doc_html(P, '%s — Орто-Рекавери, Махачкала' % s['menu'], s['lead'], body))

    # разделы
    P = '../'
    pages = {
        'o-centre/': ('О центре', 'Центр восстановительной медицины «Орто-Рекавери»', 'Лечим и восстанавливаем пациентов с заболеваниями и травмами опорно-двигательной системы — без операций, по принципам доказательной медицины.',
                      [stats_html(), manifesto_html(), section('founders'), section('how'), section('trust'), section('tour'), section('stories')]),
        'vrachi/': ('Специалисты', 'Врачи центра', 'Можно записаться к конкретному врачу. Если вам спокойнее со специалистом-женщиной, скажите об этом администратору.',
                    [section('doctors')]),
        'ceny/': ('Цены', 'Цену вы знаете до начала лечения', 'Прайс центра на ПроДокторов от 19.10.2026. Есть рассрочка без переплат и справка для налогового вычета.',
                  ['<section><div class="wrap"><div class="pgroups">%s</div></div></section>' % ''.join(
                      '<div class="pcard rv"><h2>%s</h2><ul class="plist2">%s</ul></div>' % (t, ''.join('<li><span>%s</span><b>%s</b></li>' % i for i in items)) for t, items in PRICE_GROUPS),
                   section('perks')]),
        'pacientam/': ('Пациентам', 'Всё, что нужно знать до визита', 'Как проходит первый приём, что взять с собой, как получить второе мнение и вызвать реабилитолога на дом.',
                       [steps_html(), section('prep'), flow_html(), section('wa'), section('second'), section('perks')]),
        'kontakty/': ('Контакты', 'Как нас найти', 'Махачкала, проспект Имама Шамиля, 35А, 1 этаж. Вход за шлагбаумом, рядом санаторий «Тарнаир».',
                      ['<section><div class="wrap"><div class="cpage">%s</div></div></section>' % re.search(r'<div class="contacts">(.*)</div>\s*<p class="legal">', FINAL, re.S).group(1).replace('rv"', '"')]),
    }
    for href, (kicker, title, lead, blocks) in pages.items():
        label = dict(NAV)[href]
        body = page_head(P, href, kicker, title, lead, [(None, label)]) + '\n'.join(blocks)
        write(href + 'index.html', doc_html(P, '%s — Орто-Рекавери, Махачкала' % label, lead, body))
    print('ok:', 2 + len(SERVICES) + len(pages), 'pages')

build()
