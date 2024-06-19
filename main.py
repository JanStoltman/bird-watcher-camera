#!/usr/bin/python3

import os
import shutil
import subprocess
import time

import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FileOutput


def convert_to_mp4(h_filename):
    print(f"Converting to mp4 {h_filename}")
    mp_filename = h_filename.replace(".h264", ".mp4")
    subprocess.run(f"MP4Box -add {h_filename} {mp_filename}")
    os.remove(h_filename)


def pre_start_cleanup():
    print("Cleaning up previous recordings")
    if os.path.exists("rec/"):
        shutil.rmtree("rec/")
    os.makedirs("rec/")


if __name__ == '__main__':
    lsize = (320, 240)
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(
        main={"size": (1280, 720), "format": "RGB888"},
        lores={"size": lsize, "format": "YUV420"}
    )

    picam2.configure(video_config)
    encoder = H264Encoder()
    picam2.start()

    w, h = lsize
    prev = None
    encoding = False
    ltime = 0
    filename = ""

    while True:
        cur = picam2.capture_buffer("lores")
        cur = cur[:w * h].reshape(h, w)
        if prev is not None:
            # Measure pixels differences between current and
            # previous frame
            mse = np.square(np.subtract(cur, prev)).mean()
            if mse > 6 or encoding and mse > 3:
                if not encoding:
                    filename = f"rec/{int(time.time())}.h264"
                    encoder.output = FileOutput(filename)
                    picam2.start_encoder(encoder, quality=Quality.VERY_HIGH)
                    encoding = True
                    print("New Motion", mse)
                ltime = time.time()
            else:
                if encoding and time.time() - ltime > 3.0:
                    picam2.stop_encoder()
                    encoding = False
                    print("Stopped encoding")
                    convert_to_mp4(filename)
        prev = cur
