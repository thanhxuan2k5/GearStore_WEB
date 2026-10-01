// ==========================================
// GEARVN STOREFRONT CORE JAVASCRIPT
// ==========================================

const Cart = {
    getKey() {
        return "gearvn_cart_items";
    },

    getItems() {
        try {
            return JSON.parse(localStorage.getItem(this.getKey())) || [];
        } catch {
            return [];
        }
    },

    saveItems(items) {
        localStorage.setItem(this.getKey(), JSON.stringify(items));
        this.updateBadge();
    },

    addItem(product, quantity = 1) {
        // Bắt buộc khách hàng phải đăng nhập mới được thêm vào giỏ hàng
        const token = localStorage.getItem("gearvn_token");
        if (!token) {
            showToast("Vui lòng đăng nhập tài khoản để thêm sản phẩm vào giỏ hàng!", "error");
            sessionStorage.setItem("gearvn_redirect_after_login", window.location.href);
            try {
                sessionStorage.setItem("gearvn_pending_cart_item", JSON.stringify({ product, quantity }));
            } catch (e) {}
            setTimeout(() => {
                window.location.href = "/login";
            }, 800);
            return false;
        }

        const items = this.getItems();
        const existing = items.find(i => i.id === product.id);
        if (existing) {
            existing.quantity += quantity;
        } else {
            items.push({
                id: product.id,
                name: product.name,
                slug: product.slug,
                promo_price: product.promo_price,
                original_price: product.original_price,
                thumbnail: product.thumbnail,
                quantity: quantity
            });
        }
        this.saveItems(items);
        showToast(`Đã thêm "${product.name.substring(0, 30)}..." vào giỏ hàng!`);
        return true;
    },

    removeItem(productId) {
        let items = this.getItems();
        items = items.filter(i => i.id !== productId);
        this.saveItems(items);
    },

    updateQuantity(productId, qty) {
        const items = this.getItems();
        const item = items.find(i => i.id === productId);
        if (item) {
            item.quantity = Math.max(1, qty);
            this.saveItems(items);
        }
    },

    clear() {
        localStorage.removeItem(this.getKey());
        this.updateBadge();
    },

    getTotal() {
        return this.getItems().reduce((sum, i) => sum + (i.promo_price * i.quantity), 0);
    },

    getCount() {
        return this.getItems().reduce((sum, i) => sum + i.quantity, 0);
    },

    updateBadge() {
        const badge = document.getElementById("cartCountBadge");
        if (badge) {
            badge.innerText = this.getCount();
        }
    }
};

// Toast notification
function showToast(message, type = "success") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.style.cssText = "position:fixed;top:20px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:10px;";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.style.cssText = `
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        animation: fadeIn 0.3s ease;
    `;
    toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = '0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Flash sale countdown
function initCountdown() {
    const hoursEl = document.getElementById("fsHours");
    const minsEl = document.getElementById("fsMins");
    const secsEl = document.getElementById("fsSecs");
    if (!hoursEl) return;

    let target = new Date();
    target.setHours(23, 59, 59, 999);

    setInterval(() => {
        const now = new Date();
        const diff = target - now;
        if (diff <= 0) return;

        const h = Math.floor(diff / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);

        hoursEl.innerText = String(h).padStart(2, '0');
        minsEl.innerText = String(m).padStart(2, '0');
        secsEl.innerText = String(s).padStart(2, '0');
    }, 1000);
}

function handleLogout(e) {
    if (e) e.preventDefault();
    try {
        localStorage.removeItem("gearvn_token");
        localStorage.removeItem("gearvn_user");
        sessionStorage.clear();
    } catch (err) {}
    window.location.href = "/logout";
}

function renderHeaderAuth() {
    const authBox = document.getElementById("headerAuthSection");
    if (!authBox) return;

    try {
        const userStr = localStorage.getItem("gearvn_user");
        if (userStr) {
            const user = JSON.parse(userStr);
            const isAdminOrStaff = (user.role === 'admin' || user.role === 'staff');
            
            authBox.innerHTML = `
                <div style="display:flex;align-items:center;gap:6px;">
                    <a href="${isAdminOrStaff ? '/admin/dashboard' : '/profile'}" class="action-btn" style="background:#1e293b;border:1px solid #334155;">
                        <i class="fa-solid fa-user-circle" style="color:var(--primary);"></i>
                        <span style="max-width:110px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${user.full_name || 'Tài khoản'}</span>
                    </a>
                    <a href="/profile" class="action-btn" title="Đổi mật khẩu & Tài khoản" style="padding:6px 10px;">
                        <i class="fa-solid fa-key"></i>
                    </a>
                    <a href="/logout" onclick="handleLogout(event)" class="action-btn" title="Đăng Xuất Khỏi Hệ Thống" style="padding:6px 10px;background:#fff5f5;border:1px solid #fecaca;color:#ef4444;">
                        <i class="fa-solid fa-right-from-bracket"></i>
                    </a>
                </div>
            `;
        } else {
            authBox.innerHTML = `
                <a href="/login" class="action-btn" id="loginBtnHeader">
                    <i class="fa-solid fa-user"></i>
                    <span>Đăng Nhập</span>
                </a>
            `;
        }
    } catch (e) {
        console.error(e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    Cart.updateBadge();
    initCountdown();
    renderHeaderAuth();
});


