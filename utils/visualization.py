def draw_detections(image, coins):
    import cv2
    result=image.copy()
    for c in coins:
        xy=(round(c["x"]),round(c["y"]))
        if "radius" in c:
            cv2.circle(result,xy,max(1,round(c["radius"])),(0,255,0),2)
        cv2.circle(result,xy,4,(0,0,255),-1)
    cv2.putText(result,f"Count: {len(coins)}",(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    return result
