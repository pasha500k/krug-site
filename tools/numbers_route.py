"""Handwritten Russian and English practice for the number theory route."""
from html import escape

LEVELS = [
    (
        'foundations',
        ('Признак делимости на 9', 'Divisibility by 9'),
        ('Начните здесь, если умеете делить с остатком.', 'Start here if you can divide with a remainder.'),
        2,
        (
            ('Пропущенная цифра', 'The missing digit'),
            ('Какую цифру d нужно поставить в разряд единиц числа 73d, чтобы оно делилось на 9?',
             'What digit d should go in the units place of 73d to make the number divisible by 9?'),
            ('Проверьте сумму трёх цифр.', 'Look at the sum of the three digits.'),
            ('Число делится на 9, когда на 9 делится сумма его цифр. Здесь сумма равна 10 + d и лежит между 10 и 19. Единственное кратное 9 в этом промежутке — 18, поэтому d = 8.',
             'A number is divisible by 9 if its digit sum is divisible by 9. Here the sum is 10 + d, between 10 and 19. The only multiple of 9 in that range is 18, so d = 8.'),
        ),
    ),
    (
        'methods',
        ('Остатки и сравнения', 'Remainders and congruences'),
        ('Попробуйте, если уже умеете находить остатки и хотите применить их к большим степеням.',
         'Try this if you can find remainders and want to apply them to large powers.'),
        3,
        (
            ('Две большие степени', 'Two large powers'),
            ('Найдите остаток от деления 7²⁰²⁷ + 5²⁰²⁶ на 12.',
             'Find the remainder when 7²⁰²⁷ + 5²⁰²⁶ is divided by 12.'),
            ('Сначала найдите остатки чисел 7² и 5².', 'Start with the remainders of 7² and 5².'),
            ('По модулю 12 имеем 7² ≡ 1 и 5² ≡ 1. В первой степени после выделения пар остаётся одна семёрка, во второй все множители разбиваются на пары. Значит, сумма сравнима с 7 + 1, и остаток равен 8.',
             'Modulo 12, both 7² and 5² are congruent to 1. Pairing the factors in the first power leaves one factor of 7. Every factor in the second power belongs to a pair. The sum is therefore congruent to 7 + 1, and the remainder is 8.'),
        ),
    ),
    (
        'proofs',
        ('Олимпиадные доказательства', 'Olympiad proofs'),
        ('Попробуйте, если готовы доказать утверждение для любого целого числа.',
         'Try this if you are ready to prove a statement for every integer.'),
        5,
        (
            ('Квадрат из четырёх множителей', 'A square from four factors'),
            ('Докажите, что n(n + 1)(n + 2)(n + 3) + 1 — квадрат целого числа при любом целом n.',
             'Prove that n(n + 1)(n + 2)(n + 3) + 1 is a perfect square for every integer n.'),
            ('Перемножьте крайние множители, а затем два средних. На сколько отличаются результаты?',
             'Multiply the outer pair of factors and then the inner pair. How far apart are the two products?'),
            ('Положим u = n(n + 3). Тогда (n + 1)(n + 2) = u + 2. Исходное выражение равно u(u + 2) + 1 = (u + 1)².',
             'Let u = n(n + 3). Then (n + 1)(n + 2) = u + 2. The expression is u(u + 2) + 1 = (u + 1)².'),
        ),
    ),
]


def bilingual(ru, en):
    return (f'<span class="route-copy" lang="ru">{escape(ru)}</span>'
            f'<span class="route-copy" lang="en">{escape(en)}</span>')


TRANSFER = {
    'foundations': (
        ('Ещё одна пропущенная цифра', 'Another missing digit'),
        ('Какую цифру d нужно поставить в число 4d52, чтобы оно делилось на 9? Запишите, почему подходит только одна цифра.',
         'What digit d makes 4d52 divisible by 9? Explain why exactly one digit works.'),
        ('Сумма цифр равна 11 + d и лежит между 11 и 20. Единственное кратное 9 в этом промежутке — 18, значит d = 7.',
         'The digit sum is 11 + d and lies between 11 and 20. The only multiple of 9 in this interval is 18, so d = 7.'),
    ),
    'methods': (
        ('Пары в больших степенях', 'Pairs in large powers'),
        ('Найдите остаток от деления 11²⁰²⁵ + 5²⁰²⁴ на 12. Объясните, как чётность показателей влияет на остаток.',
         'Find the remainder of 11²⁰²⁵ + 5²⁰²⁴ modulo 12. Explain how the parity of the exponents affects the remainder.'),
        ('По модулю 12 оба квадрата, 11² и 5², сравнимы с 1. После группировки в пары в первой степени остаётся множитель 11, во второй — ни одного. Сумма сравнима с 11 + 1 = 12, поэтому остаток равен 0.',
         'Modulo 12, both 11² and 5² are congruent to 1. Pairing the factors leaves one 11 in the first power and no leftover factor in the second. The sum is congruent to 11 + 1 = 12, so the remainder is 0.'),
    ),
    'proofs': (
        ('Произведение с шагом два', 'A product with step two'),
        ('Докажите, что n(n + 2)(n + 4)(n + 6) + 16 — квадрат целого числа при любом целом n. Запишите, как сгруппировать множители.',
         'Prove that n(n + 2)(n + 4)(n + 6) + 16 is a perfect square for every integer n. Write down how to group the factors.'),
        ('Сгруппируем крайние и средние множители. Если u = n(n + 6), то (n + 2)(n + 4) = u + 8. Значит, выражение равно u(u + 8) + 16 = (u + 4)².',
         'Pair the outer and inner factors. If u = n(n + 6), then (n + 2)(n + 4) = u + 8. The expression is therefore u(u + 8) + 16 = (u + 4)².'),
    ),
}


