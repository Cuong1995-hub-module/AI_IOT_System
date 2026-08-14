// ======================================================
// Face Enrollment
// ======================================================

const faceModal = document.getElementById("face-modal");

const cameraPreview = document.getElementById("camera-preview");
const cameraPlaceholder = document.getElementById("camera-placeholder");
const capturedImage = document.getElementById("captured-image");
const capturePlaceholder = document.getElementById("capture-placeholder");


// ======================================================
// Start Camera
// ======================================================

// ======================================================
// Start Camera Node
// ======================================================

async function startCamera() {

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

        if (!data.success || !data.camera) {

            throw new Error(
                "Camera Node unavailable"
            );

        }

        const videoUrl =
            data.camera.video_url;

        cameraPreview.src =
            videoUrl;

        cameraPreview.style.display =
            "block";

        cameraPlaceholder.style.display =
            "none";

        console.log(
            "[FACE] Camera Node:",
            videoUrl
        );

    }

    catch (err) {

        console.error(
            "[FACE] Camera Node error:",
            err
        );

        alert(
            "Cannot connect to Camera Node."
        );

    }

}



// ======================================================
// Stop Camera Node
// ======================================================

function stopCamera() {

    cameraPreview.src = "";

    cameraPreview.style.display =
        "none";

    cameraPlaceholder.style.display =
        "flex";

}
// ======================================================
// Open Face Modal
// ======================================================

document.querySelectorAll(".face-btn").forEach(btn => {

    btn.addEventListener("click", () => {

        document.getElementById("face-name").textContent =
            btn.dataset.name;

        document.getElementById("face-uid").textContent =
            btn.dataset.uid;

        faceModal.style.display = "flex";

        startCamera();

    });

});

// ======================================================
// Close Face Modal
// ======================================================

document.getElementById("face-cancel").addEventListener("click", () => {

    stopCamera();

    resetFaceEnrollment();

    faceModal.style.display = "none";

});

// ======================================================
// ESC Close
// ======================================================

document.addEventListener("keydown", (e) => {

    if (e.key === "Escape" && faceModal.style.display === "flex") {

        stopCamera();
        resetFaceEnrollment();

        faceModal.style.display = "none";

    }

});

// ======================================================
// Click Outside Close
// ======================================================

faceModal.addEventListener("click", (e) => {

    if (e.target === faceModal) {

        stopCamera();
        resetFaceEnrollment();

        faceModal.style.display = "none";

    }

});

// ======================================================
// Capture Steps
// ======================================================

const captureSteps = [

    "Look straight at the camera",

    "Turn LEFT about 30°",

    "Turn RIGHT about 30°",

    "Raise your head slightly",

    "Lower your head slightly"

];

let currentStep = 0;

let capturedImages = [];
// ======================================================
// Reset Face Enrollment
// ======================================================

function resetFaceEnrollment() {

    currentStep = 0;

    capturedImages = [];

    capturedImage.src = "";

    capturedImage.style.display = "none";

    capturePlaceholder.style.display = "flex";

    captureButton.disabled = false;

    retakeButton.disabled = true;

    addButton.disabled = true;

    finishButton.disabled = true;

    finishButton.textContent = "✔ Finish";

    updateCaptureStep();

}

// ======================================================
// Elements
// ======================================================

const captureButton = document.getElementById("face-capture");
const retakeButton = document.getElementById("face-retake");
const addButton = document.getElementById("face-add");
const finishButton = document.getElementById("face-finish");

const stepTitle = document.getElementById("capture-step");
const stepInstruction = document.getElementById("capture-instruction");

const progressText = document.getElementById("progress-text");
const progressFill = document.getElementById("progress-fill");


// ======================================================
// Update Step UI
// ======================================================

function updateCaptureStep() {

    stepTitle.textContent =
        `Step ${currentStep + 1} / ${captureSteps.length}`;

    stepInstruction.textContent =
        captureSteps[currentStep];

    progressText.textContent =
        `${capturedImages.length} / ${captureSteps.length} Images`;

    progressFill.style.width =
        `${(capturedImages.length / captureSteps.length) * 100}%`;

}


