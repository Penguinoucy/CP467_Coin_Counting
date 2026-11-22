"""Verify that the supplied pilot photos and labels match the recorded input audit."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from utils.data_io import load_manifest,load_label

def main():
    inventory=json.loads((ROOT/'docs/input_inventory.json').read_text())
    manifest={r['image_id']:r for r in load_manifest(ROOT)}
    errors=[];instances=0
    for record in inventory['images']:
        iid=record['image_id'];path=ROOT/manifest[iid]['image_path']
        if not path.is_file():errors.append(f'Missing photo: {path.name}');continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['image_sha256']:
            errors.append(f'Photo bytes differ from annotated source: {path.name}')
        try:
            label=load_label(ROOT,iid,allow_unreviewed=True)
            if label['coin_count']!=record['coin_count'] or (label['image_width'],label['image_height'])!=(record['image_width'],record['image_height']):
                errors.append(f'Label differs from recorded dimensions/count: {iid}')
            instances+=label['coin_count']
        except (ValueError,OSError) as e:errors.append(f'{iid}: {e}')
    if errors:
        print('\n'.join(errors));return 2
    print(f'All {len(inventory["images"])} source photographs match recorded hashes; {instances} label instances structurally valid.')
    print('This verifies files and structure, not independent human annotation review.')
    return 0
if __name__=='__main__':sys.exit(main())
