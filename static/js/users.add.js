// ======================================================
// Add User
// ======================================================

// Save New User
async function saveUser() {

    const name = nameInput.value.trim();
    const uid = uidInput.value.trim();

    if (!name) {
        alert("Please enter full name.");
        return;
    }

    if (!uid) {
        alert("Please scan RFID card.");
        return;
    }

    try {

        const response = await fetch("/api/users", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                uid: uid,
                name: name
            })

        });

        const result = await response.json();

        if (result.success) {

            alert("User added successfully.");

            stopPolling();

            modal.style.display = "none";

            nameInput.value = "";
            uidInput.value = "";

            window.location.reload();

        } else {

            alert(result.message);

        }

    } catch (error) {

        console.error(error);

        alert("Cannot connect to server.");

    }

}