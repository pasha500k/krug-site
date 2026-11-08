'use strict';
const $=id=>document.getElementById(id);
const date=v=>v?new Date(v).toLocaleString('ru'):'—';
const e=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function show(){
  try{
    const r=await fetch('status.json',{cache:'no-store'});if(!r.ok)throw Error();
    const s=await r.json();
    $('state').textContent=s.running?'Идёт проверка':'Последняя проверка завершена';
    $('schedule').textContent='Источников: '+s.total+' · Интервал: '+s.interval+' ч · Начало: '+date(s.started)+(s.next_check?' · Следующая: '+date(s.next_check):'');
    $('cards').innerHTML=s.sources.map(x=>{
      const errors=x.errors||[],message=!x.checked_at?'Ещё не проверен':errors.length?'Есть ошибки':'Проверен';
      return '<article class="card"><span class="badge'+(errors.length?' warn':'')+'">'+message+'</span><h3>'+e(x.name)+'</h3><p>Проверено: '+e(date(x.checked_at))+
        '</p><p>Ссылок: '+(x.links??'—')+' · Новых: '+(x.new??'—')+' · Без изменений: '+(x.unchanged??'—')+
        '</p>'+(x.limited?'<p>Проверены последние страницы в пределах лимита.</p>':'')+
        (errors.length?'<details><summary>Причина</summary>'+errors.map(y=>'<p>'+e(y)+'</p>').join('')+'</details>':'')+
        '<a href="'+e(x.url)+'" target="_blank" rel="noopener noreferrer">Официальный источник ↗</a></article>';
    }).join('');
  }catch{$('state').textContent='Отчёт пока недоступен';}
}
$('refresh').addEventListener('click',show);
show();setInterval(show,8000);
