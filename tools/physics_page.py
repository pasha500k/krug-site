"""Official physics archive links and original practice problems for Krug."""
from html import escape

from numbers_route import bilingual

ARCHIVES = [
    ('ВсОШ по физике', 'Russian Physics Olympiad',
     'Институт содержания и методов обучения · задания и критерии по этапам',
     'Official national archive · papers and marking criteria by round',
     'https://vserosolimp.edsoo.ru/physics'),
    ('Физтех', 'Phystech Olympiad',
     'МФТИ · варианты прошлых лет, решения и видеоразборы',
     'MIPT · past papers, solutions and video walkthroughs',
     'https://olymp-online.mipt.ru/page/primery-zadanij'),
    ('IPhO', 'IPhO',
     'Международная олимпиада по физике · задания и решения прошлых лет',
     'International Physics Olympiad · past problems and solutions',
     'https://www.ipho-new.org/documentations/'),
    ('EuPhO', 'EuPhO',
     'Европейская олимпиада по физике · теория и эксперимент',
     'European Physics Olympiad · theory and experiment',
     'https://eupho.ee/archive/'),
]

TOPICS = {
    'mechanics': ('Механика', 'Mechanics'),
    'thermal': ('Тепловые явления', 'Thermal physics'),
    'electricity': ('Электричество', 'Electricity'),
    'optics': ('Оптика', 'Optics'),
}

# The class ranges are suggested levels for practice.
PROBLEMS = [
    ('mechanics', '8–9', ('Лодка и течение', 'Boat and current'),
     ('Лодка проходит 6 км по течению за 1 час, а возвращается за 1 час 40 минут. Скорость лодки относительно воды постоянна. Найдите её и скорость течения.',
      'A boat travels 6 km downstream in one hour and returns in one hour and 40 minutes. Its speed relative to the water is constant. Find that speed and the speed of the current.'),
     ('Скорости относительно берега равны 6 и 3,6 км/ч. Их полусумма даёт скорость лодки, 4,8 км/ч, а полуразность — скорость течения, 1,2 км/ч.',
      'The ground speeds are 6 and 3.6 km/h. Their average is the boat speed, 4.8 km/h. Half their difference is the current speed, 1.2 km/h.')),
    ('mechanics', '9–11', ('Торможение на двух участках', 'Braking in two stages'),
     ('Тележка массой 2 кг скользит со скоростью 6 м/с. На первых 2 м сила трения равна 6 Н, затем — 3 Н. Какой путь пройдёт тележка до остановки?',
      'A 2 kg cart slides at 6 m/s. Friction is 6 N over the first 2 m and 3 N thereafter. How far does the cart travel before stopping?'),
     ('Начальная кинетическая энергия равна 36 Дж. На первых 2 м трение отнимает 12 Дж. Остаток 24 Дж теряется на следующих 8 м. Полный путь равен 10 м.',
      'The initial kinetic energy is 36 J. Friction removes 12 J over the first 2 m. The remaining 24 J is lost over another 8 m, giving 10 m in total.')),
    ('thermal', '8–9', ('Две порции воды', 'Two samples of water'),
     ('Смешали 200 г воды при 80 °C и 300 г воды при 20 °C. Теплообменом с сосудом и воздухом пренебрегите. Найдите итоговую температуру.',
      'Mix 200 g of water at 80 °C with 300 g of water at 20 °C. Ignore heat transfer to the container and air. Find the final temperature.'),
     ('По тепловому балансу 200(80 − T) = 300(T − 20). Отсюда T = 44 °C.',
      'Heat balance gives 200(80 − T) = 300(T − 20), so T = 44 °C.')),
    ('thermal', '10–11', ('Нагревание газа', 'Heating a gas'),
     ('Одноатомный идеальный газ при постоянном давлении получил 500 Дж теплоты. Найдите работу газа и изменение внутренней энергии.',
      'A monatomic ideal gas absorbs 500 J of heat at constant pressure. Find the work it does and its change in internal energy.'),
     ('При постоянном давлении работа A = nRΔT, а изменение внутренней энергии равно 3A/2. Поэтому 500 = 5A/2. Работа равна 200 Дж, внутренняя энергия увеличилась на 300 Дж.',
      'At constant pressure the work is W = nRΔT and the internal energy change is 3W/2. Thus 500 = 5W/2. The gas does 200 J of work and its internal energy rises by 300 J.')),
    ('electricity', '8–10', ('Мощность в параллельной цепи', 'Power in a parallel circuit'),
     ('Резисторы 6 Ом и 3 Ом соединены параллельно и подключены к источнику 12 В. Найдите общий ток и мощность на каждом резисторе.',
      'Resistors of 6 Ω and 3 Ω are connected in parallel across a 12 V supply. Find the total current and the power dissipated by each resistor.'),
     ('Токи в ветвях равны 2 и 4 А, поэтому общий ток — 6 А. По формуле P = UI мощности равны 24 и 48 Вт соответственно.',
      'The branch currents are 2 A and 4 A, so the total is 6 A. Using P = VI gives 24 W and 48 W respectively.')),
    ('optics', '9–11', ('Линза и экран', 'Lens and screen'),
     ('Предмет и экран находятся на расстоянии 60 см друг от друга. Тонкая собирающая линза с фокусным расстоянием 12 см даёт резкое изображение на экране. На каких расстояниях от предмета можно поставить линзу?',
      'An object and a screen are 60 cm apart. A thin converging lens of focal length 12 cm produces a sharp image on the screen. How far from the object can the lens be placed?'),
     ('Если a — расстояние от предмета до линзы, то 1/a + 1/(60 − a) = 1/12. Значит, a(60 − a) = 720, откуда a = 30 ± 6√5 см.',
      'With object distance a, the lens equation is 1/a + 1/(60 − a) = 1/12. Thus a(60 − a) = 720, giving a = 30 ± 6√5 cm.')),
]


