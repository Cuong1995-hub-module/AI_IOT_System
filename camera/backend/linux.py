import cv2
import subprocess
import re
import time

from threading import Lock

from .base import CameraBackend


class LinuxCameraBackend(CameraBackend):

    def __init__(self):

        self.camera = None
        self.current_camera = 0

        self.lock = Lock()

        self.open_camera(0)

    def open_camera(self, index: int) -> bool:

        with self.lock:

            if self.camera is not None:

                self.camera.release()
                self.camera = None

                time.sleep(0.2)

            cam = cv2.VideoCapture(
                index,
                cv2.CAP_V4L2
            )

            if not cam.isOpened():
                return False

            self.camera = cam
            self.current_camera = index

            return True

    def get_current_camera(self):

        return self.current_camera

    def read(self):

        with self.lock:

            if self.camera is None:
                return False, None

        try:

            return self.camera.read()

        except Exception:

            return False, None

    def release(self):

        with self.lock:

            if self.camera is not None:

                self.camera.release()
                self.camera = None

    def get_camera_list(self):

        cameras = []

        try:

            output = subprocess.check_output(
                ["v4l2-ctl", "--list-devices"],
                text=True
            )

            blocks = output.strip().split("\n\n")

            for block in blocks:

                lines = block.splitlines()

                if not lines:
                    continue

                name = lines[0].split("(")[0].strip()

                for line in lines[1:]:

                    line = line.strip()

                    m = re.match(r"/dev/video(\d+)", line)

                    if m:

                        cameras.append({
                            "id": int(m.group(1)),
                            "name": name
                        })

                        break

        except Exception:

            # fallback
            for i in range(5):

                cap = cv2.VideoCapture(
                    i,
                    cv2.CAP_V4L2
                )

                if cap.isOpened():

                    cameras.append({
                        "id": i,
                        "name": f"Camera {i}"
                    })

                    cap.release()

        return cameras


backend = LinuxCameraBackend()