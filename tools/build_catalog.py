"""Export just the files and fields needed by the static library."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'output/library'
dst=ROOT/'dist/catalog';dst.mkdir(parents=True,exist_ok=True)
m=json.loads((src/'manifest.json').read_text())
raw=json.loads((src/'catalogue.json').read_text())
vols={v['file']:v for v in m['volumes']}
if len(vols)!=len(m['volumes']):raise ValueError('Повторяющиеся файлы томов')

def destination(p,offset=0):
    if not p:return None
    filename=p['file'];page=p['page']+offset
    if filename not in vols or not 1<=page<=vols[filename]['pages']:
        raise ValueError(f'Неверная ссылка на том: {p}')
    return [filename,page]

def source_url(value):
    try:
        p=urlsplit(value or '')
        if p.scheme in ('http','https') and p.hostname and not p.username and not p.password:return value
    except ValueError: pass
    return None

rows=[]
for r in raw:
    orig=r.get('original_volume')
    if orig:
        offset=min(max((r.get('page') or 1)-1,0),orig['pages']-1)
        orig=destination(orig,offset)
    matches={}
    for s in r.get('solutions',[]):
        if not s.get('book'):continue
        target=tuple(destination(s['book']))
        matches[target]=matches.get(target,False) or bool(s.get('exact_document'))
    sol=[[*d,exact] for d,exact in sorted(matches.items(),key=lambda pair:not pair[1])]
    rows.append(dict(id=r['book_id'],n=r.get('number'),text=r['text'],topic=r['topic'],
                     source=r['source'],year=r.get('year'),grade=r.get('grade'),
                     tags=r.get('concepts',[]),at=destination(r.get('placement')),original=orig,
                     url=source_url(r.get('url')),solutions=sol))
def write(name,value):
    (dst/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
write('library.json',dict(title='Круг',volumes=list(vols.values()),pages=m['total_pages'],tasks=len(rows),
                         lessons=m['lessons'],study=m['study_volumes'],exercises=m['study_exercises'],
                         topics={x['id']:x['title'] for x in m['topics']},
                         sources={r['source']:r['source_name'] for r in raw}))
write('tasks.json',rows)
print(f'{len(vols)} томов, {len(rows)} записей')
