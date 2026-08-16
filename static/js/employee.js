const btnCheckin =
document.getElementById("btnCheckin");

const btnCancel =
document.getElementById("btnCancel");

const btnCapture =
document.getElementById("btnCapture");
const btnCheckinSubmit =
document.getElementById("btnCheckinSubmit");

const modal =
document.getElementById("checkinModal");

const video =
document.getElementById("cameraPreview");

const capturedPreview =
document.getElementById("capturedPreview");

const previewPlaceholder =
document.getElementById("previewPlaceholder");
const userName =
document.getElementById("userName");

const uidText =
document.getElementById("uidText");

const checkTime =
document.getElementById("checkTime");

let cameraStreamUrl = null;

// =========================
// CHECK-IN SESSION
// =========================

let rfidLocked = false;
let capturedImageData = null;

async function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onloadend = () => {
            resolve(reader.result);
        };

        reader.onerror = reject;

        reader.readAsDataURL(blob);
    });
}
btnCheckinSubmit.disabled = true;

// =========================
// Open Check In
// =========================

btnCheckin.onclick = async () => {

    // =========================
    // START NEW CHECK-IN SESSION
    // =========================

    try {

        await fetch(
            "/api/checkin/clear",
            {
                method: "POST"
            }
        );

        console.log(
            "[CHECK IN] New session started"
        );

    }
    catch (error) {

        console.error(
            "[CHECK IN] Failed to clear old session:",
            error
        );

    }

    // =========================
    // RESET FRONTEND STATE
    // =========================

    rfidLocked = false;

    capturedImageData = null;

    btnCheckinSubmit.disabled = true;

    modal.classList.add("show");

// =========================
// LIVE CAMERA NODE
// =========================

try {

    const response =
        await fetch("/api/camera");

    if (!response.ok) {

        throw new Error(
            "No camera registered"
        );

    }

    const data =
        await response.json();

    cameraStreamUrl =
        data.camera.video_url;

    cameraPreview.src =
        cameraStreamUrl;

    console.log(
        "[CHECK IN] Camera Node:",
        cameraStreamUrl
    );

}
catch (error) {

    console.error(
        "[CHECK IN] Camera Node error:",
        error
    );

}

console.log(
    "[CHECK IN] Camera Node live stream started"
);

};
// =========================
// Capture Image
// =========================

btnCapture.onclick = async () => {

    console.log(
        "[CHECK IN] Capture clicked"
    );

    try {

        const response =
            await fetch(
                "/api/camera/test-capture?t=" + Date.now(),
                {
                    cache: "no-store"
                }
            );

        if (!response.ok) {

            throw new Error(
                "Camera capture failed"
            );

        }

        const blob =
            await response.blob();

        // =========================
        // RELEASE OLD IMAGE URL
        // =========================

        if (capturedPreview.dataset.objectUrl) {

            URL.revokeObjectURL(
                capturedPreview.dataset.objectUrl
            );

        }

        // =========================
        // CREATE NEW IMAGE URL
        // =========================

        const imageUrl =
            URL.createObjectURL(blob);

        capturedPreview.dataset.objectUrl =
            imageUrl;

        // =========================
        // SHOW NEW IMAGE
        // =========================

        capturedPreview.src =
            imageUrl;

        capturedPreview.style.display =
            "block";

        previewPlaceholder.style.display =
            "none";

        // =========================
        // MARK CAPTURED
        // =========================

        capturedImageData =
            await blobToBase64(blob);

        if (rfidLocked) {

            btnCheckinSubmit.disabled =
                false;

        }

        console.log(
            "[CHECK IN] New image captured"
        );

        console.log(
            "[CHECK IN] Image size:",
            blob.size
        );

    }
    catch (error) {

        console.error(
            "[CHECK IN] Capture error:",
            error
        );

        alert(
            "Cannot capture image"
        );

    }

};



// =========================
// Close Check In
// =========================

btnCancel.onclick = async () => {

    try {

        await fetch(
            "/api/checkin/clear",
            {
                method: "POST"
            }
        );

        console.log(
            "[CHECK IN] Session cancelled"
        );

    }
    catch (error) {

        console.error(
            "[CHECK IN] Failed to clear session:",
            error
        );

    }

    closeModal();

};


// =========================
// Click Outside
// =========================

window.onclick = async (event) => {

    if(event.target === modal) {

        try {

            await fetch(
                "/api/checkin/clear",
                {
                    method: "POST"
                }
            );

            console.log(
                "[CHECK IN] Session cancelled"
            );

        }
        catch (error) {

            console.error(
                "[CHECK IN] Failed to clear session:",
                error
            );

        }

        closeModal();

    }

};


// =========================
// Close Function
// =========================

