'use strict';
const archiveContests=[...contestNames,...contestAliases([
  ['vosh','всероссийская олимпиада школьников по математике','всош по математике','vsoch','russian mathematical olympiad'],
  ['euler','олимпиада имени эйлера','олимпиада леонарда эйлера','эйлера','euler olympiad'],
  ['turgor','международный математический турнир городов','математический турнир городов'],
  ['oral-geometry','устная олимпиада по геометрии','устная геометрия','oral geometry olympiad'],
  ['emc','emc','европейский математический кубок','european mathematical cup'],
  ['purple-comet','purple comet math meet','purple comet','purplecomet','пурпурная комета'],
  ['vsesib','всесибирская открытая олимпиада','всесибирская','всесиб','vsesib'],
  ['sharygin','геометрическая олимпиада имени шарыгина','шарыгина','шарыгин','sharygin'],
  ['belchonok','бельчонок','belchonok'],['pvg','покори воробьёвы горы','пвг'],
  ['spbu','олимпиада школьников спбгу','спбгу'],['kurchatov','курчатов','kurchatov'],
  ['cmo','канадская математическая олимпиада','canadian mathematical olympiad','cmo'],
  ['cjmo','канадская юниорская математическая олимпиада','canadian junior mathematical olympiad','cjmo'],
  ['rmm','romanian master of mathematics','румынский математический мастер','rmm'],
  ['ukmog','uk mog','ukmog','uk mathematical olympiad for girls']
])].sort((a,b)=>b[1].length-a[1].length);
const dayKey=value=>norm(value).replace(/(?<!\p{L})(?:(?:day|день)\s*([12])|([12])(?:\s*-?\s*(?:й|ый))?\s+день)(?![\p{L}\d])/gu,(_,prefix,suffix)=>'day'+(prefix||suffix));
function archiveQuery(value,schools){
  let year='',grade='';
  const query=dayKey(value)
    .replace(/\b((?:19|20)\d{2})(?:\s*[/\-]\s*((?:19|20)?\d{2}))?\b/g,(match,start,end)=>{
      const next=Number(start)+1;
      const following=end&&(end.length===2&&String(next).endsWith(end)?next:Number(end));
      if(end&&following!==Number(start)+1)return match;
      year||=String(following||start);
      return ' ';
    })
    .replace(/(?<![\p{L}\d])(?:(?:grades?|класс)\s+(1[01]|[1-9])|(1[01]|[1-9])(?:\s*-?\s*(?:й|ый|го))?\s*(?:класс(?:а|е)?|кл\.?))(?![\p{L}\d])/gu,(_,prefix,suffix)=>{
      grade||=prefix||suffix;
      return ' ';
    });
  const parsed=schools?{contest:'',words:tokens(query)}:contestQuery(query,archiveContests);
  return {...parsed,year,grade};
}
async function archiveDirectory(){
  const pane=$('archive-filters');
  if(!pane)return;
  try{
    const data=await fetchJSON('catalog/archives.json');
    const schools=pane.dataset.mode==='schools';
    const sources=data.sources.filter(s=>schoolSource(s)===schools);
    const permissions=schools?await schoolPermissions():{};
    const byID=new Map(sources.map(s=>[s.id,s]));
    const items=data.items.filter(r=>byID.has(r.source)&&!byID.get(r.source).officialPageOnly);
    const fields=Object.fromEntries(['query','source','year','grade','lang'].map(k=>[k,$('archive-'+k)]));
    const params=new URLSearchParams(location.search);
    if(schools)fields.query.placeholder=t('Например, Летово или 239','Example: Letovo or 239');
    const names={
      vosh:'Russian Mathematical Olympiad (VsOSh)',hse:'HSE Higher Test',turgor:'Tournament of Towns',dano:'DANO — data analysis',
      mmo:'Moscow Mathematical Olympiad',rosatom:'Rosatom',lomonosov:'Lomonosov Olympiad (MSU)',imo:'International Mathematical Olympiad (IMO)',
      euler:'Euler Olympiad',ommo:'Inter-University Mathematical Olympiad (OMMO)',phystech:'Phystech Olympiad',spb:'Saint Petersburg Mathematical Olympiad',
      matfest:'Mathematical Festival',turlom:'Lomonosov Tournament',memo:'Middle European Mathematical Olympiad (MEMO)',
      bmo:'British Mathematical Olympiad (BMO)',balkan:'Balkan Mathematical Olympiad',letovo:'Letovo School',sunc:'Kolmogorov School (MSU)',school239:'Physics and Mathematics Lyceum No. 239',
      'hse-lyceum':'HSE University Lyceum',pvg:'Conquer the Sparrow Hills! (MSU)',spbu:'SPbU School Olympiad',
      belchonok:'Belchonok (Siberian Federal University)',kurchatov:'Kurchatov Olympiad',
      vsesib:'All-Siberian Open Olympiad (Novosibirsk State University)',sharygin:'Sharygin Geometry Olympiad',
      archimed:'Archimedes Mathematical Tournament',cmo:'Canadian Mathematical Olympiad',
      cjmo:'Canadian Junior Mathematical Olympiad',ukmog:'UK Mathematical Olympiad for Girls',
      'oral-geometry':'Oral Geometry Olympiad',emc:'European Mathematical Cup (EMC)'
    };
    const name=s=>t(s.name,names[s.id]||s.name);
    fill(fields.source,sources.map(s=>[s.id,name(s)]));
    const years=[...new Set(items.map(r=>r.year).filter(Boolean))].sort((a,b)=>b-a);
    fill(fields.year,years.map(y=>[String(y),String(y)]));
    fill(fields.grade,Array.from({length:11},(_,i)=>[String(i+1),String(i+1)]));
    const dn=new Intl.DisplayNames([siteLanguage],{type:'language'});
    const langName=code=>{try{return dn.of(code)||code;}catch{return code;}};
    const langs=[...new Set(items.map(r=>r.lang).filter(Boolean))].sort((a,b)=>langName(a).localeCompare(langName(b),siteLanguage));
    fill(fields.lang,langs.map(c=>[c,langName(c)]));
    for(const [k,el] of Object.entries(fields))if(params.has(k==='query'?'q':k))el.value=params.get(k==='query'?'q':k);
    const key=s=>norm([s.id,s.name,name(s),s.aliases].join(' '));
    const indexed=items.map(r=>({...r,
      key:dayKey([key(byID.get(r.source)),r.title,r.titleEn,r.originalTitle,r.source!=='dano'?'математика математике mathematics math':'',r.year,r.grade,r.lang,r.kind==='solutions'?'решения ответы solutions answers':r.kind==='combined'?'задачи решения problems solutions':'задачи задания problems'].join(' '))}));
    const grid=$('archive-files'),cards=$('archive-sources'),status=$('archive-count'),pager=$('archive-pager');
    let current=0,filtered=[];
    let activeGrade='';
    const size=24;
    const href=(url,label,cls='btn btn-line')=>'<a class="'+cls+'" href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+label+' ↗</a>';
    function paintFiles(){
      const start=current*size,end=Math.min(start+size,filtered.length);
      grid.innerHTML=filtered.slice(start,end).map(r=>{
        const kind=r.kind==='solutions'?t('Решения / ответы','Solutions / answers'):r.kind==='combined'?t('Условия и решения','Problems and solutions'):t('Условия','Problems');
        const grade=activeGrade;
        const {labelGrade:shownGrade,page}=archiveClass(r,grade);
        const heading=[name(byID.get(r.source)),shownGrade?gradeLabel(shownGrade):null].filter(Boolean).join(' · ');
        const title=t(r.title,r.titleEn||r.title);
        const details=r.source==='vosh'&&r.stage
          ? title.split(' · ').slice(1).filter(part=>part!==String(r.year)).join(' · ')
          : title;
        const parts=[r.year,r.lang?langName(r.lang):null,details?null:kind].filter(Boolean);
        const rights=materialCredit(permissions[r.source])||(schools?'<p class="muted"><a href="permissions.html#'+esc(r.source)+'">'+esc(permissionLabel(permissions[r.source]))+'</a></p>':'');
        const originalURL=new URL(r.url);
        const zip=originalURL.pathname.toLowerCase().endsWith('.zip');
        if(zip)originalURL.hash='';
        else if(page)originalURL.hash='page='+page;
        const external=schools&&permissions[r.source]?.externalOnly;
        const reader=!r.unavailable&&!zip&&!external&&r.format!=='html'&&(!schools||localPDFServer||permissions[r.source]?.status==='granted')?'<a class="btn" href="'+esc(readDocument(r.source,r.url,grade))+'">'+t('Открыть на сайте','Read on site')+'</a>':'';
        const original=r.unavailable
          ?'<p class="muted">'+t('Файл недоступен у организатора.','The organiser’s file is unavailable.')+'</p>'+
            href(byID.get(r.source).url,t('Архив организатора','Organiser’s archive'))
          :href(originalURL.href,zip?t('Скачать ZIP','Download ZIP'):r.format==='html'?t('Ответы у организатора','Answers on organiser’s site'):t('Оригинал','Original'));
        return '<article class="task"><h2 class="archive-title">'+esc(heading)+'</h2>'+
          '<div class="task-meta">'+parts.map(esc).join(' · ')+'</div>'+
          '<p class="archive-detail"'+(details?'':' hidden')+'>'+esc(details)+'</p>'+
          rights+'<div class="task-actions">'+reader+original+'</div></article>';
      }).join('')||'<p class="empty">'+t('Документы по этим фильтрам не найдены. Откройте архив организаторов или измените запрос.','No documents match. Open the organisers’ archive or change the filters.')+'</p>';
      translateCatalogue([...grid.querySelectorAll('.archive-detail')].map((node,i)=>translatedText(node,filtered[start+i].titleEn?null:filtered[start+i].title)));
      pager.hidden=filtered.length<=size;
      $('archive-page').textContent=fmt(start+1)+'–'+fmt(end)+' '+t('из','of')+' '+fmt(filtered.length);
      $('archive-prev').disabled=current===0;$('archive-next').disabled=end>=filtered.length;
    }
    function filter(){
      const parsed=archiveQuery(fields.query.value,schools);
      const query=parsed.words;
      activeGrade=fields.grade.value||parsed.grade;
      const year=fields.year.value||parsed.year,sid=fields.source.value||parsed.contest;
      const sourcesShown=sources.filter(s=>(!sid||s.id===sid)&&(!query.length||query.every(w=>key(s).includes(w))||sid===s.id));
      cards.innerHTML=sourcesShown.map(s=>{
        if(s.officialPageOnly)return '<article class="volume archive-source"><strong>'+esc(name(s))+'</strong>'+
          '<small>'+esc(officialPageNote())+'</small><div class="volume-bottom">'+href(s.url,officialPageLabel())+'</div></article>';
        const select='?'+new URLSearchParams({source:s.id});
        return '<article class="volume archive-source"><strong>'+esc(name(s))+'</strong>'+
          materialCredit(permissions[s.id])+(siteLanguage==='ru'&&s.note?'<small>'+esc(s.note)+'</small>':'')+
          '<div class="volume-bottom"><span>'+fmt(s.files)+' '+t('ссылок','links')+'</span><div class="actions"><a class="btn btn-line" href="'+esc(select)+'">'+t('Материалы','Materials')+'</a>'+
          '<a class="btn btn-line" href="'+esc(schools&&(!localPDFServer||permissions[s.id]?.externalOnly)?s.url:readDocument(s.id,s.url))+'">'+t('Архив','Archive')+'</a></div></div></article>';
      }).join('');
      filtered=indexed.filter(r=>(!sid||r.source===sid)&&(!year||String(r.year)===year)&&
        (!fields.lang.value||r.lang===fields.lang.value)&&(!activeGrade||archiveClass(r,activeGrade).matches)&&
        query.every(w=>r.key.includes(w)));
      filtered.sort((a,b)=>(b.year||0)-(a.year||0)||Number(b.lang===documentLanguage)-Number(a.lang===documentLanguage)||a.title.localeCompare(b.title,siteLanguage));
      const state=new URLSearchParams();
      for(const [k,el] of Object.entries(fields))if(el.value.trim())state.set(k==='query'?'q':k,el.value.trim());
      history.replaceState(null,'',location.pathname+(state.size?'?'+state:''));
      current=0;
      status.textContent=[t('Найдено материалов: ','Materials found: ')+fmt(filtered.length),
        parsed.contest&&byID.has(sid)?name(byID.get(sid)):null,
        parsed.year?year:null,parsed.grade?gradeLabel(activeGrade):null].filter(Boolean).join(' · ');
      paintFiles();
    }
    for(const [k,field] of Object.entries(fields))field.addEventListener(k==='query'?'input':'change',filter);
    for(const [id,delta] of [['archive-prev',-1],['archive-next',1]])$(id).addEventListener('click',()=>{current+=delta;paintFiles();grid.scrollIntoView({block:'start'});});
    filter();
  }catch(err){console.error(err);fail('archive-count');}
}
archiveDirectory();


