import os
import cv2
import numpy as np

from ai.detector import FaceDetector
from ai.recognizer import FaceRecognizer
from database.sqlite import get_embeddings


# ==========================================
# CONFIG
# ==========================================

IMAGE_PATH = "checkins/tes2.jpg"


# ==========================================
# LOAD AI
# ==========================================

print("[TEST] Loading Face Detector...")

face_detector = FaceDetector()

print("[TEST] Loading Face Recognizer...")

face_recognizer = FaceRecognizer()


# ==========================================
# READ IMAGE
# ==========================================

print(
    f"[TEST] Reading image: {IMAGE_PATH}"
)

frame = cv2.imread(
    IMAGE_PATH
)

if frame is None:

    print(
        "[TEST] ERROR: Cannot read image"
    )

    raise SystemExit(1)


# ==========================================
# FACE DETECTION
# ==========================================

faces = face_detector.detect(
    frame
)

print(
    f"[TEST] Detected "
    f"{len(faces)} face(s)"
)

if len(faces) == 0:

    print(
        "[TEST] ERROR: No face detected"
    )

    raise SystemExit(1)


# ==========================================
# CREATE EMBEDDING
# ==========================================

face = faces[0]

embedding = face_recognizer.extract(
    frame,
    face
)

if embedding is None:

    print(
        "[TEST] ERROR: "
        "Failed to create embedding"
    )

    raise SystemExit(1)


embedding = embedding.flatten()

print(
    f"[TEST] Query embedding shape: "
    f"{embedding.shape}"
)


# ==========================================
# NORMALIZE QUERY
# ==========================================

query_norm = np.linalg.norm(
    embedding
)

if query_norm == 0:

    print(
        "[TEST] ERROR: "
        "Invalid query embedding"
    )

    raise SystemExit(1)


query_embedding = (
    embedding / query_norm
)


# ==========================================
# LOAD DATABASE EMBEDDINGS
# ==========================================

rows = get_embeddings()

print(
    f"[TEST] Database templates: "
    f"{len(rows)}"
)

if len(rows) == 0:

    print(
        "[TEST] ERROR: "
        "No face templates in database"
    )

    raise SystemExit(1)


# ==========================================
# MATCH
# ==========================================

best_similarity = -1.0

best_row = None

for row in rows:

    stored_embedding = np.frombuffer(
        row["embedding"],
        dtype=np.float32
    )

    if stored_embedding.shape != (128,):

        print(
            f"[TEST] WARNING: "
            f"Invalid embedding shape: "
            f"{stored_embedding.shape}"
        )

        continue

    stored_norm = np.linalg.norm(
        stored_embedding
    )

    if stored_norm == 0:

        continue

    stored_embedding = (
        stored_embedding / stored_norm
    )

    similarity = np.dot(
        query_embedding,
        stored_embedding
    )

    print(
        f"[TEST] "
        f"{row['uid']} - "
        f"{row['name']} "
        f"→ similarity = "
        f"{similarity:.4f}"
    )

    if similarity > best_similarity:

        best_similarity = similarity

        best_row = row


# ==========================================
# RESULT
# ==========================================

print()
print(
    "=============================="
)

if best_row is not None:

    print(
        f"[TEST] Best Match:"
    )

    print(
        f"[TEST] UID: "
        f"{best_row['uid']}"
    )

    print(
        f"[TEST] Name: "
        f"{best_row['name']}"
    )

    print(
        f"[TEST] Similarity: "
        f"{best_similarity:.4f}"
    )

else:

    print(
        "[TEST] No valid template found"
    )

print(
    "=============================="
)