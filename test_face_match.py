from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

results = model.predict(
    source="checkins/2026-08-17/73D63207.jpg",
    conf=0.25,
    device="cpu",
    save=True
)

for result in results:

    # In kết quả
    for box in result.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        name = model.names[cls]

        print(f"{name}: {conf:.2f}")

    # Ảnh đã được YOLO vẽ bounding box
    annotated = result.plot()

    cv2.imshow("YOLO Phone Detection", annotated)

    print("Nhan phim bat ky de dong anh...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()