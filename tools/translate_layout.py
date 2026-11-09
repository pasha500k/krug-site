"""Replace extractable prose while retaining the original PDF page content."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

import pymupdf as fitz

TOOLS = Path(__file__).resolve().parent
LOCAL_REVIEWS = {
    '41e8c3b04c42bd8fa309b195d63b747414244fd3cc3628e3906487f5f5e2f482': 'layout-dano-en.json',
    '98b2cc3d80c16ff9bcc37fc3ee26efd1fe38c42dd5cea5cb36fa0c6abd0377e6': 'layout-vosh-en.json',
}
SAMPLE = 'dd775cebb5b10b475df3955fbbc4a969014bf6868d22948bc04637a703cfac36'
CYRILLIC = re.compile(r'[А-Яа-яЁё]')
LATIN = re.compile(r'[A-Za-z]')
# Identifiers and formula punctuation delimit prose without being erased.
RUSSIAN_RUN = re.compile(r"[А-Яа-яЁё0-9\s.,:;!?«»“”'’—–−%/+-]+")
ENGLISH_RUN = re.compile(r"[A-Za-z\s.,:;!?«»“”'’—–-]+")
TASK_NUMBER = re.compile(r"^\s*\d+[.)](?=\s)")
GLOSSARY = {
    ('ru', 'en'): {'возраст': 'age', 'переменная': 'Variable',
                   'оценка коэффициента': 'Coefficient estimate'},
}
RAW_FLAGS = fitz.TEXTFLAGS_RAWDICT & ~fitz.TEXT_PRESERVE_IMAGES
SYSTEM_FONTS = Path('/System/Library/Fonts/Supplemental')


def text_lines(page):
    for index, block in enumerate(page.get_text('rawdict', flags=RAW_FLAGS)['blocks']):
        for line in block.get('lines', ()):
            yield index, line


def spans(page):
    for _, line in text_lines(page):
        for span in line['spans']:
            yield line['dir'], span


def characters(span):
    return ''.join(char['c'] for char in span['chars'])


def glyphs(page):
    by_text = defaultdict(list)
    for _, span in spans(page):
        for char in span['chars']:
            if not char['c'].isspace():
                by_text[span['font'], char['c']].append(char['origin'])
    return by_text


def same_glyphs(expected, actual):
    if expected.keys() != actual.keys():
        return False
    for key, positions in expected.items():
        if len(positions) != len(actual[key]):
            return False
        # MuPDF can round text positioning when it rewrites a content stream.
        order = lambda point: (round(point[1], 1), point[0])
        for (x, y), (u, v) in zip(sorted(positions, key=order), sorted(actual[key], key=order)):
            if abs(x-u) > .025 or abs(y-v) > .025:
                return False
    return True


def replacement_font(span, curated):
    if curated:
        return TOOLS / 'fonts/lmroman12-regular.otf'
    style = ' Bold' if span['flags'] & fitz.TEXT_FONT_BOLD else ''
    if span['flags'] & fitz.TEXT_FONT_ITALIC:
        style += ' Italic'
    if span['flags'] & fitz.TEXT_FONT_MONOSPACED:
        family = 'Courier New'
    elif span['flags'] & fitz.TEXT_FONT_SERIFED:
        family = 'Times New Roman'
    else:
        family = 'Arial'
    return SYSTEM_FONTS / (family + style + '.ttf')


def prose_runs(text, source):
    if source == 'ru' and not CYRILLIC.search(text) and len(re.findall(r'[\u00c0-\u00ff]', text)) >= 3:
        text = text.encode('latin1', errors='replace').decode('cp1251', errors='replace')
    regex, letters = (RUSSIAN_RUN, CYRILLIC) if source == 'ru' else (ENGLISH_RUN, LATIN)
    number = TASK_NUMBER.match(text)
    for match in regex.finditer(text, number.end() if number else 0):
        start, end = match.span()
        # Leave punctuation and adjacent formula constants in their original positions.
        if source == 'ru':
            leading = re.match(r"[^А-Яа-яЁё]*", match[0])
            start += leading.end()
            trailing = re.search(r"[^А-Яа-яЁё]+$", text[start:end])
            if trailing:
                end = start+trailing.start()
        else:
            while start < end and not letters.match(text[start]):
                start += 1
            while end > start and not letters.match(text[end-1]):
                end -= 1
        if start < end and letters.search(text[start:end]):
            original = text[start:end]
            if source == 'ru' or len(original.split()) > 1 or original.islower() and len(original) > 4:
                yield start, end, original


def contextual_runs(page, source, overrides):
    """Group flowing prose across line breaks without crossing fixed glyphs."""
    groups = []
    previous = None
    for block, line in text_lines(page):
        entries = []
        if line['dir'] != (1.0, 0.0):
            previous = None
            continue
        visible = [span for span in line['spans'] if characters(span).strip()]
        for span in visible:
            raw = characters(span)
            entries.extend((span, start, end, text) for start, end, text in prose_runs(raw, source))
        if not entries:
            previous = None
            continue
        first = entries[0]
        if previous and not overrides and first[0] is visible[0] and not characters(first[0])[:first[1]].strip():
            old_block, tail, group = previous
            last_span, start, end, text = group[-1]
            delta = first[0]['origin'][1]-last_span['origin'][1]
            if (old_block == block and last_span['font'] == first[0]['font']
                    and 0 < delta < last_span['size']*1.8 and len(group) < 12
                    and re.fullmatch(r'[.?!,:;…-]*', tail)):
                if tail:
                    stop = len(characters(last_span).rstrip())
                    group[-1] = (last_span, start, stop, text+tail)
                group.append(entries.pop(0))
                groups.extend([entry] for entry in entries)
            else:
                groups.extend([entry] for entry in entries)
        else:
            groups.extend([entry] for entry in entries)
        last = groups[-1][-1]
        previous = (block, characters(last[0])[last[2]:].strip(), groups[-1]) if last[0] is visible[-1] else None
    return groups


def distribute(words, widths, font, size):
    remaining = words[:]
    result = []
    for index, width in enumerate(widths[:-1]):
        proportion = width/sum(widths[index:])
        limit = font.text_length(' '.join(remaining), fontsize=size)*proportion
        maximum = len(remaining)-(len(widths)-index-1)
        if maximum < 1:
            return []
        split = min(range(1, maximum+1),
                    key=lambda n:abs(font.text_length(' '.join(remaining[:n]), fontsize=size)-limit))
        result.append(' '.join(remaining[:split]))
        remaining = remaining[split:]
    return result+[' '.join(remaining)] if remaining else []


def group_replacements(page, source, target, models, fonts, overrides):
    replacements = {}
    for group in contextual_runs(page, source, overrides):
        if len(group) < 2:
            continue
        original = ''
        for _, _, _, text in group:
            if original.endswith('-'):
                original = original[:-1]+text
            else:
                original = (original+' '+text).strip()
        translated, ok = models.translate(source, target, original)
        if not ok or (target == 'en' and CYRILLIC.search(translated)):
            continue
        font_path = replacement_font(group[0][0], False)
        if font_path not in fonts:
            fonts[font_path] = fitz.Font(fontfile=str(font_path))
        font = fonts[font_path]
        size = group[0][0]['size']
        widths = [span['chars'][end-1]['bbox'][2]-span['chars'][start]['origin'][0]
                  for span, start, end, _ in group]
        pieces = distribute(translated.strip().rstrip('.,;:!?').split(), widths, font, size)
        if len(pieces) != len(group) or any(
            font.text_length(piece, fontsize=size)*.52 > width
            or any(not font.has_glyph(ord(char)) for char in piece)
            for piece, width in zip(pieces, widths)
        ):
            continue
        for (span, start, end, text), piece in zip(group, pieces):
            key = span['font'], span['origin'], start
            replacements[key] = (end, piece)
    return replacements


def plan(page, source, target, curated, models, fonts, overrides=None):
    edits, skipped = [], 0
    candidates = list(spans(page))
    context = {} if curated is not None or overrides else group_replacements(page, source, target, models, fonts, overrides)
    if not candidates:
        return edits, 1
    for direction, span in candidates:
        text = characters(span)
        if curated is not None:
            if span['font'] != 'F38':
                continue
            original = text.encode('latin1').decode('cp1251').strip()
            replacement = curated.get(original)
            if replacement is None:
                skipped += bool(CYRILLIC.search(original))
                continue
            runs = [(0, len(text), original, replacement)]
        else:
            detected = list(prose_runs(text, source))
            if direction != (1.0, 0.0):
                skipped += len(detected)
                continue
            runs = [(start, end, original, None) for start, end, original in detected]
        for start, end, original, replacement in runs:
            if replacement is None:
                anchored = context.get((span['font'], span['origin'], start))
                if anchored:
                    end, replacement = anchored
            reviewed = False
            if replacement is None:
                key = ' '.join(original.split())
                replacement = (overrides or {}).get(key)
                reviewed = replacement is not None
                if reviewed and re.fullmatch(r'-\s*', text[end:]):
                    end += 1
                if not reviewed:
                    replacement = GLOSSARY.get((source, target), {}).get(key.casefold())
                ok = True
                if replacement is None:
                    normalized = re.sub(r'\bтимлид\b', 'руководитель команды', original, flags=re.I)
                    replacement, ok = models.translate(source, target, normalized)
                    replacement = replacement.strip().rstrip('.,;:!?')
                expected = LATIN if target == 'en' else CYRILLIC
                if not ok or not (reviewed or expected.search(replacement) or replacement=='&') or (target == 'en' and CYRILLIC.search(replacement)):
                    skipped += 1
                    continue
            chars = [char for char in span['chars'][start:end] if not char['c'].isspace()]
            if not chars:
                continue
            point = fitz.Point(chars[0]['origin'])
            font_path = replacement_font(span, curated is not None)
            if font_path not in fonts:
                fonts[font_path] = fitz.Font(fontfile=str(font_path))
            font = fonts[font_path]
            size = span['size']
            width = chars[-1]['bbox'][2] - point.x
            scale = min(1, width / font.text_length(replacement, fontsize=size)) if replacement else 1
            minimum = .28 if replacement == '&' else (.38 if curated is not None or reviewed else .52)
            if scale < minimum or any(not font.has_glyph(ord(c)) for c in replacement):
                skipped += 1
                continue
            edits.append((span, chars, point, font_path, size, scale, replacement))
    return edits, skipped


def redact(page, edits):
    for _, chars, _, _, size, _, _ in edits:
        x0 = (chars[0]['bbox'][0] + chars[0]['bbox'][2]) / 2
        x1 = (chars[-1]['bbox'][0] + chars[-1]['bbox'][2]) / 2
        y = chars[0]['origin'][1] - size * .25
        page.add_redact_annot(fitz.Rect(x0-.03, y-.03, x1+.03, y+.03), fill=False, cross_out=False)
    page.apply_redactions(images=0, graphics=0, text=0)


def replace_page(document, index, edits):
    # Validate redaction on a staged page, then edit the original page object
    # so existing outlines and links keep their destinations.
    expected = glyphs(document[index])
    for span, chars, *_ in edits:
        for char in chars:
            key = span['font'], char['c']
            expected[key].remove(char['origin'])
            if not expected[key]:
                del expected[key]
    with fitz.open() as copy:
        copy.insert_pdf(document, from_page=index, to_page=index)
        redact(copy[0], edits)
        if not same_glyphs(expected, glyphs(copy[0])):
            return False
    page = document[index]
    redact(page, edits)
    for span, _, point, path, size, scale, replacement in edits:
        if not replacement:
            continue
        font_name = 'Krug' + path.stem.replace(' ', '').replace('-', '')
        page.insert_font(fontname=font_name, fontfile=str(path))
        page.insert_text(point, replacement, fontname=font_name, fontsize=size,
                         color=fitz.sRGB_to_pdf(span['color']), morph=(point, fitz.Matrix(scale, 1)))
    return True


def translate(source_path, result, meta, status, models, detect_language, progress):
    target = meta['target']
    with source_path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    curated = None
    sample = TOOLS / 'layout-239-en.json'
    if target == 'en' and digest == SAMPLE and sample.is_file():
        curated = json.loads(sample.read_text(encoding='utf-8'))
    overrides = None
    if target == 'en' and digest in LOCAL_REVIEWS:
        sample = TOOLS / LOCAL_REVIEWS[digest]
        if sample.is_file():
            overrides = json.loads(sample.read_text(encoding='utf-8'))
    with fitz.open(source_path) as document:
        if document.needs_pass:
            progress(status, state='unavailable')
            return
        source = meta.get('source') or detect_language(
            '\n'.join(document[i].get_text() for i in range(min(5, len(document)))), '')
        if source == target:
            progress(status, state='original')
            return
        if source not in ('ru', 'en'):
            progress(status, state='unavailable')
            return
        total, changed, skipped = len(document), 0, 0
        fonts = {}
        for index, page in enumerate(document):
            # Auto-replacement is intentionally restricted to upright text pages.
            edits, missed = plan(page, source, target, curated, models, fonts, overrides) if not page.rotation else ([], 1)
            skipped += missed
            if edits:
                if replace_page(document, index, edits):
                    changed += len(edits)
                else:
                    skipped += len(edits)
            progress(status, state='working', done=index+1, total=total)
        if not changed or (curated is not None and skipped):
            progress(status, state='unavailable', skipped=skipped)
            return
        metadata = document.metadata
        original_author = metadata.get('author') or meta.get('organizer', '')
        metadata.update(author=original_author, creator='Krug · unofficial translation',
                        subject='Unofficial translation · ' + meta.get('url', ''))
        document.set_metadata(metadata)
        temporary = result.with_suffix('.pdf.tmp')
        document.save(temporary, garbage=3, deflate=True)
        temporary.replace(result)
        progress(status, state='ready', pages=list(range(1, total+1)), total=total,
                 skipped=skipped, curated=curated is not None, reviewed=overrides is not None, layout=True)
