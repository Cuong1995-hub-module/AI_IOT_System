# Standard Library
import csv
import io
import subprocess
import os
import base64
from ai.face_match import FaceMatcher
# Third-party
from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    send_from_directory
)
from ai.runtime import runtime
from ai.enrollment import FaceEnrollment
import cv2
import numpy as np
from ai.detector import FaceDetector
from ai.recognizer import FaceRecognizer

# Local
import mqtt_server
from camera.stream import gen_frames
from camera.webcam import (
    get_camera_list,
    open_camera,
)
from database.sqlite import (
    add_user,
    check_uid,
    delete_user,
    save_embedding,
    export_logs_by_date,
    get_all_users,
    get_denied_today,
    get_logs,
    get_logs_by_date,
    get_verified_today,
    update_user,
    approve_log,
    save_log,
    reject_log,
    get_embedding_by_uid,
)
from mqtt_server import start_mqtt


app = Flask(__name__)
app.secret_key = "sic_2026"
enrollment = FaceEnrollment()
face_detector = FaceDetector()
face_recognizer = FaceRecognizer()
face_matcher = FaceMatcher()

def get_local_ip():
    return subprocess.check_output(
        "hostname -I",
        shell=True
    ).decode().split()[0]


LOCAL_IP = get_local_ip()


# ================= LOGIN =================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == "ictu":
            session["login"] = True
            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Incorrect System Access Key"
        )

    return render_template("login.html")


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if not session.get("login"):
        return redirect("/")

    logs = get_logs(20)
    users = get_all_users()
    verified = get_verified_today()
    denied = get_denied_today()

    return render_template(
        "dashboard.html",
        ip=LOCAL_IP,
        logs=logs,
        users=users,
        verified=verified,
        denied=denied
    )


# ================= USERS =================

@app.route("/users")
def users():

    if not session.get("login"):
        return redirect("/")

    users = get_all_users()

    return render_template(
        "users.html",
        users=users
    )

@app.route("/employee")
def employee():
    return render_template("employee.html")
# ================= API =================
@app.route("/api/cameras")
def api_cameras():

    if not session.get("login"):
        return jsonify([])

    return jsonify(get_camera_list())

@app.route("/api/camera/select", methods=["POST"])
def api_camera_select():

    if not session.get("login"):
        return jsonify({
            "success": False
        }), 401

    data = request.get_json()

    camera_id = int(data.get("camera", 0))

    if open_camera(camera_id):

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False,
        "message": "Cannot open camera."
    }), 400

@app.route("/api/logs")
def api_logs():

    if not session.get("login"):
        return jsonify([])

    date = request.args.get("date")

    if date:
        logs = get_logs_by_date(date)
    else:
        logs = get_logs(20)

    return jsonify([
        {
            "id": log["id"],

            "uid": log["uid"],

            "name": log["name"],

            "ai_result": log["ai_result"],

            "admin_result": log["admin_result"],

            "time": log["time"],

            "image": log["image_path"],

            "similarity": log["similarity"]
        }
        for log in logs
    ])

@app.route("/api/last_uid")
def api_last_uid():

    if not session.get("login"):
        return jsonify({"uid": ""})

    uid = mqtt_server.last_uid or ""

    print("API SEND:", uid)

    mqtt_server.last_uid = None

    return jsonify({"uid": uid})
CHECKIN_DIR = os.path.join(
    "checkins"
)

os.makedirs(
    CHECKIN_DIR,
    exist_ok=True
)
@app.route("/api/checkin/pending")
def api_checkin_pending():

    uid = mqtt_server.pending_uid

    if not uid:

        return jsonify({
            "uid": "",
            "name": ""
        })

    user = check_uid(uid)

    if user is None:

        return jsonify({
            "uid": uid,
            "name": "Unknown"
        })

    return jsonify({
        "uid": uid,
        "name": user[2]
    })

@app.route("/checkins/<path:filename>")
def serve_checkin_image(filename):
    return send_from_directory(
        CHECKIN_DIR,
        filename
    )

