// ======================================================
// Modal Events
// ======================================================

// Open Add User Modal
addBtn.addEventListener("click", () => {

    isEditMode = false;

    modal.style.display = "flex";

    currentUID = "";
    uidInput.value = "";
    nameInput.value = "";

    saveBtn.disabled = true;

    startPolling();

    setTimeout(() => {
        nameInput.focus();
    }, 100);

});

// Cancel
cancelBtn.addEventListener("click", () => {

    stopPolling();

    modal.style.display = "none";

});

// Click outside
modal.addEventListener("click", (e) => {

    if (e.target === modal) {

        stopPolling();

        modal.style.display = "none";

    }

});

// ESC
document.addEventListener("keydown", (e) => {

    if (e.key === "Escape") {

        stopPolling();

        modal.style.display = "none";

    }

});