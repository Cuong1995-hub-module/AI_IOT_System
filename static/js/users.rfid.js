// ======================================================
// RFID Polling
// ======================================================

// Get latest RFID UID
async function fetchLastUID() {

    console.log("Polling...");

    try {

        const response = await fetch("/api/last_uid");
        const data = await response.json();

        console.log("API:", data);

        if (data.uid && data.uid !== currentUID) {

            currentUID = data.uid;

            uidInput.value = currentUID;

            saveBtn.disabled = false;

            console.log("New UID:", currentUID);

        }

    } catch (error) {

        console.error("Error:", error);

    }

}

// Start polling
function startPolling() {

    if (polling) return;

    fetchLastUID();

    polling = setInterval(fetchLastUID, 500);

}

// Stop polling
function stopPolling() {

    clearInterval(polling);

    polling = null;

    currentUID = "";

    uidInput.value = "";

}