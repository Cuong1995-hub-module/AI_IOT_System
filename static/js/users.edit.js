// ======================================================
// Edit User
// ======================================================

// Open Edit Modal
document.querySelectorAll(".edit-btn").forEach(button => {

    button.addEventListener("click", () => {

        isEditMode = true;

        modal.style.display = "flex";

        currentUID = button.dataset.uid;

        uidInput.value = button.dataset.uid;

        nameInput.value = button.dataset.name;

        saveBtn.disabled = false;

    });

});

// Update User
async function updateUser() {

    try {

        const response = await fetch("/api/users/update", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                uid: currentUID,
                name: nameInput.value.trim()

            })

        });

        const result = await response.json();

        if (result.success) {

            alert("User updated successfully.");

            window.location.reload();

        } else {

            alert(result.message);

        }

    } catch (error) {

        console.error(error);

        alert("Cannot connect to server.");

    }

}