def button(action, ru, en, secondary=False):
    style = 'btn btn-line' if secondary else 'btn'
    return f'<button type="button" class="{style}" data-route-action="{action}">{bilingual(ru, en)}</button>'


def details(label, copy):
    return f'<details><summary>{bilingual(*label)}</summary><p>{bilingual(*copy)}</p></details>'


def numbers_route():
    text = bilingual
    parts = [
        '<div class="number-route" id="number-route"><header class="page-head">',
        '<h1>'+text('Числа и делимость', 'Numbers and divisibility')+'</h1>',
        '<p>'+text('За 20–30 минут разберите один метод и примените его в новой задаче.',
                   'Spend 20–30 minutes learning one method and applying it to a new problem.')+'</p></header>',
        '<div id="route-controls" class="actions" hidden>',
        button('diagnostic', 'Помогите выбрать уровень', 'Help me choose a level'),
        button('choose', 'Я знаю свой уровень', 'I know my level', True),
        '</div>',
        '<section id="route-diagnostic" class="task route-panel" hidden>',
        '<h2 tabindex="-1">'+text('Стартовая задача', 'Starting problem')+'</h2>',
        '<p>'+text('Не вычисляя число целиком, найдите остаток от деления 7⁴ + 7 на 4 и объясните свой ход.',
                   'Without computing the whole number, find the remainder of 7⁴ + 7 modulo 4 and explain your reasoning.')+'</p>',
        details(('Подсказка', 'Hint'), ('Чему равен остаток от деления 7 на 4? А от деления 7²?',
                                      'What remainder does 7 leave modulo 4? What about 7²?')),
        details(('Проверить решение', 'Check the solution'), ('Число 7 даёт остаток 3, а его квадрат — остаток 1. Поэтому 7⁴ даёт остаток 1, а 1 + 3 делится на 4. Ответ — 0.',
                                                            'The remainder of 7 is 3 and its square has remainder 1. So 7⁴ has remainder 1, and 1 + 3 is divisible by 4. The answer is 0.')),
        '<p>'+text('Как прошла попытка?', 'How did it go?')+'</p><div class="actions">',
        button('recommend-foundations', 'Не нашёл первый шаг', 'I could not find a first step', True),
        button('recommend-methods', 'Решил с подсказкой', 'I solved it with a hint', True),
        button('recommend-proofs', 'Решил и могу объяснить', 'I solved it and can explain why', True),
        '</div></section>',
        '<section id="route-picker" class="route-panel" hidden>',
        '<h2 tabindex="-1">'+text('Выберите уровень', 'Choose a level')+'</h2>',
        '<p id="route-recommendation" class="muted" role="status" hidden></p>',
        '<div class="route-levels">',
    ]
    for index, (section, name, note, _, _) in enumerate(LEVELS, 1):
        parts.extend([
            f'<button type="button" class="level" data-route-action="level-{section}"><b>'
            +text(f'Уровень {index} · {name[0]}', f'Level {index} · {name[1]}')+'</b><span>'+text(*note)+'</span></button>',
        ])
    parts.append('</div></section>')
    for section, name, _, page, main in LEVELS:
        title, problem, hint, solution = main
        transfer_title, transfer_problem, model = TRANSFER[section]
        parts.extend([
            f'<section class="route-panel" id="{section}" data-route-level aria-labelledby="{section}-title">',
            '<div class="actions route-change" hidden>'+button('choose', 'Сменить уровень', 'Change level', True)+'</div>',
            f'<h2 id="{section}-title" tabindex="-1">'+text(*name)+'</h2>',
            '<article class="task route-task" data-step="main">',
            '<h3 tabindex="-1">'+text(*title)+'</h3><p>'+text(*problem)+'</p>',
            details(('Подсказка', 'Hint'), hint),
            details(('Разбор решения', 'Worked solution'), solution),
            '<div class="actions route-next" hidden>'+button('transfer', 'Перейти к новой задаче', 'Try the next problem')+'</div></article>',
            '<article class="task route-task" data-step="transfer">',
            '<h3 tabindex="-1">'+text(*transfer_title)+'</h3><p>'+text(*transfer_problem)+'</p>',
            f'<label class="route-answer" for="{section}-answer" hidden>'+text('Ваш ключевой шаг', 'Your key step')
            +f'<textarea id="{section}-answer" rows="3" maxlength="3000"></textarea></label>',
            '<div class="route-next" hidden>'+button('check', 'Сверить с эталоном', 'Compare with the model answer')+'</div>',
            '<div data-model>'+details(('Эталонный разбор', 'Model answer'), model)+'</div>',
            '<div data-reflection hidden><p>'+text('Удалось применить тот же метод?', 'Were you able to apply the same method?')+'</p><div class="actions">',
            button('done', 'Да, получилось', 'Yes, I did'),
            button('retry', 'Хочу попробовать ещё раз', 'I want to try again', True),
            '</div></div></article>',
            '<article class="task route-task" data-step="done" hidden><h3 tabindex="-1">'
            +text('Тренировка завершена', 'Training complete')+'</h3><p>'
            +text('Вы применили метод в новой задаче. Можно выбрать другой уровень или найти задачу в архиве.',
                  'You applied the method to a new problem. Choose another level or find a problem in the archive.')+'</p>',
            '<p><a class="btn btn-line" href="tasks.html?topic=numbers">'
            +text('Архивные задачи по теме →', 'Archive problems on this topic →')+'</a></p></article>',
            f'<p><a href="reader.html?file=numbers-01.pdf&amp;page={page}&amp;lang=original">'
            +text('Теория в томе (PDF на русском) ↗', 'Read the theory (Russian PDF) ↗')+'</a></p>',
            '</section>',
        ])
    parts.append('</div>')
    return '\n'.join(parts)
