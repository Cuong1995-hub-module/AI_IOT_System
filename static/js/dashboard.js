// ======================================================
// Dashboard Entry
// ======================================================

const userCard = document.getElementById("user-card");

if (userCard) {

    userCard.addEventListener("click", () => {

        window.location.href = "/users";

    });

}