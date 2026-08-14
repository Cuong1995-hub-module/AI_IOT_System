from ai.detector import FaceDetector
from ai.recognizer import FaceRecognizer
from ai.runtime import runtime
from ai.utils.draw import draw_faces


class FacePipeline:

    def __init__(self):
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()

    def process(self, frame):

        # Detect faces
        faces = self.detector.detect(frame)

        # Lưu dữ liệu realtime
        runtime.frame = frame.copy()
        runtime.faces = faces

        # Recognize each face
        for face in faces:

            result = self.recognizer.recognize(frame, face)

            face["label"] = result["name"]
            face["confidence"] = result["confidence"]

        # Draw result
        frame = draw_faces(frame, faces)

        return frame