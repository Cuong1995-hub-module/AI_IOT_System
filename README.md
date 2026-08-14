# AI-IoT Smart Access Control System

An AI-IoT Smart Access Control System that combines RFID authentication, camera-based face recognition, MQTT communication, and a web-based management dashboard for automated access control and attendance/check-in.

> **Sponsored by Samsung Vietnam**  
> **Developed at ICTU – Thai Nguyen University of Information and Communication Technology, Thai Nguyen, Vietnam**

---

## 1. Project Overview

The system combines embedded IoT devices, a central server, camera nodes, and AI-based face verification.

```text
RFID Card
    │
    ▼
ESP32-S3 + RC522
    │
    │ MQTT
    ▼
SIC Server (Flask)
    │
    ├── RFID validation
    ├── User management
    ├── Camera management
    ├── Face enrollment
    ├── Face recognition
    ├── Check-in / access logs
    └── Web Dashboard
            │
            ▼
       Camera Node
       USB Webcam
```

### Main Components

- **ESP32-S3 + RC522** — reads RFID card UIDs and communicates through MQTT.
- **SIC Server** — Flask-based central server responsible for system logic and APIs.
- **Camera Node** — Linux computer connected to a USB webcam, providing live video and image capture.
- **Face AI** — processes face images for enrollment and verification.
- **SQLite** — stores user information and access/check-in logs.
- **Web Interface** — provides administration, user management, dashboard, and employee check-in functions.

---

## 2. System Architecture

```text
                    LAN / Wi-Fi
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ESP32-S3          Camera Node       Admin PC
   + RC522           + Webcam          Browser
        │                │                │
        │ MQTT           │ HTTP           │ HTTP
        └──────────┬─────┴───────────────┘
                   ▼
             SIC Server
             Flask :5000
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     SQLite      Face AI    Web UI
```

The devices and server should normally be connected to the same LAN/Wi-Fi network.

---

## 3. Project Directory

```text
AI_IOT_System/
├── app.py
├── mqtt_server.py
├── requirements.txt
├── database/
├── ai/
├── camera/
├── static/
├── templates/
├── checkins/
├── faces/
├── esp32_smart/
├── test_db.py
├── test_face_match.py
└── test_logs.py
```

| Component | Purpose |
|---|---|
| `app.py` | Main Flask server and API |
| `mqtt_server.py` | MQTT/RFID processing |
| `database/` | SQLite database functions and data |
| `ai/` | Face AI processing |
| `camera/` | Camera-related code |
| `templates/` | HTML pages |
| `static/` | CSS and JavaScript |
| `faces/` | Face enrollment data |
| `checkins/` | Check-in images |

> Do not publish real face images, check-in images, database files, credentials, or other personal data in a public repository.

---

# 4. Requirements

The system is currently developed and tested on Linux.

Required software:

- Python 3
- pip
- Python `venv`
- SQLite3
- MQTT broker (Mosquitto)
- USB/network camera when using a Camera Node
- ESP32-S3 + RC522 for RFID operation

---

# 5. Install the SIC Server

Clone the repository:

```bash
git clone git@github.com:Cuong1995-hub-module/AI_IOT_System.git
cd AI_IOT_System
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

The server uses port:

```text
5000
```

Local access:

```text
http://127.0.0.1:5000
```

LAN access:

```text
http://sic-server.local:5000
```

---

# 6. MQTT / RFID

The system uses MQTT for communication between the ESP32-S3 RFID node and the SIC Server.

Default MQTT broker:

```text
127.0.0.1:1883
```

RFID topic:

```text
door/rfid
```

Door control topic:

```text
door/control
```

### RFID Flow

```text
RC522
  ↓
ESP32-S3
  ↓
MQTT
  ↓
door/rfid
  ↓
mqtt_server.py
  ↓
Validate UID
  ↓