@app.route("/faces/<uid>/001_front.jpg")
def serve_registered_face(uid):

    face_dir = os.path.join(
        "faces",
        uid
    )

    return send_from_directory(
        face_dir,
        "001_front.jpg"
    )

@app.route("/api/checkin", methods=["POST"])
def api_checkin():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    uid = data.get("uid")
    image = data.get("image")


    # =========================
    # CHECK DATA
    # =========================

    if not uid:

        return jsonify({
            "success": False,
            "message": "Missing UID"
        }), 400

    if not image:

        return jsonify({
            "success": False,
            "message": "Missing image"
        }), 400

    # =========================
    # CHECK USER
    # =========================

    user = check_uid(uid)

    if user is None:

        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # =========================
    # DECODE IMAGE
    # =========================

    try:

        if "," in image:

            image = image.split(
                ",",
                1
            )[1]

        image_bytes = base64.b64decode(
            image
        )

    except Exception as e:

        print(
            "[CHECK IN] Image decode error:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Invalid image data"
        }), 400

    # =========================
    # CREATE FILE NAME
    # =========================

    from datetime import datetime

    now = datetime.now()

    filename = (
        f"{uid}_"
        f"{now.strftime('%Y%m%d_%H%M%S')}"
        f".jpg"
    )

    image_path = os.path.join(
        CHECKIN_DIR,
        filename
    )

    # =========================
    # SAVE IMAGE
    # =========================

    try:

        with open(
            image_path,
            "wb"
        ) as file:

            file.write(
                image_bytes
            )

    except Exception as e:

        print(
            "[CHECK IN] Image save error:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Failed to save image"
        }), 500

    print(
        f"[CHECK IN] Image saved: "
        f"{image_path}"
    )
        # =========================
    # AI FACE VERIFICATION
    # =========================

    stored = get_embedding_by_uid(uid)

    if stored is None:

        print(
            f"[AI] No embedding found for UID: {uid}"
        )

        ai_result = "NO_TEMPLATE"
        similarity = 0.0

    else:

        stored_embedding = np.frombuffer(
            stored["embedding"],
            dtype=np.float32
        )

        ai_result_data = face_matcher.match(
            image_path,
            stored_embedding
        )

        ai_result = ai_result_data["result"]
        similarity = ai_result_data["similarity"]

    print(
        f"[AI] UID: {uid} "
        f"Result: {ai_result} "
        f"Similarity: {similarity:.4f}"
    )
    # =========================
    # CREATE CHECK-IN LOG
    # =========================

    save_log(
        uid,
        user["name"],
        ai_result,
        image_path,
        similarity
    )

    print(
        f"[CHECK IN] Log saved: "
        f"{uid} - {user['name']}"
    )

    # =========================
    # CLEAR PENDING UID
    # =========================

    mqtt_server.pending_uid = None

    print(
        "[CHECK IN] Pending UID cleared"
    )

    return jsonify({

        "success": True,

        "message":
        "Check-in image saved",

        "uid": uid,

        "image": image_path,

        "ai_result": ai_result,

        "similarity": similarity

    })
# ================= ADD USER =================
@app.route("/api/users", methods=["POST"])

def api_add_user():

    if not session.get("login"):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = request.get_json()

    uid = data.get("uid", "").strip()
    name = data.get("name", "").strip()

    if not uid:
        return jsonify({
            "success": False,
            "message": "UID is required"
        })

    if not name:
        return jsonify({
            "success": False,
            "message": "Name is required"
        })

    if check_uid(uid):
        return jsonify({
            "success": False,
            "message": "UID already exists"
        })

    add_user(uid, name)

    return jsonify({
        "success": True
    })

@app.route("/api/users/delete", methods=["POST"])
def api_delete_user():

    if not session.get("login"):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = request.get_json()

    uid = data.get("uid", "").strip()

    if not uid:
        return jsonify({
            "success": False,
            "message": "UID is required."
        })

    if not check_uid(uid):
        return jsonify({
            "success": False,
            "message": "User not found."
        })

    delete_user(uid)

    return jsonify({
        "success": True
    })
