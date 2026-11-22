# File formats and shared rules
## Manifest
The seven columns in data/manifest.csv match run.py. Paths are relative to this folder.
Layout IDs 01-30 are planned as separated; 31-40 are planned as touching.
Each layout has light/dark backgrounds crossed with diffuse/dim/directional light.
Splits were shuffled within contact groups using seed 467, then fixed in the manifest.
Development: 21 separated + 7 touching layouts; validation: 3 + 1; test: 6 + 2.
These are planned conditions, not claims about photographs already collected.
Name photos exactly as listed, or update their paths and metadata before running.
Keep layout identity and all six conditions together. The manifest owns split membership.
Do not create another independently edited split file.

## Correct labels
This handoff includes 48 complete pilot labels in data/labels/.
The 192 unused templates are omitted to protect teammates' newer labels.
Complete: image_width, image_height, coin_count, annotator, reviewer, coins.
The coins list uses objects such as {"x": 320.0, "y": 180.0, "radius": 42.0}.
These example numbers explain the format; they are not labels for any real image.
Coordinates refer to the exact original image loaded by run.py. Check orientation/crops.
coin_count must equal the list length. Change annotation_status to complete after labelling,
and review_status to reviewed only after a different member checks the image.
null means unfinished. Do not replace null with an empty list to bypass a missing annotation.
Use [] and count 0 only for an actual verified image containing no coins.
If using VIA, keep the original export in raw_annotations/ and convert it to this format.
scripts/convert_via_labels.py supplies the converter for the circle VIA exports used here.
All 48 converted labels preserve geometry. Missing annotator/reviewer identities remain null.
For provisional analysis only, evaluate.py --allow-unreviewed-labels permits complete labels
without named review; it records provisional_unreviewed and never modifies review fields.

## Detector input and output
Both detector functions are detect(image, config, use_clahe=False).
image is an OpenCV BGR image. config contains parameters and the common settings.
Return a list of dictionaries with numeric x/y and optional positive radius.
Coordinates must refer to the original input image even if you resize internally.
Do not include label access, file loading, drawing, saving, or evaluation inside detect().
Use utils.preprocessing.prepare_gray for consistent grayscale and optional CLAHE if desired.
Add method-specific smoothing inside each detector, after the common CLAHE step.
Draw centre dots for both methods; a contour detector need not invent a circle radius.

## Prediction and evaluation files
run.py creates outputs/<run>/predictions.json and marked_images/.
Predictions include original manifest metadata, dimensions, detected centres, counts,
per-image repeated timings, settings, and environment information. No accuracy is implied.
evaluate.py validates label readiness and calls evaluation.metrics.evaluate_records.
Evaluation returns per_image, summary, by_contact, and by_background_lighting fields.
Exact keys and undefined-metric choices are documented in evaluation/README.md.
Only actual completed runs may produce metrics; empty templates are never scored.