OPEN / DENY
```

If the RFID UID is valid:

```text
door/control → OPEN
```

If the UID is invalid:

```text
door/control → DENY
```

Check Mosquitto:

```bash
sudo systemctl status mosquitto
```

Monitor RFID messages:

```bash
mosquitto_sub -h 127.0.0.1 -t door/rfid
```

---

# 7. Web Interface

## Admin Login

```text
/
```

The admin login protects the management functions.

## Dashboard

```text
/dashboard
```

Requires an authenticated admin session.

## User Management

```text
/users
```

Requires an authenticated admin session.

User management includes functions such as:

- Adding users
- Registering RFID cards
- Face enrollment
- Editing users
- Deleting users

## Employee Check-in

```text
/employee
```

The employee check-in interface is designed to be public within the local network and does not require administrator login.

---

# 8. Camera Node

The Camera Node is an independent service that can run on a Linux PC, laptop, or Raspberry Pi connected to a webcam.

The Camera Node requires:

- Python 3
- Flask
- OpenCV
- Requests
- USB webcam
- LAN/Wi-Fi connection to the SIC Server

Typical structure:

```text
SIC_CAMERA_NODE/
├── camera_service.py
├── requirements.txt
└── .venv/
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Install dependencies:

```bash
./.venv/bin/pip install -r requirements.txt
```

Start the service:

```bash
./.venv/bin/python camera_service.py
```

The Camera Node listens on:

```text
0.0.0.0:8080
```

---

# 9. Camera Endpoints

### Live Video

```text
/video_feed
```

Example:

```text
http://CAMERA_IP:8080/video_feed
```

### Capture Image

```text
/capture
```

Example:

```bash
curl http://CAMERA_IP:8080/capture -o camera.jpg
```

### Health Check

```text
/health
```

---

# 10. Automatic Camera Registration

The Camera Node automatically detects its own LAN IP address and registers itself with the SIC Server.

Registration endpoint:

```text
http://sic-server.local:5000/api/camera/register
```

Example architecture:

```text
Camera Node
192.168.1.30:8080
       │
       │ HTTP
       ▼
SIC Server
192.168.x.x:5000
```

The Camera Node does not require its own IP address to be hard-coded.

If the Camera Node receives a new IP address, it can register the new address automatically.

---

# 11. Camera Heartbeat and Automatic Reconnection

The Camera Node includes a registration heartbeat mechanism.

### Normal operation

The Camera Node re-registers every:

```text
30 seconds
```

### Server unavailable

When the SIC Server is temporarily unavailable, the Camera Node retries every:

```text
5 seconds
```

When the server becomes available again:

```text
Camera Node
    ↓
Registration successful
    ↓
Return to 30-second heartbeat
```

This allows the Camera Node to recover automatically after a temporary server restart or network interruption.

---

# 12. Test Camera Registration

From the SIC Server:

```bash
curl http://sic-server.local:5000/api/camera
```

Test image capture:

```bash
curl http://sic-server.local:5000/api/camera/test-capture \
    -o /tmp/server_camera.jpg
```

Check the resulting image:

```bash
file /tmp/server_camera.jpg
```

A successful result should identify the file as JPEG image data.

---

# 13. User and RFID Enrollment

Typical enrollment workflow:

```text
Admin Login
    ↓
Users
    ↓
Add User
    ↓
Scan RFID Card
    ↓
Enter User Information
    ↓
Capture Face
    ↓
Add Photo
    ↓
Capture Multiple Angles
    ↓
Finish Enrollment
```

Face images are organized by RFID UID.

Example:

```text
faces/BC6EF306/
├── 001_front.jpg
├── 002_left30.jpg
├── 003_right30.jpg
├── 004_up15.jpg
└── 005_down15.jpg
```

Verify an enrolled image:

```bash
file faces/<UID>/001_front.jpg
```

The result should identify the file as valid JPEG image data.

---

# 14. Face Enrollment

The web interface sends the captured images to:

```text
/api/faces/enroll
```

The server stores the images under the corresponding RFID UID and processes them through the face AI pipeline.

For reliable enrollment:

- Keep the face clearly visible.
- Avoid extreme lighting.
- Capture multiple angles.
- Keep the camera reasonably aligned with the user's face.
- Ensure the captured files are valid JPEG images.

---

# 15. Check-in Workflow

The complete check-in flow is:

```text
RFID Card
    ↓
RC522
    ↓
ESP32-S3
    ↓
MQTT
    ↓
SIC Server
    ↓
Validate RFID UID
    ↓
Camera Capture
    ↓
Face AI
    ↓
Face Matching
    ↓
APPROVED / REJECTED
    ↓
Save Check-in Log
```

