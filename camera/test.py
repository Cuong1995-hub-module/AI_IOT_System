import cv2

cap = cv2.VideoCapture(0)

print("Opened:", cap.isOpened())

while True:

    ret, frame = cap.read()

    print("Read:", ret)

    if not ret:
        break

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()