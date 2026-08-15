import cv2
import time
import socket
import requests
import threading
import os

from flask import Flask, Response


# ==========================================
# CONFIGURATION
# ==========================================

HOST = "0.0.0.0"

# Port của Camera Service
PORT = 8080

# Server Flask
SERVER_HOST = "sic-server.local"
SERVER_PORT = 5000
REGISTER_INTERVAL = 30
REGISTER_RETRY_INTERVAL = 5


# ==========================================
# CAMERA CONFIGURATION
# ==========================================
#sudo apt update
#sudo apt install v4l-utils
# Linux: Find your webcam device with:
#     ls -l /dev/v4l/by-id/
#
# Copy the returned camera path and paste it below.
# Example:
#     /dev/v4l/by-id/usb-Logitech_USB_Camera-video-index0
#
# Use /dev/v4l/by-id/ instead of /dev/video0
# because /dev/videoX may change between machines.

CAMERA_DEVICE = "/dev/v4l/by-id/usb-Logitech_USB_Camera-video-index0"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_FPS = 30

JPEG_QUALITY = 80


# ==========================================
# SERVER URL
# ==========================================

SERVER_URL = (
    f"http://{SERVER_HOST}:{SERVER_PORT}"
)


# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)


# ==========================================
# GET LOCAL IP
# ==========================================

def get_local_ip():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        # Không thực sự gửi dữ liệu.
        # Chỉ dùng để xác định interface/IP LAN.
        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]

    except Exception:

        ip = "127.0.0.1"

    finally:

        sock.close()

    return ip


# ==========================================
# REGISTER CAMERA TO SERVER
# ==========================================

def register_camera():

    camera_ip = get_local_ip()

    payload = {
        "ip": camera_ip,
        "port": PORT
    }

    url = (
        f"{SERVER_URL}/api/camera/register"
    )

    print()
    print(
        "[CAMERA] Registering camera..."
    )

    print(
        f"[CAMERA] Server: {SERVER_URL}"
    )

    print(
        f"[CAMERA] Local IP: {camera_ip}"
    )

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        if data.get("success"):

            print(
                "[CAMERA] Registration successful"
            )

            print(
                f"[CAMERA] IP: "
                f"{camera_ip}"
            )

            print(
                f"[CAMERA] Stream:"
                f" http://{camera_ip}:{PORT}/video_feed"
            )

            return True

        print(
            "[CAMERA] Registration rejected:"
        )

        print(data)

    except requests.RequestException as e:

        print(
            "[CAMERA] Registration failed:"
        )

        print(
            f"[CAMERA] {e}"
        )

    except Exception as e:

        print(
            "[CAMERA] Unexpected registration error:"
        )

        print(
            f"[CAMERA] {e}"
        )

    return False

# ==========================================
# CAMERA REGISTRATION HEARTBEAT
# ==========================================

def registration_loop():

    while True:

        print()
        print(
            "[CAMERA] Registration heartbeat..."
        )

        success = register_camera()

        if success:

            # Server đang hoạt động
            # Heartbeat bình thường mỗi 30 giây

            time.sleep(
                REGISTER_INTERVAL
            )

        else:

            # Server mất kết nối
            # Retry nhanh mỗi 5 giây

            print(
                "[CAMERA] Server unavailable."
            )

            print(
                "[CAMERA] Retrying in "
                f"{REGISTER_RETRY_INTERVAL} seconds..."
            )

            time.sleep(
                REGISTER_RETRY_INTERVAL
            )
# ==========================================
# FIND USB CAMERA
# ==========================================

def find_camera():

    print(
        f"[CAMERA] Opening configured device:"
        f" {CAMERA_DEVICE}"
    )

    # ==========================================
    # Check device exists
    # ==========================================

    if not CAMERA_DEVICE:
        print(
            "[CAMERA] CAMERA_DEVICE is not configured"
        )
        return None

    if not os.path.exists(CAMERA_DEVICE):

        print(
            f"[CAMERA] Device not found:"
            f" {CAMERA_DEVICE}"
        )

        return None

    # ==========================================
    # Open camera
    # ==========================================

    cap = cv2.VideoCapture(
        CAMERA_DEVICE,
        cv2.CAP_V4L2
    )

    if not cap.isOpened():

        print(
            f"[CAMERA] Cannot open:"
            f" {CAMERA_DEVICE}"
        )

        cap.release()

        return None

    # ==========================================
    # Configure camera
    # ==========================================

    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*"MJPG")
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    cap.set(
        cv2.CAP_PROP_FPS,
        FRAME_FPS
    )

    # ==========================================
    # Test frame
    # ==========================================

    ret, frame = cap.read()

    if not ret or frame is None:

        print(
            "[CAMERA] Camera opened but "
            "cannot read frame"
        )

        cap.release()

        return None

    # ==========================================
    # Read actual configuration
    # ==========================================

    actual_width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    actual_height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    actual_fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    # ==========================================
    # Success
    # ==========================================

    print(
        f"[CAMERA] Selected:"
        f" {CAMERA_DEVICE}"
    )

    print(
        f"[CAMERA] Resolution:"
        f" {actual_width}x{actual_height}"
    )

    print(
        f"[CAMERA] FPS:"
        f" {actual_fps}"
    )

    return cap


