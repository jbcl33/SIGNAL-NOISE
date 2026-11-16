"""Render the text-first magazine index with inline CSS and no scripts."""
from html import escape as e


def render_home(root, out, published):
    latest = published[0]
    links = []
    for number, (key, en, zh) in enumerate([
        ('morning', 'MORNING', '晨刊'),
        ('noon', 'OPEN CIRCUIT', '午刊'),
        ('night', 'AFTER HOURS', '晚刊'),
    ], start=1):
        item = next((p for p in published if p['edition'] == key), None)
        label = '<span class="row-number" aria-hidden="true">0' + str(number) + '</span><span class="row-label"><span lang="en">' + en + '</span><span>' + zh + '</span></span>'
        if item:
            links.append('<a href="' + e(item['path'], quote=True) + '">' + label + '<span class="row-status">阅读 ↗</span></a>')
        else:
            links.append('<span class="pending">' + label + '<span class="row-status">待刊</span></span>')
    values = {
        'LATEST_ISSUE': latest['issue'],
        'LATEST_DATE': latest['date'].replace('-', '.'),
        'LATEST_ISO_DATE': latest['date'],
        'LATEST_PATH': latest['path'],
        'LATEST_TITLE': latest['title'],
        'PUBLISHED_COUNT': str(len(published)).zfill(2),
    }
    page = (root / 'scripts/home.template.html').read_text()
    for key, value in values.items():
        page = page.replace('{{' + key + '}}', e(value, quote=True))
    page = page.replace('{{EDITION_LINKS}}', '\n'.join(links))
    css = (root / 'assets/home.css').read_text()
    assert '</style' not in css.lower()
    page = page.replace('<link rel="stylesheet" href="assets/home.css">', '<style>' + css + '</style>')
    (out / 'index.html').write_text(page)
