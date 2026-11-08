"""Fill catalogue metadata from cached source documents; leave unassigned levels blank."""
from collections import defaultdict
from pathlib import Path
import argparse
import json
import sqlite3
import sys
import re

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from olympiad_collector.metadata import infer_document,round_years
from olympiad_collector.archive_watch import atomic_json

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path,default=ROOT/'data/archive.sqlite')
    p.add_argument('--snapshot',type=Path,default=ROOT/'output/library/catalogue.json')
    p.add_argument('--target',type=Path,default=ROOT/'krug-site/dist/catalog/tasks.json')
    args=p.parse_args()
    original=json.loads(args.snapshot.read_text())
    rows=json.loads(args.target.read_text())
    published={r['book_id']:r for r in original}
    groups=defaultdict(list)
    for r in original:groups[r['document_id']].append(r)
    updates={}
    with sqlite3.connect(args.archive.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        for d in db.execute('SELECT id,source,url,title,text,year,grade,parent_url FROM documents'):
            group=groups.get(d['id'])
            if not group or d['url']!=group[0]['url']:continue
            inferred=infer_document(d['source'],d['url'],d['title'],d['text'],d['parent_url'])
            by_round=round_years(d['text'],group) if d['source']=='turgor' else {}
            for r in group:
                year=r['year'] or by_round.get(r['id']) or d['year'] or inferred['year']
                grade=r['grade'] or d['grade'] or inferred['grade']
                basis='round' if r['id'] in by_round else ('document' if d['year'] else inferred['year_basis'])
                grade_basis='document' if d['grade'] else inferred['grade_basis']
                if not grade and d['source']=='vosh':
                    match=re.fullmatch(r'(8|9|10|11)\.\d{1,2}',r['number'] or '')
                    if match:grade=match[1];grade_basis='vosh-number'
                updates[r['book_id']]=(year,grade,basis,grade_basis)
    years=grades=0
    for row in rows:
        if row['id'] not in updates:continue
        year,grade,basis,grade_basis=updates[row['id']]
        if not published[row['id']]['year'] and year:
            row['year']=year;row['yearBasis']=basis;years+=1
        if not published[row['id']]['grade'] and grade:
            row['grade']=grade;row['gradeBasis']=grade_basis;grades+=1
    atomic_json(args.target,rows)
    print('Год восстановлен:',years,'из',sum(not r['year'] for r in original))
    print('Класс восстановлен:',grades,'из',sum(not r['grade'] for r in original))

if __name__=='__main__':main()
