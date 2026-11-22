# Executed mid-progress experiment

Date: November 22, 2026 (UTC timestamps retained in individual predictions).
Execution: automated from supplied project snapshot; group operator attribution pending.
Inputs: layouts 01-04 and 09-12, 48 photos, 420 circle annotations. See input_inventory.json.
Sources: original upload and the three later replacement VIA exports, retained in data/raw_annotations/.
Split: development 01/03/04/09/10/11; validation 02/12. All images are separated coins.
No final-test or touching images evaluated. No photos excluded from these available layouts.

Settings: outputs/development_settings/search.json records development-only candidate runs,
all selected image IDs and selection rule. Hough accumulator 65; contour circularity .50.
The same method settings were retained with CLAHE off/on. No post-validation tuning.
Common settings and selected configs are copied into outputs/midprogress/config_snapshot/.

Recorded runs: outputs/midprogress/{development,validation}/{hough_off,hough_on,contours_off,contours_on}/.
Each contains predictions.json, marked_images and evaluation/metrics.json.
All measured comparisons use identical image IDs within a split.
Labels were explicitly scored provisionally; independent human review and identities remain pending.

Timing: one OpenCV thread, 3 warm-ups and 10 timed repetitions per image.
Includes resize, preprocessing and detector; excludes disk I/O, visualization and scoring.
Hardware/software: docs/hardware.json and per-run environment; Linux execution machine,
not a group member's Mac. Versions in requirements.txt. No repository commit was available
in the uploaded working snapshot; docs/code_fingerprint.json records source hashes instead.

Results: reports/generated/summary.csv, per_image.csv, conditions.csv, contact.csv,
capture_groups.csv, results.json, RESULTS.md and plots. The report is generated from these measurements.
Interpretation: Hough-off has the strongest pilot F1; contour recall is lower;
CLAHE causes severe false circles for some dark/diffuse photos. See actual examples and masks.
Limitations: eight arrangements; only two validation layouts; no touching/test data;
labels unreviewed; different capture setups. No final generalization claim.
