// ======================================================
// Dashboard Logs
// ======================================================

// Log được chọn
let selectedLogId = null;

// Cho phép Auto Refresh
let autoRefresh = true;

// Toàn bộ log lấy từ server
let allLogs = [];


// ======================================================
// Load Logs
// ======================================================

async function loadLogs() {

    const date = document.getElementById("log-date").value;

    let url = "/api/logs";

    if (date) {
        url += `?date=${date}`;
    }

    const response = await fetch(url);

    allLogs = await response.json();

    updateAttendance();

    filterLogs();

}


// ======================================================
// Attendance
// ======================================================

function updateAttendance() {

    const approved =
        allLogs.filter(log => log.admin_result === "APPROVED").length;

    const pending =
        allLogs.filter(log => log.admin_result === "PENDING").length;

    const total = allLogs.length;

    document.getElementById("open-count").textContent = approved;

    document.getElementById("pending-count").textContent = pending;

    document.getElementById("total-count").textContent = total;

}


// ======================================================
// Filter
// ======================================================

function filterLogs() {

    let logs = [...allLogs];

    // =========================
    // Admin Filter
    // =========================

    const adminFilter =
        document.getElementById("filter-admin").value;

    if (adminFilter !== "ALL") {

        logs = logs.filter(
            log => log.admin_result === adminFilter
        );

    }

    // =========================
    // AI Filter
    // =========================

    const aiFilter =
        document.getElementById("filter-ai").value;

    if (aiFilter !== "ALL") {

        logs = logs.filter(
            log => log.ai_result === aiFilter
        );

    }

    // =========================
    // Search
    // =========================

    const keyword =
        document.getElementById("log-search")
            .value
            .toLowerCase()
            .trim();

    if (keyword !== "") {

        logs = logs.filter(log =>

            log.name.toLowerCase().includes(keyword) ||

            log.uid.toLowerCase().includes(keyword)

        );

    }

    renderLogs(logs);

}
// ======================================================
// Render Logs
// ======================================================

function renderLogs(logs) {

    const container = document.getElementById("access-log");

    container.innerHTML = "";

    const statusMap = {

        APPROVED: {
            icon: "🟢",
            class: "success"
        },

        PENDING: {
            icon: "🟡",
            class: "pending"
        },

        REJECTED: {
            icon: "🔴",
            class: "reject"
        }

    };

    logs.forEach(log => {

        const status = statusMap[log.admin_result] || {

            icon: "⚪",

            class: "unknown"

        };

        container.innerHTML += `

        <div class="log-item ${status.class}"
                data-id="${log.id}"
                data-name="${log.name}"
                data-uid="${log.uid}"
                data-time="${log.time}"
                data-ai="${log.ai_result}"
                data-admin="${log.admin_result}"
                data-image="${log.image ?? ""}"
                data-similarity="${log.similarity ?? 0}">

            <div class="log-name">

                ${status.icon} ${log.name}

            </div>

            <div class="log-status">

                ${log.admin_result}

            </div>

            <div class="log-time">

                🕒 ${log.time.split(" ")[1]}

            </div>

            <div class="log-uid">

                🆔 ${log.uid}

            </div>

        </div>

        `;

    });

    attachLogEvents();

    // Khôi phục log đang chọn
    if (selectedLogId) {

        const active = document.querySelector(
            `.log-item[data-id="${selectedLogId}"]`
        );

        if (active) {

            showVerification(active);

        }

    }

}


// ======================================================
// Events
// ======================================================

function attachLogEvents() {

    document.querySelectorAll(".log-item").forEach(item => {

        item.addEventListener("click", () => {

            selectedLogId = item.dataset.id;

            autoRefresh = false;

            showVerification(item);

        });

    });

}


// ======================================================
// Init
// ======================================================

const today = new Date().toISOString().split("T")[0];

document.getElementById("log-date").value = today;


// Đổi ngày
document.getElementById("log-date")
    .addEventListener("change", loadLogs);


// Filter Admin
document.getElementById("filter-admin")
    .addEventListener("change", filterLogs);


// Filter AI
document.getElementById("filter-ai")
    .addEventListener("change", filterLogs);


// Search
document.getElementById("log-search")
    .addEventListener("input", filterLogs);


// Load lần đầu
loadLogs();


// ======================================================
// Auto Refresh
// ======================================================

setInterval(() => {

    if (autoRefresh) {

        loadLogs();

    }

}, 2000);