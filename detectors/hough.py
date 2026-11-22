"""Image-only gradient Hough baseline; returns original-image coordinates."""
import cv2
import numpy as np
from utils.preprocessing import analysis_image,prepare_gray

def process(image,config,use_clahe=False):
    frame,sx,sy=analysis_image(image,config['common']);p=config['parameters']
    gray=prepare_gray(frame,config['common'],use_clahe)
    smooth=cv2.GaussianBlur(gray,(int(p['blur_kernel']),)*2,float(p['blur_sigma']))
    short=min(smooth.shape)
    circles=cv2.HoughCircles(smooth,cv2.HOUGH_GRADIENT,dp=float(p['dp']),minDist=short*p['min_distance_fraction'],
        param1=float(p['edge_threshold']),param2=float(p['accumulator_threshold']),
        minRadius=max(1,round(short*p['min_radius_fraction'])),maxRadius=round(short*p['max_radius_fraction']))
    coins=[]
    if circles is not None:
        for x,y,rad in np.asarray(circles[0],dtype=float):
            if 0<=x/sx<image.shape[1] and 0<=y/sy<image.shape[0]:
                coins.append({'x':float(x/sx),'y':float(y/sy),'radius':float(rad/((sx+sy)/2))})
    return sorted(coins,key=lambda c:(c['y'],c['x'])),gray,smooth

def detect(image,config,use_clahe=False):return process(image,config,use_clahe)[0]

def diagnostics(image,config,use_clahe=False):
    _,gray,smooth=process(image,config,use_clahe);edge=config['parameters']['edge_threshold']
    return {'gray':gray,'smoothed':smooth,'edges':cv2.Canny(smooth,edge/2,edge)}
