'use strict';
const deviceLocale=navigator.languages?.[0]||navigator.language||'ru';
let languageChoice='auto';
try{languageChoice=localStorage.getItem('krug-language')||'auto';}catch{}
if(!['ru','en','auto'].includes(languageChoice))languageChoice='auto';
const documentLanguage=languageChoice==='auto'?deviceLocale.toLowerCase().split('-')[0]:languageChoice;
const siteLanguage=documentLanguage==='ru'?'ru':'en';
const t=(ru,en)=>siteLanguage==='ru'?ru:en;
const lex={
 'Круг':'Krug','К содержанию':'Skip to content','Тома':'Volumes','Задачи':'Problems','Олимпиады':'Olympiads','Поступление':'Admissions','О библиотеке':'About',
 'Круг · библиотека олимпиадной математики':'Krug · Olympiad Mathematics Library','Автор идеи — Степанов Павел':'Project idea by Pavel Stepanov',
 'Путеводитель PDF ↗':'PDF guide ↗','Поддержать автора':'Support the author','Электронная библиотека':'Digital library','Олимпиадная':'Olympiad','математика':'mathematics',
 'Теория, задачи и официальные разборы. Выберите класс, откройте нужный том или найдите задачу по условию.':'Theory, problems and official solutions. Choose a grade, open a volume, or find a problem by keywords.',
 'Выбрать том ↓':'Browse volumes ↓','Найти задачу →':'Find a problem →','томов':'volumes','страниц':'pages','записей задач':'problem entries','учебных томов':'study volumes',
 'Учебная серия':'Study series','Начните с класса':'Start with your grade','По пять томов на класс: теория, схемы, упражнения и разборы.':'Five volumes per grade: theory, diagrams, exercises and solutions.',
 '8 класс':'Grade 8','9 класс':'Grade 9','10 класс':'Grade 10','11 класс':'Grade 11','5 томов →':'5 volumes →','Полное собрание':'Complete collection','Все тома':'All volumes',
 'Все':'All','Учебные':'Study','Задачники':'Problem books','Разборы':'Solutions','Архив':'Archive','Название, тема или номер':'Title, topic or number','Класс учебного тома':'Study grade',
 'Все классы':'All grades','Сбросить':'Reset','Загружаем оглавление…':'Loading contents…','Библиотека без интернета':'Library offline',
 'Сохрани указатель сейчас, а нужные PDF — на странице чтения.':'Save the catalogue now and individual PDFs from the reader.','Сохранить указатель':'Save catalogue',
 'Архив олимпиад':'Olympiad archive','Найти задачу':'Find a problem','Ищите по словам, названию олимпиады, году и классу. Например: «ВсОШ 2025 треугольник».':'Search by keywords, contest, year or grade. For example: “IMO 2025 triangle”.',
 'Поиск по условиям':'Search problems','Тема':'Topic','Все темы':'All topics','Олимпиада':'Olympiad','Все олимпиады':'All contests','Класс':'Grade','Год':'Year','Все годы':'All years','Найти':'Search',
 'Есть официальный материал':'Has official material','Загружаем указатель…':'Loading catalogue…','← Назад':'← Previous','Далее →':'Next →',
 'Чтение тома':'Read volume','Библиотека':'Library','Открыть PDF ↗':'Open PDF ↗','Скачать':'Download','Сохранить для офлайна':'Save for offline use','Загружаем том…':'Loading volume…',
 'Официальные источники':'Official sources','Архивы олимпиад':'Olympiad archives','Вступительные испытания':'School entrance exams',
 'Выберите олимпиаду, год или язык. Здесь собраны ссылки на официальные условия, разборы и архивы.':'Choose a contest, year or language. Find official papers, solutions and archives.',
 'Демоверсии и варианты прошлых лет по математике со ссылками на сайты школ.':'Browse sample and past mathematics papers on school websites.',
 'Разрешения школ':'School permissions','Статус разрешений школ':'School permission status','← К вступительным испытаниям':'← Back to entrance exams',
 'Здесь указан статус разрешения на публикацию оригинальных PDF и английских переводов.':'Permission status for publishing original PDFs and English translations.',
 'Пока разрешения не подтверждены, публичный каталог ведёт к оригиналам на сайтах школ. Статус «На согласовании» появляется после отправки обращения.':'Until permission is confirmed, the public catalogue links to the school originals. A request is marked as pending after it has been sent.',
 'Название или ключевые слова':'Name or keywords','Источник':'Source','Все источники':'All sources','Язык документа':'Document language','Все языки':'All languages',
 'Официальные файлы на других сайтах требуют интернета. Язык документа указан, если его удалось определить.':'External documents require an internet connection. Document languages are shown where known.',
 'Поддержка проекта':'Support the project','Если «Круг» пригодился вам в подготовке, вы можете добровольно поддержать его автора.':'If Krug helped you prepare, you can support its author.',
 'Узнать, как поддержать →':'How to support →','Добровольная поддержка':'Optional support','Степанов Павел':'Pavel Stepanov',
 'Если сборник помог вам подготовиться к олимпиаде или разобраться в сложной теме, вы можете добровольно поддержать Павла Степанова, автора идеи «Круга».':'If the library helped you prepare for a contest or understand a difficult topic, you can support Pavel Stepanov, who came up with Krug.',
 'Ссылка для поддержки пока не подключена.':'The support link is not set up yet.','Поддержать Павла ↗':'Support Pavel ↗','Библиотека остаётся открытой':'The library stays free',
 'Все тома и поиск доступны бесплатно. Если решите поддержать автора, перевод оформляется на странице платёжного сервиса, где можно проверить получателя и сумму.':'All volumes and search are free. If you choose to support the author, the payment provider will show the recipient and amount.',
 '← Вернуться к библиотеке':'← Back to the library','Независимое учебное собрание материалов по олимпиадной математике.':'An independent learning collection for olympiad mathematics.',
 'Как начать':'How to start','Выберите свой класс на главной странице. В томах 38–57 есть теория, схемы, разобранный пример и самостоятельные задания с решениями. В тематических томах 01–10 больше архивной практики.':'Choose your grade on the home page. Volumes 38–57 contain theory, diagrams, worked examples and practice with solutions. Volumes 01–10 contain more archive practice.',
 'Перейти к томам':'Browse volumes','Условия и разборы':'Problems and solutions','В указателе есть повторы и языковые версии. Темы размечены автоматически. Если условие нельзя надёжно выделить, откройте полный оригинал. Ссылки на возможные разборы помечены отдельно: проверяйте год, класс и номер задачи.':'The catalogue includes duplicates and language editions. Topics are assigned automatically. Open the original when extraction is uncertain. Check the year, grade and problem number on suggested solutions.',
 'Открыть поиск':'Open search','Файлы':'Files','Каждый том — отдельный PDF. Простое оглавление даёт прямые ссылки на все книги, а путеводитель содержит маршрут чтения.':'Each volume is a separate PDF. The plain contents page links directly to every volume, and the guide suggests a reading route.',
 'Все PDF':'All PDFs','Путеводитель ↗':'Guide ↗',
 'Например, геометрия или 55':'Example: geometry or 55','Например, вписанный угол':'Example: inscribed angle','Например, ВсОШ или IMO':'Example: IMO or EGMO'
};
function localize(){
  document.documentElement.lang=siteLanguage;
  const select=document.getElementById('site-language');
  if(select){
    select.value=languageChoice;
    select.addEventListener('change',()=>{try{localStorage.setItem('krug-language',select.value);location.reload();}catch{}});
  }
  if(siteLanguage==='ru')return;
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){
    const node=walker.currentNode;
    if(node.parentElement?.closest('script,style'))continue;
    const text=node.nodeValue.trim();
    if(lex[text])node.nodeValue=node.nodeValue.replace(text,lex[text]);
  }
  document.querySelectorAll('[placeholder]').forEach(el=>{if(lex[el.placeholder])el.placeholder=lex[el.placeholder];});
}
localize();
