# CP467 Coin Counting - Mid-Progress Report Package

This update contains changed/new files for the report with **eight example panels**:
layout03_dark_directional and layout10_dark_diffuse, each shown under all four configurations.
All numerical tables still cover the 48 supplied photographs. No remote GitHub changes were made.

Original photos and the large per-photo marked copies are omitted from this update. Reuse your
existing photos. The entries below describe the combined project after merging.

## Project files after merging

| Location | Contents |
|---|---|
| data/images/ | Reuse your existing 48 original JPEGs; not included in this update |
| data/labels/ | All 48 converted labels used in scoring; independent review pending |
| data/raw_annotations/ | Original VIA exports, including the three supplied replacements |
| data/manifest.csv | Fixed 240-photo plan; all six photos of each arrangement stay together |
| detectors/, utils/, evaluation/ | Working processing, matching, metrics and plotting code |
| configs/ | Selected settings and final-test approval template (not approved) |
| run.py, evaluate.py, scripts/ | Run, evaluate, verify, convert, summarize and rebuild tools |
| outputs/development_settings/ | Recorded development parameter search |
| outputs/midprogress/ | All eight actual runs, predictions, timings and metrics; marked photo copies omitted |
| reports/generated/ | CSVs, full results, plots, eight-panel comparison and intermediate masks |
| reports/Mid_Progress_Report_Draft.pdf | Latest report: five main pages plus references |
| reports/progress_report.md | Editable text of that report |
| references/, docs/, tests/ | Citations, records, merge instructions and software checks |

192 unfinished label templates are intentionally omitted from this handoff so they cannot overwrite
new labels your teammates have completed. Existing unrelated repository files must be preserved.

## Setup and verify

Use Python 3.12 and a fresh virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/verify_inputs.py
python run.py --check-setup
python -m unittest discover -s tests -v
```

The input verifier checks all 48 original-photo hashes and label counts/dimensions.
Setup correctly reports 192 planned photos still missing and zero independently reviewed labels.
That is the state of the supplied pilot, not a software failure.

## Rebuild the report from the saved measured results

```bash
python scripts/summarize_results.py --run-root outputs/midprogress
python scripts/build_midprogress_report.py
```

The builder reconstructs all eight example panels from source photos, predictions and matching records.
It does not run new experiments or change settings. It writes the canonical PDF/text files above.

## Re-run the experiments

```bash
python scripts/run_midprogress.py --output-root outputs/reproduction_01 --include-validation --allow-unreviewed-labels
```

Use a new output root each time. `--allow-unreviewed-labels` explicitly records PROVISIONAL scoring;
it does not mark annotations reviewed. Settings were explored on development layouts 01/03/04/09/10/11
(36 photos, 306 instances), then fixed for validation layouts 02/12 (12 photos, 114 instances).
All supplied photos contain separated coins. No final-test or touching-coin photos were evaluated.
No post-validation tuning was done. Original annotator and reviewer identities remain unspecified.

Common processing resizes to max side 1200, applies grayscale and optional CLAHE (clip 2.0, 8x8),
then method-specific smoothing/detection. Results are restored to original-image coordinates.
The same detector settings are used for CLAHE off/on. Matching maximizes valid one-to-one pairs within
half the labelled radius, then minimizes total centre distance. Count error and detection accuracy
are reported separately. Absent touching groups are not_evaluated/null, not zero performance.

## Recorded validation results

| Method / CLAHE | F1 | Count MAE | Exact-count accuracy |
|---|---:|---:|---:|
| Hough off | 0.969 | 0.583 | 66.7% |
| Hough on | 0.893 | 2.167 | 66.7% |
| Contours off | 0.820 | 2.333 | 33.3% |
| Contours on | 0.814 | 2.000 | 41.7% |

Timing uses one OpenCV thread, three warm-ups and ten repeats per image on the recorded Linux
execution machine, not Kevin's Mac. Disk I/O, drawing and scoring are excluded. See docs/hardware.json.
Only eight arrangements are available and all labels remain unreviewed; these are preliminary results.

## Put this on GitHub

Follow PUSH_TO_GITHUB.md. Extract first and merge the folder contents, not the ZIP file.
The ignore rules deliberately include the recorded midprogress/development_settings folders.
New reproduction output folders remain ignored. No virtual environment or Git metadata is included.

The implementation and draft were produced with coding assistance. Group members still need to
review the code/labels, confirm actual contributions, collection details and schedule, and verify
private instructor/TA access. Remaining role sections and final-report files are contribution templates.
