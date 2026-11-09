"""Handwritten Russian and English practice for the number theory route."""
from html import escape

LEVELS = [
    (
        'foundations',
        ('Делимость и НОД', 'Divisibility and GCD'),
        ('Начните здесь, если умеете делить с остатком.', 'Start here if you can divide with a remainder.'),
        2,
        [
            (
                ('Пропущенная цифра', 'The missing digit'),
                ('Какую цифру d нужно поставить в разряд единиц числа 73d, чтобы оно делилось на 9?',
                 'What digit d should go in the units place of 73d to make the number divisible by 9?'),
                ('Проверьте сумму трёх цифр.', 'Look at the sum of the three digits.'),
                ('Число делится на 9, когда на 9 делится сумма его цифр. Здесь сумма равна 10 + d и лежит между 10 и 19. Единственное кратное 9 в этом промежутке — 18, поэтому d = 8.',
                 'A number is divisible by 9 if its digit sum is divisible by 9. Here the sum is 10 + d, between 10 and 19. The only multiple of 9 in that range is 18, so d = 8.'),
            ),
            (
                ('Общие делители', 'Common divisors'),
                ('Найдите НОД чисел 144 и 90. Представьте его как 144a + 90b, где a и b — целые числа.',
                 'Find the greatest common divisor of 144 and 90. Write it as 144a + 90b, where a and b are integers.'),
                ('Примените алгоритм Евклида, затем подставляйте равенства в обратном порядке.',
                 'Use the Euclidean algorithm, then substitute the equations in reverse order.'),
                ('144 = 90 + 54, 90 = 54 + 36, 54 = 36 + 18 и 36 = 2 · 18. Последний ненулевой остаток равен 18. Идя назад, получаем 18 = 54 − 36 = 2 · 54 − 90 = 2 · 144 − 3 · 90.',
                 '144 = 90 + 54, 90 = 54 + 36, 54 = 36 + 18, and 36 = 2 · 18. The last nonzero remainder is 18. Working backwards gives 18 = 54 − 36 = 2 · 54 − 90 = 2 · 144 − 3 · 90.'),
            ),
        ],
    ),
    (
        'methods',
        ('Остатки и сравнения', 'Remainders and congruences'),
        ('Выберите этот уровень, если умеете находить НОД и хотите научиться работать с большими степенями и несколькими остатками.',
         'Choose this level if you can find a GCD and want to work with large powers and simultaneous congruences.'),
        3,
        [
            (
                ('Две большие степени', 'Two large powers'),
                ('Найдите остаток от деления 7²⁰²⁷ + 5²⁰²⁶ на 12.',
                 'Find the remainder when 7²⁰²⁷ + 5²⁰²⁶ is divided by 12.'),
                ('Сначала найдите остатки чисел 7² и 5².', 'Start with the remainders of 7² and 5².'),
                ('По модулю 12 имеем 7² ≡ 1 и 5² ≡ 1. В первой степени после выделения пар остаётся одна семёрка, во второй все множители разбиваются на пары. Значит, сумма сравнима с 7 + 1, и остаток равен 8.',
                 'Modulo 12, both 7² and 5² are congruent to 1. Pairing the factors in the first power leaves one factor of 7. Every factor in the second power belongs to a pair. The sum is therefore congruent to 7 + 1, and the remainder is 8.'),
            ),
            (
                ('Три условия на одно число', 'Three conditions on one number'),
                ('Найдите все целые числа, которые нечётны, дают остаток 2 при делении на 5 и остаток 3 при делении на 7. Назовите наименьшее положительное решение.',
                 'Find all odd integers that leave remainder 2 on division by 5 and remainder 3 on division by 7. Give the least positive solution.'),
                ('Запишите число в виде 2 + 5k. Сначала найдите допустимые k по модулю 7.',
                 'Write the number as 2 + 5k. First find the possible values of k modulo 7.'),
                ('Требуется 5k ≡ 1 (mod 7). Умножив на 3, получаем k ≡ 3 (mod 7). Значит, число имеет вид 17 + 35t. Оно нечётно ровно при чётном t. Ответ — 17 + 70s для любого целого s. Наименьшее положительное решение равно 17.',
                 'We need 5k ≡ 1 (mod 7). Multiplying by 3 gives k ≡ 3 (mod 7). Thus the number has the form 17 + 35t. It is odd exactly when t is even. The solutions are 17 + 70s for any integer s, and the least positive one is 17.'),
            ),
        ],
    ),
    (
        'proofs',
        ('Олимпиадные доказательства', 'Olympiad proofs'),
        ('Попробуйте, если можете объяснить, почему работает ваш метод, и проверить границы утверждения.',
         'Try these if you can explain why a method works and test the limits of a claim.'),
        5,
        [
            (
                ('Квадрат из четырёх множителей', 'A square from four factors'),
                ('Докажите, что n(n + 1)(n + 2)(n + 3) + 1 — квадрат целого числа при любом целом n.',
                 'Prove that n(n + 1)(n + 2)(n + 3) + 1 is a perfect square for every integer n.'),
                ('Перемножьте крайние множители, а затем два средних. На сколько отличаются результаты?',
                 'Multiply the outer pair of factors and then the inner pair. How far apart are the two products?'),
                ('Положим u = n(n + 3). Тогда (n + 1)(n + 2) = u + 2. Исходное выражение равно u(u + 2) + 1 = (u + 1)².',
                 'Let u = n(n + 3). Then (n + 1)(n + 2) = u + 2. The expression is u(u + 2) + 1 = (u + 1)².'),
            ),
            (
                ('Квадраты простых чисел', 'Squares of primes'),
                ('Пусть p и q — различные простые числа больше 3. Докажите, что p² − q² делится на 24. Всегда ли оно делится на 48?',
                 'Let p and q be distinct primes greater than 3. Prove that p² − q² is divisible by 24. Is it always divisible by 48?'),
                ('Докажите делимость на 3 и на 8 отдельно. Для второго шага разложите p² − 1 на множители.',
                 'Prove divisibility by 3 and by 8 separately. For the second step, factor p² − 1.'),
                ('Каждое из чисел p и q даёт остаток 1 или 2 по модулю 3, поэтому оба квадрата дают остаток 1. Кроме того, p − 1 и p + 1 — соседние чётные числа, одно из которых делится на 4. Поэтому их произведение p² − 1 кратно 8. То же верно для q² − 1. Значит, разность кратна и 3, и 8, а потому и 24. При p = 7 и q = 5 разность равна 24, так что делимость на 48 не гарантирована.',
                 'Each of p and q leaves remainder 1 or 2 modulo 3, so both squares are congruent to 1. Also, p − 1 and p + 1 are consecutive even numbers, one divisible by 4. Their product p² − 1 is divisible by 8, and so is q² − 1. The difference is therefore divisible by both 3 and 8, hence by 24. For p = 7 and q = 5 the difference is 24, so divisibility by 48 is not guaranteed.'),
            ),
        ],
    ),
]


