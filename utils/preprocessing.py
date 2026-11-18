"""Shared grayscale and CLAHE helper; detector owners add their own smoothing."""
def prepare_gray(image, common, use_clahe=False):
    import cv2
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if use_clahe:
        settings = common["clahe"]
        gray = cv2.createCLAHE(
            clipLimit=float(settings["clip_limit"]),
            tileGridSize=tuple(settings["tile_grid_size"]),
        ).apply(gray)
    return gray
