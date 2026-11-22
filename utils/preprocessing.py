import cv2

def analysis_image(image, common):
    h,w=image.shape[:2]; scale=min(1.0, common.get('max_side',1200)/max(h,w))
    frame=cv2.resize(image,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_AREA) if scale<1 else image
    return frame,frame.shape[1]/w,frame.shape[0]/h

def prepare_gray(image,common,use_clahe=False):
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    if use_clahe:
        p=common['clahe'];gray=cv2.createCLAHE(clipLimit=float(p['clip_limit']),tileGridSize=tuple(p['tile_grid_size'])).apply(gray)
    return gray
