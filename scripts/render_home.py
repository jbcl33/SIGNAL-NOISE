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
    (out/'index.html').write_text(s)
