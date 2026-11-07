'use strict';
const $=id=>document.getElementById(id);
const ru=new Intl.NumberFormat('ru');
const fmt=value=>ru.format(value);
const norm=value=>String(value??'').normalize('NFKC').toLocaleLowerCase('ru').replaceAll('ё','е').replace(/[‐‑‒–—−]/g,'-').replace(/\s+/g,' ').trim();
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const read=(file,page)=>'reader.html?'+new URLSearchParams({file,page});
const types={study:'Учебный том',practice:'Тематический задачник',solutions:'Официальные материалы',originals:'Архивный оригинал',contexts:'Кейсы DANO'};
const fetchJSON=async path=>{const res=await fetch(path);if(!res.ok)throw Error(path);return res.json();};
function fill(select,options){for(const [key,label] of options)select.add(new Option(label,key));}
function fail(status){
  $(status).innerHTML='Не удалось загрузить указатель. Откройте сайт через локальный запуск или используйте <a href="contents.html">прямые ссылки на PDF</a>.';
}
function shelf(data){
  for(const [id,value] of [['books',data.volumes.length],['pages',data.pages],['tasks',data.tasks],['study',data.study]])$('stat-'+id).textContent=fmt(value);
  const grid=$('volume-grid'),q=$('volume-query'),grade=$('volume-grade');
  const chips=[...document.querySelectorAll('#kinds button')];let kind='';
  const indexed=data.volumes.map(v=>[v,norm([v.title,data.topics[v.topic],v.number,String(v.number).padStart(2,'0'),v.grade,types[v.kind]].join(' '))]);
  function paint(){
    const words=norm(q.value).split(' ').filter(Boolean);
    const selected=indexed.filter(([v,key])=>
      (!kind||(kind==='archive'?['originals','contexts'].includes(v.kind):v.kind===kind))&&
      (!grade.value||String(v.grade)===grade.value)&&words.every(word=>key.includes(word)));
    $('volume-count').textContent='Показано '+fmt(selected.length)+' из '+fmt(data.volumes.length)+' томов';
    grid.innerHTML=selected.map(([v])=>{
      const number=String(v.number).padStart(2,'0');
      return '<a class="volume" data-kind="'+esc(v.kind)+'" href="'+esc(read(v.file,1))+'"><div class="volume-top"><span class="volume-no">'+number+
        '</span><small>'+esc(v.grade?v.grade+' класс':types[v.kind]||'Том')+'</small></div><strong>'+esc(v.title)+
        '</strong><div class="volume-bottom"><span>'+fmt(v.pages)+' стр.</span><span>Читать ↗</span></div></a>';
    }).join('')||'<p class="empty">По этим фильтрам нет томов. Попробуйте изменить запрос.</p>';
  }
  function selectKind(value){kind=value;for(const c of chips)c.setAttribute('aria-pressed',String(c.dataset.kind===value));}
  chips.forEach(c=>c.addEventListener('click',()=>{selectKind(c.dataset.kind);if(kind!=='study')grade.value='';paint();}));
  document.querySelectorAll('[data-level]').forEach(c=>c.addEventListener('click',()=>{
    q.value='';grade.value=c.dataset.level;selectKind('study');paint();$('volumes').scrollIntoView({block:'start'});
  }));
  $('volume-reset').addEventListener('click',()=>{q.value='';grade.value='';selectKind('');paint();q.focus();});
  q.addEventListener('input',paint);grade.addEventListener('change',()=>{if(grade.value)selectKind('study');paint();});paint();
}
function browserReader(data){
  const params=new URLSearchParams(location.search);
  const file=params.get('file');const v=data.volumes.find(x=>x.file===file);
  if(!v){$('read-note').innerHTML='Том не найден. <a href="index.html#volumes">Вернуться к оглавлению</a>.';return;}
  const page=Math.max(1,Math.min(v.pages,parseInt(params.get('page'),10)||1));
  const url='books/'+encodeURIComponent(v.file);
  $('read-title').textContent=v.title;
  document.title=v.title+' · Круг';
  $('read-meta').textContent='Том '+String(v.number).padStart(2,'0')+(v.grade?' · '+v.grade+' класс':'');
  $('read-note').textContent='Страница '+page+' из '+v.pages+'. Если просмотр не отображается, откройте PDF отдельно.';
  $('read-direct').href=url+'#page='+page;$('read-download').href=url;$('read-actions').hidden=false;
  if(navigator.pdfViewerEnabled!==false){$('read-frame').src=url+'#page='+page;$('read-frame').hidden=false;}
}
async function taskSearch(data){
  const form=$('task-form'),grid=$('task-grid'),status=$('task-count');
  const q=$('task-query'),topic=$('task-topic'),source=$('task-source'),grade=$('task-grade'),solved=$('task-solved');
  fill(topic,Object.entries(data.topics));
  fill(source,Object.entries(data.sources).sort((a,b)=>a[1].localeCompare(b[1],'ru')));
  fill(grade,Array.from({length:7},(_,i)=>[String(5+i),String(5+i)]));
  const initial=new URLSearchParams(location.search);
  for(const el of [q,topic,source,grade])if(initial.has(el.name))el.value=initial.get(el.name);
  solved.checked=initial.get('solved')==='1';
  let page=0,selected=[],timer;
  const size=24;
  const rows=(await fetchJSON('catalog/tasks.json')).map(r=>({
    ...r,grades:(r.grade||'').match(/\d+/g)?.map(Number)||[],
    key:norm([r.id,r.n,r.text,r.year,r.grade,data.sources[r.source],data.topics[r.topic],...(r.tags||[])].join(' ')),
    official:r.solutions.some(s=>s[2])
  }));
  const title=r=>esc(data.topics[r.topic]||'Архивная задача');
  const button=(location,label,primary=false)=>'<a class="btn'+(primary?'':' btn-line')+'" href="'+esc(read(location[0],location[1]))+'">'+label+' ↗</a>';
  function card(r){
    const short=r.text.length>360;
    const preview=short?r.text.slice(0,360).trimEnd()+'…':r.text;
    const meta=[data.sources[r.source],r.year,r.grade?'Класс '+r.grade:null,r.n?'№ '+r.n:null].filter(Boolean);
    const allLinks=r.solutions.map(s=>button(s,s[2]?'Официальные материалы':'Возможный разбор'));
    const full=short?'<details><summary>Показать полный извлечённый текст</summary><div class="snippet">'+esc(r.text)+'</div></details>':'';
    return '<article class="task"><div class="task-meta"><a class="tag" href="tasks.html?q='+encodeURIComponent(r.id)+'">'+esc(r.id)+'</a>'+
      meta.map(x=>'<span>'+esc(x)+'</span>').join(' · ')+'</div><h2>'+title(r)+'</h2><div class="snippet">'+esc(preview)+'</div>'+full+
      '<div class="task-actions">'+(r.at?button(r.at,'Условие',true):'')+(r.original?button(r.original,'Полный оригинал',!r.at):'')+
      allLinks.slice(0,2).join('')+(r.url?'<a class="btn btn-line" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer">Источник ↗</a>':'')+
      '</div>'+(allLinks.length>2?'<details><summary>Другие найденные материалы ('+(allLinks.length-2)+')</summary><div class="task-actions">'+allLinks.slice(2).join('')+'</div></details>':'')+'</article>';
  }
  function render(){
    const start=page*size,end=Math.min(start+size,selected.length);
    status.textContent='Найдено записей: '+fmt(selected.length);
    grid.innerHTML=selected.slice(start,end).map(card).join('')||'<p class="empty">Задачи не найдены. Измените запрос или сбросьте фильтры.</p>';
    $('task-pager').hidden=selected.length<=size;
    $('task-page').textContent=fmt(start+1)+'–'+fmt(end)+' из '+fmt(selected.length);
    $('task-prev').disabled=page===0;$('task-next').disabled=end>=selected.length;
  }
  function filter(){
    const words=norm(q.value).split(' ').filter(Boolean),g=Number(grade.value);
    selected=rows.filter(r=>(!topic.value||r.topic===topic.value)&&(!source.value||r.source===source.value)&&
      (!g||(r.grades.length&&Math.min(...r.grades)<=g&&Math.max(...r.grades)>=g))&&(!solved.checked||r.official)&&words.every(w=>r.key.includes(w)));
    const params=new URLSearchParams();
    for(const el of [q,topic,source,grade])if(el.value.trim())params.set(el.name,el.value.trim());
    if(solved.checked)params.set('solved','1');
    history.replaceState(null,'',location.pathname+(params.size?'?'+params:''));
    page=0;render();
  }
  form.addEventListener('submit',e=>{e.preventDefault();clearTimeout(timer);filter();});
  form.addEventListener('reset',e=>{e.preventDefault();for(const el of [q,topic,source,grade])el.value='';solved.checked=false;filter();q.focus();});
  form.addEventListener('change',filter);q.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(filter,180);});
  for(const [id,delta] of [['task-prev',-1],['task-next',1]])$(id).addEventListener('click',()=>{page+=delta;render();status.scrollIntoView({block:'start'});});
  filter();
}
(async()=>{
  if(!($('volume-grid')||$('task-grid')||$('read-frame')))return;
  try{
    const data=await fetchJSON('catalog/library.json');
    if($('volume-grid'))shelf(data);
    if($('task-grid'))await taskSearch(data);
    if($('read-frame'))browserReader(data);
  }catch(err){console.error(err);fail($('volume-grid')?'volume-count':$('task-grid')?'task-count':'read-note');}
})();
