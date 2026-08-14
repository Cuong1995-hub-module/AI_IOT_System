const exportBtn = document.getElementById("export-csv-btn");

exportBtn.addEventListener("click", () => {

    const date = document.getElementById("log-date").value;

    window.location.href = `/api/logs/export?date=${date}`;

});