'use strict';
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
      bmo:'British Mathematical Olympiad (BMO)',balkan:'Balkan Mathematical Olympiad',letovo:'Letovo School',sunc:'Kolmogorov School (MSU)',school239:'Physics and Mathematics Lyceum No. 239'
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
    const indexed=items.map(r=>({...r,grades:(r.grade||'').match(/\d+/g)?.map(Number)||[],
      key:norm([key(byID.get(r.source)),r.title,r.year,r.grade,r.lang,r.kind==='solutions'?'решения solutions':r.kind==='combined'?'задачи решения problems solutions':'задачи problems'].join(' '))}));
    const grid=$('archive-files'),cards=$('archive-sources'),status=$('archive-count'),pager=$('archive-pager');
    let current=0,filtered=[];
    const size=24;
    const href=(url,label,cls='btn btn-line')=>'<a class="'+cls+'" href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+label+' ↗</a>';
    function paintFiles(){
      const start=current*size,end=Math.min(start+size,filtered.length);
      grid.innerHTML=filtered.slice(start,end).map(r=>{
        const kind=r.kind==='solutions'?t('Решения / ответы','Solutions / answers'):r.kind==='combined'?t('Условия и решения','Problems and solutions'):t('Условия','Problems');
        const parts=[name(byID.get(r.source)),r.year,r.grade?t('Класс ','Grade ')+r.grade:null,r.lang?langName(r.lang):null,kind].filter(Boolean);
        const rights=schools?'<p class="muted"><a href="permissions.html#'+esc(r.source)+'">'+esc(permissionLabel(permissions[r.source]))+'</a></p>':'';
        const reader=!schools||localPDFServer?'<a class="btn" href="'+esc(readDocument(r.source,r.url))+'">'+t('Открыть на сайте','Read on site')+'</a>':'';
        return '<article class="task"><div class="task-meta">'+parts.map(esc).join(' · ')+'</div><h2 class="archive-title">'+esc(r.title||kind)+'</h2>'+rights+'<div class="task-actions">'+reader+href(r.url,t('Оригинал','Original'))+'</div></article>';
      }).join('')||'<p class="empty">'+t('Документы по этим фильтрам не найдены. Откройте архив организаторов или измените запрос.','No documents match. Open the organisers’ archive or change the filters.')+'</p>';
      pager.hidden=filtered.length<=size;
      $('archive-page').textContent=fmt(start+1)+'–'+fmt(end)+' '+t('из','of')+' '+fmt(filtered.length);
      $('archive-prev').disabled=current===0;$('archive-next').disabled=end>=filtered.length;
    }
    function filter(){
      const parsed=schools?{contest:'',words:tokens(fields.query.value)}:contestQuery(fields.query.value);
      const query=parsed.words;
      const grade=Number(fields.grade.value),sid=fields.source.value||parsed.contest;
      const sourcesShown=sources.filter(s=>(!sid||s.id===sid)&&(!query.length||query.every(w=>key(s).includes(w))||sid===s.id));
      cards.innerHTML=sourcesShown.map(s=>{
        if(s.officialPageOnly)return '<article class="volume archive-source"><strong>'+esc(name(s))+'</strong>'+
          '<small>'+esc(officialPageNote())+'</small><div class="volume-bottom">'+href(s.url,officialPageLabel())+'</div></article>';
        const select='?'+new URLSearchParams({source:s.id});
        return '<article class="volume archive-source"><strong>'+esc(name(s))+'</strong>'+
          (siteLanguage==='ru'&&s.note?'<small>'+esc(s.note)+'</small>':'')+
          '<div class="volume-bottom"><span>'+fmt(s.files)+' '+t('ссылок','links')+'</span><div class="actions"><a class="btn btn-line" href="'+esc(select)+'">'+t('Материалы','Materials')+'</a>'+
          '<a class="btn btn-line" href="'+esc(schools&&!localPDFServer?s.url:readDocument(s.id,s.url))+'">'+t('Архив','Archive')+'</a></div></div></article>';
      }).join('');
      filtered=indexed.filter(r=>(!sid||r.source===sid)&&(!fields.year.value||String(r.year)===fields.year.value)&&
        (!fields.lang.value||r.lang===fields.lang.value)&&(!grade||(r.grades.length&&grade>=Math.min(...r.grades)&&grade<=Math.max(...r.grades)))&&
        query.every(w=>r.key.includes(w)));
      filtered.sort((a,b)=>(b.year||0)-(a.year||0)||Number(b.lang===documentLanguage)-Number(a.lang===documentLanguage)||a.title.localeCompare(b.title,siteLanguage));
      const state=new URLSearchParams();
      for(const [k,el] of Object.entries(fields))if(el.value.trim())state.set(k==='query'?'q':k,el.value.trim());
      history.replaceState(null,'',location.pathname+(state.size?'?'+state:''));
      current=0;
      status.textContent=t('Найдено материалов: ','Materials found: ')+fmt(filtered.length);
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
        (why?'<p>'+esc(why)+'</p>':'')+'<div class="task-actions">'+list+
        '<a class="btn btn-line" href="'+esc(source.officialPageOnly?source.url:info?.evidence||source.url)+'" target="_blank" rel="noopener noreferrer">'+
        (source.officialPageOnly?officialPageLabel():t('Официальный источник','Official source'))+' ↗</a></div></article>';
    }).join('');
    if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
  }catch(err){console.error(err);fail('permission-count');}
}
permissionsPage();
