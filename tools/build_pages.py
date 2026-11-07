from pathlib import Path
root=Path(__file__).resolve().parents[1]/'dist'
def page(name,title,body):
    nav=''.join(f'<a href="{file}"'+(' aria-current="page"' if name==file else '')+f'>{label}</a>' for file,label in [('index.html','Тома'),('tasks.html','Задачи'),('about.html','О библиотеке')])
    (root/name).write_text(f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Круг — библиотека олимпиадной математики. 57 томов, теория и поиск по архивным задачам.">
<title>{title} · Круг</title><link rel="icon" href="assets/mark.svg"><link rel="stylesheet" href="assets/site.css">
<script defer src="assets/site.js"></script></head>
<body><a class="skip" href="#main">К содержанию</a><header class="top"><div class="wrap"><a class="brand" href="index.html"><img src="assets/mark.svg" alt="" width="37" height="37">Круг</a><nav class="nav" aria-label="Основное меню">{nav}</nav></div></header>
<main class="wrap" id="main">{body}</main>
<footer class="footer"><div class="wrap"><span>Круг · библиотека олимпиадной математики</span><a href="books/00-start.pdf">Путеводитель PDF ↗</a></div></footer></body></html>''',encoding='utf-8')
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
''')
page('tasks.html','Поиск задач','''
<header class="page-head"><div class="eyebrow">Архив олимпиад</div><h1>Найти задачу</h1><p>Ищите по условию, теме, олимпиаде или номеру З-00001. Формулы и рисунки сверяйте с исходным PDF.</p></header>
<form class="filters" id="task-form">
<div class="field grow"><label for="task-query">Поиск по условиям</label><input type="search" id="task-query" name="q" placeholder="Например, вписанный угол"></div>
<div class="field"><label for="task-topic">Тема</label><select id="task-topic" name="topic"><option value="">Все темы</option></select></div>
<div class="field"><label for="task-source">Олимпиада</label><select id="task-source" name="source"><option value="">Все олимпиады</option></select></div>
<div class="field"><label for="task-grade">Класс</label><select id="task-grade" name="grade"><option value="">Все классы</option></select></div>
<button class="btn">Найти</button><button class="btn btn-line" type="reset">Сбросить</button>
<label class="check"><input type="checkbox" id="task-solved" name="solved" value="1"> Есть официальный материал</label>
</form>
<p class="count" id="task-count" role="status">Загружаем указатель…</p>
<div class="task-grid" id="task-grid"></div>
<div class="pagination" id="task-pager" hidden><button class="btn btn-line" id="task-prev">← Назад</button><span id="task-page"></span><button class="btn btn-line" id="task-next">Далее →</button></div>
<noscript><p>Для поиска включите JavaScript. Все книги доступны в <a href="contents.html">оглавлении</a>.</p></noscript>
''')
page('reader.html','Чтение тома','''
<div class="page-head reader-head"><div><div class="eyebrow" id="read-meta">Библиотека</div><h1 id="read-title">Чтение тома</h1></div>
<div class="actions" id="read-actions" hidden><a class="btn btn-line" id="read-direct" target="_blank" rel="noopener">Открыть PDF ↗</a><a class="btn" id="read-download" download>Скачать</a></div></div>
<p class="compact muted" id="read-note">Загружаем том…</p><iframe class="reader-frame" title="Просмотр PDF" id="read-frame" hidden></iframe>
<noscript><p>Откройте нужный PDF из <a href="contents.html">оглавления</a>.</p></noscript>
''')
page('about.html','О библиотеке','''
<div class="about"><header class="page-head"><div class="eyebrow">Круг</div><h1>О библиотеке</h1><p>Независимое учебное собрание материалов по олимпиадной математике.</p></header>
<section class="guide"><h2>Как начать</h2><p>Выберите свой класс на главной странице. В томах 38–57 есть теория, схемы, разобранный пример и самостоятельные задания с решениями. В тематических томах 01–10 больше архивной практики.</p><a class="btn btn-line" href="index.html">Перейти к томам</a></section>
<section class="guide"><h2>Условия и разборы</h2><p>В указателе есть повторы и языковые версии. Темы размечены автоматически. Если условие нельзя надёжно выделить, откройте полный оригинал. Ссылки на возможные разборы помечены отдельно: проверяйте год, класс и номер задачи.</p><a class="btn btn-line" href="tasks.html">Открыть поиск</a></section>
<section class="guide"><h2>Файлы</h2><p>Каждый том — отдельный PDF. Простое оглавление даёт прямые ссылки на все книги, а путеводитель содержит маршрут чтения.</p><div class="actions"><a class="btn btn-line" href="contents.html">Все PDF</a><a class="btn btn-line" href="books/00-start.pdf">Путеводитель ↗</a></div></section></div>
''')
