"""Check planned structure, or require all photos and reviewed labels."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from utils.data_io import load_manifest, load_label
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--require-ready",action="store_true")
    args=p.parse_args()
    rows=load_manifest(ROOT);missing=0;pending=0
    for row in rows:
        if not (ROOT/row["image_path"]).is_file():missing+=1
        try:load_label(ROOT,row["image_id"])
        except (ValueError,OSError):pending+=1
    print(f"Valid manifest: {len(rows)} rows. Missing photos: {missing}. Incomplete/unreviewed labels: {pending}.")
    if args.require_ready and (missing or pending):sys.exit(2)
if __name__=="__main__":
    try:main()
    except (ValueError,OSError) as e:print(e,file=sys.stderr);sys.exit(2)