def physics_page():
    text = bilingual
    cards = ''.join(
        f'<article class="volume archive-source"><h3>{text(ru, en)}</h3>'
        f'<p>{text(note_ru, note_en)}</p><div class="volume-bottom">'
        f'<a class="btn btn-line" href="{escape(url)}" target="_blank" rel="noopener noreferrer">'
        f'{text("Архив организатора ↗", "Official archive ↗")}</a></div></article>'
        for ru, en, note_ru, note_en, url in ARCHIVES
    )
    options = ''.join(
        f'<option value="{key}" data-en="{escape(en)}">{escape(ru)}</option>'
        for key, (ru, en) in TOPICS.items()
    )
    problems = ''.join(
        f'<article class="task" data-topic="{topic}"><div class="task-meta">'
        f'{text(*TOPICS[topic])} · {text(grade + " классы", "Grades " + grade)}</div>'
        f'<h3>{text(*title)}</h3><p>{text(*problem)}</p>'
        f'<details><summary>{text("Разбор решения", "Worked solution")}</summary>'
        f'<p>{text(*solution)}</p></details></article>'
        for topic, grade, title, problem, solution in PROBLEMS
    )
    return f'''
<header class="page-head">
  <h1>{text("Олимпиадная физика", "Olympiad physics")}</h1>
  <p>{text("Официальные архивы и задачи с разборами для 8–11 классов.",
           "Official archives and worked practice problems for grades 8–11.")}</p>
  <div class="actions route-jumps"><a class="btn" href="#physics-practice">{text("Решать задачи", "Try problems")}</a>
    <a class="btn btn-line" href="#physics-olympiads">{text("Найти олимпиаду", "Find a contest")}</a></div>
</header>
<section class="section" id="physics-olympiads" aria-labelledby="physics-olympiads-heading">
  <h2 id="physics-olympiads-heading">{text("Олимпиады по физике", "Physics olympiads")}</h2>
  <div class="grid">{cards}</div>
</section>
<section class="section" id="physics-practice" aria-labelledby="physics-practice-heading">
  <h2 id="physics-practice-heading">{text("Задачи для тренировки", "Practice problems")}</h2>
  <p class="muted">{text("Задачи и разборы подготовлены для «Круга». Класс указан как ориентир.",
                         "These problems and solutions were written for Krug. Grade ranges are a guide.")}</p>
  <div class="filters" id="physics-filters" hidden>
    <div class="field grow"><label for="physics-query">{text("Поиск по задачам", "Search problems")}</label><input type="search" id="physics-query"></div>
    <div class="field"><label for="physics-topic">{text("Тема", "Topic")}</label>
      <select id="physics-topic"><option value="" data-en="All topics">Все темы</option>{options}</select></div>
  </div>
  <p class="count" id="physics-count" role="status" hidden></p>
  <div class="task-grid" id="physics-problems">{problems}</div>
  <p class="empty" id="physics-empty" hidden>{text("По этому запросу задач не найдено.", "No problems match your search.")}</p>
</section>
'''
