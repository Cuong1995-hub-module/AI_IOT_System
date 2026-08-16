// ======================================================
// Users Page - Global Variables
// ======================================================

// ---------- Modal ----------
const modal = document.getElementById("user-modal");
const addBtn = document.getElementById("add-user-btn");
const cancelBtn = document.getElementById("cancel-btn");

// ---------- Inputs ----------
const nameInput = document.getElementById("user-name");
const uidInput = document.getElementById("rfid-uid");

// ---------- Buttons ----------
const saveBtn = document.getElementById("save-btn");

// ======================================================
// Global State
// ======================================================

let currentUID = "";
let polling = null;
let isEditMode = false;

// ======================================================
// Save Button
// ======================================================

saveBtn.addEventListener("click", () => {

    if (isEditMode) {

        updateUser();

    } else {

        saveUser();

    }

});

// ============================================================
// USER SEARCH
// ============================================================

const searchInput = document.getElementById("search");

if (searchInput) {

    searchInput.addEventListener("input", function () {

        const keyword = this.value
            .trim()
            .toLowerCase();

        const rows = document.querySelectorAll(
            "table tbody tr"
        );

        rows.forEach(row => {

            const uid = row
                .cells[0]
                ?.textContent
                .toLowerCase() || "";

            const name = row
                .cells[1]
                ?.textContent
                .toLowerCase() || "";

            const matched =
                uid.includes(keyword) ||
                name.includes(keyword);

            row.style.display =
                matched ? "" : "none";

        });

    });

}