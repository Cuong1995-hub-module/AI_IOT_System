// ======================================================
// Delete User
// ======================================================

// Delete User
async function deleteUser(uid) {

    if (!confirm("Delete this user?")) {
        return;
    }

    try {

        const response = await fetch("/api/users/delete", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                uid: uid
            })

        });

        const result = await response.json();

        if (result.success) {

            alert("User deleted successfully.");

            window.location.reload();

        } else {

            alert(result.message);

        }

    } catch (error) {

        console.error(error);

        alert("Cannot connect to server.");

    }

}

// Register Delete Button Events
document.querySelectorAll(".delete-btn").forEach(button => {

    button.addEventListener("click", () => {

        deleteUser(button.dataset.uid);

    });

});