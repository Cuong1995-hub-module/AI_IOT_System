const exportBtn = document.getElementById("export-csv-btn");
const reportBtn = document.getElementById("generate-report-btn");


// ============================================================
// CSV EXPORT
// ============================================================

exportBtn.addEventListener("click", () => {

    const date = document.getElementById("log-date").value;

    if (!date) {
        alert("Please select a date.");
        return;
    }

    window.location.href =
        `/api/logs/export?date=${encodeURIComponent(date)}`;

});


// ============================================================
// DAILY PDF REPORT
// ============================================================

reportBtn.addEventListener("click", () => {

    const date = document.getElementById("log-date").value;

    if (!date) {
        alert("Please select a date.");
        return;
    }

    window.location.href =
        `/api/report/daily?date=${encodeURIComponent(date)}`;

});