#!/usr/bin/env python3
"""Convert VIA 2 circles without inventing identities, reviews, or zero-coin labels.

Run from the project root, for example:
python scripts/convert_via_labels.py --via-dir data/raw_annotations/layout01 \
    --image-dir data/images --output-dir data/labels_converted
Requires OpenCV (already in project requirements) or Pillow for image dimensions.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys


def image_dimensions(path):
    """Use the original photo's displayed orientation, as VIA does.

    OpenCV's default reader applies EXIF orientation. Pillow is the fallback
    when OpenCV is unavailable. No photo or coordinates are modified.
    """
    try:
        import cv2
    except ImportError:
        cv2 = None
    if cv2 is not None:
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Cannot decode image: {path}")
        height, width = image.shape[:2]
        return int(width), int(height), 'OpenCV'
    try:
        from PIL import Image
    except ImportError as exc:
        raise ValueError('Activate the project environment and install requirements.txt first.') from exc
    with Image.open(path) as image:
        width, height = image.size
        if image.getexif().get(274, 1) in (5, 6, 7, 8):
            width, height = height, width
        return width, height, 'Pillow EXIF-aware'


def entries_from_export(data, source):
    if not isinstance(data, dict):
        raise ValueError(f'{source}: expected a VIA JSON object')
    if 'image_id' in data and 'coins' in data:
        raise ValueError(f'{source}: already project-format; use a folder of original VIA exports')
    entries = data.get('_via_img_metadata', data)
    if not isinstance(entries, dict):
        raise ValueError(f'{source}: invalid VIA image metadata')
    return [entry for entry in entries.values()
            if isinstance(entry, dict) and 'filename' in entry and 'regions' in entry]


def convert_export(source, image_dir, annotator=None):
    data = json.loads(source.read_text(encoding='utf-8-sig'))
    entries = entries_from_export(data, source)
    if not entries:
        raise ValueError(f'{source}: no VIA image entries found')
    converted, skipped, audit = {}, [], []
    for entry in entries:
        filename = entry['filename']
        if not isinstance(filename, str) or Path(filename).name != filename or '\\' in filename:
            raise ValueError(f'{source}: filename must be a simple image filename')
        regions = entry['regions']
        if isinstance(regions, dict):
            regions = list(regions.values())
        if not isinstance(regions, list):
            raise ValueError(f'{source}: regions must be a list or object')
        if not regions:
            skipped.append({'source': source.name, 'filename': filename,
                            'reason': 'No circles; left unlabelled, not assumed to contain zero coins.'})
            continue
        image_path = image_dir / filename
        if not image_path.is_file():
            raise ValueError(f'{source}: missing image {filename}; do not guess a filename or dimensions')
        if entry.get('size') is not None and entry['size'] != image_path.stat().st_size:
            raise ValueError(f'{filename}: VIA byte size differs from photo; verify it is the annotated version')
        width, height, decoder = image_dimensions(image_path)
        coins = []
        for index, region in enumerate(regions, 1):
            shape = region.get('shape_attributes', {})
            if shape.get('name') != 'circle':
                raise ValueError(f'{filename}: region {index} is not a circle')
            coin = {'x': shape.get('cx'), 'y': shape.get('cy'), 'radius': shape.get('r')}
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in coin.values()):
                raise ValueError(f'{filename}: invalid coordinates in region {index}')
            x, y, radius = coin['x'], coin['y'], coin['radius']
            if not (0 <= x < width and 0 <= y < height and radius > 0):
                raise ValueError(f'{filename}: invalid centre or radius in region {index}; check orientation')
            if x-radius < 0 or x+radius > width or y-radius < 0 or y+radius > height:
                raise ValueError(f'{filename}: region {index} crosses an image edge; check the annotation')
            coins.append(coin)
        iid = Path(filename).stem
        label = {
            'image_id': iid,
            'annotation_status': 'complete',
            'review_status': 'not_reviewed',
            'annotator': annotator,
            'reviewer': None,
            'image_width': width,
            'image_height': height,
            'coin_count': len(coins),
            'coins': coins,
            'notes': f'Converted from VIA export {source.name}. Circle measurements unchanged. '
                     'Original annotator identity and independent human review must be recorded.'
        }
        if iid in converted and converted[iid] != label:
            raise ValueError(f'{source}: duplicate image entries disagree: {iid}')
        converted[iid] = label
        audit.append({'image_id': iid, 'source_file': source.name, 'image_filename': filename,
                      'image_width': width, 'image_height': height, 'dimension_reader': decoder,
                      'coin_count': len(coins),
                      'image_sha256': hashlib.sha256(image_path.read_bytes()).hexdigest(),
                      'via_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    return converted, skipped, audit


def convert_directory(via_dir, image_dir, output_dir, annotator=None):
    if annotator is not None and not annotator.strip():
        raise ValueError('Annotator name must be nonempty if supplied')
    if output_dir.resolve() == via_dir.resolve():
        raise ValueError('Output must differ from the original VIA folder')
    sources = sorted(via_dir.glob('*.json'))
    if not sources:
        raise ValueError('No VIA .json files found in the selected folder')
    labels, skipped, audit = {}, [], []
    # Plan and validate the entire batch before writing any labels.
    for source in sources:
        current, omitted, checks = convert_export(source, image_dir, annotator)
        for iid, label in current.items():
            if iid in labels:
                # Identical circles can occur in repeated exports, but conflicting ones must not win silently.
                comparable = ['image_id', 'image_width', 'image_height', 'coin_count', 'coins']
                if any(labels[iid][k] != label[k] for k in comparable):
                    raise ValueError(f'Conflicting exports for {iid}; select the latest authoritative source')
            else:
                labels[iid] = label
        skipped.extend(omitted)
        audit.extend(checks)
    if not labels:
        raise ValueError('No annotated circle entries found; no labels written')
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError('Output folder is not empty. Use a new folder to preserve previous labels and reviews.')
    output_dir.mkdir(parents=True, exist_ok=True)
    for iid, label in sorted(labels.items()):
        (output_dir / (iid+'.json')).write_text(json.dumps(label, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return {'converted_files': len(labels), 'total_coin_annotations': sum(x['coin_count'] for x in labels.values()),
            'reviewed_files': 0, 'annotator_supplied': annotator is not None,
            'counts_by_layout': dict(Counter(iid.split('_')[0] for iid in labels)),
            'skipped_entries': skipped, 'images': audit}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--via-dir', type=Path, required=True)
    parser.add_argument('--image-dir', type=Path, default=Path('data/images'))
    parser.add_argument('--output-dir', type=Path, default=Path('data/labels_converted'))
    parser.add_argument('--annotator', help='Original annotator name; use only for a batch they actually annotated')
    args = parser.parse_args()
    report = convert_directory(args.via_dir, args.image_dir, args.output_dir, args.annotator)
    print(json.dumps({k:v for k,v in report.items() if k != 'images'}, indent=2))
    print('Conversion finished. Record original annotators and obtain a different member\'s review.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print(f'Conversion stopped: {exc}', file=sys.stderr)
        sys.exit(2)
