"""Build static Pages output using only the Python standard library."""
from pathlib import Path
import json, html, re, shutil, os
from datetime import date, datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets', OUT/'assets')
    shutil.copytree(ROOT/'data', OUT/'data')
    # Standalone editions retain their own asset paths.
    shutil.copytree(ROOT/'static', OUT, dirs_exist_ok=True)
    catalog=json.loads((ROOT/'data/issues.json').read_text())
    assert catalog['schemaVersion']==1 and catalog['issues'], 'Empty or unsupported catalog'
    entries=sorted(catalog['issues'],key=lambda x:(x['date'],x['id']),reverse=True)
    template=(ROOT/'scripts/issue.template.html').read_text()
    registry=json.loads((ROOT/'data/publications.json').read_text())
    assert registry['schemaVersion']==1
    published=registry['publications']
    publication_keys=set()
    for publication in published:
        date.fromisoformat(publication['date'])
        assert publication['edition'] in ['morning','noon','lab','night']
        key=(publication['date'],publication['edition'])
        assert key not in publication_keys, f'Duplicate publication: {key}'
        publication_keys.add(key)
        path=publication['path']
        assert re.fullmatch(r'[a-z0-9/-]+/',path) and not path.startswith('/')
        assert (OUT/path/'index.html').is_file(), f'Missing publication page: {path}'
    edition_order={'morning':0,'noon':1,'lab':2,'night':3}
    published=sorted(published,key=lambda p:(p['date'],edition_order[p['edition']]),reverse=True)
    feed={'schemaVersion':1,'deploymentCommit':os.environ.get('GITHUB_SHA','local-preview'),
          'generatedAt':datetime.now(timezone.utc).isoformat(),'publications':published}
    (OUT/'publications.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n')
    links=''.join('<aside class="morning-entry" aria-label="独立分刊"><div><span class="pixel">'+html.escape(p['date'])+' / '+html.escape(p['edition'].upper())+'</span><h2>'+html.escape(p['title'])+'</h2><p>'+html.escape(p['summary'])+'</p></div><a href="'+html.escape(p['path'])+'">阅读分刊 ↗</a></aside>' for p in published[:8])
    template=template.replace('{{publications}}',links)
    seen=set()
    for entry in entries:
        ident=entry['id']
        assert re.fullmatch(r'\d{3,}',ident) and ident not in seen
        seen.add(ident)
        issue=json.loads((ROOT/f'data/issues/{ident}.json').read_text())
        assert issue['schemaVersion']==1 and all(issue[k]==entry[k] for k in ['id','date','title','status'])
        assert [x['id'] for x in issue['editions']]==['morning','noon','night']
        page=template
        for edition in issue['editions']:
            assert f'id="{edition["id"]}"' in edition['contentHtml']
            page=page.replace('{{'+edition['id']+'}}',edition['contentHtml'])
        # Stable URLs and a relative base also work on /SIGNAL-NOISE/ project Pages.
        page=page.replace('<head>','<head><base href="../">')
        (OUT/'issues').mkdir(exist_ok=True)
        (OUT/f'issues/{ident}.html').write_text(page)
        if entry==entries[0]: (OUT/'index.html').write_text(page.replace('<base href="../">',''))
    cards=''.join(f'<a class="issue" href="issues/{e["id"]}.html"><span>{html.escape(e["date"])} / ISSUE {e["id"]}</span><h2>{html.escape(e["title"])}</h2><p>{html.escape(e["description"])} · 晨刊 / 午刊 / 晚刊</p><b>阅读本期 ↗</b></a>' for e in entries)
    edition_labels={'morning':'晨刊','noon':'午刊','lab':'工具实验室','night':'夜刊'}
    publication_cards=''.join('<a class="issue" href="'+html.escape(p['path'])+'"><span>'+html.escape(p['date'])+' / '+edition_labels[p['edition']]+' / '+html.escape(p['issue'])+'</span><h2>'+html.escape(p['title'])+'</h2><p>'+html.escape(p['summary'])+'</p><b>阅读分刊 ↗</b></a>' for p in published)
    cards=publication_cards+cards
    archive='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>历史归档 — SIGNAL / NOISE</title><style>*{box-sizing:border-box}body{margin:0;background:#f4f2eb;color:#111;font-family:Arial,"Noto Sans SC",sans-serif}header,main,footer{max-width:1050px;margin:auto;padding:25px}header{display:flex;justify-content:space-between;border-bottom:3px solid}a{color:inherit}h1{font-size:clamp(60px,12vw,140px);line-height:.85;letter-spacing:-.08em;margin:70px 0 35px}h1 em{color:#f04b31;font-style:normal}label{display:block;margin:35px 0}input{display:block;margin-top:12px;padding:15px;width:100%;max-width:550px;font:inherit;border:1px solid;background:transparent}.issue{display:block;border-top:3px solid;padding:30px 0;text-decoration:none}.issue:hover h2{color:#f04b31}.issue span{font-family:monospace}.issue h2{font-size:clamp(24px,5vw,45px)}.issue p,footer{line-height:1.8;color:#555}:focus-visible{outline:3px solid #1c48cc;outline-offset:4px}[hidden]{display:none!important}</style><header><a href="index.html">SIGNAL / NOISE.</a><a href="index.html">最新一期 ↗</a></header><main><h1>THE<br><em>ARCHIVE.</em></h1><p>历史归档 / 按日期倒序 · 只收录已发布期刊</p><label>检索期号、日期或主题<input id="search" type="search" placeholder="例如：001、GPIO、2026-11" autocomplete="off"></label><p id="count" role="status"></p>'''+cards+'''<p id="empty" hidden>没有匹配的期刊，请尝试其他关键词。</p></main><footer>第 001 期为模拟试刊。尚未接入每日 AI 自动写稿。<br>每期包含晨刊、午刊与晚刊。</footer><script>const input=document.querySelector('input'),items=[...document.querySelectorAll('.issue')];function filter(){let n=0;items.forEach(x=>{x.hidden=!x.textContent.toLowerCase().includes(input.value.trim().toLowerCase());if(!x.hidden)n++});document.querySelector('#count').textContent=`共 ${n} 期`;document.querySelector('#empty').hidden=n>0}input.addEventListener('input',filter);filter()</script></html>'''
    (OUT/'archive.html').write_text(archive)
    (OUT/'.nojekyll').touch()
    # Keep the requested root index and archive reviewable and directly hostable.
    shutil.copy(OUT/'index.html',ROOT/'index.html')
    shutil.copy(OUT/'archive.html',ROOT/'archive.html')
    print(f'Built {len(entries)} issue(s) to _site')
if __name__=='__main__': build()
