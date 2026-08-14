import cv2
from pathlib import Path


class FaceRecognizer:

    def __init__(self):

        model_path = (
            Path(__file__).parent
            / "models"
            / "face_recognition_sface_2021dec.onnx"
        )

        self.recognizer = cv2.FaceRecognizerSF.create(
            model=str(model_path),
            config=""
        )

        print("[INFO] Face Recognizer Ready")

    def extract(self, frame, face):

        aligned = self.recognizer.alignCrop(
            frame,
            face["landmarks"]
        )

        embedding = self.recognizer.feature(aligned)

        return embedding

    def recognize(self, frame, face):

        embedding = self.extract(frame, face)

        return {
            "name": "Unknown",
            "confidence": 0.0,
            "embedding": embedding
        }