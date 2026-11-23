"""Manifest and annotation checks. Standard library only; safe before photos exist."""
import csv
import json
import math
from collections import defaultdict
from itertools import product
from pathlib import Path

FIELDS = ["image_id", "image_path", "arrangement_id", "background", "lighting", "contact", "split"]
SPLITS = {"development", "validation", "test"}

def load_manifest(root):
    root = Path(root).resolve()
    with (root / "data/manifest.csv").open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError("manifest.csv must use the seven documented columns in order")
        rows = list(reader)
    if not rows:
        raise ValueError("Manifest has no photos")
    ids, paths, groups = set(), set(), defaultdict(list)
    for row in rows:
        if set(row) != set(FIELDS) or any(not row[k] for k in FIELDS):
            raise ValueError("Manifest contains an empty field or malformed row")
        if row["image_id"] in ids or row["image_path"] in paths:
            raise ValueError("Duplicate image ID or image path")
        if not all(c.isalnum() or c in "_-" for c in row["image_id"]):
            raise ValueError("Image IDs must contain letters, numbers, underscores, or hyphens")
        path = Path(row["image_path"])
        if path.is_absolute() or not (root / path).resolve().is_relative_to(root):
            raise ValueError("Image paths must stay inside the project folder")
        if row["split"] not in SPLITS or row["contact"] not in {"separated", "touching"}:
            raise ValueError("Unknown split or contact value")
        if row["background"] not in {"light", "dark"} or row["lighting"] not in {"diffuse", "dim", "directional"}:
            raise ValueError("Unknown capture condition")
        ids.add(row["image_id"]); paths.add(row["image_path"])
        groups[row["arrangement_id"]].append(row)
    conditions = set(product(["light", "dark"], ["diffuse", "dim", "directional"]))
    for aid, items in groups.items():
        if len({r["split"] for r in items}) != 1:
            raise ValueError(f"Layout {aid} crosses dataset splits")
        if len({r["contact"] for r in items}) != 1:
            raise ValueError(f"Layout {aid} has inconsistent contact labels")
        if len(items) != 6 or {(r["background"],r["lighting"]) for r in items} != conditions:
            raise ValueError(f"Layout {aid} must have all six unique conditions")
    return rows

def validate_label(label, image_id, allow_unreviewed=False):
    if label.get("image_id") != image_id:
        raise ValueError("Label image_id does not match manifest")
    # Minimal labels omit administrative fields. Accept them only for explicit
    # provisional scoring; dimensions, counts and geometry are still checked below.
    status_present = "annotation_status" in label
    status_complete = label.get("annotation_status") == "complete"
    if not status_complete and (status_present or not allow_unreviewed):
        raise ValueError(f"Labels for {image_id} are incomplete or unreviewed")
    if not allow_unreviewed and label.get("review_status") != "reviewed":
        raise ValueError(f"Labels for {image_id} are incomplete or unreviewed")
    for key in ["annotator", "reviewer"]:
        if not allow_unreviewed and (not isinstance(label.get(key), str) or not label[key].strip()):
            raise ValueError(f"Missing {key}")
    if not allow_unreviewed and label["annotator"].strip().casefold() == label["reviewer"].strip().casefold():
        raise ValueError("A second member must review the labels")
    w,h=label.get("image_width"),label.get("image_height")
    if type(w) is not int or type(h) is not int or w<=0 or h<=0:
        raise ValueError("Label image dimensions must be positive integers")
    coins=label.get("coins")
    if not isinstance(coins,list) or type(label.get("coin_count")) is not int or label["coin_count"] != len(coins):
        raise ValueError("coin_count must agree with the labelled coins")
    for c in coins:
        if not isinstance(c,dict): raise ValueError("Each coin must be an object")
        for k in ["x","y","radius"]:
            if type(c.get(k)) not in (int,float) or not math.isfinite(c[k]):
                raise ValueError("Coin coordinates and radius must be finite numbers")
        if not (0<=c["x"]<w and 0<=c["y"]<h and c["radius"]>0):
            raise ValueError("Coin centre outside the image or radius not positive")
    return label

def load_label(root, image_id, allow_unreviewed=False):
    p=Path(root)/"data/labels"/(image_id+".json")
    return validate_label(json.loads(p.read_text(encoding="utf-8")),image_id,allow_unreviewed=allow_unreviewed)
