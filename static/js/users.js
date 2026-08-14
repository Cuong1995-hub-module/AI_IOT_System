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