captureButton.addEventListener("click", async () => {

    try {

        console.log("[FACE] Capture clicked");

        const response = await fetch(
            "/api/camera/test-capture"
        );

        if (!response.ok) {

            throw new Error(
                "Camera capture failed"
            );

        }

        const blob = await response.blob();

        console.log(
            "[FACE] Image received:",
            blob.size,
            "bytes"
        );

        // ==========================================
        // Convert JPEG Blob → Base64 Data URL
        // ==========================================

        const reader = new FileReader();

        reader.onloadend = () => {

            const imageData =
                reader.result;

            // ======================================
            // Validate
            // ======================================

            if (
                typeof imageData !== "string" ||
                !imageData.startsWith("data:image/")
            ) {

                console.error(
                    "[FACE] Invalid image data"
                );

                alert("Invalid captured image.");

                return;

            }

            console.log(
                "[FACE] Base64 image length:",
                imageData.length
            );

            // ======================================
            // Show captured image
            // ======================================

            capturedImage.src =
                imageData;

            capturedImage.style.display =
                "block";

            capturePlaceholder.style.display =
                "none";

            // ======================================
            // Enable buttons
            // ======================================

            retakeButton.disabled =
                false;

            addButton.disabled =
                false;

            captureButton.disabled =
                true;

        };

        reader.readAsDataURL(blob);

    }
    catch (error) {

        console.error(
            "[FACE] Capture error:",
            error
        );

        alert(
            "Cannot capture image."
        );

    }

});


// ======================================================
// Retake
// ======================================================

retakeButton.addEventListener("click", () => {

    capturedImage.src = "";

    capturedImage.style.display = "none";

    capturePlaceholder.style.display = "flex";

    captureButton.disabled = false;

    retakeButton.disabled = true;

    addButton.disabled = true;

});


// ======================================================
// Add Photo
// ======================================================

addButton.addEventListener("click", () => {

    if (!capturedImage.src) {

        return;

    }

    // Save current image temporarily

    capturedImages.push(capturedImage.src);

    // Move to next step

    currentStep++;

    // Reset preview

    capturedImage.src = "";

    capturedImage.style.display = "none";

    capturePlaceholder.style.display = "flex";

    // Reset buttons

    captureButton.disabled = false;

    retakeButton.disabled = true;

    addButton.disabled = true;

    // Update progress

    if (currentStep < captureSteps.length) {

        updateCaptureStep();

    } else {

        // Completed all 5 images

        stepTitle.textContent = "Completed";

        stepInstruction.textContent =
            "All 5 face images have been captured.";

        progressText.textContent =
            `${capturedImages.length} / ${captureSteps.length} Images`;

        progressFill.style.width = "100%";

        captureButton.disabled = true;

        finishButton.disabled = false;

    }

});


// ======================================================
// Initial UI
// ======================================================

updateCaptureStep();
// ======================================================
// Finish Face Enrollment
// ======================================================

// ======================================================
// Finish Face Enrollment
// ======================================================

finishButton.addEventListener("click", async () => {

    if (capturedImages.length !== captureSteps.length) {

        alert("Please capture all 5 face images.");

        return;

    }

    const uid =
        document.getElementById("face-uid").textContent.trim();

    if (!uid) {

        alert("UID is missing.");

        return;

    }

    finishButton.disabled = true;
    finishButton.textContent = "⏳ Saving...";

    try {

        const response = await fetch("/api/faces/enroll", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                uid: uid,

                images: capturedImages

            })

        });

        const result = await response.json();

        console.log("Face enrollment response:", result);

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Face enrollment failed."
            );

        }

        alert("Face enrollment completed successfully.");

        stopCamera();

        faceModal.style.display = "none";

        location.reload();

    }

    catch (error) {

        console.error("Face enrollment error:", error);

        alert(
            "Face enrollment failed: " + error.message
        );

        finishButton.disabled = false;
        finishButton.textContent = "✔ Finish";

    }

});