@app.route("/api/users/update", methods=["POST"])
def api_update_user():

    if not session.get("login"):
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    data = request.get_json()

    uid = data.get("uid", "").strip()
    name = data.get("name", "").strip()

    if not uid or not name:
        return jsonify({
            "success": False,
            "message": "UID and name are required."
        }), 400

    if not check_uid(uid):
        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    if update_user(uid, name):
        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False,
        "message": "Update failed."
    }), 500

@app.route("/api/logs/export")
def export_logs():

    date = request.args.get("date")

    logs = export_logs_by_date(date)

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "UID",
        "Employee",
        "AI Result",
        "Admin Result",
        "Time"
    ])

    for log in logs:

        writer.writerow([
            log["uid"],
            log["name"],
            log["ai_result"],
            log["admin_result"],
            log["time"]
        ])

    csv_data = output.getvalue()

    output.close()

    return Response(

        csv_data,

        mimetype="text/csv",

        headers={

            "Content-Disposition":
                f"attachment; filename=Access_Log_{date}.csv"

        }

    )
@app.route("/api/checkin/clear", methods=["POST"])
def api_checkin_clear():

    mqtt_server.pending_uid = None

    print("[CHECK IN] Pending UID cleared")

    return jsonify({
        "success": True
    })

# ================= ADMIN APPROVE =================

@app.route("/api/approve", methods=["POST"])
def api_approve():

    if not session.get("login"):
        return jsonify({"success": False}), 401

    data = request.get_json()

    log_id = data.get("id")

    approve_log(log_id)

    return jsonify({
        "success": True
    })


# ================= ADMIN REJECT =================

@app.route("/api/reject", methods=["POST"])
def api_reject():

    if not session.get("login"):
        return jsonify({"success": False}), 401

    data = request.get_json()

    log_id = data.get("id")

    reject_log(log_id)

    return jsonify({
        "success": True
    })

# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ================= CAMERA =================

