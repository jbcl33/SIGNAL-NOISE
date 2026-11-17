"""Render a C-source magazine index; links remain native HTML anchors."""
from html import escape as e
import json


def render_home(root, out, published):
    latest = published[0]
    rows = []
    latest_index = 0
    for index, (key, zh) in enumerate([
        ('morning', '晨刊'), ('noon', '午刊'), ('night', '晚刊'), ('lab', '工具实验室'),
    ]):
        item = next((p for p in published if p['edition'] == key), None)
        if item and item['path'] == latest['path']:
            latest_index = index
        path = e(json.dumps(item['path'], ensure_ascii=False)) if item else 'NULL'
        rows.append('    { &quot;' + zh + '&quot;, ' + path + ' },' + (' <span class="comment">/* 待刊 */</span>' if not item else ''))
    links = []
    for index, (key, zh) in enumerate([('morning', '晨刊'), ('noon', '午刊'), ('night', '晚刊'), ('lab', '工具实验室')]):
        item = next((p for p in published if p['edition'] == key), None)
        call = 'read_issue(&amp;issues[' + str(index) + ']);'
        if item:
            links.append('    <a href="' + e(item['path'], quote=True) + '" aria-label="阅读' + zh + '">' + call + '</a> <span class="comment">// ' + zh + ' ↗</span>')
        else:
            links.append('    <span class="comment">// ' + call + ' ' + zh + '待刊</span>')
    latest_pointer = '&issues[' + str(latest_index) + ']'
    extra = ''
    values = {
        'LATEST_ISSUE': latest['issue'], 'LATEST_DATE': latest['date'],
        'LATEST_PATH': latest['path'], 'LATEST_TITLE': latest['title'],
        'PUBLISHED_COUNT': str(len(published)), 'LATEST_POINTER': latest_pointer,
        'EXTRA_LATEST': extra,
    }
    page = (root / 'scripts/home.template.html').read_text()
    for key, value in values.items():
        page = page.replace('{{' + key + '}}', e(value, quote=True))
    page = page.replace('{{ISSUE_ROWS}}', '\n'.join(rows)).replace('{{READ_CALLS}}', '\n'.join(links))
    css = (root / 'assets/home.css').read_text()
    assert '</style' not in css.lower()
    page = page.replace('<link rel="stylesheet" href="assets/home.css">', '<style>' + css + '</style>')
    (out / 'index.html').write_text(page)
