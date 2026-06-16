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

    // Scroll fade-up reveals
    const reveals = document.querySelectorAll('[data-reveal]');
    const io = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.classList.add('is-visible');
                io.unobserve(e.target);
            }
        });
    }, { threshold: 0.15 });
    reveals.forEach(el => io.observe(el));

    // Mobile nav toggle
    const navToggle = document.querySelector('.nav__toggle');
    const navLinks = document.querySelector('.nav__links');
    navToggle?.addEventListener('click', function () {
        navLinks?.classList.toggle('nav__links--open');
    });
});
