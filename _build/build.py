"""Сборка многостраничной концепции из блоков одностраничной (_build/source.html).

Запуск из папки hero-v3:  python3 _build/build.py
Пишет index.html и папки страниц рядом, общие assets/site.css и assets/site.js.
Данные услуг, цен и заболеваний берутся из многостраничного Next.js-сайта (orto-recovery-site), чтобы версии не расходились.
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(os.path.dirname(ROOT), 'orto-recovery-site', 'src', 'lib')
SRC = open(os.path.join(HERE, 'source.html'), encoding='utf-8').read()
# юридический пакет — общий источник для всех версий сайта (orto-recovery/legal/docs.py)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), 'legal'))
from docs import DOCS as LEGAL_DOCS, ORG as LEGAL_ORG, GROUPS as LEGAL_GROUPS, UPDATED as LEGAL_UPDATED  # noqa: E402
# статьи блога — общий источник (orto-recovery/blog/posts.py)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), 'blog'))
from posts import POSTS as BLOG_POSTS, CATEGORIES as BLOG_CATEGORIES  # noqa: E402

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
        'slug': g('slug'), 'menu': g('menu'), 'kind': g('kind'), 'price': (re.search(r"\n    price: '([^']*)'", block) or [None, None])[1], 'kicker': g('kicker'), 'title': g('title'), 'lead': g('lead'),
        'photo': g('photo').replace('/photos/', 'assets/'), 'alt': g('photoAlt'),
        'doctors': re.findall(r"'([^']+)'", re.search(r"doctors: \[(.*?)\]", block).group(1)),
        'prices': re.findall(r"\['([^']+)', '([^']+)'\]", re.search(r"prices: \[(.*?)\],\n", block, re.S).group(1)),
        'conditions': re.findall(r"'(\w+)'", re.search(r"conditions: \[(.*?)\]", block).group(1)),
        'extras': re.findall(r"'(\w+)'", re.search(r"extras: \[(.*?)\]", block).group(1)),
    })

# Вкладка «Услуги» в меню — список услуг с ценами (SERVICE_MENU в nav.ts)
SERVICE_MENU = re.findall(r"\{ name: '([^']+)', price: '([^']+)', href: '([^']+)' \}", ts('nav.ts'))
PRICE_GROUPS = []
clinic = ts('clinic.ts')
pg = clinic[clinic.index('export const PRICE_GROUPS'):clinic.index('// Экскурсия')]
for m in re.finditer(r"title: '([^']+)',\s*items: \[(.*?)\],(?:\s*note: '([^']+)',)?\s*\}", pg, re.S):
    PRICE_GROUPS.append((m.group(1), re.findall(r"name: '([^']+)', price: '([^']+)'", m.group(2)), m.group(3)))

assert len(SERVICE_MENU) == 21 and len(SERVICES) == 9 and len(CONDITIONS) == 5 and len(PRICE_GROUPS) == 5, (len(SERVICES), len(CONDITIONS), len(PRICE_GROUPS))

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

CARD_LINKS = ['spina', 'koleno', 'plecho', 'stopa', 'reabilitaciya']

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
NAV = [('', 'Главная'), ('o-centre/', 'О центре'), ('uslugi/', 'Услуги'), ('vrachi/', 'Врачи'), ('ceny/', 'Цены'), ('pacientam/', 'Пациентам'), ('otzyvy/', 'Отзывы'), ('blog/', 'Блог'), ('kontakty/', 'Контакты')]
CHEV = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
BURGER = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

def nav(P, active):
    links = []
    for href, label in NAV:
        if href == '':
            continue  # «Главная» — по логотипу, в мобильном меню остаётся
        on = ' class="on"' if href == active else ''
        if href == 'uslugi/':
            panel = ''.join('<a href="%s%s">%s<span>%s</span></a>' % (P, h.lstrip('/'), n, pr) for n, pr, h in SERVICE_MENU)
            links.append('<div class="mm"><a href="%suslugi/"%s>Услуги %s</a><div class="mm-panel svc">%s</div></div>' % (P, on, CHEV, panel))
        else:
            links.append('<a href="%s%s"%s>%s</a>' % (P, href, on, label))
    mob = ''.join('<a href="%s%s"%s>%s</a>' % (P, h, ' class="on"' if h == active else '', l) for h, l in NAV if h != 'uslugi/')
    mob_svc = ''.join('<a href="%s%s">%s<span>%s</span></a>' % (P, h.lstrip('/'), n, pr) for n, pr, h in SERVICE_MENU)
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

def page_head(P, active, kicker, title, lead, crumbs=None, img=None):
    cr = ''
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Хлебные крошки"><a href="%s">Главная</a>%s</nav>' % (P, ''.join(
            '<span><a href="%s%s">%s</a></span>' % (P, h, l) if h is not None else '<span>%s</span>' % l for h, l in crumbs))
    fig = ('<figure class="phead-img"><img src="%sassets/%s" alt="%s"><figcaption>%s</figcaption></figure>' % (P, img[0], img[1], img[2])) if img else ''
    return '''<header class="phead"><div class="wrap">
    %s
    <div class="%s"><div class="phead-in">%s<p class="kicker">%s</p><h1>%s</h1>%s</div>%s</div>
  </div></header>''' % (nav(P, active), 'phead-row' if img else '', cr, kicker, title, '<p class="lead">%s</p>' % lead if lead else '', fig)

def doc_html(P, title, desc, body):
    return '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s</title>
<meta name="description" content="%s">
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
''' % (title, desc, P, P, fix(body, P), fix(FINAL, P) + legal_foot(P), NOTE, dock(P), P)

def asset_ver():
    # метка версии для site.css/site.js: после обновления браузер не берёт старую копию из кэша
    import hashlib
    h = hashlib.sha1()
    for f in ('site.css', 'site.js'):
        p = os.path.join(ROOT, 'assets', f)
        if os.path.exists(p):
            h.update(open(p, 'rb').read())
    return h.hexdigest()[:8]

def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    v = asset_ver()
    html = html.replace('assets/site.css"', 'assets/site.css?v=%s"' % v).replace('assets/site.js"', 'assets/site.js?v=%s"' % v)
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
    top = [('Травматолог-ортопед', 'до 3 000 ₽'), ('Невролог', 'от 8 000 ₽'), ('Ударно-волновая терапия', 'до 3 000 ₽'), ('PRP-терапия', 'до 10 500 ₽'), ('Лечебная физкультура', 'от 2 000 ₽'), ('Массаж всех видов', 'от 1 600 ₽')]
    return '''<section><div class="wrap"><div class="tease rv">
    <div><p class="kicker">Цены</p><h2>Цену вы знаете до начала лечения</h2><p>Цены по данным центра на 7 ноября 2026 года. Есть рассрочка без переплат и справка для налогового вычета.</p><a class="btn-lime" href="{P}ceny/">Весь прайс →</a></div>
    <ul>%s</ul></div></div></section>''' % ''.join('<li><span>%s</span><b>%s</b></li>' % x for x in top)

EXTRA = {
    'second': lambda: section('second'), 'twin': lambda: section('twin'), 'glossary': methods_section, 'procedures': methods_section,
    'prp': lambda: section('prp'), 'sport': lambda: section('sport'), 'after': lambda: section('after'), 'home': lambda: section('perks'),
    'family': lambda: section('perks'), 'whole': lambda: section('whole'),
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
    items = [(5, 1, '', 'рейтинг в 2ГИС'), (121, 0, '', 'оценка пациентов'), (4.9, 1, '', 'на Яндекс Картах'), (5, 0, ' лет', 'стаж каждого врача'), (23, 0, '', 'методики восстановления'), (9, 0, '', 'направлений в одном центре')]
    # стаж — «более 5 лет»: приставка ставится перед счётчиком
    li = ''.join('<li><b>%s<span data-count="%s" data-dec="%d">0</span>%s</b><span>%s</span></li>' % ('<small>более </small>' if lab == 'стаж каждого врача' else '', v, d, '<small>%s</small>' % suf if suf else '', lab) for v, d, suf, lab in items)
    return '<section><div class="wrap"><div class="cstats beam-border rv"><ul>%s</ul></div></div></section>' % li

STEPS2 = [('Расскажите, что беспокоит', 'Врач собирает жалобы и историю: когда началось, что усиливает боль, были ли травмы и операции.', 'cabinet.jpg'),
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
            '<button class="btn-deep" type="button">Записаться на приём</button></div>'
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

def hover_list_html(items, title=''):
    li = ''.join('<li data-img="{P}%s"><a href="{P}uslugi/%s/"><span style="display:flex;align-items:baseline;gap:24px"><span class="num">%02d</span><span class="t">%s</span></span>'
                 '<span style="display:flex;align-items:center;gap:20px"><span class="k">%s</span><span class="p">%s</span></span></a></li>' % (s['photo'], s['slug'], i + 1, s['menu'], s['kicker'], s['price'] or s['prices'][0][1]) for i, s in enumerate(items))
    head = '<h2 class="rv-vh hl-head" style="margin:0 0 24px">%s</h2>' % title if title else ''
    return '<section><div class="wrap">%s<div style="position:relative"><ul class="hlist">%s</ul><div class="hl-float" aria-hidden="true"><img alt="" src="{P}%s"></div></div></div></section>' % (head, li, items[0]['photo'])

def dock(P):
    small = lambda k: ICON[k].replace('width="24" height="24"', 'width="18" height="18"')
    return ('<nav class="dock" aria-label="Быстрая запись"><a href="tel:+78722522333">%s Позвонить</a>'
            '<a href="https://wa.me/79883011805" target="_blank" rel="noreferrer">%s WhatsApp</a><a class="main" href="%s#quiz" data-lead="">Записаться</a></nav>') % (small('phone'), small('chat'), P)



# ---------- юридический подвал, баннер cookie и раздел «Документы» ----------
LEGAL_LINKS = [('svedeniya', 'Сведения о центре и лицензия'), ('vrachi', 'Сведения о врачах'), ('platnye-uslugi', 'Условия платных услуг'), ('dogovor', 'Образец договора'), ('politika', 'Политика обработки ПДн'), ('soglasie', 'Согласие на обработку ПДн'), ('cookie', 'Политика cookie'), ('kontroliruyushchie-organy', 'Контролирующие органы'), ('', 'Все документы')]

def legal_foot(P):
    o = LEGAL_ORG
    links = ''.join('<a href="%sdokumenty/%s">%s</a>' % (P, (s + '/') if s else '', t) for s, t in LEGAL_LINKS)
    return ('<div class="med-warn">Имеются противопоказания. Необходима консультация специалиста</div>'
            '<div class="legal-foot"><div class="wrap"><nav aria-label="Документы">%s</nav>'
            '<p>%s (ОГРН %s, ИНН %s). Адрес: %s. Лицензия на медицинскую деятельность № %s от %s, выдана: %s. Электронная почта для обращений: <a href="mailto:%s">%s</a>. '
            'Информация на сайте не является публичной офертой и не заменяет консультацию врача. Демо-версия сайта, подготовлена для обсуждения с центром.</p></div></div>'
            '<div class="cookie" role="dialog" aria-label="Уведомление о cookie" hidden><p>Сайт использует необходимые cookie, а карта проезда — cookie Яндекса. Нажимая «Принять все», вы соглашаетесь на их использование по <a href="%sdokumenty/cookie/">Политике cookie</a> и <a href="%sdokumenty/politika/">Политике обработки персональных данных</a>.</p>'
            '<div class="row"><button type="button" class="yes" data-cookie="all">Принять все</button><button type="button" class="no" data-cookie="necessary">Только необходимые</button></div></div>') % (
        links, o['full'], o['ogrn'], o['inn'], o['address'], o['license_no'], o['license_date'], o['license_body'], o['email'], o['email'], P, P)

def build_docs():
    P = '../'
    groups = ''.join('<section><h2>%s</h2><ul>%s</ul></section>' % (g, ''.join('<li><a href="{P}dokumenty/%s/"><span>%s</span><span aria-hidden="true">›</span></a></li>' % (d['slug'], d['title']) for d in LEGAL_DOCS if d['group'] == g)) for g in LEGAL_GROUPS)
    body = page_head(P, 'dokumenty/', 'Документы', 'Документы и сведения о центре', 'Информация, которую медицинская организация обязана раскрывать пациентам: лицензия и реквизиты, врачи, условия платных услуг, образец договора, работа с персональными данными.', [(None, 'Документы')])
    body += '<section><div class="wrap"><div class="docs-grid">%s</div></div></section>' % groups
    write('dokumenty/index.html', doc_html(P, 'Документы — Орто-Рекавери', 'Лицензия, реквизиты, сведения о врачах, образец договора и политика обработки персональных данных.', body))
    for d in LEGAL_DOCS:
        P2 = '../../'
        others = ''.join('<li><a href="{P}dokumenty/%s/">%s</a></li>' % (x['slug'], x['title']) for x in LEGAL_DOCS if x['slug'] != d['slug'])
        body = page_head(P2, 'dokumenty/', 'Документы', d['title'], d['lead'], [('dokumenty/', 'Документы'), (None, d['title'])])
        body += '<section><div class="wrap"><div class="doc-layout"><article class="legal-doc">%s</article><aside class="doc-aside"><b>Другие документы</b><ul>%s</ul><p style="margin-top:20px;color:var(--muted)">Редакция от %s</p></aside></div></div></section>' % (d['html'], others, LEGAL_UPDATED)
        write('dokumenty/%s/index.html' % d['slug'], doc_html(P2, '%s — Орто-Рекавери' % d['title'], d['lead'], body))

# ---------- отзывы ----------
PD_PAGE = 'https://prodoctorov.ru/mahachkala/lpu/90155-orto-rekaveri/#otzivi'
GIS_URL = 'https://2gis.ru/makhachkala/firm/70000001060465369/tab/reviews'
YA_URL = 'https://yandex.ru/maps/org/orto_rekaveri/20949908898/reviews/'

# Видео из orto-recovery/видеоотзывы, сжатые в 720p (web/review-*.mp4)
VIDEO_REVIEWS = [
    ('8301', 'Обошла почти 10 клиник, пришла на костыле — теперь хожу без него', '56 сек'),
    ('0931', 'Травма колена за три недели до турнира', '52 сек'),
    ('5233', '16 лет с болезнью, лечился в Москве и Петербурге', '1 мин 2 сек'),
    ('6986', 'Много раз обращался в центр: ортопедия, травматология, обследования', '43 сек'),
]

DOCTOR_VIDEOS = [
    ('shpora', 'Болит пятка по утрам: подошвенная фасция и пяточная шпора', '46 сек'),
    ('ukol', 'Укол в сустав не помог: когда причина не в самом суставе', '43 сек'),
    ('perelom', '«Ушиб», который оказался переломом пяточной кости', '37 сек'),
    ('oshibka', 'Две ошибки при восстановлении после травмы', '43 сек'),
    ('obuv', 'Нестабильная обувь и боль в коленях', '31 сек'),
    ('2747', 'Главный результат — вернуться к жизни без боли и ограничений', '52 сек'),
    ('0912', 'Почему упражнения при боли в пояснице могут навредить', '55 сек'),
    ('0871', 'Травма крестообразной связки: что нужно после операции', '32 сек'),
    ('4617', 'Индивидуальные стельки Formthotics: кому нужны и как подбирают', '1 мин 8 сек'),
]

def video_grid(kind, items, label):
    return ''.join('<figure><video controls playsinline preload="none" poster="{P}assets/video/%s-%s.jpg" src="{P}assets/video/%s-%s.mp4" aria-label="%s: %s"></video><figcaption>%s</figcaption><small>%s</small></figure>' % (kind, i, kind, i, label, t, t, d) for i, t, d in items)

# Оборудование центра — из orto-recovery-site/src/lib/clinic.ts (EQUIPMENT)
_eq_src = open(os.path.join(os.path.dirname(ROOT), 'orto-recovery-site', 'src', 'lib', 'clinic.ts'), encoding='utf-8').read()
EQUIPMENT = [dict(id=m[0], img=m[1], title=m[2], text=m[3], alt=m[4], services=re.findall(r"'([^']+)'", m[5]))
             for m in re.findall(r"\{ id: '([^']+)', image: asset\('/photos/([^']+)'\), title: '([^']+)', text: '([^']+)', alt: '([^']+)', services: \[([^\]]*)\] \}", _eq_src.split('export const EQUIPMENT')[1])]

def equipment_html(service=None):
    items = [e for e in EQUIPMENT if service is None or service in e['services']]
    if not items:
        return ''
    cards = ''.join('<figure><img src="{P}assets/%s" alt="%s" loading="lazy"><figcaption>%s</figcaption><small>%s</small></figure>' % (e['img'], e['alt'], e['title'], e['text']) for e in items)
    return '''<section class="sec"><div class="wrap"><h2 class="rv-vh">%s</h2>
    <p class="rv-vp">Фото из кабинетов центра. Аппарат и параметры процедуры подбирает врач по показаниям.</p>
    <div class="eq-grid">%s</div></div></section>''' % ('На чём проводим процедуры' if service else 'Оборудование центра', cards)

def doctor_videos_html():
    return '''<section class="sec"><div class="wrap"><h2 class="rv-vh">Врачи объясняют</h2>
    <p class="rv-vp">Короткие видео от специалистов центра. Видео начинает загружаться, только когда вы нажмёте «воспроизвести».</p>
    <div class="rv-videos">%s</div>
    <p class="rv-legal">Имеются противопоказания. Необходима консультация специалиста.</p></div></section>''' % video_grid('doctor', DOCTOR_VIDEOS, 'Видео')

def build_reviews():
    P = '../'
    video = video_grid('review', VIDEO_REVIEWS, 'Видеоотзыв')
    body = page_head(P, 'otzyvy/', 'Отзывы', 'Отзывы пациентов — на независимых площадках', 'Мы не пишем и не редактируем отзывы. Здесь собраны оценки центра и отзывы с площадок, где оставить отзыв может любой пациент.', [(None, 'Отзывы')])
    body += '''<section><div class="wrap">
    <div class="rv-rates">
      <a href="%(gis)s" target="_blank" rel="noreferrer"><i style="background:#19AA1E">2Г</i><span><b>2ГИС</b><em>121 оценка</em></span><strong>★ 5,0</strong></a>
      <a href="%(ya)s" target="_blank" rel="noreferrer"><i style="background:#FC3F1D">Я</i><span><b>Яндекс Карты</b><em>отзывы на карте</em></span><strong>★ 4,9</strong></a>
      <a href="%(pd)s" target="_blank" rel="noreferrer"><i style="background:#1A5DD0">ПД</i><span><b>ПроДокторов</b><em>39 отзывов</em></span><strong class="go">↗</strong></a>
    </div>
    <p class="rv-date">Данные площадок на 1 ноября 2026 года.</p>
    <h2 class="rv-vh">Видеоотзывы пациентов</h2>
    <p class="rv-vp">Пациенты рассказывают о лечении своими словами. Видео начинает загружаться, только когда вы нажмёте «воспроизвести».</p>
    <div class="rv-videos">%(video)s</div>
    <div class="rv-widgets">
      <div class="rv-box"><h2>ПроДокторов</h2><p>Площадка проверяет, что автор действительно был на приёме. Виджет загружается с сервера prodoctorov.ru и использует его cookie.</p>
        <div class="pd-slot"><button type="button" class="btn-deep" data-pd="90155">Показать отзывы с ПроДокторов</button></div></div>
      <div class="rv-box"><h2>Яндекс Карты</h2><p>Отзывы и оценки с карточки центра на Яндекс Картах.</p>
        <div class="consent-frame rv-ya" data-title="Отзывы о центре на Яндекс Картах" data-src="https://yandex.ru/maps-reviews-widget/20949908898?comments"><p>Виджет отзывов загружается с серверов Яндекса и использует их cookie.</p><button type="button" class="btn-deep">Показать отзывы Яндекса</button></div></div>
    </div>
  </div></section>
  <section class="rv-leave"><div class="wrap">
    <div><h2>Были у нас? Расскажите о визите</h2><p>Отзыв помогает другим пациентам выбрать врача, а нам — понять, что улучшить. Выберите удобную площадку.</p>
      <div class="rv-btns"><a href="%(gis)s" target="_blank" rel="noreferrer">в 2ГИС</a><a href="%(ya)s" target="_blank" rel="noreferrer">на Яндексе</a><a href="https://prodoctorov.ru/new/rate/lpu/90155/" target="_blank" rel="noreferrer">на ПроДокторов</a></div></div>
    <div class="rv-box"><h2>Что-то пошло не так?</h2><p>Напишите администратору в WhatsApp — передадим руководителю центра и ответим. Официальное обращение можно отправить письмом на <a href="mailto:%(mail)s">%(mail)s</a>.</p>
      <a class="rv-wa" href="https://wa.me/79883011805" target="_blank" rel="noreferrer">Написать администратору</a></div>
  </div></section>
  <section><div class="wrap"><p class="rv-legal">Видеоотзывы — личное мнение пациентов, результат лечения у каждого свой. Имеются противопоказания, необходима консультация специалиста. Отзывы в блоках площадок показывают виджеты 2ГИС, Яндекса и ПроДокторов: они загружаются с их серверов по вашему нажатию, клиника не может изменить или удалить отзыв.</p></div></section>''' % {'gis': GIS_URL, 'ya': YA_URL, 'pd': PD_PAGE, 'mail': LEGAL_ORG['email'], 'video': video}
    write('otzyvy/index.html', doc_html(P, 'Отзывы — Орто-Рекавери, Махачкала', 'Оценки и отзывы о центре на независимых площадках: 2ГИС, Яндекс Карты, ПроДокторов.', body))

# ---------- блог ----------
DOCTOR_ROLES = {m.group(1): m.group(2) for m in re.finditer(r"name: '([^']+)',\s*role: '([^']+)'", clinic)}
DOCTOR_PHOTOS = {'Муртузалиева Зарема Гаджимурадовна': 'd-murtuzalieva.jpg', 'Хаджалов Абузар Магомедович': 'd-khadzhalov.jpg', 'Мусаева Эльмира Ашурбеговна': 'd-musaeva.jpg', 'Нажмудинова Айшат Абдурахмановна': 'd-nazhmudinova.jpg'}

def reviewer(name, cls='bl-rev'):
    f, i, o = name.split(' ')
    ava = ('<img src="{P}assets/%s" alt="">' % DOCTOR_PHOTOS[name]) if name in DOCTOR_PHOTOS else '<i aria-hidden="true">%s%s</i>' % (f[0], i[0])
    return '<span class="%s">%s<span><b>%s %s. %s.</b><em>%s · проверка текста</em></span></span>' % (cls, ava, f, i[0], o[0], DOCTOR_ROLES.get(name, 'врач центра').split(',')[0])

def blog_card(p, big=False):
    return '''<a class="bl-card%s" href="{P}blog/%s/" data-cat="%s"><span class="bl-img"><img src="{P}assets/%s" alt="%s"><em>%s</em></span>
      <span class="bl-txt"><b>%s</b><span>%s</span><span class="bl-meta">%s<small>%d мин</small></span></span></a>''' % (
        ' big' if big else '', p['slug'], p['category'], p['cover'], p['coverAlt'], p['category'], p['title'], p['lead'], reviewer(p['reviewer']), p['minutes'])

def build_blog():
    P = '../'
    chips = '<button type="button" class="on" data-cat="">Все статьи</button>'
    cards = ''.join(blog_card(p, i == 0) for i, p in enumerate(BLOG_POSTS))
    body = page_head(P, 'blog/', 'Блог', 'Разбираемся в боли вместе с врачами', 'Короткие статьи о том, что делать дома, какие признаки нельзя пропускать и как подготовиться к обследованию. Каждый текст проверяет врач центра.', [(None, 'Блог')])
    body += '<section><div class="wrap"><div class="bl-chips" role="tablist" aria-label="Темы">%s</div><div class="bl-grid">%s</div></div></section>' % (chips, cards)
    write('blog/index.html', doc_html(P, 'Блог — Орто-Рекавери, Махачкала', 'Статьи врачей центра: боль в спине, суставы и стопы, сколиоз у детей.', body))
    for p in BLOG_POSTS:
        P2 = '../../'
        s = next((x for x in SERVICES if x['slug'] == p['service']), None)
        more = ([x for x in BLOG_POSTS if x['slug'] != p['slug'] and x['category'] == p['category']] + [x for x in BLOG_POSTS if x['category'] != p['category']])[:2]
        toc = ''.join('<li><a href="#%s">%s</a></li>' % (t['id'], t['title']) for t in p['toc'])
        cta = ('<div class="bl-cta"><p class="kicker">%s</p><b>%s</b><span>%s — <strong>%s</strong></span><a class="go" href="{P}#quiz">Записаться</a><a href="{P}uslugi/%s/">Подробнее о направлении</a></div>' % (
            s['kicker'], s['menu'], s['prices'][0][0], s['prices'][0][1], s['slug'])) if s else ''
        meta = '<div class="bl-head-meta">%s<small>%d минуты чтения</small></div>' % (reviewer(p['reviewer'], 'bl-rev bl-rev--dark'), p['minutes'])
        top = page_head(P2, 'blog/', p['category'], p['title'], p['lead'], [('blog/', 'Блог'), (None, p['category'])])
        top = top.replace('</p></div>\n  </div></header>', '</p>%s</div>\n  </div></header>' % meta, 1)
        body = top + '''<section class="bl-post"><div class="wrap">
      <img class="bl-cover" src="{P}assets/%s" alt="%s">
      <div class="bl-layout"><article class="legal-doc article">%s</article>
        <aside><nav class="bl-toc" aria-label="Содержание"><b>Содержание</b><ol>%s</ol></nav>%s</aside></div>
      <div class="bl-warn">Имеются противопоказания. Необходима консультация специалиста</div>
      <h2 class="bl-more">Читайте также</h2><div class="bl-grid two">%s</div>
    </div></section>''' % (p['cover'], p['coverAlt'], p['html'], toc, cta, ''.join(blog_card(x) for x in more))
        write('blog/%s/index.html' % p['slug'], doc_html(P2, '%s — блог Орто-Рекавери' % p['title'], p['lead'], body))

# ---------- страницы ----------
def build():
    # шрифты лежат на сервере сайта — никаких запросов к Google (трансграничная передача IP посетителей)
    css = open(os.path.join(HERE, 'fonts.css'), encoding='utf-8').read() + re.search(r'<style>(.*?)</style>', SRC, re.S).group(1) + open(os.path.join(HERE, 'motion.css'), encoding='utf-8').read() + open(os.path.join(HERE, 'legal.css'), encoding='utf-8').read()
    open(os.path.join(ROOT, 'assets', 'site.css'), 'w', encoding='utf-8').write(css + open(os.path.join(HERE, 'pages.css'), encoding='utf-8').read())
    open(os.path.join(ROOT, 'assets', 'site.js'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'site.js'), encoding='utf-8').read() + open(os.path.join(HERE, 'motion.js'), encoding='utf-8').read() + open(os.path.join(HERE, 'legal.js'), encoding='utf-8').read())

    # главная
    hero = re.sub(r'<nav class="nav".*?</nav>', lambda m: nav('', ''), HERO, flags=re.S)
    home = '\n'.join([hero, FINDER, section('start'), stats_html(), cards_section(), steps_html(), manifesto_html(), section('second'), section('doctors'), flow_html(), marquee_html(), section('trust'), prices_teaser()])
    write('index.html', doc_html('', 'Орто-Рекавери — центр восстановительной медицины в Махачкале', 'Лечим боль в спине и суставах без операции: ортопед, невролог, реабилитация и лечебная физкультура, физиотерапия, PRP.', home))

    # услуги
    problems = [s for s in SERVICES if s['kind'] == 'problem']; methods = [s for s in SERVICES if s['kind'] == 'method']
    cards = lambda items, title: '<section class="mob-only"><div class="wrap"><h2 style="font-size:28px;margin:0 0 16px">%s</h2><div class="svc-cards">%s</div></div></section>' % (title, ''.join('<a href="{P}uslugi/%s/"><img src="assets/%s" alt="%s"><span><b>%s</b><em>%s</em><i>%s →</i></span></a>' % (s['slug'], s['photo'][7:], s['alt'], s['menu'], s['lead'], s['price'] or s['prices'][0][1]) for s in items))
    body = page_head('../', 'uslugi/', 'Услуги', 'Что мы лечим', 'Выберите, что беспокоит, — или подберите врача за три вопроса. Ниже — методы лечения, которые есть в центре.', [(None, 'Услуги')])
    body += hover_list_html(problems) + cards(problems, 'Что беспокоит') + hover_list_html(methods, 'Методы лечения') + cards(methods, 'Методы лечения') + section('start') + marquee_html()
    write('uslugi/index.html', doc_html('../', 'Услуги — Орто-Рекавери', 'Боль в суставах и спине, восстановление после травм и операций, осанка и стопы у детей; физиотерапия и PRP-терапия.', body))

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
      <div class="pcard rv"><h2>Цены</h2><ul class="plist2">%s</ul><small>Цены по данным центра на 7 ноября 2026 года. <a href="%sceny/">Все цены</a></small></div>
      <div class="dcard rv"><h2>%s</h2>%s</div>
    </div></div></section>''' % (''.join('<li><span>%s</span><b>%s</b></li>' % p for p in s['prices']), P, 'Ведут приём' if len(s['doctors']) > 1 else 'Ведёт приём', docs)
        seen, extras = set(), []
        for e in s['extras']:
            html = EXTRA[e]()
            if html not in seen:
                seen.add(html); extras.append(html)
        others = ''.join('<a href="%suslugi/%s/">%s</a>' % (P, o['slug'], o['menu']) for o in SERVICES if o['slug'] != s['slug'])
        body = top + grid + (conds_block(s['conditions']) if s['conditions'] else '') + '\n'.join(extras)
        body += equipment_html(s['slug'])
        body += '<section class="sec"><div class="wrap"><h2 style="font-size:28px">Другие направления</h2><div class="others">%s</div></div></section>' % others
        write('uslugi/%s/index.html' % s['slug'], doc_html(P, '%s — Орто-Рекавери, Махачкала' % s['menu'], s['lead'], body))

    # разделы
    P = '../'
    pages = {
        'o-centre/': ('О центре', 'Центр восстановительной медицины «Орто-Рекавери»', 'Лечим и восстанавливаем пациентов с заболеваниями и травмами опорно-двигательной системы — без операций, по принципам доказательной медицины.',
                      [stats_html(), manifesto_html(), section('founders'), section('how'), section('trust'), section('tour'), equipment_html()]),
        'vrachi/': ('Специалисты', 'Врачи центра', 'Можно записаться к конкретному врачу. Если вам спокойнее со специалистом-женщиной, скажите об этом администратору.',
                    [section('doctors'), doctor_videos_html()]),
        'ceny/': ('Цены', 'Цену вы знаете до начала лечения', 'Цены по данным центра на 7 ноября 2026 года. Есть рассрочка без переплат и справка для налогового вычета.',
                  ['<section><div class="wrap"><div class="pgroups">%s</div></div></section>' % ''.join(
                      '<div class="pcard rv"><h2>%s</h2><ul class="plist2">%s</ul>%s</div>' % (t, ''.join('<li><span>%s</span><b>%s</b></li>' % i for i in items), '<p class="pnote">%s</p>' % note if note else '') for t, items, note in PRICE_GROUPS),
                   section('perks')]),
        'pacientam/': ('Пациентам', 'Всё, что нужно знать до визита', 'Как проходит первый приём, что взять с собой, как получить второе мнение и вызвать реабилитолога на дом.',
                       [steps_html(), section('prep'), flow_html(), section('wa'), section('second'), section('perks')]),
        'kontakty/': ('Контакты', 'Как нас найти', 'Махачкала, проспект Имама Шамиля, 35А, 1 этаж. Вход за шлагбаумом, рядом санаторий «Тарнаир».',
                      ['<section><div class="wrap"><div class="cpage">%s</div></div></section>' % re.search(r'<div class="contacts">(.*)</div>\s*<!--LEGAL-->', FINAL, re.S).group(1).replace('rv"', '"')]),
    }
    for href, (kicker, title, lead, blocks) in pages.items():
        label = dict(NAV)[href]
        img = ('admin-desk.jpg', 'Администратор центра за стойкой регистрации', 'Администратор Зарема Муртузалиева встретит вас на ресепшене') if href == 'o-centre/' else None
        body = page_head(P, href, kicker, title, lead, [(None, label)], img) + '\n'.join(blocks)
        write(href + 'index.html', doc_html(P, '%s — Орто-Рекавери, Махачкала' % label, lead, body))
    build_docs()
    build_reviews()
    build_blog()
    print('ok:', 2 + len(SERVICES) + len(pages) + 1 + len(LEGAL_DOCS) + 2 + len(BLOG_POSTS), 'pages')

build()
