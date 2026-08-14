import cv2
import numpy as np

from ai.detector import FaceDetector
from ai.recognizer import FaceRecognizer


FACE_THRESHOLD = 0.60


class FaceMatcher:

    def __init__(self):

        print("[AI] Loading Face Detector...")

        self.detector = FaceDetector()

        print("[AI] Loading Face Recognizer...")

        self.recognizer = FaceRecognizer()

        print("[AI] Face Matcher Ready")

    def get_embedding(self, image_path):

        frame = cv2.imread(image_path)

        if frame is None:
            print(
                f"[AI] Cannot read image: "
                f"{image_path}"
            )
            return None

        faces = self.detector.detect(frame)

        print(
            f"[AI] Detected "
            f"{len(faces)} face(s)"
        )

        if len(faces) == 0:
            return None

        # Chỉ lấy khuôn mặt đầu tiên
        face = faces[0]

        embedding = self.recognizer.extract(
            frame,
            face
        )

        if embedding is None:
            return None

        embedding = embedding.flatten()

        norm = np.linalg.norm(
            embedding
        )

        if norm == 0:
            return None

        return embedding / norm

    def compare(
        self,
        query_embedding,
        stored_embedding
    ):

        stored_embedding = np.asarray(
            stored_embedding,
            dtype=np.float32
        ).flatten()

        norm = np.linalg.norm(
            stored_embedding
        )

        if norm == 0:
            return 0.0

        stored_embedding = (
            stored_embedding / norm
        )

        similarity = np.dot(
            query_embedding,
            stored_embedding
        )

        return float(similarity)

    def match(
        self,
        image_path,
        stored_embedding
    ):

        query_embedding = self.get_embedding(
            image_path
        )

        if query_embedding is None:

            return {
                "result": "NO_FACE",
                "similarity": 0.0
            }

        similarity = self.compare(
            query_embedding,
            stored_embedding
        )

        result = (
            "MATCH"
            if similarity >= FACE_THRESHOLD
            else "MISMATCH"
        )

        print(
            f"[AI] Similarity: "
            f"{similarity:.4f}"
        )

        print(
            f"[AI] Result: "
            f"{result}"
        )

        return {
            "result": result,
            "similarity": similarity
        }

if __name__ == "__main__":

    from database.sqlite import get_embeddings

    image_path = (
        "checkins/73D63207_20260812_170107.jpg"
    )

    rows = get_embeddings()

    row = rows[0]

    stored_embedding = np.frombuffer(
        row["embedding"],
        dtype=np.float32
    )

    matcher = FaceMatcher()

    result = matcher.match(
        image_path,
        stored_embedding
    )

    print()
    print("==============================")
    print("[TEST] UID:", row["uid"])
    print("[TEST] Name:", row["name"])
    print(
        "[TEST] Similarity:",
        f"{result['similarity']:.4f}"
    )
    print(
        "[TEST] Result:",
        result["result"]
    )
    print("==============================")