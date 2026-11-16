"""Fetch public RSS metadata for editorial discovery; does not invent scores or publish articles."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
import argparse, html, json, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def collect(limit=5):
    sources=json.loads((ROOT/'data/music-sources.json').read_text())['sources']
    path=ROOT/'data/music-radar.json'
    previous=json.loads(path.read_text()) if path.exists() else {'sources':[]}
    old={x['id']:x for x in previous['sources']}
    now=datetime.now(timezone.utc).isoformat()
    def fetch(source):
        row={**source,'checkedAt':now}
        try:
            req=Request(source['feed'],headers={'User-Agent':'SIGNAL-NOISE/1.0 (editorial RSS reader)'})
            with urlopen(req,timeout=20) as response:
                data=response.read(2_000_001)
            if len(data)>2_000_000: raise ValueError('Feed exceeds size limit')
            if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper(): raise ValueError('Unsupported XML declaration')
            root=ET.fromstring(data);entries=[];seen=set()
            for item in root.findall('.//item'):
                url=(item.findtext('link') or '').strip()
                if urlsplit(url).scheme not in ['https','http'] or url in seen: continue
                # Exclude general news/opinion for broad publications; category metadata is retained.
                if source['id']=='needle-drop' and '/album-reviews/' not in url: continue
                if source['id']=='quietus' and not any(x in url for x in ['/reviews/','/quietus-reviews/','/electronic/']): continue
                raw=item.findtext('pubDate') or ''
                try: date=parsedate_to_datetime(raw).isoformat()
                except (ValueError,TypeError): date=None
                title=html.unescape(re.sub('<[^>]+>','',item.findtext('title') or '')).strip()
                if not title: continue
                entries.append({'title':title,'url':url,'publishedAt':date,'categories':[x.text for x in item.findall('category') if x.text],'status':'discovery-only','score':None})
                seen.add(url)
                if len(entries)>=limit: break
            row.update(status='ok',lastSuccessAt=now,entries=entries)
        except Exception as error:
            row.update(status='unavailable',error=str(error)[:160],lastSuccessAt=old.get(source['id'],{}).get('lastSuccessAt'),entries=old.get(source['id'],{}).get('entries',[]))
        return row
    rows=list(ThreadPoolExecutor(max_workers=4).map(fetch,sources))
    result={'schemaVersion':1,'collectedAt':now,'note':'RSS titles/dates/categories only; discovery candidates are not scored recommendations. Failed feeds retain visibly dated previous entries.','sources':rows}
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f"Fetched {sum(x['status']=='ok' for x in rows)}/{len(rows)} feeds; {sum(len(x['entries']) for x in rows)} discovery items")
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=5);args=parser.parse_args()
    if not 1<=args.limit<=10: parser.error('--limit must be 1..10')
    collect(args.limit)
