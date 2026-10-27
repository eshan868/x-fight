
function openGameMateSearch() {
    const modal = document.getElementById("gamemateModal");

    if (!modal) {
        console.error("Game Mate modal not found");
        return;
    }

    modal.classList.add("show");

    document.body.style.overflow = "hidden";
}


function closeGameMateSearch() {
    const modal = document.getElementById("gamemateModal");

    if (!modal) {
        console.error("Game Mate modal not found");
        return;
    }

    modal.classList.remove("show");

    document.body.style.overflow = "";

    const searchInput = document.getElementById("searchUser");

    if (searchInput) {
        searchInput.value = "";
        filterUsers();
    }
}


function filterUsers() {
    const input = document.getElementById("searchUser");

    if (!input) {
        return;
    }

    const search = input.value.toLowerCase().trim();

    document.querySelectorAll(".user-item").forEach(user => {

        const username =
            user.dataset.username ||
            user.querySelector("h5")?.textContent.toLowerCase() ||
            "";

        user.style.display =
            username.includes(search) ? "flex" : "none";
    });
}


/* Close when clicking the dark background */

document.addEventListener("click", function (event) {

    const modal = document.getElementById("gamemateModal");

    if (!modal) {
        return;
    }

    if (
        modal.classList.contains("show") &&
        event.target === modal
    ) {
        closeGameMateSearch();
    }

});


/* Close with ESC */

document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {
        closeGameMateSearch();
    }

});




