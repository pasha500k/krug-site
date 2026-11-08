'use strict';
const $=id=>document.getElementById(id);
const ru=new Intl.NumberFormat(siteLanguage);
const fmt=value=>ru.format(value);
const norm=value=>String(value??'').normalize('NFKC').toLocaleLowerCase('ru').replaceAll('ё','е').replace(/[‐‑‒–—−]/g,'-').replace(/\s+/g,' ').trim();
const tokens=value=>norm(value).match(/[\p{L}\p{N}]+/gu)||[];
const contestNames=[
  ['vosh','всош','вош','всеросс','vsosh','всероссийская олимпиада школьников'],
  ['hse','вп','вшэ','вышка','hse','высшая проба'],
  ['turgor','тургор','тг','turgor','турнир городов','tournament of towns'],
  ['mmo','ммо','mmo','московская математическая олимпиада'],
  ['imo','имо','imo','международная математическая олимпиада','international mathematical olympiad'],
  ['egmo','егмо','egmo'],['apmo','апмо','apmo'],['dano','олимпиада дано','dano'],['euler','эйлер','euler'],
  ['ommo','оммо','ommo'],['rosatom','росатом','rosatom'],['lomonosov','ломоносов','lomonosov'],
  ['turlom','турлом','турнир ломоносова'],['spb','спбмо'],['phystech','физтех','мфти'],
  ['matfest','матпраздник','математический праздник'],['memo','мемо','memo'],['bmo','британская олимпиада','bmo'],
  ['balkan','балканская олимпиада']
].flatMap(([id,...names])=>names.map(name=>[id,' '+tokens(name).join(' ')+' '])).sort((a,b)=>b[1].length-a[1].length);
function contestQuery(query){
  const key=' '+tokens(query).join(' ')+' ';
  if(key===' дано ')return {contest:'dano',words:[]};
  const match=contestNames.find(([,name])=>key.includes(name));
  return match?{contest:match[0],words:tokens(key.replace(match[1],' '))}:{contest:'',words:tokens(query)};
}
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const read=(file,page)=>'reader.html?'+new URLSearchParams({file,page});
const readDocument=(source,doc)=>'reader.html?'+new URLSearchParams({source,doc});
const types={study:t('Учебный том','Study volume'),practice:t('Тематический задачник','Topic problem book'),solutions:t('Официальные материалы','Official materials'),originals:t('Архивный оригинал','Original archive'),contexts:t('Кейсы DANO','DANO cases')};
const fetchJSON=async path=>{const res=await fetch(path);if(!res.ok)throw Error(path);return res.json();};
function fill(select,options){for(const [key,label] of options)select.add(new Option(label,key));}
function fail(status){
  $(status).innerHTML=t('Не удалось загрузить указатель. Откройте сайт через локальный запуск или используйте <a href="contents.html">прямые ссылки на PDF</a>.','Could not load the catalogue. Start the local site or use the <a href="contents.html">direct PDF links</a>.');
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
    $('volume-count').textContent=t('Показано ','Showing ')+fmt(selected.length)+t(' из ',' of ')+fmt(data.volumes.length)+t(' томов',' volumes');
    grid.innerHTML=selected.map(([v])=>{
      const number=String(v.number).padStart(2,'0');
      return '<a class="volume" data-kind="'+esc(v.kind)+'" href="'+esc(read(v.file,1))+'"><div class="volume-top"><span class="volume-no">'+number+
        '</span><small>'+esc(v.grade?t(v.grade+' класс','Grade '+v.grade):types[v.kind]||t('Том','Volume'))+'</small></div><strong>'+esc(v.title)+
        '</strong><div class="volume-bottom"><span>'+fmt(v.pages)+t(' стр.',' pp.')+'</span><span>'+t('Читать ↗','Read ↗')+'</span></div></a>';
    }).join('')||'<p class="empty">'+t('По этим фильтрам нет томов. Попробуйте изменить запрос.','No volumes match these filters.')+'</p>';
  }
  function selectKind(value){kind=value;for(const c of chips)c.setAttribute('aria-pressed',String(c.dataset.kind===value));}
  chips.forEach(c=>c.addEventListener('click',()=>{selectKind(c.dataset.kind);if(kind!=='study')grade.value='';paint();}));
  document.querySelectorAll('[data-level]').forEach(c=>c.addEventListener('click',()=>{
    q.value='';grade.value=c.dataset.level;selectKind('study');paint();$('volumes').scrollIntoView({block:'start'});
  }));
  $('volume-reset').addEventListener('click',()=>{q.value='';grade.value='';selectKind('');paint();q.focus();});
  q.addEventListener('input',paint);grade.addEventListener('change',()=>{if(grade.value)selectKind('study');paint();});paint();
}
function showBook(v,page){
  const url='books/'+encodeURIComponent(v.file);
  $('read-title').textContent=v.title;
  document.title=v.title+' · Круг';
  $('read-meta').textContent=t('Том ','Volume ')+String(v.number).padStart(2,'0')+(v.grade?t(' · '+v.grade+' класс',' · Grade '+v.grade):'');
  $('read-note').textContent=t('Страница '+page+' из '+v.pages+'. Если просмотр не отображается, откройте PDF отдельно.','Page '+page+' of '+v.pages+'. If the viewer does not load, open the PDF separately.');
  $('read-direct').href=url+'#page='+page;$('read-download').href=url;$('read-actions').hidden=false;
  if(navigator.pdfViewerEnabled!==false){$('read-frame').src=url+'#page='+page;$('read-frame').hidden=false;}
}
const schoolSource=source=>source?.category==='Вступительные';
const officialPageNote=()=>t('Материалы доступны на официальной странице школы.','Materials are available on the official school page.');
const officialPageLabel=()=>t('Официальная страница школы','Official school page');
const schoolPermissions=()=>fetchJSON('catalog/permissions.json').catch(()=>({}));
function permissionLabel(row){
  if(row?.status==='draft')return t('Разрешение не подтверждено · письмо подготовлено, не отправлено','Permission unconfirmed · request drafted, unsent');
  if(row?.status==='sent')return t('На согласовании · ожидаем ответа школы','Permission pending · awaiting the school’s reply');
  return t('Разрешение не подтверждено','Permission unconfirmed');
}
async function browserReader(data){
  const params=new URLSearchParams(location.search);
  if(!params.has('doc')){
    const v=data.volumes.find(x=>x.file===params.get('file'));
    if(!v){$('read-note').innerHTML=t('Том не найден. <a href="index.html#volumes">Вернуться к оглавлению</a>.','Volume not found. <a href="index.html#volumes">Back to contents</a>.');return;}
    const page=Math.max(1,Math.min(v.pages,parseInt(params.get('page'),10)||1));
    showBook(v,page);
    await pdfLanguages({href:'books/'+encodeURIComponent(v.file),page,request:{file:v.file},originalNote:$('read-note').textContent});
    return;
  }
  const directory=await fetchJSON('catalog/archives.json');
  const sid=params.get('source'),url=params.get('doc');
  const source=directory.sources.find(s=>s.id===sid);
  let item=directory.items.find(r=>r.source===sid&&r.url===url);
  if(source&&!source.officialPageOnly&&!item&&source.url!==url){
    const tasks=await fetchJSON('catalog/tasks.json').catch(()=>[]);
    const task=tasks.find(r=>r.source===sid&&r.url===url);
    if(task)item={title:source.name,year:task.year,grade:task.grade,source:sid,url};
  }
  if(!source||(!source.officialPageOnly&&!item&&source.url!==url)){
    $('read-note').textContent=t('Документ не найден в каталоге.','Document not found in the catalogue.');
    return;
  }
  const official=new URL(source.officialPageOnly?source.url:url);
  if(!['https:','http:'].includes(official.protocol)||official.username||official.password)return;
  $('read-back').href=(source.category==='Вступительные'?'schools.html':'archives.html')+'?'+new URLSearchParams({source:sid});
  $('read-back').textContent=t('← К материалам','← Back to materials');
  $('read-back-row').hidden=false;
  $('read-source').href=official.href;
  $('read-source').textContent=source.officialPageOnly?officialPageLabel()+' ↗':t('Оригинал у источника ↗','Open official original ↗');
  $('read-source').hidden=false;
  $('read-title').textContent=item?.title||source.name;
  $('read-meta').textContent=[source.name,item?.year,item?.grade].filter(Boolean).join(' · ');
  document.title=$('read-title').textContent+' · Круг';
  if(schoolSource(source)){
    const info=(await schoolPermissions())[sid];
    const status=$('read-permission');
    status.hidden=false;
    status.textContent=permissionLabel(info)+' · ';
    const details=document.createElement('a');
    details.href='permissions.html#'+encodeURIComponent(sid);
    details.textContent=t('Подробнее','Details');
    status.append(details);
    if(source.officialPageOnly||!localPDFServer){
      for(const id of ['read-direct','read-download','offline-book'])$(id).hidden=true;
      $('read-actions').hidden=false;
      $('read-note').textContent=officialPageNote();
      return;
    }
  }
  const links=await fetchJSON('catalog/book-documents.json').catch(()=>({}));
  const entry=Object.hasOwn(links,url)?links[url]:null;
  const volume=entry&&data.volumes.find(v=>v.file===entry[0]);
  const local=await localPDFMaterial(sid,url);
  if(local){
    setPDFViewer(local.href,1);
    $('read-note').textContent=t('Локальная копия оригинала. Организатор: ','Local copy of the original. Organiser: ')+source.name+'.';
  }else if(volume){
    showBook(volume,entry[1]);
    $('read-note').textContent=t('Полный документ в томе № '+volume.number+', начиная со страницы '+entry[1]+'.',
      'Full document in volume '+volume.number+', starting at page '+entry[1]+'.');
  }else{
    for(const id of ['read-direct','read-download','offline-book'])$(id).hidden=true;
    $('read-actions').hidden=false;
    const mixed=location.protocol==='https:'&&official.protocol==='http:';
    if(!mixed){
      $('read-frame').referrerPolicy='no-referrer';
      $('read-frame').title=t('Документ с официального сайта','Document from the official website');
      $('read-frame').src=official.href;
      $('read-frame').hidden=false;
    }
    $('read-note').textContent=mixed
      ?t('Источник доступен по HTTP. Откройте оригинал по ссылке выше.','This source uses HTTP. Open the official original above.')
      :t('Документ загружается с сайта организатора. Если просмотр недоступен, откройте оригинал по ссылке выше.',
        'This document loads from the organiser’s website. If it cannot be displayed here, open the official original above.');
  }
  if(item){
    await pdfLanguages({item,directory,request:{source:sid,doc:url},canTranslate:!!local,
      href:local?.href||(volume?'books/'+encodeURIComponent(volume.file):official.href),
      page:local?1:volume?entry[1]:0,originalNote:$('read-note').textContent});
  }
}
async function taskSearch(data){
  const form=$('task-form'),grid=$('task-grid'),status=$('task-count');
  const q=$('task-query'),topic=$('task-topic'),source=$('task-source'),grade=$('task-grade'),year=$('task-year'),solved=$('task-solved');
  const [records,directory]=await Promise.all([fetchJSON('catalog/tasks.json'),fetchJSON('catalog/archives.json')]);
  const aliases=Object.fromEntries(directory.sources.map(s=>[s.id,s.aliases]));
  const years=[...new Set(records.map(r=>r.year).filter(Boolean))].sort((a,b)=>b-a);
  fill(topic,Object.entries(data.topics));
  fill(source,Object.entries(data.sources).sort((a,b)=>a[1].localeCompare(b[1],'ru')));
  fill(grade,Array.from({length:7},(_,i)=>[String(5+i),String(5+i)]));
  fill(year,years.map(y=>[String(y),String(y)]));
  const initial=new URLSearchParams(location.search);
  for(const el of [q,topic,source,grade,year])if(initial.has(el.name))el.value=initial.get(el.name);
  solved.checked=initial.get('solved')==='1';
  let page=0,selected=[],timer;
  const size=24;
  const rows=records.map(r=>({
    ...r,grades:(r.grade||'').match(/\d+/g)?.map(Number)||[],
    key:tokens([r.id,r.n,r.text,r.year,r.grade?r.grade+' класс grade':'',r.source,data.sources[r.source],aliases[r.source],data.topics[r.topic],...(r.tags||[])].join(' ')).join(' '),
    official:r.solutions.some(s=>s[2])
  }));
  const title=r=>esc(data.topics[r.topic]||t('Архивная задача','Archive problem'));
  const button=(location,label,primary=false)=>'<a class="btn'+(primary?'':' btn-line')+'" href="'+esc(read(location[0],location[1]))+'">'+label+' ↗</a>';
  function card(r){
    const short=r.text.length>360;
    const preview=short?r.text.slice(0,360).trimEnd()+'…':r.text;
    const meta=[data.sources[r.source],r.year,r.grade?t('Класс ','Grade ')+r.grade:null,r.n?'№ '+r.n:null].filter(Boolean);
    const allLinks=r.solutions.map(s=>button(s,s[2]?t('Официальные материалы','Official material'):t('Возможный разбор','Suggested solution')));
    const full=short?'<details><summary>'+t('Показать полный извлечённый текст','Show full extracted text')+'</summary><div class="snippet">'+esc(r.text)+'</div></details>':'';
    const versions=r.year&&['imo','egmo'].includes(r.source)?'<a class="btn btn-line" href="archives.html?'+esc(new URLSearchParams({source:r.source,year:r.year}).toString())+'">'+t('Языковые версии','Language editions')+'</a>':'';
    return '<article class="task"><div class="task-meta"><a class="tag" href="tasks.html?q='+encodeURIComponent(r.id)+'">'+esc(r.id)+'</a>'+
      meta.map(x=>'<span>'+esc(x)+'</span>').join(' · ')+'</div><h2>'+title(r)+'</h2><div class="snippet">'+esc(preview)+'</div>'+full+
      '<div class="task-actions">'+(r.at?button(r.at,t('Условие','Problem'),true):'')+(r.original?button(r.original,t('Полный оригинал','Full original'),!r.at):'')+
      allLinks.slice(0,2).join('')+(r.url?'<a class="btn btn-line" href="'+esc(readDocument(r.source,r.url))+'">'+t('Документ источника','Source document')+'</a>':'')+versions+
      '</div>'+(allLinks.length>2?'<details><summary>'+t('Другие найденные материалы','Other materials')+' ('+(allLinks.length-2)+')</summary><div class="task-actions">'+allLinks.slice(2).join('')+'</div></details>':'')+'</article>';
  }
  function render(){
    const start=page*size,end=Math.min(start+size,selected.length);
    status.textContent=t('Найдено записей: ','Problems found: ')+fmt(selected.length);
    grid.innerHTML=selected.slice(start,end).map(card).join('')||'<p class="empty">'+t('Задачи не найдены. ','No problems found. ')+'<a href="archives.html?q='+encodeURIComponent(q.value)+'">'+t('Проверить официальные архивы','Search official archives')+'</a>.</p>';
    $('task-pager').hidden=selected.length<=size;
    $('task-page').textContent=fmt(start+1)+'–'+fmt(end)+t(' из ',' of ')+fmt(selected.length);
    $('task-prev').disabled=page===0;$('task-next').disabled=end>=selected.length;
  }
  function filter(){
    const {contest,words}=contestQuery(q.value),g=Number(grade.value),id=/^з-\d{5}$/.test(norm(q.value))?norm(q.value):'';
    const queryYear=contest&&words.find(w=>/^(?:19|20)\d{2}$/.test(w));
    selected=rows.filter(r=>(!topic.value||r.topic===topic.value)&&(!source.value||r.source===source.value)&&
      (!contest||r.source===contest)&&(!queryYear||String(r.year)===queryYear)&&
      (!year.value||String(r.year)===year.value)&&(!g||(r.grades.length&&Math.min(...r.grades)<=g&&Math.max(...r.grades)>=g))&&
      (!solved.checked||r.official)&&(id?norm(r.id)===id:words.every(w=>r.key.includes(w))));
    const params=new URLSearchParams();
    for(const el of [q,topic,source,grade,year])if(el.value.trim())params.set(el.name,el.value.trim());
    if(solved.checked)params.set('solved','1');
    history.replaceState(null,'',location.pathname+(params.size?'?'+params:''));
    page=0;render();
  }
  form.addEventListener('submit',e=>{e.preventDefault();clearTimeout(timer);filter();});
  form.addEventListener('reset',e=>{e.preventDefault();for(const el of [q,topic,source,grade,year])el.value='';solved.checked=false;filter();q.focus();});
  form.addEventListener('change',filter);q.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(filter,180);});
  for(const [id,delta] of [['task-prev',-1],['task-next',1]])$(id).addEventListener('click',()=>{page+=delta;render();status.scrollIntoView({block:'start'});});
  filter();
}
async function supportPage(){
  try{
    const config=await fetchJSON('catalog/support.json');
    if(typeof config.url!=='string'||!config.url.trim())return;
    const url=new URL(config.url);
    if(url.protocol!=='https:'||url.username||url.password)return;
    $('support-status').textContent=t('Кнопка откроет страницу перевода в платёжном сервисе.','The button opens the payment provider’s page.');
    const link=$('support-link');
    link.href=url.href;
    link.hidden=false;
  }catch{
    // Keep the inactive notice if the configuration is unavailable.
  }
}
(async()=>{
  if($('support-card')){await supportPage();return;}
  if(!($('volume-grid')||$('task-grid')||$('read-frame')))return;
  try{
    const data=await fetchJSON('catalog/library.json');
    if($('volume-grid'))shelf(data);
    if($('task-grid'))await taskSearch(data);
    if($('read-frame'))await browserReader(data);
  }catch(err){console.error(err);fail($('volume-grid')?'volume-count':$('task-grid')?'task-count':'read-note');}
})();
