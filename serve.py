"""Run the same static site that can be published to Pages."""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import re
from urllib.parse import urlsplit,parse_qs
from urllib.request import urlopen
import webbrowser
from background_translation import BackgroundTranslation
from local_pdfs import LocalPDFs

class LibraryHandler(SimpleHTTPRequestHandler):
    server_version='KrugLibrary/1'
    def list_directory(self,path):
        self.send_error(404,'Open index.html')
        return None

    def local_request(self,post=False):
        port=self.server.server_port
        host=self.headers.get('Host')
        valid=host in (f'127.0.0.1:{port}',f'localhost:{port}')
        if not valid or self.headers.get('Sec-Fetch-Site')=='cross-site':return False
        return not post or self.headers.get('Origin')=='http://'+host

    def json(self,value,status=200):
        body=json.dumps(value,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path=urlsplit(self.path)
        if path.path in ('/__krug/material','/__krug/status','/__krug/text','/__krug/translation-progress'):
            if not self.local_request():return self.send_error(403)
            try:query=parse_qs(path.query,max_num_fields=80)
            except ValueError:return self.send_error(400)
            q={k:v[0] for k,v in query.items()}
            if path.path=='/__krug/text':
                return self.json(self.server.translations.text_results(q.get('lang',''),query.get('key',[])))
            if path.path=='/__krug/translation-progress':
                return self.json(self.server.translations.progress(q.get('lang','en')))
            if path.path.endswith('/status'):return self.json(self.server.pdfs.state(q.get('key','')))
            row=self.server.pdfs.material(q.get('source'),q.get('doc'))
            return self.json({k:row[k] for k in ('href','lang')} if row else {'href':None})
        return super().do_GET()

    def do_POST(self):
        if self.path!='/__krug/translate':return self.send_error(404)
        if not self.local_request(post=True):return self.send_error(403)
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=8192:return self.send_error(413)
            req=json.loads(self.rfile.read(size))
            if not isinstance(req,dict) or any(not isinstance(v,str) for v in req.values()):
                return self.send_error(400)
        except (ValueError,UnicodeError):return self.send_error(400)
        return self.json(self.server.pdfs.submit(req))

    def send_head(self):
        route=urlsplit(self.path).path
        if not route.startswith('/__krug/'):return super().send_head()
        if not self.local_request():self.send_error(403);return None
        match=re.fullmatch(r'/__krug/(pdf|translated)/([0-9a-f]{64})\.pdf',route)
        if match and self.server.pdfs.restricted(*match.groups()):
            self.send_error(410,'Available only on the official school page')
            return None
        p=self.server.pdfs.file(*match.groups()) if match else None
        if not p:self.send_error(404);return None
        f=p.open('rb');size=p.stat().st_size;start,end=0,size-1
        req=self.headers.get('Range')
        if req:
            m=re.fullmatch(r'bytes=(\d*)-(\d*)',req)
            if m and (m[1] or m[2]):
                start=int(m[1]) if m[1] else max(0,size-int(m[2]))
                end=min(int(m[2]),size-1) if m[1] and m[2] else size-1
            if not m or not (m[1] or m[2]) or start>end or start>=size:
                f.close();self.send_response(416);self.send_header('Content-Range',f'bytes */{size}')
                self.send_header('Content-Length','0');self.end_headers();return None
        self.send_response(206 if req else 200)
        self.send_header('Content-Type','application/pdf')
        self.send_header('Content-Disposition','inline')
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Length',str(end-start+1))
        if req:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        f.seek(start);self._bytes_remaining=end-start+1
        return f

    def copyfile(self,source,outputfile):
        left=getattr(self,'_bytes_remaining',None)
        if left is None:return super().copyfile(source,outputfile)
        self._bytes_remaining=None
        while left:
            data=source.read(min(128*1024,left))
            if not data:break
            outputfile.write(data);left-=len(data)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8780)
    parser.add_argument('--open',action='store_true',help='Открыть в браузере')
    parser.add_argument('--no-background-translation',action='store_true')
    args=parser.parse_args()
    folder=Path(__file__).resolve().parent/'dist'
    url=f'http://127.0.0.1:{args.port}/'
    try:
        server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(LibraryHandler,directory=str(folder)))
    except OSError:
        try:
            with urlopen(url,timeout=2) as response:
                if not response.headers.get('Server','').startswith('KrugLibrary/'):raise ValueError()
        except (OSError,ValueError):
            parser.exit(1,f'Порт {args.port} занят. Укажите другой порт через --port.\n')
        print('Сайт уже работает:',url,flush=True)
        if args.open:webbrowser.open(url)
        return
    print('Сайт открыт:',url,flush=True)
    server.pdfs=LocalPDFs(folder)
    server.translations=BackgroundTranslation(server.pdfs)
    if not args.no_background_translation:server.translations.start()
    if args.open:threading.Thread(target=webbrowser.open,args=(url,),daemon=True).start()
    with server:
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.translations.stop.set()
if __name__=='__main__':main()
