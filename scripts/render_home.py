"""Render a component-based editorial PCB, with self-contained assets."""
from html import escape as e

def render_home(root,out,published):
    latest=published[0];modules=[]
    for number,key,zh in [(2,'morning','晨刊'),(3,'noon','午刊'),(4,'night','晚刊')]:
        item=next((p for p in published if p['edition']==key),None)
        inside='<span class="reference">U'+str(number)+' / LDO</span><span class="ldo-package"><small>3V3</small></span><i class="ldo-led" aria-hidden="true"></i><span class="ldo-label">'+zh+(' ↗' if item else '')+'</span><span class="status">'+('READY' if item else '待刊')+'</span>'
        modules.append('<a class="ldo available" data-node="'+key+'" href="'+e(item['path'])+'" aria-label="阅读'+zh+'">'+inside+'</a>' if item else '<button class="ldo" data-node="'+key+'" disabled aria-label="'+zh+'尚未发布">'+inside+'</button>')
    short={'morning':'MORNING','noon':'OPEN CIRCUIT','night':'AFTER HOURS','lab':'TOOL LAB'}[latest['edition']]+' / '+latest['issue']
    s=(root/'scripts/home.template.html').read_text().replace('{{LATEST_DATE}}',e(latest['date'].replace('-','.'))).replace('{{LATEST_PATH}}',e(latest['path'])).replace('{{LATEST_SHORT}}',e(short)).replace('{{LDO_MODULES}}',''.join(modules))
    css=(root/'assets/home.css').read_text();js=(root/'assets/home.js').read_text()
    assert '</style' not in css.lower() and '</script' not in js.lower()
    s=s.replace('<link rel="stylesheet" href="assets/home.css">','<style>'+css+'</style>').replace('<script src="assets/home.js" defer></script>','').replace('</body>','<script>'+js+'</script></body>')
    (out/'index.html').write_text(s)
