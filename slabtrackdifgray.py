import glob
import os
import shutil

import cv2
import numpy as np
import pandas as pd
#cap = cv2.VideoCapture("hotBox1.avi")
cap = cv2.VideoCapture("rtsp://10.50.119.124:554/axis-media/media.amp")
import plot_from_csv
import calculating_deviations
import datetime as dt
import matplotlib.pyplot as plt
from statistics import mean
from collections import deque
import pyarrow as pa
import pyarrow.parquet as pq


_,frame1 = cap.read()
cv2.imwrite("image.jpg",frame1)
g_kernel_h = cv2.getGaborKernel((3, 5), 5.0, np.pi, 5.0, 0.1, 0, ktype=cv2.CV_32F)
h, w = g_kernel_h.shape[:2]
g_kernel_h= cv2.resize(g_kernel_h, (8*w, 8*h), interpolation=cv2.INTER_CUBIC)
kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(45,45))
# cv2.imshow('gabor kernelh (resized)', g_kernel_h)

time = deque([0],1)
ylist = deque([0],2)
velocity = deque([0],1)
ymax = deque([0,0],19)
yymax =0
t=0


def slab_func():
    global yymax
    ret, frame = cap.read()

    img = np.ones((frame.shape[0], frame.shape[1]), dtype=np.uint8) * 20

    frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame1 = cv2.bitwise_or(frame1, img)

    frame1 = cv2.GaussianBlur(frame1, (5, 5), 5)
    thresh = cv2.inRange(frame1, 210, 255)

    thresh = cv2.filter2D(thresh, cv2.CV_8UC3, g_kernel_h)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = thresh[:, 230:370]
    frame1 = frame1[:, 230:370]
    frame = frame[:, 230:370]

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.001 * cv2.arcLength(cnt, True), True)
        rect = cv2.minAreaRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        box = cv2.boxPoints(rect)
        center = rect[0]
        area = cv2.contourArea(cnt)
        box = np.intp(box)
        if (len(approx) > 5) & (area > 100):
            # cv2.circle(frame,(int(center[0]),int(center[1])), 20,(255,0,0),2)
            cv2.circle(frame, (int(center[0]), int(center[1])), 2, (255, 0, 255), 2)
            cv2.drawContours(frame, [box], 0, (255, 255, 0), 3)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (int(x + w / 2), int(y + h - 20)), 2, (0, 0, 255), 5)
            yy = int(y + h - 20)
            ymax.append(yy)
        yymax = mean(ymax)

    cv2.imshow('Frame', frame)
    cv2.imshow('Frame1', frame1)
    cv2.imshow('thresh', thresh)
    cv2.waitKey(1)
    # t += 1
    # time.append(t)
    ylist.append(yymax)
    if len(ylist) > 1:
        vel = (ylist[-1] - ylist[-2])
        velocity.append(vel)
    a = mean(ylist)
    b = mean(velocity)
    name_curtime = c[:10] + "_" + c[11:13] + "_" + c[14:15]

    name_dir = f'Data_tracking_csv_{c[8:10]}'
    filename = f'slabdata{name_curtime}.csv'
    name_dir_parquet = f'Data_tracking_parquet_{c[8:10]}'
    filename_parquet = f'slabdata{name_curtime}.parquet'
    if not os.path.exists(name_dir):
        os.mkdir(name_dir)
    fullname = os.path.join(name_dir, filename)
    if not os.path.exists(name_dir_parquet):
        os.mkdir(name_dir_parquet)
    fullname_parquet = os.path.join(name_dir_parquet, filename_parquet)

    slabdata = pd.DataFrame([[a, b, c]], columns=['ylist', 'velocity', 'current time'])

    slabdata.to_csv(fullname, mode='a', index=False)


while True:
    curtime = dt.datetime.now()
    c=str(curtime)

    if int(c[11:13]) == 16 or int(c[11:13]) == 17 or int(c[11:13]) == 18:
        slab_func()

    elif int(c[11:13]) == 19 and int(c[14:16]) == 0 and int(c[17:19]) == 5:
        plot_from_csv.start()
        calculating_deviations.deviation()
        print(f'Файлы от {c[:10]} загружены в необходимые директории')
