"""Evaluation entry point. Requires reviewed labels and Role 4's implementation."""
import argparse
import json
from pathlib import Path
import sys
from utils.data_io import load_manifest, load_label
from evaluation import metrics
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predictions",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--allow-unreviewed-labels",action="store_true",help="Explicit provisional scoring; peer review pending")
    args=p.parse_args()
    if metrics.IMPLEMENTATION_READY is not True:
        raise ValueError("Role 4 must complete evaluation/metrics.py and matching.py first")
    run=json.loads((ROOT/args.predictions).read_text(encoding="utf-8"))
    if run.get("status")!="completed" or not run.get("images"):
        raise ValueError("Predictions must come from a completed run")
    manifest={r["image_id"]:r for r in load_manifest(ROOT)}
    seen=set();labels={}
    for record in run["images"]:
        iid=record["image_id"]
        if iid in seen or iid not in manifest:raise ValueError("Duplicate or unknown image ID")
        seen.add(iid)
        if any(record.get(k)!=manifest[iid][k] for k in ["split","arrangement_id","contact","background","lighting"]):
            raise ValueError("Prediction metadata disagrees with manifest")
        if record["split"]!=run["split"]:raise ValueError("Mixed dataset splits")
        label=load_label(ROOT,iid,allow_unreviewed=args.allow_unreviewed_labels)
        if (label["image_width"],label["image_height"])!=(record["image_width"],record["image_height"]):
            raise ValueError("Label and prediction image dimensions differ")
        if record["count"]!=len(record["coins"]):raise ValueError("Prediction count mismatch")
        labels[iid]=label
    expected={iid for iid,r in manifest.items() if r["split"]==run["split"]}
    if not run.get("pilot_run") and seen!=expected:raise ValueError("Full run is missing selected-split images")
    result=metrics.evaluate_records(run["images"],labels)
    required={"per_image","summary","by_contact","by_background_lighting"}
    if not isinstance(result,dict) or not required.issubset(result):
        raise ValueError("Evaluator must return the four documented result fields")
    if not isinstance(result["per_image"],list) or len(result["per_image"])!=len(seen):
        raise ValueError("Evaluator per_image results must cover all evaluated photos")
    output=(ROOT/args.output).resolve();output.mkdir(parents=True,exist_ok=False)
    payload={"status":"completed","method":run["method"],"clahe":run["clahe"],
             "split":run["split"],"pilot_run":run.get("pilot_run",False),
             "annotation_review":"provisional_unreviewed" if args.allow_unreviewed_labels else "reviewed",
             "review_disclosure":"Scores use supplied VIA annotations; original annotator names and independent review pending." if args.allow_unreviewed_labels else "Reviewed labels required.",
             "results":result}
    (output/"metrics.json").write_text(json.dumps(payload,indent=2,allow_nan=False),encoding="utf-8")
    print(f"Saved {output/'metrics.json'}")
    if args.allow_unreviewed_labels:print('PROVISIONAL: independent peer annotation review is pending.')
if __name__=="__main__":
    try:main()
    except (ValueError,OSError,NotImplementedError,KeyError) as e:
        print(f"Cannot evaluate: {e}",file=sys.stderr);sys.exit(2)
