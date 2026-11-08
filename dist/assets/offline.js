'use strict';
if('serviceWorker' in navigator){
  const registration=navigator.serviceWorker.register('sw.js').catch(()=>null);
  function setup(button,status,type,params){
    if(!button)return;
    button.addEventListener('click',async()=>{
      button.disabled=true;
      status.textContent=t('Сохраняем…','Saving…');
      try{
        const reg=await registration;
        if(!reg)throw Error();
        const ready=await navigator.serviceWorker.ready;
        const channel=new MessageChannel();
        const result=await new Promise((resolve,reject)=>{
          const timeout=setTimeout(()=>{channel.port1.close();reject(Error());},120000);
          channel.port1.onmessage=e=>{clearTimeout(timeout);channel.port1.close();resolve(e.data);};
          ready.active.postMessage({type,...params()},[channel.port2]);
        });
        if(!result.ok)throw Error();
        status.textContent=result.existing?t('Уже сохранено для офлайна.','Already saved for offline use.'):t('Сохранено. Можно открыть без интернета.','Saved. Available offline.');
      }catch{
        status.textContent=t('Не удалось сохранить. Проверь подключение и свободное место.','Could not save. Check your connection and available storage.');
      }finally{button.disabled=false;}
    });
  }
  setup(document.getElementById('offline-save'),document.getElementById('offline-status'),'save-catalogue',()=>({}));
  setup(document.getElementById('offline-book'),document.getElementById('offline-book-status'),'save-book',()=>({path:document.getElementById('read-download').getAttribute('href')}));
}else{
  for(const id of ['offline-save','offline-book'])if(document.getElementById(id))document.getElementById(id).hidden=true;
  const status=document.getElementById('offline-status');
  if(status)status.textContent=t('Сохранение в браузере недоступно. PDF можно скачать со страницы тома.','Offline browser storage is unavailable. Download PDFs from the reader instead.');
}
