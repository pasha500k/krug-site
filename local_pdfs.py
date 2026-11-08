"""Loopback-only local originals and a single cached PDF translation queue."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
import hashlib
import json
import re
import subprocess

PROJECT=Path(__file__).resolve().parent
ROOT=PROJECT.parent
DATA=ROOT/'data'
RUNTIME=ROOT/'.venv-translate/bin/python'
JOBS=DATA/'translated'
RENDERER='krug-pdf-layout-v1'
HEX=re.compile(r'^[0-9a-f]{64}$')

def read(path,default):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError):return default

class LocalPDFs:
    def __init__(self,dist):
        self.dist=Path(dist)
        self.lock=Lock()
        self.active=set()
        self.memo={}
        self.hashes={}
        self.pool=ThreadPoolExecutor(max_workers=1)

    def cached_json(self,path,default):
        try:stamp=path.stat().st_mtime_ns
        except OSError:return default
        with self.lock:
            if path not in self.memo or self.memo[path][0]!=stamp:
                self.memo[path]=(stamp,read(path,default))
            return self.memo[path][1]

    def mirror(self):
        return self.cached_json(DATA/'mirror.json',{})

    def page_only(self):
        permissions=self.cached_json(self.dist/'catalog/permissions.json',{})
        return {sid for sid,row in permissions.items() if row.get('officialPageOnly')}

    def restricted(self,kind,key):
        if not HEX.fullmatch(key):return False
        page_only=self.page_only()
        if kind=='pdf':
            return any(row['sha']==key and row['source'] in page_only for row in self.mirror().values())
        if kind=='translated':
            meta=read(JOBS/(key+'.metadata.json'),{})
            return self.mirror().get(meta.get('url'),{}).get('source') in page_only
        return False

    def material(self,sid,url):
        if sid in self.page_only():return None
        row=self.mirror().get(url)
        if not row or row['source']!=sid or not HEX.fullmatch(row['sha']):return None
        path=DATA/'files'/(row['sha']+'.pdf')
        if not path.is_file():return None
        return dict(row,path=path,href='__krug/pdf/'+row['sha']+'.pdf')

    def file(self,kind,key):
        if not HEX.fullmatch(key) or self.restricted(kind,key):return None
        if kind=='pdf':
            # No filesystem path from the client; only a catalogued content hash.
            if not any(v['sha']==key for v in self.mirror().values()):return None
            p=DATA/'files'/(key+'.pdf')
        elif kind=='translated':
            if self.state(key).get('state')!='ready':return None
            p=JOBS/(key+'.pdf')
        else:return None
        return p if p.is_file() else None

    def state(self,key):
        if not HEX.fullmatch(key):return {'state':'missing'}
        if self.restricted('translated',key):return {'state':'unavailable'}
        with self.lock:
            status=read(JOBS/(key+'.json'),{})
            active=key in self.active
        if status.get('state')=='ready':
            if (JOBS/(key+'.pdf')).is_file():return dict(status,href='__krug/translated/'+key+'.pdf')
            return {'state':'missing'}
        if status.get('state') in ('original','unavailable','error'):return status
        return (status or {'state':'working'}) if active else {'state':'missing'}

    def resolve(self,req):
        if req.get('file'):
            library=self.cached_json(self.dist/'catalog/library.json',{})
            volume=next((v for v in library.get('volumes',[]) if v['file']==req['file']),None)
            if not volume:return None
            path=self.dist/'books'/volume['file']
            if not path.is_file():return None
            stat=path.stat();cache_key=(path,stat.st_size,stat.st_mtime_ns)
            with self.lock:
                sha=self.hashes.get(cache_key)
            if not sha:
                with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
                with self.lock:self.hashes[cache_key]=sha
            return path,sha,dict(title=volume['title'],organizer='Круг / Krug',url='',source='')
        row=self.material(req.get('source'),req.get('doc'))
        if not row:return None
        archive=self.cached_json(self.dist/'catalog/archives.json',{})
        sid=row['source']
        name=next((s['name'] for s in archive.get('sources',[]) if s['id']==sid),sid)
        title=row.get('title') or name
        if title.isdecimal():title=name+' · '+title+(' · класс '+row['grade'] if row.get('grade') else '')
        return row['path'],row['sha'],dict(title=title,organizer=name,url=row['url'],source=row.get('lang',''))

    def submit(self,req):
        target=req.get('lang')
        if target not in ('ru','en'):return {'state':'unavailable'}
        resolved=self.resolve(req)
        if not resolved:return {'state':'missing'}
        path,sha,meta=resolved
        if meta['source']==target:return {'state':'original'}
        if meta['source'] not in ('','en','ru'):return {'state':'unavailable'}
        if not RUNTIME.is_file() or not all((DATA/'translation-models'/pair/'model/model.bin').is_file() for pair in ('en-ru','ru-en')):
            return {'state':'unavailable','reason':'models'}
        meta['target']=target
        payload=json.dumps(meta,ensure_ascii=False,sort_keys=True)
        key=hashlib.sha256((RENDERER+sha+payload).encode()).hexdigest()
        status=self.state(key)
        if status['state'] not in ('missing','error'):return dict(status,key=key)
        JOBS.mkdir(parents=True,exist_ok=True)
        with self.lock:
            if key not in self.active:
                if len(self.active)>=6:return {'state':'busy'}
                self.active.add(key)
                try:self.pool.submit(self.run,key,path,payload)
                except RuntimeError:
                    self.active.discard(key)
                    return {'state':'error'}
        return {'state':'working','key':key}

    def run(self,key,path,payload):
        state=JOBS/(key+'.json')
        spec=JOBS/(key+'.metadata.json')
        try:
            spec.write_text(payload,encoding='utf-8')
            state.write_text('{"state":"working"}',encoding='utf-8')
            with (JOBS/(key+'.log')).open('wb') as log:
                process=subprocess.run([str(RUNTIME),str(PROJECT/'tools/translate_pdf.py'),
                    str(path),str(JOBS/(key+'.pdf')),str(spec),str(state)],
                    stdout=log,stderr=log,timeout=3600)
            if process.returncode:raise RuntimeError('worker failed')
        except Exception:
            state.write_text('{"state":"error"}',encoding='utf-8')
        finally:
            with self.lock:self.active.discard(key)
