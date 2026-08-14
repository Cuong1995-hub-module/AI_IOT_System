import cv2


def draw_faces(frame, faces):

    for face in faces:

        x, y, w, h = map(int, face["bbox"])

        label = face.get("label", "FACE")

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    return frame