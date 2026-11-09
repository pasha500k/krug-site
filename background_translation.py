"""Incremental local translation of catalogue text and mirrored PDFs."""
from collections import OrderedDict
from hashlib import sha256
from itertools import chain
from threading import Event, Lock, Thread
from time import monotonic
from urllib.parse import urlsplit
import json
import re
import subprocess

from local_pdfs import DATA, PROJECT, RUNTIME, read

TEXT_CACHE = DATA / 'translated' / 'catalogue-text-v2.json'
TEXT_BATCH = 24
KEY = re.compile(r'^[0-9a-f]{64}$')
LOCALES = ('ru', 'en')


def text_key(text):
    return sha256(text.encode('utf-8')).hexdigest()


def official_group(row):
    path = urlsplit(row['url']).path
    if row['source'] == 'imo':
        pattern = r'/assets/documents/problems/(\d{4})/\1_[a-z]+\.pdf'
    elif row['source'] == 'egmo':
        pattern = r'/egmos/(egmo\d+)/paper-(day[12])-[a-z]+\.pdf'
    else:
        return None
    match = re.fullmatch(pattern, path, re.I)
    return (row['source'], row.get('kind'), *match.groups()) if match else None


class BackgroundTranslation:
    def __init__(self, pdfs):
        self.pdfs = pdfs
        self.stop = Event()
        self.lock = Lock()
        self.requested = OrderedDict()
        self.texts = {}
        self.results = read(TEXT_CACHE, {})
        self.pdf_requests = iter(())
        self.pdf_refresh = 0
        self.pdf_pending = None
        self.pdf_total = self.pdf_done = self.pdf_ready = 0
        self.last_catalog = 0

    def start(self):
        Thread(target=self.text_loop, name='catalogue-translation', daemon=True).start()
        Thread(target=self.pdf_loop, name='archive-translation', daemon=True).start()

    def catalogue(self):
        dist = self.pdfs.dist / 'catalog'
        tasks = self.pdfs.cached_json(dist / 'tasks.json', [])
        library = self.pdfs.cached_json(dist / 'library.json', {})
        archive = self.pdfs.cached_json(dist / 'archives.json', {})
        blocked = self.pdfs.page_only()
        labels = [*library.get('topics', {}).values(), *library.get('sources', {}).values()]
        labels.extend(v['title'] for v in library.get('volumes', []))
        labels.extend(s['name'] for s in archive.get('sources', []))
        labels.extend(s.get('note', '') for s in archive.get('sources', []))
        labels.extend(r['title'] for r in archive.get('items', []) if r['source'] not in blocked)
        labels.extend(r['text'] for r in tasks if r['source'] not in blocked)
        return {text_key(text): text for text in labels if text and len(text) <= 10000}

    def text_results(self, target, keys):
        if target not in LOCALES:
            return {}
        with self.lock:
            translations = self.results.get(target, {})
            found = {}
            for key in keys[:72]:
                if not KEY.fullmatch(key):
                    continue
                if key in translations:
                    found[key] = translations[key]
                elif key in self.texts and len(self.requested) < 250:
                    self.requested[(target, key)] = None
            return found

    def progress(self, target):
        with self.lock:
            entries = self.results.get(target, {})
            key = self.pdf_pending
            counts = dict(textTotal=len(self.texts), textDone=sum(k in entries for k in self.texts),
                          textTranslated=sum(bool(entries.get(k)) for k in self.texts),
                          pdfTotal=self.pdf_total, pdfDone=self.pdf_done, pdfReady=self.pdf_ready)
        state = self.pdfs.state(key) if key else {}
        return dict(counts, models=self.pdfs.models_ready(), pdfPages=state.get('total', 0),
                    pdfPagesDone=state.get('done', 0))

    def next_text_batch(self):
        with self.lock:
            batch = {}
            while self.requested and len(batch) < TEXT_BATCH:
                (target, key), _ = self.requested.popitem(last=False)
                if key in self.texts and key not in self.results.get(target, {}):
                    batch[(target, key)] = self.texts[key]
            for key, value in self.texts.items():
                for target in ('en', 'ru'):
                    if key not in self.results.get(target, {}):
                        batch.setdefault((target, key), value)
                    if len(batch) >= TEXT_BATCH:
                        return batch
            return batch

    def text_loop(self):
        while not self.stop.is_set():
            try:
                if monotonic()-self.last_catalog >= 30 or not self.last_catalog:
                    texts = self.catalogue()
                    with self.lock:
                        self.texts = texts
                        for target, results in self.results.items():
                            self.results[target] = {k: v for k, v in results.items() if k in texts}
                    self.last_catalog = monotonic()
                batch = self.next_text_batch() if self.pdfs.models_ready() else {}
                if not batch:
                    self.stop.wait(5)
                    continue
                rows = [(target, key, value) for (target, key), value in batch.items()]
                run = subprocess.run([str(RUNTIME), str(PROJECT/'tools/translate_text.py')],
                                     input=json.dumps(rows), capture_output=True, text=True,
                                     timeout=180, check=True)
                translated = json.loads(run.stdout)
                with self.lock:
                    for target, key, value in translated:
                        self.results.setdefault(target, {})[key] = value
                    temp = TEXT_CACHE.with_suffix('.tmp')
                    temp.parent.mkdir(parents=True, exist_ok=True)
                    temp.write_text(json.dumps(self.results, ensure_ascii=False, separators=(',', ':')),
                                    encoding='utf-8')
                    temp.replace(TEXT_CACHE)
                self.stop.wait(1)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                print(f'Catalogue translation: {error}', flush=True)
                self.stop.wait(30)

    def requests(self):
        dist = self.pdfs.dist / 'catalog'
        sources = self.pdfs.cached_json(dist / 'archives.json', {}).get('items', [])
        official = {(official_group(row), row.get('lang')) for row in sources
                    if row['source'] in ('imo', 'egmo')}
        blocked = self.pdfs.page_only()
        originals = sorted(self.pdfs.mirror().values(),
                           key=lambda row: (-(row.get('year') or 0), row.get('kind') != 'problems', row['url']))
        volumes = iter(self.pdfs.cached_json(dist / 'library.json', {}).get('volumes', []))
        count = 0
        for row in originals:
            lang = row.get('lang') or ''
            if row['source'] in blocked or lang not in ('', *LOCALES):
                continue
            group = official_group(row)
            for target in ('en', 'ru'):
                if target == lang or (group and (group, target) in official):
                    continue
                yield dict(source=row['source'], doc=row['url'], lang=target)
                count += 1
                if count % 12 == 0 and (volume := next(volumes, None)):
                    yield dict(file=volume['file'], lang='en')
        for volume in volumes:
            yield dict(file=volume['file'], lang='en')

    def pdf_loop(self):
        while not self.stop.is_set():
            try:
                if not self.pdfs.models_ready() or self.pdfs.has_active_jobs():
                    self.stop.wait(2)
                    continue
                if self.pdf_pending:
                    self.record_pdf(self.pdfs.state(self.pdf_pending))
                    with self.lock:
                        self.pdf_pending = None
                for request in self.pdf_requests:
                    if self.stop.is_set():
                        return
                    status = self.pdfs.submit(request, background=True)
                    if status['state'] == 'busy':
                        self.pdf_requests = chain((request,), self.pdf_requests)
                        break
                    if status['state'] == 'working':
                        with self.lock:
                            self.pdf_pending = status['key']
                        break
                    self.record_pdf(status)
                else:
                    if monotonic() >= self.pdf_refresh:
                        requests = list(self.requests())
                        with self.lock:
                            self.pdf_total = len(requests)
                            self.pdf_done = self.pdf_ready = 0
                        self.pdf_requests = iter(requests)
                        self.pdf_refresh = monotonic()+60
                    else:
                        self.stop.wait(5)
                self.stop.wait(1)
            except (OSError, ValueError) as error:
                print(f'Archive translation: {error}', flush=True)
                self.stop.wait(30)

    def record_pdf(self, status):
        with self.lock:
            self.pdf_done += 1
            self.pdf_ready += status['state'] == 'ready'
