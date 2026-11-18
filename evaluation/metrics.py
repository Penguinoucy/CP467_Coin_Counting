"""Role 4 implements metric computation using matching.py."""
IMPLEMENTATION_READY = False

def evaluate_records(prediction_records, labels_by_image_id):
    """Return {"per_image": [...], "summary": {...}, "by_contact": {...},
    "by_background_lighting": {...}} with real measured values only.
    Per-image output includes image_id, TP, FP, FN, predicted/true count,
    absolute count error, exact_count, and median_ms from the runner.
    Aggregate detection metrics from summed TP/FP/FN. Count MAE is mean
    absolute error; exact-count accuracy is the fraction counted correctly.
    Document undefined-metric handling. Include separated/touching breakdowns.
    """
    raise NotImplementedError("Role 4 must implement evaluation/metrics.py")
