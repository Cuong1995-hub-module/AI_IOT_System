const btnCheckin =
document.getElementById("btnCheckin");

const btnCancel =
document.getElementById("btnCancel");


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
let captureInProgress = false;
let captureTimer = null;

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
    captureInProgress = false;

    if (captureTimer) {
        clearTimeout(captureTimer);
        captureTimer = null;
}

    captureTimer = null;

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

    video.src =
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
    captureInProgress = false;

    if (captureTimer) {
        clearTimeout(captureTimer);
        captureTimer = null;
    }

    video.src = "";

    // =========================
    // CLEAR RFID INFO
    // =========================

    userName.textContent =
        "Waiting for RFID...";

    uidText.textContent =
        "Waiting for RFID...";

    checkTime.textContent =
        "-- : -- : --";


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

        console.log(
            "[CHECK IN] RFID LOCKED:",
            data.name,
            "| UID:",
            data.uid
        );
        startCaptureCountdown();
    }
    catch (error) {

        console.error(
            "[CHECK IN] RFID error:",
            error
        );

    }

}

// =========================
// CAPTURE COUNTDOWN
// =========================

function startCaptureCountdown() {

    captureInProgress = true;

    console.log(
        "[CHECK IN] Preparing capture..."
    );

    console.log(
        "[CHECK IN] Capture in: 3"
    );

    captureTimer = setTimeout(() => {

        captureTimer = null;

        console.log(
            "[CHECK IN] Requesting server capture..."
        );

        submitCheckIn();

    }, 2500);

}
// =========================
// SUBMIT CHECK IN
// =========================

async function submitCheckIn() {



    const uid =
        uidText.textContent.trim();

    if (!uid || uid === "Waiting for RFID...") {

        captureInProgress = false;
        rfidLocked = false;

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

                        uid: uid
                    

                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok || !data.success) {

            captureInProgress = false;
            rfidLocked = false;

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
        captureInProgress = false;

    }
    catch (error) {

        console.error(
            "[CHECK IN] Submit error:",
            error
        );

        alert(
            "Cannot connect to server."
        );
        captureInProgress = false;
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
