from pathlib import Path
root=Path(__file__).resolve().parents[1]/'dist'
def page(name,title,body):
    nav=''.join(f'<a href="{file}"'+(' aria-current="page"' if name==file else '')+f'>{label}</a>' for file,label in [('index.html','Тома'),('tasks.html','Задачи'),('archives.html','Олимпиады'),('schools.html','Поступление'),('about.html','О библиотеке')])
    (root/name).write_text(f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Круг — библиотека олимпиадной математики. 57 томов, теория и поиск по архивным задачам.">
<title>{title} · Круг</title><link rel="icon" href="assets/mark.svg"><link rel="stylesheet" href="assets/site.css">
<script defer src="assets/locale.js"></script><script defer src="assets/pdf-local.js"></script><script defer src="assets/site.js"></script><script defer src="assets/archive.js"></script><script defer src="assets/offline.js"></script></head>
<body><a class="skip" href="#main">К содержанию</a><header class="top"><div class="wrap"><a class="brand" href="index.html"><img src="assets/mark.svg" alt="" width="37" height="37">Круг</a><nav class="nav" aria-label="Основное меню">{nav}</nav><select id="site-language" class="language" aria-label="Язык / Language"><option value="auto">Auto</option><option value="ru">RU</option><option value="en">EN</option></select></div></header>
<main class="wrap" id="main">{body}</main>
<footer class="footer"><div class="wrap"><div>Круг · библиотека олимпиадной математики<br>Автор идеи — Степанов Павел</div><div class="footer-links"><a href="support.html">Поддержать автора</a><a href="permissions.html">Разрешения школ</a><a href="books/00-start.pdf">Путеводитель PDF ↗</a></div></div></footer></body></html>''',encoding='utf-8')
page('index.html','Библиотека олимпиадной математики','''
<section class="hero">
<div class="hero-copy"><div class="eyebrow">Электронная библиотека</div><h1>Олимпиадная<br>математика</h1>
<p>Теория, задачи и официальные разборы. Выберите класс, откройте нужный том или найдите задачу по условию.</p>
<div class="actions"><a class="btn btn-light" href="#volumes">Выбрать том ↓</a><a class="btn btn-line" href="tasks.html">Найти задачу →</a></div></div>
<img class="hero-art" src="assets/geometry.svg" alt="" width="520" height="460"></section>
<div class="metrics" aria-label="Библиотека в цифрах">
<div class="metric"><b id="stat-books">57</b><span>томов</span></div><div class="metric"><b id="stat-pages">9 699</b><span>страниц</span></div>
<div class="metric"><b id="stat-tasks">8 089</b><span>записей задач</span></div><div class="metric"><b id="stat-study">20</b><span>учебных томов</span></div>
</div>
<section class="guide offline-box" aria-labelledby="offline-title"><div><strong id="offline-title">Библиотека без интернета</strong><p id="offline-status" role="status">Сохрани указатель сейчас, а нужные PDF — на странице чтения.</p></div><button class="btn btn-line" id="offline-save" type="button">Сохранить указатель</button></section>
<section class="section"><div class="section-head"><div><div class="eyebrow">Учебная серия</div><h2>Начните с класса</h2><p>По пять томов на класс: теория, схемы, упражнения и разборы.</p></div></div>
<div class="levels"><button class="level" type="button" data-level="8"><b>8 класс</b><span>5 томов →</span></button>
<button class="level" type="button" data-level="9"><b>9 класс</b><span>5 томов →</span></button>
<button class="level" type="button" data-level="10"><b>10 класс</b><span>5 томов →</span></button>
<button class="level" type="button" data-level="11"><b>11 класс</b><span>5 томов →</span></button></div></section>
<section class="section" id="volumes"><div class="section-head"><div><div class="eyebrow">Полное собрание</div><h2>Все тома</h2></div><a class="btn btn-line" href="books/00-start.pdf">Путеводитель PDF ↗</a></div>
<div class="chips" id="kinds" aria-label="Тип тома"><button class="chip" data-kind="" aria-pressed="true">Все</button><button class="chip" data-kind="study" aria-pressed="false">Учебные</button><button class="chip" data-kind="practice" aria-pressed="false">Задачники</button><button class="chip" data-kind="solutions" aria-pressed="false">Разборы</button><button class="chip" data-kind="archive" aria-pressed="false">Архив</button></div>
<div class="filters"><div class="field grow"><label for="volume-query">Название, тема или номер</label><input type="search" id="volume-query" placeholder="Например, геометрия или 55"></div><div class="field"><label for="volume-grade">Класс учебного тома</label><select id="volume-grade"><option value="">Все классы</option><option>8</option><option>9</option><option>10</option><option>11</option></select></div><button class="btn btn-line" id="volume-reset">Сбросить</button></div>
<p class="count" id="volume-count" role="status">Загружаем оглавление…</p><div class="grid" id="volume-grid"></div></section>
<noscript><p>Для фильтров нужен JavaScript. Откройте <a href="contents.html">простое оглавление</a>.</p></noscript>
<section class="support-banner" aria-labelledby="support-heading"><div><div class="eyebrow">Поддержка проекта</div><h2 id="support-heading">Поддержать автора</h2><p>Если «Круг» пригодился вам в подготовке, вы можете добровольно поддержать его автора.</p></div><a class="btn" href="support.html">Узнать, как поддержать →</a></section>
''')
page('tasks.html','Поиск задач','''
<header class="page-head"><div class="eyebrow">Архив олимпиад</div><h1>Найти задачу</h1><p>Ищите по словам, названию олимпиады, году и классу. Например: «ВсОШ 2025 треугольник».</p></header>
<form class="filters" id="task-form">
<div class="field grow"><label for="task-query">Поиск по условиям</label><input type="search" id="task-query" name="q" placeholder="Например, вписанный угол"></div>
<div class="field"><label for="task-topic">Тема</label><select id="task-topic" name="topic"><option value="">Все темы</option></select></div>
<div class="field"><label for="task-source">Олимпиада</label><select id="task-source" name="source"><option value="">Все олимпиады</option></select></div>
<div class="field"><label for="task-grade">Класс</label><select id="task-grade" name="grade"><option value="">Все классы</option></select></div>
<div class="field"><label for="task-year">Год</label><select id="task-year" name="year"><option value="">Все годы</option></select></div>
<button class="btn">Найти</button><button class="btn btn-line" type="reset">Сбросить</button>
<label class="check"><input type="checkbox" id="task-solved" name="solved" value="1"> Есть официальный материал</label>
</form>
<p class="count" id="task-count" role="status">Загружаем указатель…</p>
<div class="task-grid" id="task-grid"></div>
<div class="pagination" id="task-pager" hidden><button class="btn btn-line" id="task-prev">← Назад</button><span id="task-page"></span><button class="btn btn-line" id="task-next">Далее →</button></div>
<noscript><p>Для поиска включите JavaScript. Все книги доступны в <a href="contents.html">оглавлении</a>.</p></noscript>
''')
page('reader.html','Чтение тома','''
<p class="compact" id="read-back-row" hidden><a id="read-back">← К материалам</a></p>
<div class="page-head reader-head"><div><div class="eyebrow" id="read-meta">Библиотека</div><h1 id="read-title">Чтение тома</h1></div>
<div class="actions" id="read-actions" hidden><a class="btn btn-line" id="read-source" target="_blank" rel="noopener noreferrer" hidden>Оригинал у источника ↗</a><a class="btn btn-line" id="read-direct" target="_blank" rel="noopener">Открыть PDF ↗</a><a class="btn" id="read-download" download>Скачать</a><button class="btn btn-line" id="offline-book" type="button">Сохранить для офлайна</button></div></div>
<p id="read-permission" class="muted" hidden></p>
<p class="count" id="offline-book-status" role="status"></p>
<div class="field pdf-language" id="read-language-field" hidden><label id="read-language-label" for="read-language">Язык PDF</label><select id="read-language"><option value="original">Оригинал</option></select></div>
<p class="count" id="pdf-translation-status" role="status"></p>
<p class="compact muted" id="read-note">Загружаем том…</p><iframe class="reader-frame" title="Просмотр PDF" id="read-frame" hidden></iframe>
<noscript><p>Откройте нужный PDF из <a href="contents.html">оглавления</a>.</p></noscript>
''')
page('about.html','О библиотеке','''
<div class="about"><header class="page-head"><div class="eyebrow">Круг</div><h1>О библиотеке</h1><p>Независимое учебное собрание материалов по олимпиадной математике.</p></header>
<section class="guide"><h2>Как начать</h2><p>Выберите свой класс на главной странице. В томах 38–57 есть теория, схемы, разобранный пример и самостоятельные задания с решениями. В тематических томах 01–10 больше архивной практики.</p><a class="btn btn-line" href="index.html">Перейти к томам</a></section>
<section class="guide"><h2>Условия и разборы</h2><p>В указателе есть повторы и языковые версии. Темы размечены автоматически. Если условие нельзя надёжно выделить, откройте полный оригинал. Ссылки на возможные разборы помечены отдельно: проверяйте год, класс и номер задачи.</p><a class="btn btn-line" href="tasks.html">Открыть поиск</a></section>
<section class="guide"><h2>Файлы</h2><p>Каждый том — отдельный PDF. Простое оглавление даёт прямые ссылки на все книги, а путеводитель содержит маршрут чтения.</p><div class="actions"><a class="btn btn-line" href="contents.html">Все PDF</a><a class="btn btn-line" href="books/00-start.pdf">Путеводитель ↗</a></div></section></div>
''')
page('support.html','Поддержать автора','''
<div class="about"><header class="page-head"><div class="eyebrow">Поддержка проекта</div><h1>Поддержать автора</h1><p>Если сборник помог вам подготовиться к олимпиаде или разобраться в сложной теме, вы можете добровольно поддержать Павла Степанова, автора идеи «Круга».</p></header>
<section class="guide support-card" id="support-card" aria-labelledby="support-title">
<div class="eyebrow">Добровольная поддержка</div>
<h2 id="support-title">Степанов Павел</h2>
<p id="support-status" role="status">Ссылка для поддержки пока не подключена.</p>
<a class="btn" id="support-link" target="_blank" rel="noopener noreferrer" hidden>Поддержать Павла ↗</a>
</section>
<section class="guide"><h2>Библиотека остаётся открытой</h2><p>Все тома и поиск доступны бесплатно. Если решите поддержать автора, перевод оформляется на странице платёжного сервиса, где можно проверить получателя и сумму.</p><a href="index.html">← Вернуться к библиотеке</a></section></div>
''')

def directory(schools=False):
    title='Вступительные испытания' if schools else 'Архивы олимпиад'
    intro=('Демоверсии и варианты прошлых лет по математике со ссылками на сайты школ.'
           if schools else 'Выберите олимпиаду, год или язык. Здесь собраны ссылки на официальные условия, разборы и архивы.')
    return f'''
<header class="page-head"><div class="eyebrow">Официальные источники</div><h1>{title}</h1><p>{intro}</p></header>
{'<p><a href="permissions.html">Статус разрешений школ</a></p>' if schools else ''}
<div class="filters" id="archive-filters" data-mode="{'schools' if schools else 'olympiads'}">
<div class="field grow"><label for="archive-query">Название или ключевые слова</label><input type="search" id="archive-query" placeholder="Например, ВсОШ или IMO"></div>
<div class="field"><label for="archive-source">Источник</label><select id="archive-source"><option value="">Все источники</option></select></div>
<div class="field"><label for="archive-year">Год</label><select id="archive-year"><option value="">Все годы</option></select></div>
<div class="field"><label for="archive-grade">Класс</label><select id="archive-grade"><option value="">Все классы</option></select></div>
<div class="field"><label for="archive-lang">Язык документа</label><select id="archive-lang"><option value="">Все языки</option></select></div>
</div>
<p class="count" id="archive-count" role="status">Загружаем указатель…</p>
<div id="archive-sources" class="grid"></div><div id="archive-files" class="task-grid"></div>
<div class="pagination" id="archive-pager" hidden><button class="btn btn-line" id="archive-prev">← Назад</button><span id="archive-page"></span><button class="btn btn-line" id="archive-next">Далее →</button></div>
<p class="muted">Официальные файлы на других сайтах требуют интернета. Язык документа указан, если его удалось определить.</p>
'''
page('archives.html','Архивы олимпиад',directory())
page('schools.html','Вступительные испытания',directory(True))

page('permissions.html','Разрешения школ','''
<header class="page-head"><div class="eyebrow">Вступительные испытания</div><h1>Разрешения школ</h1>
<p>Здесь указан статус разрешения на публикацию оригинальных PDF и английских переводов.</p></header>
<p>Пока разрешения не подтверждены, публичный каталог ведёт к оригиналам на сайтах школ. Статус «На согласовании» появляется после отправки обращения.</p>
<p id="permission-count" class="count" role="status">Загружаем указатель…</p>
<div id="permission-schools" class="task-grid"></div>
<p><a href="schools.html">← К вступительным испытаниям</a></p>
''')
