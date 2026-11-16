"""Render the magazine portal; independent from archived issue layout."""
from html import escape as e

def render_home(root,out,published):
    latest=published[0]
    cards=[]
    labels={'morning':'晨刊','noon':'午刊','lab':'工具实验室','night':'夜刊'}
    for p in published[:6]:
        y,m,d=p['date'].split('-')
        cards.append('<a class="publication" href="'+e(p['path'])+'"><div class="publication-date">'+y+'.'+m+'<b>'+d+'</b>'+e(p['issue'])+'</div><div><h3>'+e(labels[p['edition']])+' / '+e(p['title'])+'</h3><p>'+e(p['summary'])+'</p></div><span class="arrow">↗</span></a>')
    descriptions={'morning':('MORNING FREQUENCY','技术简报、独立互联网，附少量电子音乐选片。'),'noon':('OPEN CIRCUIT','从原理图、时序与源码，拆解一个硬件项目。'),'lab':('TOOL LAB','EDA、Agent 与代码工具的可复现实验。'),'night':('AFTER HOURS','制作过程、艺术实践与技术文化。')}
    editions=[]
    for key,(name,description) in descriptions.items():
        p=next((p for p in published if p['edition']==key),None)
        action='<a href="'+e(p['path'])+'">阅读最近一期 ↗</a>' if p else '<span class="not-yet">尚无独立分刊</span>'
        editions.append('<article class="edition"><p class="kicker">'+name+'</p><h3>'+labels[key]+'</h3><p>'+description+'</p>'+action+'</article>')
    s=(root/'scripts/home.template.html').read_text()
    s=s.replace('{{LATEST_DATE}}',e(latest['date'].replace('-','.'))).replace('{{LATEST_PATH}}',e(latest['path'])).replace('{{PUBLICATIONS}}',''.join(cards)).replace('{{EDITIONS}}',''.join(editions))
    # Feature selections belong to the preserved 001 issue, independent of latest edition.
    s=s.replace(e(latest['path'])+'#deep','morning/001/#deep').replace(e(latest['path'])+'#news','morning/001/#news')
    (out/'index.html').write_text(s)
