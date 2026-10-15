"""Preserve all source package entries except slides 18–20 and their notes.

Uses only the Python standard library. Resolves slide order via relationships,
checks titles and refuses unexpected slide sizes or dependency-bearing objects.
"""
import copy
import posixpath
import zipfile
from xml.etree import ElementTree as E

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
for prefix, uri in NS.items():
    E.register_namespace(prefix, uri)


def relationships(z, part):
    folder, filename = posixpath.split(part)
    root = E.fromstring(z.read(f'{folder}/_rels/{filename}.rels'))
    return {r.get('Id'): (r.get('Type'), posixpath.normpath(posixpath.join(folder, r.get('Target'))).lstrip('/')) for r in root}


def slide_paths(z):
    root = E.fromstring(z.read('ppt/presentation.xml'))
    rels = relationships(z, 'ppt/presentation.xml')
    return [rels[e.get(f'{{{NS["r"]}}}id')][1] for e in root.find('p:sldIdLst', NS)]


def notes_path(z, slide):
    return next(target for kind, target in relationships(z, slide).values() if kind.endswith('/notesSlide'))


def note_body(root):
    for shape in root.findall('.//p:sp', NS):
        ph = shape.find('p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is not None and ph.get('type') == 'body':
            return shape
    raise ValueError('Missing speaker-notes body')


def merge_slides(source, replacement, output):
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(replacement) as edited:
        old_paths, new_paths = slide_paths(original), slide_paths(edited)
        if len(old_paths) != 27 or len(new_paths) != 3:
            raise ValueError('Expected the 27-slide NorthByte deck and a three-slide replacement.')
        size = lambda z: E.fromstring(z.read('ppt/presentation.xml')).find('p:sldSz', NS).attrib
        for axis in ('cx', 'cy'):
            if size(original)[axis] != size(edited)[axis]:
                raise ValueError('Slide size mismatch')
        replacements = {}
        for i, (num, title) in enumerate(((18, 'RECOMMENDATION'), (19, 'IMPLEMENTATION'), (20, 'RISKS'))):
            old_path, new_path = old_paths[num-1], new_paths[i]
            root = E.fromstring(original.read(old_path)); new = E.fromstring(edited.read(new_path))
            if title not in [e.text for e in root.findall('.//a:t', NS)]:
                raise ValueError(f'Slide {num} is no longer {title}; review numbering before rebuilding.')
            tree = new.find('p:cSld/p:spTree', NS)
            if any(k.startswith(f'{{{NS["r"]}}}') for e in tree.iter() for k in e.attrib):
                raise ValueError('Replacement contains external package dependencies; merge requires text/shapes only.')
            parent = root.find('p:cSld', NS); old_tree = parent.find('p:spTree', NS)
            parent.remove(old_tree); parent.insert(0, copy.deepcopy(tree))
            replacements[old_path] = E.tostring(root, encoding='utf-8', xml_declaration=True)
            nk, nn = notes_path(original, old_path), notes_path(edited, new_path)
            nr, ne = E.fromstring(original.read(nk)), E.fromstring(edited.read(nn))
            body = note_body(nr); previous = body.find('p:txBody', NS)
            body.remove(previous); body.append(copy.deepcopy(note_body(ne).find('p:txBody', NS)))
            replacements[nk] = E.tostring(nr, encoding='utf-8', xml_declaration=True)
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as final:
            for item in original.infolist():
                final.writestr(copy.copy(item), replacements.get(item.filename, original.read(item.filename)))
        with zipfile.ZipFile(output) as final:
            if set(original.namelist()) != set(final.namelist()):
                raise ValueError('Package entries changed unexpectedly')
            changes = [n for n in original.namelist() if original.read(n) != final.read(n)]
            if not set(changes).issubset(replacements):
                raise ValueError('An unrelated package part changed')
            for n in final.namelist():
                if n.endswith(('.xml', '.rels')):
                    E.fromstring(final.read(n))
        return changes
