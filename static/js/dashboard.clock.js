// =========================
// Clock
// =========================

function updateClock() {

    const now = new Date();

    const date = now.toLocaleDateString("vi-VN");

    const time = now.toLocaleTimeString("vi-VN");

    document.getElementById("clock").innerHTML =
        `${date}<br>${time}`;
}

updateClock();

setInterval(updateClock, 1000);
