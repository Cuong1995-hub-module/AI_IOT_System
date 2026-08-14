import cv2
from pathlib import Path


class FaceDetector:

    def __init__(self):

        model_path = (
            Path(__file__).parent
            / "models"
            / "face_detection_yunet_2026may.onnx"
        )

        self.detector = cv2.FaceDetectorYN.create(
            model=str(model_path),
            config="",
            input_size=(320, 320),
            score_threshold=0.8,
            nms_threshold=0.3,
            top_k=5000
        )

    def detect(self, frame):

        h, w = frame.shape[:2]

        self.detector.setInputSize((w, h))

        _, faces = self.detector.detect(frame)

        results = []

        if faces is not None:

            for face in faces:

                x, y, width, height = map(int, face[:4])

                results.append({
                    "bbox": (x, y, width, height),
                    "score": float(face[-1]),
                    "landmarks": face[:-1]   # Dùng cho SFace alignCrop()
                })

        return results

    def crop(self, frame, face):

        x, y, w, h = map(int, face["bbox"])

        return frame[y:y + h, x:x + w]