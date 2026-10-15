"""Build only slides 18–20. Uses only Python standard-library modules.

Run from the repository root: python slides/build_recommendation.py
Use --in-place only when intentionally updating the tracked presentation.
"""
import argparse
from pathlib import Path
import shutil
import tempfile

from merge_recommendation import merge_slides
from render_recommendation import build_subset

SLIDES = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deck', type=Path, default=SLIDES / 'NorthByte_FirstByte2026_template.pptx')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--output', type=Path, help='Default: slides/generated/NorthByte_FirstByte2026.pptx')
    group.add_argument('--in-place', action='store_true', help='Replace the source only after preservation checks pass')
    parser.add_argument('--content', type=Path, default=SLIDES / 'recommendation_content.json')
    args = parser.parse_args()
    source = args.deck.resolve()
    if not source.is_file():
        raise SystemExit(f'Missing input deck: {source}')
    output = source if args.in_place else (args.output or SLIDES / 'generated/NorthByte_FirstByte2026.pptx').resolve()
    if output == source and not args.in_place:
        raise SystemExit('Use --in-place to overwrite the source deck.')
    build_root = SLIDES / 'generated'
    build_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='build-', dir=build_root) as folder:
        build = Path(folder)
        build_subset(source, build / 'redesigned-subset.pptx', args.content, SLIDES)
        candidate = build / 'complete.pptx'
        changes = merge_slides(source, build / 'redesigned-subset.pptx', candidate)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate, output)
    print(f'Wrote {output}')
    print('PNG previews are not regenerated; export them in PowerPoint after content changes.')
    print(f'Preservation check passed: only {len(changes)} slide/notes parts changed; all other ZIP entries identical.')


if __name__ == '__main__':
    main()
