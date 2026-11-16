"""Validate local links using a real project-subpath URL, never localhost root."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.base=None; self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='base': self.base=a.get('href')
        if tag=='a' and a.get('href'): self.links.append(a['href'])

def validate(root):
    prefix='https://example.test/SIGNAL-NOISE/'
    for page in root.rglob('*.html'):
        parser=Links();parser.feed(page.read_text())
        base=urljoin(prefix,page.relative_to(root).as_posix())
        if parser.base: base=urljoin(base,parser.base)
        for href in parser.links:
            parsed=urlsplit(urljoin(base,href))
            if parsed.netloc!='example.test' or parsed.scheme not in ('http','https'): continue
            assert parsed.path.startswith('/SIGNAL-NOISE/'), f'Link escapes project Pages path: {page}: {href}'
            path=unquote(parsed.path[len('/SIGNAL-NOISE/'):])
            target=root/path
            assert target.is_file() or (target/'index.html').is_file(), f'Missing local link: {page}: {href}'