function closeModal(){

    modal.classList.remove("show");

    rfidLocked = false;

    cameraPreview.src = "";

    if (capturedPreview.dataset.objectUrl) {

    URL.revokeObjectURL(
        capturedPreview.dataset.objectUrl
    );

    delete capturedPreview.dataset.objectUrl;

    }

    capturedPreview.src = "";

    capturedPreview.style.display =
        "none";

    previewPlaceholder.style.display =
        "flex";

    // =========================
    // CLEAR RFID INFO
    // =========================

    userName.textContent =
        "Waiting for RFID...";

    uidText.textContent =
        "Waiting for RFID...";

    checkTime.textContent =
        "-- : -- : --";

capturedImageData = null;

btnCheckinSubmit.disabled = true;
}


// =========================
// RFID CHECK-IN
// =========================

async function updateCheckinUser() {

    // Đã nhận RFID trong phiên này
    if (rfidLocked) {

        return;

    }

    try {

        const response =
            await fetch(
                "/api/checkin/pending"
            );

        const data =
            await response.json();

        if (!data.uid) {

            return;

        }

        // =========================
        // LOCK RFID
        // =========================

        rfidLocked = true;

        userName.textContent =
            data.name;

        uidText.textContent =
            data.uid;

        checkTime.textContent =
            new Date().toLocaleTimeString();
        if (capturedImageData) {

    btnCheckinSubmit.disabled = false;

}

        console.log(
            "[CHECK IN] RFID LOCKED:",
            data.name,
            "| UID:",
            data.uid
        );

    }
    catch (error) {

        console.error(
            "[CHECK IN] RFID error:",
            error
        );

    }

}
// =========================
// SUBMIT CHECK IN
// =========================

btnCheckinSubmit.onclick = async () => {

    if (!rfidLocked) {

        alert("Please scan RFID first.");

        return;

    }


    const uid =
        uidText.textContent.trim();

    if (!uid || uid === "Waiting for RFID...") {

        alert("Invalid RFID.");

        return;

    }

    console.log(
        "[CHECK IN] Sending to server:",
        uid
    );

    try {

        const response =
            await fetch(
                "/api/checkin",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        uid: uid,
                        image: capturedImageData

                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok || !data.success) {

            alert(
                data.message ||
                "Check-in failed."
            );

            return;

        }

        console.log(
            "[CHECK IN] Server accepted"
        );

        alert(
            "Check-in successful!"
        );

        closeModal();

    }
    catch (error) {

        console.error(
            "[CHECK IN] Submit error:",
            error
        );

        alert(
            "Cannot connect to server."
        );

    }

};

// =========================
// Start RFID Polling
// =========================

setInterval(
    updateCheckinUser,
    500
);
// =========================
// TODAY'S CHECK-IN LIST
// =========================

const todayCheckinsList =
    document.getElementById("todayCheckinsList");


async function loadTodayCheckins() {

    if (!todayCheckinsList) {
        return;
    }

    try {

        const response =
            await fetch("/api/checkins/today");

        if (!response.ok) {
            throw new Error(
                "Failed to load today's check-ins"
            );
        }

        const logs =
            await response.json();

        // Không có log
        if (!logs.length) {

            todayCheckinsList.innerHTML = `
                <div class="checkin-empty">
                    Chưa có lượt check-in hôm nay
                </div>
            `;

            return;
        }

        todayCheckinsList.innerHTML =
            logs.map(log => {

                let statusIcon = "🟡";
                let statusText = "PENDING";
                let statusClass = "pending";

                if (
                    log.admin_result === "APPROVED"
                ) {

                    statusIcon = "🟢";
                    statusText = "CHECKED IN";
                    statusClass = "approved";

                }
                else if (
                    log.admin_result === "REJECTED"
                ) {

                    statusIcon = "🔴";
                    statusText = "REJECTED";
                    statusClass = "rejected";
                }

                let aiText =
                    log.ai_result === "MATCH"
                        ? "AI PASS"
                        : "AI CHECK";

                let similarityText = "";

                if (
                    log.similarity !== null &&
                    log.similarity !== undefined
                ) {

                    similarityText =
                        `${Math.round(
                            log.similarity * 100
                        )}%`;
                }

                const time =
                    log.time
                        ? log.time.substring(11, 16)
                        : "--:--";

                return `
                    <div class="checkin-item ${statusClass}">

                        <div class="checkin-item-main">

                            <div class="checkin-name">
                                ${statusIcon}
                                ${log.name || "Unknown"}
                            </div>

                            <div class="checkin-time">
                                🕐 ${time}
                            </div>

                        </div>

                        <div class="checkin-item-status">

                            <span class="ai-status">
                                ${aiText}
                            </span>

                            ${
                                similarityText
                                    ? `<span class="similarity">
                                        ${similarityText}
                                       </span>`
                                    : ""
                            }

                            <span class="admin-status">
                                ${statusText}
                            </span>

                        </div>

                    </div>
                `;

            }).join("");

    }
    catch (error) {

        console.error(
            "[CHECK IN] Failed to load today's logs:",
            error
        );

    }
}


// Load immediately
loadTodayCheckins();


// Refresh every 2 seconds
setInterval(
    loadTodayCheckins,
    2000
);
