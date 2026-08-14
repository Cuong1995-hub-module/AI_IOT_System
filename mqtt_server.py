import paho.mqtt.client as mqtt

from database.sqlite import check_uid, save_log

BROKER = "127.0.0.1"
PORT = 1883

# UID vừa quét gần nhất
# =========================
# RFID CHECK-IN STATE
# =========================

# UID vừa quét gần nhất
last_uid = None

# UID hợp lệ đang chờ giao diện Check-in xử lý
pending_uid = None


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected")
    client.subscribe("door/rfid")


def on_message(client, userdata, msg):

    global last_uid
    global pending_uid

    uid = msg.payload.decode().strip()

    if not uid:
        return

    # UID vừa quét - dùng cho User Management
    last_uid = uid

    print(
        f"\n[RFID] UID: {uid}"
    )

    # =========================
    # CHECK RFID
    # =========================

    user = check_uid(uid)

    if user is None:

        print(
            f"[RFID] ACCESS DENIED: {uid}"
        )

        client.publish(
            "door/control",
            "DENY"
        )

        return

    # =========================
    # RFID VALID
    # =========================

    print(
        f"[RFID] ACCESS GRANTED: {uid}"
    )

    client.publish(
        "door/control",
        "OPEN"
    )

    # =========================
    # CHECK-IN PENDING
    # =========================

    pending_uid = uid

    print(
        f"[RFID] Pending UID: {uid}"
    )

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message


def start_mqtt():
    client.connect(BROKER, PORT)
    client.loop_start()