def bilingual(ru, en):
    return (f'<span class="route-copy" lang="ru">{escape(ru)}</span>'
            f'<span class="route-copy" lang="en">{escape(en)}</span>')


def numbers_route():
    text = bilingual
    parts = [
        '<div class="number-route" id="number-route"><header class="page-head">',
        '<div class="eyebrow">'+text('Учебный маршрут', 'Study route')+'</div>',
        '<h1>'+text('Числа и делимость', 'Numbers and divisibility')+'</h1>',
        '<p>'+text('Выберите уровень по тому, что уже умеете. Сначала попробуйте решить задачу, затем откройте подсказку или разбор.',
                   'Choose a level based on what you already know. Try each problem first, then open a hint or check the worked solution.')+'</p></header>',
        '<nav class="actions route-jumps" aria-label="Уровни / Levels">',
    ]
    for section, name, _, _, _ in LEVELS:
        parts.append(f'<a class="btn btn-line" href="#{section}">{text(*name)}</a>')
    parts.append('</nav><p class="muted" id="route-progress" role="status" hidden></p>')
    for index, (section, name, note, page, problems) in enumerate(LEVELS, 1):
        parts.extend([
            f'<section class="route-level" id="{section}" aria-labelledby="{section}-title">',
            '<div class="eyebrow">'+text(f'Уровень {index}', f'Level {index}')+'</div>',
            f'<h2 id="{section}-title">'+text(*name)+'</h2>',
            '<p>'+text(*note)+'</p>',
            f'<p><a href="reader.html?file=numbers-01.pdf&amp;page={page}&amp;lang=original">'
            +text('Теория в томе (PDF на русском) ↗', 'Read the theory (Russian PDF) ↗')+'</a></p>',
            '<div class="task-grid">',
        ])
        for number, (title, problem, hint, solution) in enumerate(problems, 1):
            parts.extend([
                '<article class="task route-task">',
                f'<h3>{text(*title)}</h3><p>{text(*problem)}</p>',
                f'<details><summary>{text("Подсказка", "Hint")}</summary><p>{text(*hint)}</p></details>',
                f'<details><summary>{text("Разбор решения", "Worked solution")}</summary><p>{text(*solution)}</p></details>',
                f'<label class="route-done" hidden><input type="checkbox" data-route-id="{section}-{number}"> '
                +text('Задача решена', 'Problem solved')+'</label></article>',
            ])
        parts.append('</div></section>')
    parts.append('<p><a class="btn btn-line" href="tasks.html?topic=numbers">'+
                 text('Найти архивные задачи по теме →', 'Find archive problems on this topic →')+'</a></p></div>')
    return '\n'.join(parts)
