'use strict';
const catalogueTranslations=new Map();
const translatedText=(node,text,apply=value=>{node.textContent=value;})=>({node,text,apply});
const needsTextTranslation=text=>siteLanguage==='en'?/[а-яё]/i.test(text):/[a-z]/i.test(text)&&!/[а-яё]/i.test(text);
async function translateCatalogue(entries){
  if(!localPDFServer||!globalThis.crypto?.subtle)return;
  const pending=new Map();
  for(const entry of entries){
    if(!entry.node||!entry.text||entry.text.length>10000||!needsTextTranslation(entry.text))continue;
    if(catalogueTranslations.has(entry.text)){
      const value=catalogueTranslations.get(entry.text);
      if(value&&entry.node.isConnected)entry.apply(value);
      continue;
    }
    const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(entry.text));
    const key=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('');
    if(!pending.has(key))pending.set(key,[]);
    pending.get(key).push(entry);
  }
  while(pending.size){
    for(const [key,group] of pending)if(!group.some(entry=>entry.node.isConnected))pending.delete(key);
    if(!pending.size)return;
    if(!document.hidden){
      try{
        const keys=[...pending.keys()];
        for(let offset=0;offset<keys.length;offset+=72){
          const params=new URLSearchParams({lang:siteLanguage});
          for(const key of keys.slice(offset,offset+72))params.append('key',key);
          const data=await fetchJSON('__krug/text?'+params);
          for(const [key,value] of Object.entries(data)){
            for(const entry of pending.get(key)||[]){
              catalogueTranslations.set(entry.text,value);
              if(value&&entry.node.isConnected)entry.apply(value);
            }
            pending.delete(key);
          }
        }
      }catch{/* Keep the readable original during a connection interruption. */}
    }
    if(pending.size)await new Promise(resolve=>setTimeout(resolve,4500));
  }
}

async function showTranslationProgress(){
  const el=document.getElementById('site-translation-progress');
  if(!el||!localPDFServer)return;
  while(el.isConnected){
    if(!document.hidden)try{
      const p=await fetchJSON('__krug/translation-progress?'+new URLSearchParams({lang:siteLanguage}));
      if(p.models&&(p.textTotal||p.pdfTotal)){
        const parts=[];
        if(p.textTotal)parts.push(t('Тексты проверены ','Text checked ')+fmt(p.textDone)+' / '+fmt(p.textTotal)+
          t(' · Переведено ',' · Translated ')+fmt(p.textTranslated));
        if(p.pdfTotal)parts.push(t('PDF готовы ','PDFs ready ')+fmt(p.pdfReady)+
          t(' · Проверено ',' · Checked ')+fmt(p.pdfDone)+' / '+fmt(p.pdfTotal));
        if(p.pdfPages)parts.push(t('Текущий PDF ','Current PDF ')+fmt(p.pdfPagesDone)+' / '+fmt(p.pdfPages));
        el.textContent=t('Фоновый перевод. ','Background translation. ')+parts.join(' · ');
        el.hidden=false;
      }
    }catch{/* The progress counter is optional. */}
    await new Promise(resolve=>setTimeout(resolve,5000));
  }
}
document.addEventListener('DOMContentLoaded',showTranslationProgress);
