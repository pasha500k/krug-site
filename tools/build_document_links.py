"""Link official URLs to the full documents already included in the books."""
import json
from pathlib import Path
import sys

site=Path(__file__).resolve().parents[1]/'dist'
source=Path(sys.argv[1]) if len(sys.argv)>1 else site.parents[1]/'output/library/document-map.json'
volumes={v['file']:v['pages'] for v in json.loads((site/'catalog/library.json').read_text())['volumes']}
links={}
for group in json.loads(source.read_text()).values():
    for row in group.values():
        file,start,length=row['file'],row['page'],row['pages']
        if file not in volumes or not 1<=start<=start+length-1<=volumes[file]:
            raise ValueError(f'Invalid document location: {row}')
        links[row['source_url']]=[file,start,length]
(site/'catalog/book-documents.json').write_text(json.dumps(links,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(f'{len(links)} документов связаны с томами.')
