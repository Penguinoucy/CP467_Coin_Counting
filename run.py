"""Role 5 runner. --check-setup works without OpenCV or actual photographs."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import importlib
import json
import math
from pathlib import Path
from statistics import median
import sys
from time import perf_counter

from utils.data_io import load_manifest, load_label
from utils.experiment import metadata

ROOT=Path(__file__).resolve().parent

def check_setup(rows):
    print(f"Manifest valid: {len(rows)} planned photos, {len({r['arrangement_id'] for r in rows})} layouts")
    for split,n in sorted(Counter(r["split"] for r in rows).items()):print(f"  {split}: {n} photos")
    missing=sum(not (ROOT/r["image_path"]).is_file() for r in rows)
    ready=0
    for r in rows:
        try:load_label(ROOT,r["image_id"]);ready+=1
        except (ValueError,OSError):pass
    print(f"Photos still needed: {missing}; reviewed labels ready: {ready}/{len(rows)}")
    for method in ["hough","contours"]:
        c=json.loads((ROOT/f"configs/{method}.json").read_text())
        print(f"{method} implementation_ready: {c.get('implementation_ready') is True}")
    print("Setup check passed. Pending photos, labels, and implementations are not completed experiments.")

def normalize(coins,width,height):
    if not isinstance(coins,list):raise ValueError("detect() must return a list")
    result=[]
    for c in coins:
        if not isinstance(c,dict):raise ValueError("Each detection must be a dictionary")
        d={}
        for k in ["x","y"]+(["radius"] if "radius" in c else []):
            if isinstance(c.get(k),bool):raise ValueError("Boolean coordinates are not valid")
            value=float(c[k])
            if not math.isfinite(value):raise ValueError("Detection values must be finite")
            d[k]=value
        if not (0<=d["x"]<width and 0<=d["y"]<height) or ("radius" in d and d["radius"]<=0):
            raise ValueError("Detection has an invalid centre or radius")
        result.append(d)
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-setup",action="store_true")
    ap.add_argument("--method",choices=["hough","contours"])
    ap.add_argument("--split",choices=["development","validation","test"])
    ap.add_argument("--clahe",choices=["off","on"])
    ap.add_argument("--output")
    ap.add_argument("--limit",type=int,help="Optional development-only pilot limit")
    args=ap.parse_args()
    rows=load_manifest(ROOT)
    if args.check_setup:check_setup(rows);return
    if any(getattr(args,k) is None for k in ["method","split","clahe","output"]):
        ap.error("A run requires --method, --split, --clahe, and --output")
    if args.limit is not None and (args.limit<=0 or args.split!="development"):
        ap.error("--limit must be positive and is allowed only for development")
    if args.split=="test":
        approval=json.loads((ROOT/"configs/final_test_approval.json").read_text())
        if not all(approval.get(k) is True for k in ["settings_frozen","validation_completed","test_layouts_unused_for_tuning"]) or not approval.get("approved_by") or not approval.get("approved_date"):
            raise ValueError("Complete configs/final_test_approval.json truthfully before a final test run")
    config=json.loads((ROOT/f"configs/{args.method}.json").read_text())
    if config.get("implementation_ready") is not True:
        raise ValueError(f"Role owner must complete detectors/{args.method}.py and configs/{args.method}.json first")
    common=json.loads((ROOT/"configs/common.json").read_text())
    if type(common.get("warmup_runs")) is not int or common["warmup_runs"]<0 or type(common.get("timed_runs")) is not int or common["timed_runs"]<1:
        raise ValueError("Invalid timing repetition settings")
    config["common"]=common
    selected=[r for r in rows if r["split"]==args.split]
    if args.limit is not None:selected=selected[:args.limit]
    if not selected:raise ValueError("No selected photos")
    missing=[r["image_path"] for r in selected if not (ROOT/r["image_path"]).is_file()]
    if missing:raise ValueError(f"{len(missing)} selected photos missing; first: {missing[0]}")
    try:import cv2
    except ImportError as e:raise ValueError("Install requirements.txt before image processing") from e
    from utils.visualization import draw_detections
    detector=importlib.import_module(f"detectors.{args.method}").detect
    output=(ROOT/args.output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    (output/"marked_images").mkdir()
    results=[]
    for row in selected:
        image=cv2.imread(str(ROOT/row["image_path"]))
        if image is None:raise ValueError(f"Cannot decode {row['image_path']}")
        h,w=image.shape[:2]
        for _ in range(common["warmup_runs"]):detector(image.copy(),config,use_clahe=args.clahe=="on")
        timings=[]
        for _ in range(common["timed_runs"]):
            frame=image.copy()
            start=perf_counter()
            raw=detector(frame,config,use_clahe=args.clahe=="on")
            timings.append((perf_counter()-start)*1000)
        coins=normalize(raw,w,h)
        marked=draw_detections(image,coins)
        if not cv2.imwrite(str(output/"marked_images"/(row["image_id"]+".jpg")),marked):
            raise ValueError("Failed to write marked image")
        results.append({**row,"image_width":w,"image_height":h,"count":len(coins),"coins":coins,
                        "median_ms":median(timings),"timings_ms":timings})
    run={"status":"completed","created_at":datetime.now(timezone.utc).isoformat(),
         "method":args.method,"clahe":args.clahe=="on","split":args.split,
         "pilot_run":args.limit is not None,"config":config,"environment":metadata(ROOT),"images":results}
    (output/"predictions.json").write_text(json.dumps(run,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Completed {len(results)} photos. Saved {output/'predictions.json'}")
    print("Accuracy has not been evaluated. Use evaluate.py after Role 4 completes it.")

if __name__=="__main__":
    try:main()
    except (ValueError,OSError,NotImplementedError,KeyError) as e:
        print(f"Cannot complete run: {e}",file=sys.stderr);sys.exit(2)
