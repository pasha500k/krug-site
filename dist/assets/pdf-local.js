'use strict';
const localPDFServer=['127.0.0.1','localhost'].includes(location.hostname);
const localPDFPath=/^__krug\/(?:pdf|translated)\/[0-9a-f]{64}\.pdf$/;
const pdfStorage=(key,value)=>{
  try{
    if(value!==undefined){localStorage.setItem(key,JSON.stringify(value));return value;}
    return JSON.parse(localStorage.getItem(key)||'null');
  }catch{return null;}
};
async function localPDFMaterial(source,doc){
  if(!localPDFServer)return null;
  const key='krug-pdf:original:'+source+':'+doc;
  try{
    const row=await fetchJSON('__krug/material?'+new URLSearchParams({source,doc}));
    if(row.href&&localPDFPath.test(row.href))return pdfStorage(key,row)||row;
    return null;
  }catch{
    const saved=pdfStorage(key);
    return saved&&localPDFPath.test(saved.href)?saved:null;
  }
}
function versionGroup(item){
  if(!item?.url)return '';
  const path=new URL(item.url).pathname;
  if(item.source==='imo'){
    const m=path.match(/^\/assets\/documents\/problems\/(\d{4})\/\1_[a-z]+\.pdf$/i);
    return m?'imo-'+m[1]:'';
  }
  if(item.source==='egmo'){
    const m=path.match(/^\/egmos\/(egmo\d+)\/paper-(day[12])-[a-z]+\.pdf$/i);
    return m?'egmo-'+m[1]+'-'+m[2]:'';
  }
  if(item.source==='rmm'){
    const m=path.match(/\/RMM(20\d{2})-Day([12])-[a-z]+(?:[-_]?Solutions)?\.pdf$/i);
    return m?'rmm-'+m[1]+'-'+m[2]:'';
  }
  return '';
}
function setPDFViewer(href,page,local=true){
  const url=href+(page>0?'#page='+page:'');
  const frame=$('read-frame');
  const mixed=location.protocol==='https:'&&href.startsWith('http:');
  if(!mixed&&navigator.pdfViewerEnabled!==false){
    frame.referrerPolicy=local?'same-origin':'no-referrer';
    if(frame.getAttribute('src')!==url)frame.src=url;
    frame.hidden=false;
  }else frame.hidden=true;
  $('read-direct').href=url;$('read-direct').hidden=mixed;
  $('read-download').href=href;$('read-download').hidden=!local;
  $('offline-book').hidden=!local||!('serviceWorker' in navigator);
  $('read-actions').hidden=false;
}
async function pdfLanguages({item,directory,request,href,page=0,originalNote,canTranslate=true}){
  const select=$('read-language');
  const group=versionGroup(item);
  const versions=new Map();
  if(group)for(const candidate of directory.items){
    if(candidate.lang&&candidate.kind===item.kind&&versionGroup(candidate)===group&&!versions.has(candidate.lang))
      versions.set(candidate.lang,candidate);
  }
  const choices=new Set(['ru','en',...versions.keys()]);
  const names=new Intl.DisplayNames([siteLanguage],{type:'language'});
  for(const lang of [...choices].sort()){
    let label=lang;try{label=names.of(lang)||lang;}catch{}
    select.add(new Option(label,lang));
  }
  select.options[0].textContent=t('Оригинал','Original');
  $('read-language-label').textContent=t('Язык PDF','PDF language');
  $('read-language-field').hidden=false;
  let generation=0;
  const originalLocal=!/^https?:/.test(href);
  const showOriginal=()=>{
    setPDFViewer(href,page,originalLocal);
    $('read-note').textContent=originalNote;
  };
  async function load(lang){
    const run=++generation;
    showOriginal();
    $('pdf-translation-status').textContent='';
    if(lang==='original'||item?.lang===lang)return;
    const official=versions.get(lang);
    if(official){
      const local=await localPDFMaterial(official.source,official.url);
      if(run!==generation)return;
      setPDFViewer(local?.href||official.url,1,!!local);
      $('read-note').textContent=t('Официальная языковая версия от организатора.','Official language edition from the organiser.');
      return;
    }
    if(!localPDFServer||!canTranslate||!['ru','en'].includes(lang)){
      $('pdf-translation-status').textContent=t('Для перевода нужна локальная копия PDF или официальная версия на выбранном языке.',
          'Translation requires a local PDF copy or an official edition in the selected language.');
      return;
    }
    const cacheKey='krug-pdf:layout:v3:'+JSON.stringify({...request,lang});
    const show=(r)=>{
      setPDFViewer(r.href,page||1);
      $('read-note').textContent=r.curated
        ?t('Неофициальный английский перевод условий в исходном макете.','Unofficial English translation of the problems in the original layout.')
        :r.reviewed
          ?t('Неофициальный перевод с проверенными фрагментами.','Unofficial translation with reviewed passages.')
          :t('Машинный перевод в исходном макете.','Machine translation in the original layout.');
      $('pdf-translation-status').textContent=r.skipped
        ?t('Часть текста осталась на языке оригинала: её нельзя надёжно заменить в этом макете.',
          'Some text remains in the original language because it could not be safely replaced in this layout.')
        :'';
    };
    try{
      const start=async()=>{
        const response=await fetch('__krug/translate',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({...request,lang})});
        if(!response.ok)throw Error();
        return response.json();
      };
      let result=await start();
      while(result.state==='busy'&&run===generation){
        $('pdf-translation-status').textContent=t('Перевод в очереди… Пока доступен оригинал.',
          'Translation queued… The original is available in the meantime.');
        await new Promise(resolve=>setTimeout(resolve,3500));
        if(run!==generation)return;
        result=await start();
      }
      const jobKey=result.key;
      while(result.state==='working'&&jobKey&&run===generation){
        $('pdf-translation-status').textContent=result.total
          ?t('Перевод: ','Translating: ')+fmt(result.done||0)+' / '+fmt(result.total)
          :t('Готовим перевод… Оригинал уже можно читать.','Preparing the translation… You can read the original now.');
        await new Promise(resolve=>setTimeout(resolve,1500));
        result=await fetchJSON('__krug/status?'+new URLSearchParams({key:jobKey}));
      }
      if(run!==generation)return;
      if(result.state==='ready'&&localPDFPath.test(result.href)){pdfStorage(cacheKey,result);show(result);return;}
      if(result.state!=='original')$('pdf-translation-status').textContent=
        t('Перевод недоступен или не удалось извлечь текст. Показан оригинал.','Translation is unavailable or the text could not be extracted. Showing the original.');
    }catch{
      if(run!==generation)return;
      const cached=pdfStorage(cacheKey);
      if(cached&&localPDFPath.test(cached.href))show(cached);
      else $('pdf-translation-status').textContent=t('Локальный перевод недоступен.','Local translation is unavailable.');
    }
  }
  select.addEventListener('change',()=>{
    const params=new URLSearchParams(location.search);
    params.set('lang',select.value);
    history.replaceState(null,'',location.pathname+'?'+params+location.hash);
    load(select.value);
  });
  const requested=new URLSearchParams(location.search).get('lang');
  const preferred=requested==='original'||choices.has(requested)?requested:
    choices.has(documentLanguage)?documentLanguage:siteLanguage;
  select.value=preferred;
  await load(preferred);
}
