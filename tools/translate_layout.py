"""Replace extractable prose while retaining the original PDF page content."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

import pymupdf as fitz

TOOLS = Path(__file__).resolve().parent
SAMPLE = 'dd775cebb5b10b475df3955fbbc4a969014bf6868d22948bc04637a703cfac36'
CYRILLIC = re.compile(r'[А-Яа-яЁё]')
LATIN = re.compile(r'[A-Za-z]')
# Skip mixed runs whose mathematical glyphs cannot be isolated reliably.
PROSE = re.compile(r"[A-Za-zА-Яа-яЁё\s.,:;!?«»“”'’—–-]+")
RAW_FLAGS = fitz.TEXTFLAGS_RAWDICT & ~fitz.TEXT_PRESERVE_IMAGES
SYSTEM_FONTS = Path('/System/Library/Fonts/Supplemental')


def spans(page):
    for block in page.get_text('rawdict', flags=RAW_FLAGS)['blocks']:
        for line in block.get('lines', ()):
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


def source_run(text, source):
    if source == 'ru':
        if not CYRILLIC.search(text) and len(re.findall(r'[\u00c0-\u00ff]', text)) >= 3:
            text = text.encode('latin1', errors='replace').decode('cp1251', errors='replace')
        return text if CYRILLIC.search(text) else ''
    return text if LATIN.search(text) else ''


def plan(page, source, target, curated, models, fonts):
    edits, skipped = [], 0
    candidates = list(spans(page))
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
        else:
            original = source_run(text.strip(), source)
            if not original:
                continue
            if direction != (1.0, 0.0) or not PROSE.fullmatch(original) or len(original.split()) < 2:
                skipped += 1
                continue
            replacement, ok = models.translate(source, target, original)
            if not ok or not (LATIN if target == 'en' else CYRILLIC).search(replacement):
                skipped += 1
                continue
        chars = [char for char in span['chars'] if not char['c'].isspace()]
        if not chars:
            continue
        point = fitz.Point(chars[0]['origin'])
        font_path = replacement_font(span, curated is not None)
        if font_path not in fonts:
            fonts[font_path] = fitz.Font(fontfile=str(font_path))
        font = fonts[font_path]
        size = span['size']
        right = chars[-1]['bbox'][2]
        # A trailing or leading space adjacent to a formula belongs to the original layout.
        width = right - point.x
        scale = min(1, width / font.text_length(replacement, fontsize=size))
        minimum_scale = .72
        if curated is not None:
            minimum_scale = .2 if original == 'и' else .4
        if scale < minimum_scale or any(not font.has_glyph(ord(c)) for c in replacement):
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
            edits, missed = plan(page, source, target, curated, models, fonts) if not page.rotation else ([], 1)
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
                 skipped=skipped, curated=curated is not None, layout=True)
