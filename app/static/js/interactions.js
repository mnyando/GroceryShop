document.addEventListener("DOMContentLoaded", function () {
    // Cart Drawer Toggle
    const cartModal = document.getElementById("cartModal");
    const openCartButtons = document.querySelectorAll("[data-cart-open]");
    const closeCartElements = document.querySelectorAll("[data-cart-close]");

    openCartButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            cartModal?.classList.add("is-open");
        });
    });

    closeCartElements.forEach(el => {
        el.addEventListener("click", function (e) {
            e.preventDefault();
            cartModal?.classList.remove("is-open");
        });
    });

    // Escape key to close cart
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            cartModal?.classList.remove("is-open");
        }
    });
});