If the RFID card is valid and the face matches the registered user:

```text
APPROVED
```

If the authentication fails:

```text
REJECTED
```

---

# 16. Database

The main SQLite database is:

```text
database/access.db
```

View today's logs:

```bash
sqlite3 ./database/access.db \
"SELECT * FROM logs WHERE date(time) = date('now','localtime');"
```

Delete today's logs for testing:

```bash
sqlite3 ./database/access.db \
"DELETE FROM logs WHERE date(time) = date('now','localtime');"
```

Verify:

```bash
sqlite3 ./database/access.db \
"SELECT * FROM logs WHERE date(time) = date('now','localtime');"
```

> Only use the delete command during testing. Do not use it on a production system if attendance history must be preserved.

---

# 17. RFID API Test

Get the latest RFID UID:

```bash
curl http://127.0.0.1:5000/api/last_uid
```

Example:

```json
{
  "uid": "BC6EF306"
}
```

If no UID is currently available:

```json
{
  "uid": ""
}
```

---

# 18. Troubleshooting

## Camera cannot open

Check available video devices:

```bash
ls /dev/video*
```

Check whether another process is using the webcam:

```bash
sudo fuser -v /dev/video0
```

## Port 8080 is already in use

```bash
sudo lsof -i :8080
```

or:

```bash
sudo ss -ltnp | grep :8080
```

## Camera Node cannot reach the server

Test hostname resolution/network connectivity:

```bash
ping sic-server.local
```

Test the server:

```bash
curl http://sic-server.local:5000/api/camera
```

## Server was restarted

The Camera Node should automatically reconnect using its heartbeat/retry mechanism.

Normal:

```text
30-second heartbeat
```

During failure:

```text
5-second retry
```

---

# 19. Git / Development Workflow

Check changes:

```bash
git status
```

Stage:

```bash
git add .
```

Commit:

```bash
git commit -m "Describe your changes"
```

Push:

```bash
git push
```

Do not commit:

```text
.venv/
.env
faces/
checkins/
database/access.db
__pycache__/
```

when they contain local runtime data, credentials, or personal information.

---

# 20. Deployment Model

The intended deployment model is:

```text
                    LAN / Wi-Fi
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ESP32-S3          Camera Node       Admin PC
   + RC522           + Webcam          Browser
        │                │                │
        │ MQTT           │ HTTP           │ HTTP
        └──────────┬─────┴───────────────┘
                   ▼
             SIC Server
             Flask :5000
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     SQLite      Face AI    Web UI
```

The Camera Node can be deployed independently from the main SIC Server.

Possible Camera Node platforms:

- Linux desktop
- Linux laptop
- Raspberry Pi

---

# 21. Planned Production Deployment

For permanent deployment, the Camera Node can be installed as a `systemd` service.

Target behavior:

```text
Linux Boot
    ↓
systemd
    ↓
Camera Service
    ↓
USB Webcam
    ↓
Port 8080
    ↓
Auto Registration
    ↓
30-second Heartbeat
    ↓
5-second Retry if Server is unavailable
```

This removes the need to manually run:

```bash
python camera_service.py
```

after every reboot.

---

# 22. Current System Status

- [x] RFID UID reading
- [x] MQTT communication
- [x] RFID validation
- [x] User management
- [x] RFID enrollment
- [x] Face enrollment
- [x] Camera Node
- [x] Live camera
- [x] Camera capture
- [x] Automatic camera registration
- [x] Camera heartbeat
- [x] Automatic reconnection
- [x] Face verification
- [x] Check-in logging
- [x] Admin authentication
- [x] Dashboard
- [x] Employee check-in interface
- [x] Git/GitHub version control

---

# 23. Project Repository

```text
https://github.com/Cuong1995-hub-module/AI_IOT_System
```

---

## Project Information

**Project:** AI-IoT Smart Access Control System  
**Sponsor:** Samsung Vietnam  
**Developed at:** ICTU – Thai Nguyen University of Information and Communication Technology  
**Location:** Thai Nguyen, Vietnam  
**Team:** SIC Nexus Embedded Team
Passcode ictu
---

**Sponsored by Samsung Vietnam · Developed at ICTU, Thai Nguyen, Vietnam**
