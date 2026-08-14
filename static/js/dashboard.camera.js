async function loadCameraList() {
    const select = document.getElementById("camera-source");

    if (!select) {
        console.error("Camera select element not found.");
        return;
    }

    try {
        const response = await fetch("/api/cameras");

        if (!response.ok) {
            throw new Error("Failed to load camera list.");
        }

        const cameras = await response.json();

        select.innerHTML = "";

        if (cameras.length === 0) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "No Camera";
            select.appendChild(option);
            return;
        }

        cameras.forEach(camera => {
            const option = document.createElement("option");
            option.value = camera.id;
            option.textContent = camera.name;
            select.appendChild(option);
        });

    } catch (err) {
        console.error("Load camera error:", err);

        select.innerHTML = "";

        const option = document.createElement("option");
        option.value = "";
        option.textContent = "Load Failed";
        select.appendChild(option);
    }
}

async function changeCamera(cameraId) {

    try {

        const response = await fetch("/api/camera/select", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                camera: Number(cameraId)
            })
        });

        const result = await response.json();

        if (!result.success) {

            alert("Không thể mở camera.");
            return;

        }

        // Làm mới luồng video
        const img = document.getElementById("camera-stream");

        if (img) {
            img.src = "/video_feed?t=" + Date.now();
        }

    } catch (err) {

        console.error(err);
        alert("Không thể kết nối tới server.");

    }

}

window.addEventListener("DOMContentLoaded", () => {

    loadCameraList();

    const select = document.getElementById("camera-source");

    if (!select) return;

    select.addEventListener("change", function () {
        changeCamera(this.value);
    });

});