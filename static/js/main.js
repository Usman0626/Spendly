// main.js — students will add JavaScript here as features are built

document.querySelectorAll(".flash-success").forEach((el) => {
    setTimeout(() => {
        el.classList.add("flash-fade-out");
        setTimeout(() => el.remove(), 400);
    }, 3000);
});
