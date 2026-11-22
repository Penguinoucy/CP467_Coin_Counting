"""Global Otsu + morphology + external contours. No label/filename-dependent rules."""
import math
import cv2
import numpy as np
from utils.preprocessing import analysis_image,prepare_gray

def process(image,config,use_clahe=False):
    frame,sx,sy=analysis_image(image,config['common']);p=config['parameters']
    gray=prepare_gray(frame,config['common'],use_clahe)
    smooth=cv2.GaussianBlur(gray,(int(p['blur_kernel']),)*2,float(p['blur_sigma']))
    threshold,mask=cv2.threshold(smooth,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    band=max(1,round(min(mask.shape)*p['border_fraction']))
    border=np.concatenate([mask[:band].ravel(),mask[-band:].ravel(),mask[band:-band,:band].ravel(),mask[band:-band,-band:].ravel()])
    if np.count_nonzero(border)>border.size/2:mask=cv2.bitwise_not(mask)
    initial=mask.copy()
    for op,name in [(cv2.MORPH_OPEN,'open_kernel'),(cv2.MORPH_CLOSE,'close_kernel')]:
        k=int(p[name])
        if k>1:mask=cv2.morphologyEx(mask,op,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    short=min(mask.shape);lo=math.pi*(short*p['min_radius_fraction'])**2;hi=math.pi*(short*p['max_radius_fraction'])**2
    coins=[];accepted=[]
    for contour in contours:
        area=cv2.contourArea(contour);perimeter=cv2.arcLength(contour,True)
        if perimeter<=0 or not lo<=area<=hi or 4*math.pi*area/perimeter**2<p['min_circularity']:continue
        x,y,w,h=cv2.boundingRect(contour)
        if x<=0 or y<=0 or x+w>=mask.shape[1] or y+h>=mask.shape[0]:continue
        m=cv2.moments(contour)
        if m['m00']<=0:continue
        coins.append({'x':float(m['m10']/m['m00']/sx),'y':float(m['m01']/m['m00']/sy)});accepted.append(contour)
    outline=frame.copy();cv2.drawContours(outline,accepted,-1,(0,255,0),2)
    return sorted(coins,key=lambda c:(c['y'],c['x'])),{'gray':gray,'threshold_mask':initial,'clean_mask':mask,'accepted_contours':outline,'otsu_threshold':float(threshold)}

def detect(image,config,use_clahe=False):return process(image,config,use_clahe)[0]

def diagnostics(image,config,use_clahe=False):return process(image,config,use_clahe)[1]
