"""Validate the whole deployable tree without external dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
import json

root=Path(__file__).resolve().parents[1]/'dist'
m=json.loads((root/'catalog/library.json').read_text())
rows=json.loads((root/'catalog/tasks.json').read_text())
vols=m['volumes'];pages={v['file']:v['pages'] for v in vols}
assert len(pages)==len(vols)
assert [v['number'] for v in vols]==list(range(1,len(vols)+1))
assert sum(pages.values())==m['pages'] and len(rows)==m['tasks']
assert len({r['id'] for r in rows})==len(rows)
expected=set(pages)|{'00-start.pdf'}
assert {p.name for p in (root/'books').glob('*.pdf')}==expected
for name in expected:
    with (root/'books'/name).open('rb') as file:assert file.read(5)==b'%PDF-',name
for r in rows:
    for d in [r['at'],r['original'],*r['solutions']]:
        if d:assert d[0] in pages and 1<=d[1]<=pages[d[0]],(r['id'],d)

class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('href','src') or not value:continue
            url=urlsplit(value)
            if url.scheme or url.netloc or not url.path:continue
            assert not url.path.startswith('/'),value
            target=(root/unquote(url.path)).resolve()
            assert target.is_relative_to(root) and target.is_file(),value

for html in root.glob('*.html'):Links().feed(html.read_text(encoding='utf-8'))
files=list(root.rglob('*'));assert not any(f.is_symlink() for f in files)
sizes=[f.stat().st_size for f in files if f.is_file()]
assert max(sizes)<100*1024**2
assert sum(sizes)<1_000_000_000
print(f'Проверено: {len(vols)} томов, {len(rows)} записей, {sum(sizes):,} байт сайта.')