async function permissionsPage(){
  const grid=$('permission-schools');
  if(!grid)return;
  try{
    const [data,permissions]=await Promise.all([fetchJSON('catalog/archives.json'),schoolPermissions()]);
    const sources=data.sources.filter(schoolSource);
    const counts=new Map(sources.map(source=>[source.id,0]));
    for(const item of data.items)if(counts.has(item.source)&&!permissions[item.source]?.officialPageOnly)counts.set(item.source,counts.get(item.source)+1);
    const total=[...counts.values()].reduce((sum,n)=>sum+n,0);
    $('permission-count').textContent=t('Документов в каталоге: ','Documents in the catalogue: ')+fmt(total);
    grid.innerHTML=sources.map(source=>{
      const info=permissions[source.id];
      const why=t(info?.reason,info?.reasonEn);
      const list=source.officialPageOnly?'':'<a class="btn" href="schools.html?'+new URLSearchParams({source:source.id})+'">'+t('Список документов','List of documents')+'</a>';
      const count=source.officialPageOnly?officialPageNote():fmt(counts.get(source.id))+' '+t('документов','documents');
      return '<article class="task" id="'+esc(source.id)+'"><div class="task-meta">'+esc(count)+'</div>'+
        '<h2>'+esc(source.name)+'</h2><p><strong>'+esc(permissionLabel(info))+'</strong></p>'+
        materialCredit(info)+(why?'<p>'+esc(why)+'</p>':'')+'<div class="task-actions">'+list+
        '<a class="btn btn-line" href="'+esc(source.officialPageOnly?source.url:info?.evidence||source.url)+'" target="_blank" rel="noopener noreferrer">'+
        (source.officialPageOnly?officialPageLabel():t('Официальный источник','Official source'))+' ↗</a></div></article>';
    }).join('');
    if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
  }catch(err){console.error(err);fail('permission-count');}
}
permissionsPage();
