import numpy as np

from ai.recognizer import FaceRecognizer

from database.sqlite import (
    check_uid,
    save_embedding,
    delete_embeddings
)


class FaceEnrollment:

    def __init__(self):

        self.recognizer = FaceRecognizer()

    def enroll(self, frame, face, uid):

        user = check_uid(uid)

        if user is None:
            return False

        embedding = self.recognizer.extract(frame, face)

        embedding = embedding.flatten().astype(np.float32)

        # Remove old embedding if exists
        delete_embeddings(user["id"])

        # Save new embedding
        save_embedding(
            user_id=user["id"],
            embedding=embedding.tobytes()
        )

        return True