# ==========================================
# CAMERA INITIALIZATION
# ==========================================

camera = find_camera()


# ==========================================
# GENERATE MJPEG STREAM
# ==========================================

def generate_frames():

    global camera

    while True:

        # ----------------------------------
        # Camera disconnected / unavailable
        # ----------------------------------

        if camera is None:

            print(
                "[CAMERA] Camera unavailable. "
                "Retrying..."
            )

            time.sleep(2)

            camera = find_camera()

            continue

        # ----------------------------------
        # Read frame
        # ----------------------------------

        success, frame = camera.read()

        if not success:

            print(
                "[CAMERA] Failed to read frame"
            )

            camera.release()

            camera = None

            time.sleep(1)

            continue

        # ----------------------------------
        # Encode JPEG
        # ----------------------------------

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                JPEG_QUALITY
            ]
        )

        if not success:

            continue

        frame_bytes = buffer.tobytes()

        # ----------------------------------
        # MJPEG HTTP frame
        # ----------------------------------

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n"
            b"Content-Length: "
            + str(len(frame_bytes)).encode()
            + b"\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


# ==========================================
# STATUS PAGE
# ==========================================

@app.route("/")
def index():

    camera_status = (
        "CONNECTED"
        if camera is not None
        else "NOT CONNECTED"
    )

    camera_ip = get_local_ip()

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>
            SIC IoT Camera Service
        </title>

        <style>

            body {{
                background:#101828;
                color:white;
                font-family:Arial,sans-serif;
                text-align:center;
                padding:40px;
            }}

            .box {{
                max-width:700px;
                margin:auto;
                padding:30px;
                border-radius:20px;
                background:#18243a;
                box-shadow:0 20px 50px rgba(0,0,0,.4);
            }}

            h1 {{
                margin-bottom:10px;
            }}

            .status {{
                margin:20px 0;
                font-size:22px;
            }}

            a {{
                display:inline-block;
                margin-top:20px;
                padding:12px 20px;
                border-radius:10px;
                background:#2563eb;
                color:white;
                text-decoration:none;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>
                SIC IoT Camera Service
            </h1>

            <div class="status">
                Camera:
                <b>{camera_status}</b>
            </div>

            <p>
                Camera IP:
                {camera_ip}
            </p>

            <p>
                Resolution:
                {FRAME_WIDTH} × {FRAME_HEIGHT}
            </p>

            <p>
                Target FPS:
                {FRAME_FPS}
            </p>

            <p>
                MJPEG Quality:
                {JPEG_QUALITY}
            </p>

            <p>
                Server:
                {SERVER_HOST}:{SERVER_PORT}
            </p>

            <a href="/video_feed">
                Open Camera Stream
            </a>

        </div>

    </body>

    </html>
    """


# ==========================================
# VIDEO STREAM
# ==========================================

@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )
    )

# ==========================================
# CAPTURE SINGLE FRAME
# ==========================================

@app.route("/capture")
def capture():

    global camera

    if camera is None:

        return {
            "success": False,
            "message": "Camera not connected"
        }, 503

    success, frame = camera.read()

    if not success or frame is None:

        return {
            "success": False,
            "message": "Failed to capture frame"
        }, 500

    success, buffer = cv2.imencode(
        ".jpg",
        frame,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            JPEG_QUALITY
        ]
    )

    if not success:

        return {
            "success": False,
            "message": "Failed to encode image"
        }, 500

    return Response(
        buffer.tobytes(),
        mimetype="image/jpeg"
    )


# ==========================================
# HEALTH CHECK
# ==========================================

@app.route("/health")
def health():

    if camera is not None:

        return {
            "status": "ok",
            "camera": "connected",
            "resolution": (
                f"{FRAME_WIDTH}x{FRAME_HEIGHT}"
            ),
            "fps": FRAME_FPS
        }

    return {
        "status": "error",
        "camera": "not_connected"
    }, 503


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print()
    print(
        "======================================"
    )

    print(
        "      SIC IoT CAMERA SERVICE"
    )

    print(
        "======================================"
    )

    print(
        f"[SERVER] Camera Service:"
        f" {HOST}:{PORT}"
    )

    print(
        f"[SERVER] AI Server:"
        f" {SERVER_HOST}:{SERVER_PORT}"
    )

    # --------------------------------------
    # Register camera to Flask server
    # --------------------------------------

    # --------------------------------------
    # Register camera immediately
    # --------------------------------------

    register_camera()

    # --------------------------------------
    # Start registration heartbeat
    # --------------------------------------

    threading.Thread(
        target=registration_loop,
        daemon=True
    ).start()

    print()

    print(
    "[SERVER] Camera stream:"
)

    print(
        f"http://<CAMERA_IP>:{PORT}/video_feed"
    )

    print(
        "======================================"
    )

    print()

    app.run(
        host=HOST,
        port=PORT,
        threaded=True
    )
