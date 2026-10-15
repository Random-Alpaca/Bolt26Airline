"""Build editable slides from OOXML layouts and JSON text, with no external dependencies."""
import copy
import json
import re
import zipfile
from xml.sax.saxutils import escape

from merge_recommendation import E, NS, slide_paths, notes_path, note_body


def build_subset(source, output, content_path, source_dir):
    content = json.loads(content_path.read_text(encoding='utf-8'))
    notes = json.loads((source_dir / 'recommendation_notes.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(source) as original:
        paths = slide_paths(original)
        if len(paths) != 27:
            raise ValueError('Expected the 27-slide NorthByte deck.')
        updates = {}
        for n in (18, 19, 20):
            layout = (source_dir / 'layouts' / f'slide-{n}.xml').read_text(encoding='utf-8')
            keys = set(re.findall(r'\{\{(text_\d+)\}\}', layout))
            if keys != set(content[str(n)]):
                raise ValueError(f'Slide {n}: content keys do not match layout placeholders')
            xml = re.sub(r'\{\{(text_\d+)\}\}', lambda m: escape(content[str(n)][m[1]]), layout)
            E.fromstring(xml)
            updates[paths[n-1]] = xml.encode('utf-8')
            note_part = notes_path(original, paths[n-1])
            root = E.fromstring(original.read(note_part))
            body = note_body(root).find('p:txBody', NS)
            paragraphs = body.findall('a:p', NS)
            prototype = paragraphs[0] if paragraphs else E.Element(f'{{{NS["a"]}}}p')
            for paragraph in paragraphs:
                body.remove(paragraph)
            for line in notes[str(n)].split('\n'):
                paragraph = E.SubElement(body, f'{{{NS["a"]}}}p')
                props = prototype.find('a:pPr', NS)
                if props is not None:
                    paragraph.append(copy.deepcopy(props))
                run = E.SubElement(paragraph, f'{{{NS["a"]}}}r')
                style = prototype.find('a:r/a:rPr', NS)
                if style is not None:
                    run.append(copy.deepcopy(style))
                E.SubElement(run, f'{{{NS["a"]}}}t').text = line
            updates[note_part] = E.tostring(root, encoding='utf-8', xml_declaration=True)
        presentation = E.fromstring(original.read('ppt/presentation.xml'))
        ids = presentation.find('p:sldIdLst', NS)
        for index, item in enumerate(list(ids), 1):
            if index not in (18, 19, 20):
                ids.remove(item)
        updates['ppt/presentation.xml'] = E.tostring(presentation, encoding='utf-8', xml_declaration=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as result:
            for item in original.infolist():
                result.writestr(copy.copy(item), updates.get(item.filename, original.read(item.filename)))
