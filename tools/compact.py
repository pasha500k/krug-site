"""Copy the entire edition. Adopt a compact PDF only after checking its content."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import shutil
import sys
import pymupdf as fitz

def refs(page):
    return [{k: v for k,v in link.items() if k not in ('xref','id')} for link in page.get_links()]

def copy_volume(job):
    source,target,expected=job
    with fitz.open(source) as a:
        if len(a)!=expected: raise ValueError(f'Unexpected page count: {source.name}')
        if source.stat().st_size < 12_000_000:
            shutil.copy2(source,target)
            return source.name,source.stat().st_size,target.stat().st_size,'copy'
    with TemporaryDirectory(dir=target.parent) as temp:
        candidate=Path(temp)/'compact.pdf'
        try:
            with fitz.open(source) as doc:
                doc.subset_fonts()
                doc.save(candidate,garbage=4,deflate=True,deflate_fonts=True)
            with fitz.open(source) as a,fitz.open(candidate) as b:
                same=len(a)==len(b) and a.get_toc()==b.get_toc()
                matrix=fitz.Matrix(.37,.37)
                for p,q in zip(a,b):
                    if not same:break
                    same=(p.get_text()==q.get_text() and refs(p)==refs(q)
                          and p.get_pixmap(matrix=matrix).samples==q.get_pixmap(matrix=matrix).samples)
            if same and candidate.stat().st_size<source.stat().st_size:
                os.replace(candidate,target)
                return source.name,source.stat().st_size,target.stat().st_size,'verified'
        except (RuntimeError,ValueError) as err:
            print(f'{source.name}: {err}',file=sys.stderr,flush=True)
        shutil.copy2(source,target)
        return source.name,source.stat().st_size,target.stat().st_size,'copy'

if __name__=='__main__':
    src,dst=map(Path,sys.argv[1:3]);dst.mkdir(parents=True,exist_ok=True)
    m=json.loads((src/'manifest.json').read_text());volumes=m['volumes']
    with fitz.open(src/'00-start.pdf') as d:guide=len(d)
    jobs=[(src/v['file'],dst/v['file'],v['pages']) for v in volumes+[dict(file='00-start.pdf',pages=guide)]]
    with ProcessPoolExecutor(max_workers=4) as pool:
        results=[]
        for row in pool.map(copy_volume,jobs):
            print(*row,flush=True);results.append(row)
    print('TOTAL',sum(r[1] for r in results),sum(r[2] for r in results),flush=True)
