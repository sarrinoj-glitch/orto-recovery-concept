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
<script src="%sassets/site.js"></script>
</body>
</html>
''' % (title, desc, P, P, fix(body, P), fix(FINAL, P), NOTE, P)

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

# ---------- страницы ----------
def build():
    css = re.search(r'<style>(.*?)</style>', SRC, re.S).group(1)
    open(os.path.join(ROOT, 'assets', 'site.css'), 'w', encoding='utf-8').write(css + open(os.path.join(HERE, 'pages.css'), encoding='utf-8').read())
    shutil.copy(os.path.join(HERE, 'site.js'), os.path.join(ROOT, 'assets', 'site.js'))

    # главная
    hero = re.sub(r'<nav class="nav".*?</nav>', lambda m: nav('', ''), HERO, flags=re.S)
    home = '\n'.join([hero, FINDER, section('start'), cards_section(), section('second'), section('wa'), section('doctors'), section('trust'), section('tour'), prices_teaser()])
    write('index.html', doc_html('', 'Орто-Рекавери — центр восстановительной медицины в Махачкале', 'Лечим боль в спине и суставах без операции: ортопед, невролог, реабилитация и ЛФК, физиотерапия, PRP, эндоскопия во сне.', home))

    # услуги
    cards = ''.join('<a href="{P}uslugi/%s/"><img src="assets/%s" alt="%s"><span><b>%s</b><em>%s</em><i>%s →</i></span></a>' % (s['slug'], s['photo'][7:], s['alt'], s['menu'], s['lead'], s['prices'][0][1]) for s in SERVICES)
    body = page_head('../', 'uslugi/', 'Услуги', 'Что мы лечим', 'Восемь направлений в одном центре: от консультации ортопеда до обследования во сне. Выберите своё или подберите врача за три вопроса.', [(None, 'Услуги')])
    body += '<section><div class="wrap"><div class="svc-cards">%s</div></div></section>' % cards + section('start')
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
                      [section('founders'), section('how'), section('trust'), section('tour'), section('stories')]),
        'vrachi/': ('Специалисты', 'Врачи центра', 'Можно записаться к конкретному врачу. Если вам спокойнее со специалистом-женщиной, скажите об этом администратору.',
                    [section('doctors')]),
        'ceny/': ('Цены', 'Цену вы знаете до начала лечения', 'Прайс центра на ПроДокторов от 19.10.2026. Есть рассрочка без переплат и справка для налогового вычета.',
                  ['<section><div class="wrap"><div class="pgroups">%s</div></div></section>' % ''.join(
                      '<div class="pcard rv"><h2>%s</h2><ul class="plist2">%s</ul></div>' % (t, ''.join('<li><span>%s</span><b>%s</b></li>' % i for i in items)) for t, items in PRICE_GROUPS),
                   section('perks')]),
        'pacientam/': ('Пациентам', 'Всё, что нужно знать до визита', 'Как проходит первый приём, что взять с собой, как получить второе мнение и вызвать реабилитолога на дом.',
                       [section('prep'), section('how'), section('second'), section('perks')]),
        'kontakty/': ('Контакты', 'Как нас найти', 'Махачкала, проспект Имама Шамиля, 35А, 1 этаж. Вход за шлагбаумом, рядом санаторий «Тарнаир».',
                      ['<section><div class="wrap"><div class="cpage">%s</div></div></section>' % re.search(r'<div class="contacts">(.*)</div>\s*<p class="legal">', FINAL, re.S).group(1).replace('rv"', '"')]),
    }
    for href, (kicker, title, lead, blocks) in pages.items():
        label = dict(NAV)[href]
        body = page_head(P, href, kicker, title, lead, [(None, label)]) + '\n'.join(blocks)
        write(href + 'index.html', doc_html(P, '%s — Орто-Рекавери, Махачкала' % label, lead, body))
    print('ok:', 2 + len(SERVICES) + len(pages), 'pages')

build()
