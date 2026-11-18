# CP467 Coin Counting
A starter project for comparing Hough circles and segmentation/contours, each with CLAHE off/on.
Read CONTRIBUTIONS.md to choose roles and find unfinished files. Nothing here claims the study
has been completed. Detectors and evaluation algorithms deliberately raise NotImplementedError.

## Start here
1. Extract the ZIP and open the CP467_Coin_Counting folder.
2. Create an environment: `python -m venv .venv` (use python3 on macOS if needed).
3. Activate: macOS/Linux `source .venv/bin/activate`; Windows Command Prompt `.venv\Scripts\activate.bat`.
4. Install: `python -m pip install -r requirements.txt`.
5. Check planned structure: `python run.py --check-setup`.
   This check also works before installing third-party packages. It reports pending work.
6. Add photos, review labels, and complete role-owned detector/evaluator files.
7. Confirm complete data: `python scripts/validate_data.py --require-ready`.
8. Freeze the checked environment: `python -m pip freeze > requirements.txt`.
Do not copy someone else's .venv folder. Everyone builds their own environment.

## Folder map
- data/manifest.csv: 240 planned images; final 70:10:20 split at layout level.
- data/images/: add photos; data/labels/: 240 JSON annotation templates.
- data/raw_annotations/: original VIA or other tool exports, if used.
- configs/: method settings, shared CLAHE/timing settings, final-test checklist.
- detectors/: Role 2 and Role 3 implementations go here.
- evaluation/: Role 4 matching, metrics, and plot implementations go here.
- utils/: provided shared input, preprocessing, drawing, and metadata helpers.
- scripts/: data checks and all-four-configurations runner.
- docs/: format guide, capture procedure, machine record, run log, and demo checklist.
- reports/: report outlines, five member sections, figures, and presentation outline.
- references/: full citation templates.
- outputs/: generated predictions, marked images, and evaluation results.
- tests/: provided infrastructure checks; no course detection algorithm is implemented.

## Planned photos
Layouts 01-30 are separated; 31-40 are touching. Six photos per layout:
light/dark backgrounds crossed with diffuse/dim/directional lighting. Examples:
`data/images/layout01_light_diffuse.jpg`, `data/images/layout01_dark_directional.jpg`.
Use original images with consistent orientation and dimensions for both labels and detection.
Manifest allocation: development 28 layouts/168 photos, validation 4/24, test 8/48.
All six photos of a layout stay together. Verify these plans against actual collection.

## Detector and evaluator completion
Follow docs/data_formats.md. Both detectors expose detect(image, config, use_clahe=False).
Fill configs/hough.json and contours.json and mark implementation_ready true only when code works.
Role 4 implements matching.py and metrics.py before setting IMPLEMENTATION_READY true.
configs/common.json has proposed CLAHE settings (clip limit 2, grid 8x8), not tuned results.

## Run one method when ready
`python run.py --method hough --split development --clahe off --output outputs/dev_hough_off_01`
For a development-only pilot append `--limit 6`. It is explicitly marked as a pilot.
Change method to contours or CLAHE to on for the other configurations.
Output directories must be new. Fix inputs rather than overwriting past evidence.

## Run all four when ready
`python scripts/run_all.py --split development --output-root outputs/dev_comparison_01`
It creates hough_off, hough_on, contours_off, contours_on folders.
The same common settings and manifest split are used for each.

## Evaluate when Role 4 and labels are ready
`python evaluate.py --predictions outputs/dev_comparison_01/hough_off/predictions.json --output outputs/dev_comparison_01/hough_off/evaluation`
Repeat for all four folders. Evaluation will reject unfinished labels or unfinished metric code.
Role 4 uses evaluation/plots.py to create comparison figures after measurements exist.

## Timing and reproducibility
The runner times preprocessing plus detection, with image copying/loading, drawing, saving,
and evaluation excluded. Defaults are 3 warm-ups and 10 measured repeats per image.
Record the actual computer in docs/hardware.json and keep one computer for comparisons.
predictions.json records parameters, package-independent environment details, Git commit/changes,
per-image timings and medians. Record installed package versions with the run log.
Keep method parameters fixed between CLAHE-off/on comparisons.

## Final test
Use development photos for implementation, validation for choosing settings.
Before a final test, the group completes configs/final_test_approval.json with true statements,
an approver and date. Then use --split test for the runner. This is a checklist, not an
access-control system. Avoid examining test performance during development.
Report separated/touching results and note that the test photos represent eight layouts.

## Check the supplied infrastructure
`python -m unittest discover -s tests -v`
Checks use temporary synthetic data/mocked image operations. They do not prove that real
images, OpenCV detection algorithms, accuracy, or camera conditions work.

## Reports
The working template sets the progress deadline to November 22, 2026; final delivery is planned
for December 2. Each owner fills reports/sections/role_N.md. Role 5 combines and reviews these
with the group. Include complete sources for Hough, Otsu, contours, morphology, and CLAHE.
