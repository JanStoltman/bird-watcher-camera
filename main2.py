#!/usr/bin/python3

import time

import numpy as np
import os
import shutil

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FileOutput

if os.path.exists("rec/"):
    shutil.rmtree("rec/")

os.makedirs("rec/")

lsize = (320, 240)
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"},
                                                 lores={"size": lsize, "format": "YUV420"})
picam2.configure(video_config)
encoder = H264Encoder()
picam2.start()

w, h = lsize
prev = None
encoding = False
ltime = 0

while True:
    cur = picam2.capture_buffer("lores")
    cur = cur[:w * h].reshape(h, w)
    if prev is not None:
        # Measure pixels differences between current and
        # previous frame
        mse = np.square(np.subtract(cur, prev)).mean()
        if mse > 8:
            if not encoding:
                encoder.output = FileOutput(f"rec/{int(time.time())}.h264")
                picam2.start_encoder(encoder, quality = Quality.VERY_HIGH)
                encoding = True
                print("New Motion", mse)
            ltime = time.time()
        else:
            if encoding and time.time() - ltime > 2.0:
                picam2.stop_encoder()
                encoding = False
                print("Stopped encoding")
    prev = cur
