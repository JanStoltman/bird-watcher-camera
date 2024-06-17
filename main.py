from picamera2 import Picamera2, Preview
import time
import cv2
import shutil

picam2 = Picamera2()
capture_config = picam2.create_still_configuration()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})

picam2.configure(preview_config)
picam2.start()

bird_cascade = cv2.CascadeClassifier("bird_model.xml")
face_cascade = cv2.CascadeClassifier("face_model.xml")
counter = 0

while True:
    time.sleep(2)
    print(".")
    imageArray = picam2.capture_array("main")

    birds = bird_cascade.detectMultiScale(imageArray, 1.1, 3)
    faces = face_cascade.detectMultiScale(imageArray,1.1, 3)

    if hasattr(birds, "size") and birds.size > 0:
        print("--------------------------- Bird detected!")
        imgName = "bird" + str(counter) + ".jpg"
        picam2.switch_mode_and_capture_file(capture_config, imgName)
        shutil.move(imgName, "pics/" + imgName)
        counter += 1 

    if hasattr(faces, "size") and faces.size > 0:
        print("Face detected!")
        # imgName = "face" + str(counter) + ".jpg"
        # picam2.switch_mode_and_capture_file(capture_config, imgName)
        # shutil.move(imgName, "pics/" + imgName)
        # counter += 1

    if counter >= 100:
        break
