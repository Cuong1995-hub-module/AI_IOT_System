const espCard = document.getElementById("esp32-card");
const popup = document.getElementById("network-popup");
const closeBtn = document.getElementById("close-popup");

if (espCard && popup && closeBtn) {

    espCard.addEventListener("click", () => {

        popup.classList.add("show");

    });

    closeBtn.addEventListener("click", () => {

        popup.classList.remove("show");

    });

}