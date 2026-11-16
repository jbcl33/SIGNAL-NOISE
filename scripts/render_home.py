"""Render the minimal monochrome magazine entry page."""
from html import escape as e

def render_home(root,out,published):
    latest=published[0]
    links=[]
    for key,en,zh in [('morning','MORNING','晨刊'),('noon','OPEN CIRCUIT','午刊'),('night','AFTER HOURS','晚刊')]:
        p=next((p for p in published if p['edition']==key),None)
        links.append('<a href="'+e(p['path'])+'"><span>'+en+'</span>'+zh+' ↗</a>' if p else '<div class="unavailable"><span>'+en+'</span>'+zh+' · 待刊</div>')
    last='<a href="'+e(latest['path'])+'">最近更新 / '+e(latest['date'])+' / '+e(latest['title'])+' ↗</a>'
    s=(root/'scripts/home.template.html').read_text().replace('{{LATEST_DATE}}',e(latest['date'].replace('-','.'))).replace('{{EDITION_LINKS}}',''.join(links)).replace('{{LATEST_LINK}}',last)
    # Keep the entry page self-contained: mobile networks must not be able to
    # load the markup while leaving the entire theme/animation behind.
    css=(root/'assets/home.css').read_text()
    js=(root/'assets/home.js').read_text()
    assert '</style' not in css.lower() and '</script' not in js.lower()
    s=s.replace('<link rel="stylesheet" href="assets/home.css">','<style>'+css+'</style>')
    s=s.replace('<script src="assets/home.js" defer></script>','')
    s=s.replace('</body>','<script>'+js+'</script></body>')
    (out/'index.html').write_text(s)
