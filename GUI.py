# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#-*- coding: utf-8 -*-
import cv2
#import numpy as np
 
def nothing(x):
     pass

img = cv2.imread('f1.jpg',1)
res=cv2.resize(img,None,fx=0.2, fy=0.2,interpolation = cv2.INTER_CUBIC)
#img = np.zeros((300,512,3), np.uint8)
cv2.namedWindow('image',cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('smile','image',0,10,nothing)
cv2.createTrackbar('eyes','image',0,10,nothing)
switch = 'ON/OFF'
cv2.createTrackbar(switch, 'image',0,1,nothing)
 
while(1):
    r = cv2.getTrackbarPos('smile','image')
    g = cv2.getTrackbarPos('eyes','image')
    s = cv2.getTrackbarPos(switch,'image')
    cv2.imshow('image',res)
    k = cv2.waitKey(0) & 0xFF
    if k == 27:
        break
    if s == 0:
        img[:] = 0
      
cv2.destroyAllWindows()