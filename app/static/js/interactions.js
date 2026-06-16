document.addEventListener("DOMContentLoaded", function () {
    // Cart Drawer Toggle
    const cartModal = document.getElementById("cartModal");
    const openCartButtons = document.querySelectorAll("[data-cart-open]");
    const closeCartElements = document.querySelectorAll("[data-cart-close]");
    let lastFocusedElement = null;

    openCartButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            lastFocusedElement = document.activeElement;
            cartModal?.classList.add("is-open");
            // Set focus to the close button inside the drawer for accessibility
            const closeBtn = cartModal?.querySelector('[data-cart-close][aria-label="Close cart"]');
            setTimeout(() => {
                closeBtn?.focus();
            }, 100);
        });
    });

    function closeCart() {
        if (cartModal?.classList.contains("is-open")) {
            cartModal.classList.remove("is-open");
            // Restore focus to the element that opened the drawer
            if (lastFocusedElement) {
                lastFocusedElement.focus();
            }
        }
    }

    closeCartElements.forEach(el => {
        el.addEventListener("click", function (e) {
            e.preventDefault();
            closeCart();
        });
    });

    // Escape key to close cart
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeCart();
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
        const isOpen = navLinks?.classList.toggle('nav__links--open');
        navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
});
