# Role 4 implementation checklist
Implement matching.py, metrics.py, and plots.py. Set IMPLEMENTATION_READY in metrics.py
only when the first two are checked. evaluate.py already loads reviewed labels and
checks image IDs, dimensions, split membership, and completeness of non-pilot runs.

Match one-to-one within half the labelled radius. Maximize the number of valid pairs,
then minimize total centre distance among equal-size pairings. Avoid greedy matching.
Check duplicates, no detections, and a pairing where greedy matching loses a valid match.
Report TP/FP/FN, precision/recall/F1, count MAE, exact-count accuracy, and sample sizes.
Aggregate detection metrics from summed counts. State zero-denominator handling.
Provide touching/separated and lighting/background breakdowns, plus timing summaries.
Write plots only from actual evaluated files and compare the same image IDs across all four runs.
Targets apply to separated test coins: F1 >= 0.90, MAE <= 0.5, exact-count accuracy >= 80%.
These targets are goals, not measured results. Development results are preliminary.
Document finalized output keys here after implementing the common interface.
