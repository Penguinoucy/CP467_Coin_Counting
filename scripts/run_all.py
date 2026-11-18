"""Run the four configurations through run.py. Detectors must be completed first."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--split",choices=["development","validation","test"],required=True)
p.add_argument("--output-root",required=True,help="New folder; refuses to overwrite an existing run group")
a=p.parse_args()
base=(ROOT/a.output_root).resolve();base.mkdir(parents=True,exist_ok=False)
for method in ["hough","contours"]:
    for clahe in ["off","on"]:
        subprocess.run([sys.executable,str(ROOT/"run.py"),"--method",method,"--split",a.split,
                        "--clahe",clahe,"--output",str(base/f"{method}_{clahe}")],cwd=ROOT,check=True)
print("All four detection runs completed. Evaluate each predictions.json separately.")
