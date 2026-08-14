// ======================================================
// Verification Details
// ======================================================

function showVerification(logItem) {

 // Bỏ highlight log cũ
    document.querySelectorAll(".log-item").forEach(item => {
        item.classList.remove("active");
    });

    // Highlight log đang chọn
    logItem.classList.add("active");

    const aiResult = logItem.dataset.ai;
    const adminResult = logItem.dataset.admin;
    const name = logItem.dataset.name;

    const btnApprove = document.getElementById("btnApprove");
    const btnReject = document.getElementById("btnReject");
    btnApprove.disabled = true;
    btnReject.disabled = true;

  if (name === "Unknown") {

    btnApprove.disabled = true;
    btnReject.disabled = true;

}
else if (adminResult === "APPROVED") {

    btnApprove.disabled = true;
    btnReject.disabled = false;

}
else if (adminResult === "REJECTED") {

    btnApprove.disabled = false;
    btnReject.disabled = true;

}
else {

    btnApprove.disabled = false;
    btnReject.disabled = false;

}
    // ==========================
    // Employee Information
    // ==========================

    document.getElementById("verify-name").textContent =
        logItem.dataset.name || "Unknown";

    document.getElementById("verify-uid").textContent =
        logItem.dataset.uid || "-";

    document.getElementById("verify-time").textContent =
        logItem.dataset.time || "-";

    // Demo (sau này AI sẽ trả về)
    const similarity =
    parseFloat(logItem.dataset.similarity || "0");

document.getElementById("verify-confidence").textContent =
    (similarity * 100).toFixed(2) + " %";

    // ==========================
    // Verification Result
    // ==========================

    const resultElement = document.getElementById("verify-result");

    resultElement.className = "";

   switch (aiResult) {

    case "MATCH":

        resultElement.textContent =
            "🟢 AI MATCH";

        resultElement.classList.add(
            "success-text"
        );

        break;

    case "MISMATCH":

        resultElement.textContent =
            "🔴 AI MISMATCH";

        resultElement.classList.add(
            "fail-text"
        );

        break;

    case "NO_FACE":

        resultElement.textContent =
            "⚫ NO FACE";

        resultElement.classList.add(
            "fail-text"
        );

        break;

    case "NO_TEMPLATE":

        resultElement.textContent =
            "⚫ NO TEMPLATE";

        resultElement.classList.add(
            "unknown-text"
        );

        break;

    default:

        resultElement.textContent =
            aiResult || "UNKNOWN";

        break;
}

    // ==========================
    // Current Check In Image
    // ==========================

    const capturedImage = document.getElementById("captured-image");

    if (capturedImage) {

        capturedImage.src = logItem.dataset.image
            ? "/" + logItem.dataset.image
            : "/static/images/samsung-bg.jpeg";

    }
    // ==========================
    // Registered Face Image
    // ==========================

const registeredImage =
    document.getElementById("registered-image");

const uid = logItem.dataset.uid;

if (registeredImage && uid) {

    registeredImage.src =
        `/faces/${uid}/001_front.jpg`;

}

}

btnApprove.addEventListener("click", async () => {

    const active = document.querySelector(".log-item.active");

    if (!active) {

        alert("Please select a log first.");

        return;

    }

    const response = await fetch("/api/approve", {

        method: "POST",

        headers: {

            "Content-Type": "application/json"

        },

        body: JSON.stringify({

            id: active.dataset.id

        })

    });

    const result = await response.json();

    if (result.success) {

    selectedLogId = null;

    autoRefresh = true;

    await loadLogs();

    alert("Approved successfully.");

}

});

btnReject.addEventListener("click", async () => {

    const active = document.querySelector(".log-item.active");

    if (!active) {

        alert("Please select a log first.");

        return;

    }

    const response = await fetch("/api/reject", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            id: active.dataset.id
        })

    });

    const result = await response.json();

    if (result.success) {

        selectedLogId = null;

        autoRefresh = true;

        await loadLogs();

        alert("Rejected successfully.");

    }

});