@app.route("/video_feed")
def video_feed():

    return Response(
        gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/api/enroll", methods=["POST"])
def api_enroll():

    data = request.get_json()

    uid = data.get("uid")

    if not uid:

        return jsonify({
            "success": False,
            "message": "UID is required."
        }), 400

    if runtime.frame is None:

        return jsonify({
            "success": False,
            "message": "No camera frame."
        }), 400

    if len(runtime.faces) != 1:

        return jsonify({
            "success": False,
            "message": "Exactly one face must be visible."
    }), 400

    success = enrollment.enroll(

        runtime.frame,
        runtime.faces[0],
        uid

    )

    if success:

        return jsonify({
            "success": True
        })

    return jsonify({

        "success": False,
        "message": "Enrollment failed."

    }), 400
@app.route("/api/faces/enroll", methods=["POST"])
def enroll_faces():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    uid = data.get("uid")
    images = data.get("images")

    # ================= CHECK UID =================

    if not uid:

        return jsonify({
            "success": False,
            "message": "Missing UID"
        }), 400

    # ================= CHECK IMAGES =================

    if not isinstance(images, list):

        return jsonify({
            "success": False,
            "message": "Images must be a list"
        }), 400

    if len(images) != 5:

        return jsonify({
            "success": False,
            "message":
                f"Expected 5 images, received {len(images)}"
        }), 400

    # ================= CREATE FOLDER =================

    face_dir = os.path.join(
        "faces",
        uid
    )

    os.makedirs(
        face_dir,
        exist_ok=True
    )

    # ================= SAVE IMAGES =================

    image_names = [
        "001_front.jpg",
        "002_left30.jpg",
        "003_right30.jpg",
        "004_up15.jpg",
        "005_down15.jpg"
    ]

    try:

        for image_data, image_name in zip(
            images,
            image_names
        ):

        # Base64 dạng:
        # data:image/jpeg;base64,XXXX

            if "," in image_data:

                image_data = image_data.split(
                    ",",
                    1
            )[1]

            image_bytes = base64.b64decode(
                image_data
        )

            image_path = os.path.join(
                face_dir,
                image_name
        )

            with open(
                image_path,
                "wb"
        ) as file:

                file.write(image_bytes)

            print(
                f"[FACE ENROLL] Saved: {image_path}"
        )

    except Exception as e:

        print(
            "[FACE ENROLL] Save error:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Failed to save face images."
    }), 500


    # ================= SUCCESS =================

    print(
        f"[FACE ENROLL] UID: {uid}"
    )

    print(
        f"[FACE ENROLL] Saved {len(images)} images"
    )
        # ================= AI EMBEDDING TEST =================

    embedding_results = []

    for image_name in image_names:

        image_path = os.path.join(
            face_dir,
            image_name
        )

        # Đọc ảnh
        frame = cv2.imread(image_path)

        if frame is None:

            print(
                f"[FACE AI] Cannot read: {image_name}"
            )

            return jsonify({
                "success": False,
                "message":
                    f"Cannot read image: {image_name}"
            }), 500

        # YuNet detect face
        faces = face_detector.detect(frame)

        print(
            f"[FACE AI] {image_name} → "
            f"{len(faces)} face(s)"
        )

        if len(faces) == 0:

            return jsonify({
                "success": False,
                "message":
                    f"No face detected in {image_name}"
            }), 400

        # Tạm thời lấy khuôn mặt đầu tiên
        face = faces[0]

        # SFace tạo embedding
        embedding = face_recognizer.extract(
            frame,
            face
        )

        if embedding is None:

            return jsonify({
                "success": False,
                "message":
                    f"Embedding failed: {image_name}"
            }), 500

        embedding_results.append(
            embedding
        )

        print(
            f"[FACE AI] {image_name} "
            f"→ embedding OK "
            f"{embedding.shape}"
        )

    print(
        f"[FACE AI] Generated "
        f"{len(embedding_results)} embeddings"
    )
    # ================= EMBEDDING SIMILARITY =================

    print(
        "[FACE AI] Similarity check"
    )

    # Chuyển 5 embedding về vector 1 chiều
    embeddings = [
        embedding.flatten()
        for embedding in embedding_results
    ]

    # Chuẩn hóa từng embedding
    normalized_embeddings = []

    for embedding in embeddings:

        norm = np.linalg.norm(
            embedding
        )

        if norm == 0:

            return jsonify({
                "success": False,
                "message":
                    "Invalid face embedding."
            }), 500

        normalized_embeddings.append(
            embedding / norm
        )

    # Tính cosine similarity giữa từng cặp ảnh

    for i in range(
        len(normalized_embeddings)
    ):

        for j in range(
            i + 1,
            len(normalized_embeddings)
        ):

            similarity = np.dot(
                normalized_embeddings[i],
                normalized_embeddings[j]
            )

            print(
                f"[FACE AI] "
                f"{image_names[i]} ↔ "
                f"{image_names[j]} "
                f"= {similarity:.4f}"
            )
    # ================= FINAL EMBEDDING =================

    # Gộp 5 embedding bằng trung bình
    final_embedding = np.mean(
        normalized_embeddings,
        axis=0
    )

    # Chuẩn hóa lại vector cuối
    final_norm = np.linalg.norm(
        final_embedding
    )

    if final_norm == 0:

        return jsonify({
            "success": False,
            "message":
                "Failed to create final embedding."
        }), 500

    final_embedding = (
        final_embedding / final_norm
    )

    print(
        "[FACE AI] Final embedding generated"
    )

    print(
        f"[FACE AI] Shape: "
        f"{final_embedding.shape}"
    )

    print(
        f"[FACE AI] Norm: "
        f"{np.linalg.norm(final_embedding):.4f}"
    )

    # ================= SAVE EMBEDDING =================

    user = check_uid(uid)

    if user is None:

        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    save_embedding(
        user["id"],
        final_embedding
    )

    print(
        f"[FACE AI] Embedding saved "
        f"for UID: {uid}"
    )

    return jsonify({

        "success": True,

        "message":
            "Face images saved successfully.",

        "uid": uid,

        "count": len(images)

    })
# ================= MAIN =================
if __name__ == "__main__":

    print(">>> Before start_mqtt")
    start_mqtt()
    print(">>> After start_mqtt")

    print(">>> Before app.run")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
        
    )


