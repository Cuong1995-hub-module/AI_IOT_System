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

const canvas =
document.getElementById("captureCanvas");

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

let stream = null;

// =========================
// CHECK-IN SESSION
// =========================

let rfidLocked = false;
let capturedImageData = null;
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
    // START CAMERA
    // =========================

    try {

        stream =
            await navigator.mediaDevices.getUserMedia({

                video: true,

                audio: false

            });

        video.srcObject = stream;

    }

    catch(error) {

        alert(
            "Cannot access camera!"
        );

        console.error(error);

    }

};


// =========================
// Capture Image
// =========================

btnCapture.onclick = () => {

    console.log(
        "[CHECK IN] Capture clicked"
    );

    if (!video.srcObject) {

        alert("Camera is not active!");

        return;

    }

    canvas.width =
        video.videoWidth;

    canvas.height =
        video.videoHeight;

    const context =
        canvas.getContext("2d");

    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    const imageData =
        canvas.toDataURL(
            "image/jpeg",
            0.9
        );
    capturedImageData =
    imageData;
    if (rfidLocked) {

    btnCheckinSubmit.disabled = false;

}

    // Hiển thị ảnh vừa chụp
    capturedPreview.src =
        imageData;

    capturedPreview.style.display =
        "block";

    previewPlaceholder.style.display =
        "none";

    console.log(
        "[CHECK IN] Image captured"
    );

    console.log(
        "[CHECK IN] Image size:",
        imageData.length
    );

};

// =========================
// SUBMIT CHECK IN
// =========================

btnCheckinSubmit.onclick = async () => {

    if (!rfidLocked) {

        alert("Please scan RFID first.");

        return;

    }

    if (!capturedImageData) {

        alert("Please capture image first.");

        return;

    }

    const uid =
        uidText.textContent.trim();

    if (!uid) {

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

                        image:
                            capturedImageData

                    })
                }
            );

        const data =
            await response.json();

        console.log(
            "[CHECK IN] Server response:",
            data
        );

        if (!response.ok || !data.success) {

            alert(
                data.message ||
                "Check-in failed."
            );

            return;

        }

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

    if(stream){

        stream.getTracks().forEach(
            track => {
                track.stop();
            }
        );

        stream = null;
    }

    video.srcObject = null;

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

    if (!capturedImageData) {

        alert("Please capture image first.");

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

                        image:
                            capturedImageData

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
 

