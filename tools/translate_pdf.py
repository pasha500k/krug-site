"""Translate PDF prose on the original pages using local language models."""
import argparse
import json
from pathlib import Path
import re

import ctranslate2
import sentencepiece

from translate_layout import translate

ROOT=Path(__file__).resolve().parents[2]
MODEL_ROOT=ROOT/'data/translation-models'
MATH=re.compile(r'\$[^$\n]+\$|\\\([^\n]+?\\\)|(?<!\w)[A-Za-z](?!\w)|\b[A-Z]{2,4}\b|(?<!\w)[−-]?\d+(?:[.,]\d+)?(?!\w)|[=<>≤≥≠∑∏∫√±×÷∞π²³⁰¹⁴⁵⁶⁷⁸⁹]+')
PLACEHOLDER=re.compile(r'QZ\s*(\d+)\s*ZQ',re.I)
def mask(text):
    values=[]
    def keep(match):
        values.append(match.group())
        return 'QZ'+str(len(values)-1)+'ZQ'
    return MATH.sub(keep,text),values

def restore(text,values):
    ids=[int(m[1]) for m in PLACEHOLDER.finditer(text)]
    if sorted(ids)!=list(range(len(values))):return None
    return PLACEHOLDER.sub(lambda m:values[int(m[1])],text)

class Models:
    def __init__(self):self.engines={}
    def translate(self,source,target,text):
        if source==target:return text,True
        pair=source+'-'+target
        if pair not in self.engines:
            root=MODEL_ROOT/pair
            tok=sentencepiece.SentencePieceProcessor(model_file=str(root/'sentencepiece.model'))
            eng=ctranslate2.Translator(str(root/'model'),device='cpu',compute_type='int8',intra_threads=3)
            self.engines[pair]=(tok,eng)
        tok,eng=self.engines[pair]
        pieces=[]
        for para in re.split(r'(?<=[.!?])\s+',text):
            words=para.split()
            pieces.extend(' '.join(words[i:i+100]) for i in range(0,len(words),100))
        if not pieces:return text,True
        masks=[mask(p) for p in pieces]
        inputs=[tok.encode(a,out_type=str) for a,_ in masks]
        limit=min(256,max(48,2*max(map(len,inputs))))
        out=eng.translate_batch(inputs,beam_size=2,max_input_length=512,max_decoding_length=limit)
        translated=[]
        all_ok=True
        for original,(_,values),result in zip(pieces,masks,out):
            new=restore(tok.decode(result.hypotheses[0]).strip(),values)
            if not new:all_ok=False
            translated.append(new or original)
        return ' '.join(translated),all_ok

def language(text,source):
    if source and source not in ('ru','en'):return source
    latin=len(re.findall('[A-Za-z]',text));cyr=len(re.findall('[А-Яа-яЁё]',text))
    if latin+cyr<5:return ''
    return 'ru' if cyr>=max(4,latin*.25) else 'en'

def progress(path,**state):
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(state,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    temp.replace(path)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('pdf','result','meta','status'):p.add_argument(name,type=Path)
    a=p.parse_args()
    translate(a.pdf,a.result,json.loads(a.meta.read_text()),a.status,Models(),language,progress)
