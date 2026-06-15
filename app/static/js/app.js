// Client-side Cart & Payment controller for Mama Mboga

let cart = JSON.parse(localStorage.getItem("mama_cart")) || [];

document.addEventListener("DOMContentLoaded", function () {
    // 1. Initial State
    updateCartUI();
    setupCategoryFilters();
    setupFuzzySearch();
    setupCartActions();
    
    // 2. Checkout Page logic
    if (document.getElementById("checkout-summary-items")) {
        renderCheckoutSummary();
        setupPaymentSimulations();
    }
});

// Update Cart Badge and Modal lists
function updateCartUI() {
    const badge = document.getElementById("cart-badge-count");
    const modalItemsContainer = document.getElementById("cart-modal-items");
    const emptyMsg = document.getElementById("cart-empty-message");
    const clearBtn = document.getElementById("clear-cart-modal-btn");
    const checkoutBtn = document.getElementById("checkout-modal-btn");
    const totalDisplay = document.getElementById("cart-total-price-display");

    // Compute metrics
    let totalItems = 0;
    let totalPrice = 0;
    cart.forEach(item => {
        totalItems += item.quantity;
        totalPrice += item.price * item.quantity;
    });

    // Update Badge
    if (badge) {
        badge.innerText = totalItems;
        if (totalItems > 0) {
            badge.classList.remove("d-none");
        } else {
            badge.classList.add("d-none");
        }
    }

    // Update Modal
    if (modalItemsContainer) {
        modalItemsContainer.innerHTML = "";
        
        if (cart.length === 0) {
            if (emptyMsg) emptyMsg.classList.remove("d-none");
            if (clearBtn) clearBtn.disabled = true;
            if (checkoutBtn) checkoutBtn.classList.add("disabled");
            if (totalDisplay) totalDisplay.innerText = "KSh 0.00";
        } else {
            if (emptyMsg) emptyMsg.classList.add("d-none");
            if (clearBtn) clearBtn.disabled = false;
            if (checkoutBtn) checkoutBtn.classList.remove("disabled");
            
            cart.forEach(item => {
                const itemRow = `
                    <div class="cart-item-row">
                        <img src="${item.image}" alt="${item.name}" class="cart-item-img shadow-sm border">
                        <div>
                            <h6 class="fw-bold text-dark mb-0">${item.name}</h6>
                            <small class="text-muted">KSh ${item.price.toFixed(2)} / ${item.unit}</small>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <button class="btn btn-sm btn-outline-success btn-quantity px-2 py-0" onclick="adjustItemQty('${item.id}', -1)">&minus;</button>
                            <span class="fw-bold px-1">${item.quantity}</span>
                            <button class="btn btn-sm btn-outline-success btn-quantity px-2 py-0" onclick="adjustItemQty('${item.id}', 1)">&plus;</button>
                            <button class="btn btn-sm btn-outline-danger ms-2 py-1 px-2 border-0" onclick="removeItemFromCart('${item.id}')"><i class="fa-solid fa-trash-can"></i></button>
                        </div>
                    </div>
                `;
                modalItemsContainer.insertAdjacentHTML("beforeend", itemRow);
            });
            
            if (totalDisplay) {
                totalDisplay.innerText = `KSh ${totalPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }
        }
    }
}

// Adjust Item quantity in cart
window.adjustItemQty = function(id, amount) {
    const item = cart.find(i => i.id === id);
    if (item) {
        item.quantity += amount;
        if (item.quantity <= 0) {
            cart = cart.filter(i => i.id !== id);
        }
        localStorage.setItem("mama_cart", JSON.stringify(cart));
        updateCartUI();
        if (document.getElementById("checkout-summary-items")) {
            renderCheckoutSummary();
        }
    }
};

// Remove single item from cart
window.removeItemFromCart = function(id) {
    cart = cart.filter(item => item.id !== id);
    localStorage.setItem("mama_cart", JSON.stringify(cart));
    updateCartUI();
    if (document.getElementById("checkout-summary-items")) {
        renderCheckoutSummary();
    }
};

// Clear all cart contents
function setupCartActions() {
    const clearBtn = document.getElementById("clear-cart-modal-btn");
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            if (confirm("Are you sure you want to empty your shopping cart?")) {
                cart = [];
                localStorage.removeItem("mama_cart");
                updateCartUI();
            }
        });
    }

    // Add product to cart button handlers
    const catalogContainer = document.getElementById("products-grid");
    if (catalogContainer) {
        catalogContainer.addEventListener("click", function(e) {
            const btn = e.target.closest(".add-to-cart-action-btn");
            if (btn) {
                const id = btn.getAttribute("data-id");
                const name = btn.getAttribute("data-name");
                const price = parseFloat(btn.getAttribute("data-price"));
                const image = btn.getAttribute("data-image");
                const unit = btn.getAttribute("data-unit");

                const existingItem = cart.find(item => item.id === id);
                if (existingItem) {
                    existingItem.quantity += 1;
                } else {
                    cart.push({ id, name, price, image, quantity: 1, unit });
                }

                localStorage.setItem("mama_cart", JSON.stringify(cart));
                updateCartUI();

                // Button Micro-interaction: Change text temporarily to show checkmark
                const originalHTML = btn.innerHTML;
                btn.innerHTML = `<i class="fa-solid fa-check me-1"></i> Added!`;
                btn.classList.replace("btn-outline-success", "btn-success");
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.classList.replace("btn-success", "btn-outline-success");
                }, 1000);
            }
        });
    }
}

// Category Filters toolbar selector
function setupCategoryFilters() {
    const filterContainer = document.getElementById("category-filters");
    if (filterContainer) {
        filterContainer.addEventListener("click", function (e) {
            const btn = e.target.closest(".filter-btn");
            if (!btn) return;

            // Update active state
            filterContainer.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active", "btn-success"));
            filterContainer.querySelectorAll(".filter-btn").forEach(b => b.classList.add("btn-outline-success"));
            btn.classList.remove("btn-outline-success");
            btn.classList.add("active", "btn-success");

            const selectedCat = btn.getAttribute("data-category");
            const cards = document.querySelectorAll(".product-card-item");
            
            cards.forEach(card => {
                const cardCat = card.getAttribute("data-category");
                if (selectedCat === "all" || cardCat === selectedCat) {
                    card.classList.remove("d-none");
                } else {
                    card.classList.add("d-none");
                }
            });
        });
    }
}

// Fuzzy Search matching names
function setupFuzzySearch() {
    const search = document.getElementById("search-input");
    if (search) {
        search.addEventListener("keyup", function () {
            const value = this.value.toLowerCase().trim();
            const cards = document.querySelectorAll(".product-card-item");
            
            cards.forEach(card => {
                const name = card.getAttribute("data-name");
                if (name.includes(value)) {
                    card.classList.remove("d-none");
                } else {
                    card.classList.add("d-none");
                }
            });
        });
    }
}

// Render Order Summary in Checkout Page
let verifiedTransactionDetails = null; // Stored validation properties

function renderCheckoutSummary() {
    const container = document.getElementById("checkout-summary-items");
    const subtotalDisplay = document.getElementById("summary-subtotal");
    const grandDisplay = document.getElementById("summary-grand-total");
    
    if (!container) return;
    
    container.innerHTML = "";
    
    if (cart.length === 0) {
        container.innerHTML = `<p class="text-muted text-center py-3">No items in your cart. <a href="/" class="text-success">Go shop first!</a></p>`;
        subtotalDisplay.innerText = "KSh 0.00";
        grandDisplay.innerText = "KSh 150.00";
        return;
    }
    
    let subtotal = 0;
    cart.forEach(item => {
        subtotal += item.price * item.quantity;
        const itemSummary = `
            <div class="d-flex justify-content-between align-items-center mb-2 fs-7">
                <span class="text-muted" style="max-width: 250px;">
                    <strong class="text-dark">${item.name}</strong> 
                    <span class="badge bg-secondary-subtle text-secondary ms-1">x${item.quantity}</span>
                </span>
                <span class="text-dark fw-bold">KSh ${(item.price * item.quantity).toFixed(2)}</span>
            </div>
        `;
        container.insertAdjacentHTML("beforeend", itemSummary);
    });

    const deliveryFee = 150.0;
    const grandTotal = subtotal + deliveryFee;
    
    subtotalDisplay.innerText = `KSh ${subtotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    grandDisplay.innerText = `KSh ${grandTotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
}

// Simulated Payment Verification methods
function setupPaymentSimulations() {
    const mpesaOption = document.getElementsByName("mpesa-option");
    const stkPanel = document.getElementById("stk-push-panel");
    const paybillPanel = document.getElementById("paybill-panel");
    const completeBtn = document.getElementById("complete-purchase-btn");
    
    // Toggle M-Pesa STK/Paybill sub-sections
    mpesaOption.forEach(opt => {
        opt.addEventListener("change", function () {
            if (this.value === "stk") {
                stkPanel.classList.remove("d-none");
                paybillPanel.classList.add("d-none");
                completeBtn.disabled = !verifiedTransactionDetails || verifiedTransactionDetails.method !== 'mpesa_stk';
            } else {
                stkPanel.classList.add("d-none");
                paybillPanel.classList.remove("d-none");
                const paybillCode = document.getElementById("mpesa-code").value.trim();
                completeBtn.disabled = paybillCode.length !== 10;
            }
        });
    });

    // 1. M-Pesa STK push simulation
    const triggerStkBtn = document.getElementById("trigger-stk-btn");
    const stkPhoneInput = document.getElementById("stk-phone");
    const stkLoader = document.getElementById("stk-loader");
    const stkStatusText = document.getElementById("stk-status-text");

    // Populate phone number initially if available in form
    const mainPhone = document.getElementById("shipping-phone");
    if (mainPhone && stkPhoneInput) {
        stkPhoneInput.value = mainPhone.value;
        mainPhone.addEventListener("input", function() {
            stkPhoneInput.value = this.value;
        });
    }

    if (triggerStkBtn) {
        triggerStkBtn.addEventListener("click", function() {
            const phone = stkPhoneInput.value.trim();
            if (!/^(07|01)\d{8}$/.test(phone)) {
                alert("Please enter a valid Kenyan phone number starting with 07 or 01 (10 digits).");
                return;
            }

            let subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            const amount = subtotal + 150; // Total price

            // Show simulated spinner
            stkLoader.classList.remove("d-none");
            stkStatusText.innerText = "Connecting to Safaricom Daraja API...";
            triggerStkBtn.disabled = true;

            // Make POST API trigger
            fetch("/api/payment/stk-push", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone: phone, amount: amount })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    stkStatusText.innerHTML = `<i class="fa-solid fa-bell text-warning animate-bounce mb-2 d-block fs-3"></i> STK prompt pushed to ${phone}. Enter M-Pesa PIN now.`;
                    
                    // Simulate user entering PIN and Safaricom callback after 3.5 seconds
                    setTimeout(() => {
                        stkLoader.innerHTML = `
                            <div class="text-success mb-2"><i class="fa-solid fa-circle-check fs-2"></i></div>
                            <p class="mb-0 text-success fw-bold">M-Pesa Payment Received & Approved!</p>
                            <small class="text-muted font-monospace">Receipt Code: ${data.transaction_id}</small>
                        `;
                        
                        verifiedTransactionDetails = {
                            method: "mpesa",
                            transaction_id: data.transaction_id
                        };
                        
                        completeBtn.disabled = false; // Enable final checkout execution
                    }, 3500);
                } else {
                    stkLoader.classList.add("d-none");
                    triggerStkBtn.disabled = false;
                    alert("STK push simulation failed: " + data.message);
                }
            })
            .catch(err => {
                stkLoader.classList.add("d-none");
                triggerStkBtn.disabled = false;
                alert("Error connecting to server STK endpoint.");
            });
        });
    }

    // 2. M-Pesa Paybill transaction code listener
    const mpesaCodeInput = document.getElementById("mpesa-code");
    if (mpesaCodeInput) {
        mpesaCodeInput.addEventListener("input", function() {
            const val = this.value.toUpperCase().trim();
            this.value = val;
            
            if (val.length === 10) {
                verifiedTransactionDetails = {
                    method: "mpesa",
                    transaction_id: val
                };
                completeBtn.disabled = false;
            } else {
                completeBtn.disabled = true;
            }
        });
    }

    // 3. PayPal Simulation
    const paypalBtn = document.getElementById("paypal-simulate-btn");
    const paypalLoader = document.getElementById("paypal-loader");
    if (paypalBtn) {
        paypalBtn.addEventListener("click", function() {
            paypalBtn.disabled = true;
            paypalLoader.classList.remove("d-none");
            
            setTimeout(() => {
                paypalLoader.innerHTML = `
                    <div class="text-success mb-2"><i class="fa-solid fa-circle-check fs-2"></i></div>
                    <p class="mb-0 text-success fw-bold">PayPal Account Verified & Charged!</p>
                    <small class="text-muted font-monospace">Ref: PAYPAL-${Math.random().toString(36).substr(2, 9).toUpperCase()}</small>
                `;
                
                verifiedTransactionDetails = {
                    method: "paypal",
                    transaction_id: "PAYPAL_" + Math.random().toString(36).substr(2, 8).toUpperCase()
                };
                completeBtn.disabled = false;
            }, 2000);
        });
    }

    // 4. Visa Credit Card Simulation
    const cardBtn = document.getElementById("card-simulate-btn");
    const cardLoader = document.getElementById("card-loader");
    if (cardBtn) {
        cardBtn.addEventListener("click", function() {
            const holder = document.getElementById("card-holder").value.trim();
            const number = document.getElementById("card-number").value.trim();
            const expiry = document.getElementById("card-expiry").value.trim();
            const cvv = document.getElementById("card-cvv").value.trim();
            
            if (!holder || number.length < 15 || expiry.length < 5 || cvv.length < 3) {
                alert("Please fill in valid Card Details before verifying.");
                return;
            }
            
            cardBtn.disabled = true;
            cardLoader.classList.remove("d-none");
            
            setTimeout(() => {
                cardLoader.innerHTML = `
                    <div class="text-success mb-2"><i class="fa-solid fa-circle-check fs-2"></i></div>
                    <p class="mb-0 text-success fw-bold">Card Authorized Successfully!</p>
                    <small class="text-muted font-monospace">Auth Code: VISA-${Math.random().toString(36).substr(2, 6).toUpperCase()}</small>
                `;
                
                verifiedTransactionDetails = {
                    method: "visa",
                    transaction_id: "VISA_" + Math.random().toString(36).substr(2, 8).toUpperCase()
                };
                completeBtn.disabled = false;
            }, 2000);
        });
    }

    // 5. Checkout Form Final Submission
    const checkoutForm = document.getElementById("checkout-form");
    if (checkoutForm) {
        checkoutForm.addEventListener("submit", function (e) {
            e.preventDefault();
            
            if (cart.length === 0) {
                alert("Your cart is empty. Please add items to checkout.");
                return;
            }

            if (!verifiedTransactionDetails) {
                alert("Please validate your payment choice prior to completing the order.");
                return;
            }

            const shippingName = document.getElementById("shipping-name").value.trim();
            const shippingPhone = document.getElementById("shipping-phone").value.trim();
            const shippingEmail = document.getElementById("shipping-email").value.trim();
            const shippingAddress = document.getElementById("shipping-address").value.trim();

            const orderPayload = {
                shipping: {
                    name: shippingName,
                    phone: shippingPhone,
                    email: shippingEmail,
                    address: shippingAddress
                },
                items: cart,
                payment_method: verifiedTransactionDetails.method,
                payment_details: {
                    transaction_id: verifiedTransactionDetails.transaction_id
                }
            };

            completeBtn.disabled = true;
            completeBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Submitting Order...`;

            fetch("/api/order/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(orderPayload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(`Congratulations! Your order has been placed successfully. Order Reference: ${data.order_id}`);
                    // Clear cart
                    cart = [];
                    localStorage.removeItem("mama_cart");
                    // Redirect Home
                    window.location.href = "/";
                } else {
                    alert("Order placement failed: " + data.message);
                    completeBtn.disabled = false;
                    completeBtn.innerHTML = `<i class="fa-solid fa-circle-check me-2"></i> Submit and Complete Order`;
                }
            })
            .catch(err => {
                alert("Network error: Could not complete order registration.");
                completeBtn.disabled = false;
                completeBtn.innerHTML = `<i class="fa-solid fa-circle-check me-2"></i> Submit and Complete Order`;
            });
        });
    }
}
