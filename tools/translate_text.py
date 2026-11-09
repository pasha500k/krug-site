"""Low-priority worker for one catalogue translation batch."""
import json
import os
import re
import sys

from translate_pdf import Models, language


def main():
    os.nice(8)
    models = Models(threads=1)
    result = []
    for target, key, text in json.load(sys.stdin):
        source = language(text, '')
        russian = bool(re.search(r'[А-Яа-яЁё]{2,}', text))
        if target == 'en' and russian:
            source = 'ru'
        value = None
        if source in ('ru', 'en') and source != target:
            translated, _ = models.translate(source, target, text, preserve_latin=(source=='ru'))
            expected = r'[A-Za-z]' if target == 'en' else r'[А-Яа-яЁё]'
            if translated != ' '.join(text.split()) and re.search(expected, translated):
                value = translated
        result.append((target, key, value))
    json.dump(result, sys.stdout, ensure_ascii=False)


if __name__ == '__main__':
    main()
