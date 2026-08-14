import cv2

from .base import CameraBackend


class WindowsCameraBackend(CameraBackend):

    def __init__(self):

        self.camera = None
        self.current_camera = 0

        self.open_camera(0)

    # ==========================
    # Open Camera
    # ==========================

    def open_camera(self, index: int) -> bool:

        if self.camera is not None:
            self.camera.release()

        # CAP_DSHOW giúp mở camera ổn định hơn trên Windows
        cam = cv2.VideoCapture(index, cv2.CAP_DSHOW)

        if not cam.isOpened():
            return False

        self.camera = cam
        self.current_camera = index

        return True

    # ==========================
    # Current Camera
    # ==========================

    def get_current_camera(self):

        return self.current_camera

    # ==========================
    # Read Frame
    # ==========================

    def read(self):

        if self.camera is None:
            return False, None

        return self.camera.read()

    # ==========================
    # Release
    # ==========================

    def release(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None

    # ==========================
    # Camera List
    # ==========================

    def get_camera_list(self):

        cameras = []

        # Quét tối đa 10 camera
        for i in range(10):

            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

            if cap.isOpened():

                ret, _ = cap.read()

                if ret:

                    cameras.append({
                        "id": i,
                        "name": f"Camera {i}"
                    })

            cap.release()

        return cameras


backend = WindowsCameraBackend()
