# Implemented evaluation

Matching uses SciPy linear_sum_assignment with dummy columns and bounded costs. Only pairs
within 0.5 times each ground-truth radius are valid. Costs first maximize valid pair count,
then minimize total Euclidean centre distance. Distances use original-image pixels.

metrics.json contains metadata and results: per_image, summary, by_contact,
by_background_lighting, by_arrangement, and by_capture_group. Per-image records include
TP/FP/FN, matched indices, unmatched indices, true/predicted counts, absolute count error,
exact_count, and median_ms. Summary/group records include sample sizes, summed counts,
precision/recall/F1, count_mae, exact_count_accuracy and median_ms.

Detection metrics use summed TP/FP/FN, not averages of per-image percentages.
For an evaluated group, a zero metric denominator gives 0. An absent group is
not_evaluated with null scores. Timing is the median of per-image medians.
Count agreement alone does not establish correct detection (FP and FN can cancel).

Strict evaluation requires completed independently reviewed labels. The explicit
--allow-unreviewed-labels option permits provisional scoring with a recorded warning;
it does not alter labels or bypass geometry/count/dimension checks.

The saved pilot has 36 development and 12 validation photos. Settings were selected only
on development photos. No touching or final-test photos have been evaluated.
Proposal targets (separated final-test F1 >= .90, MAE <= .5, exact-count >= 80%) remain
GOALS. They are not acceptance claims based on this small pilot.
