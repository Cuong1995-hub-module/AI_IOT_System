import cv2
import time

from ai.pipeline import FacePipeline
from camera.webcam import read

pipeline = FacePipeline()

error_reported = False


def gen_frames():

    global error_reported

    while True:

        success, frame = read()

        if not success:

            if not error_reported:
                print("[ERROR] Camera disconnected")
                error_reported = True

            time.sleep(0.1)
            continue

        error_reported = False

        # AI Pipeline
        frame = pipeline.process(frame)

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + buffer.tobytes() +
            b'\r\n'
        )