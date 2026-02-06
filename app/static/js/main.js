const btn = document.getElementById("menuBtn");
const menu = document.getElementById("menu");

if (btn) {
    btn.addEventListener("click", () => {
        menu.classList.toggle("hidden");
    });
}
