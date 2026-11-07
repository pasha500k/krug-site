"""Run the same static site that can be published to Pages."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.request import urlopen
import webbrowser

class LibraryHandler(SimpleHTTPRequestHandler):
    server_version='KrugLibrary/1'
    def list_directory(self,path):
        self.send_error(404,'Open index.html')
        return None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8780)
    parser.add_argument('--open',action='store_true',help='Открыть в браузере')
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
    if args.open:threading.Thread(target=webbrowser.open,args=(url,),daemon=True).start()
    with server:
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
