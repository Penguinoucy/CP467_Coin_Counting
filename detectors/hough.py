"""Role 2 implements this detector. An unfinished detector must never return fake results."""

def detect(image, config, use_clahe=False):
    """Return [{"x": float, "y": float, "radius": float (optional)}].

    image: OpenCV BGR uint8 image in original analysis-image coordinates.
    config: method JSON dictionary plus config["common"] from common.json.
    Include grayscale conversion, optional CLAHE, smoothing, and detection here.
    Use utils.preprocessing.prepare_gray for the agreed CLAHE step if helpful.
    Do not load files, draw/save results, or read correct coin labels here.
    If resizing internally, map detections back to the input coordinates.
    Return [] only when a completed detector actually finds no coins.
    """
    raise NotImplementedError("Role 2 must implement detectors/hough.py")
