// ==========================================
// GEARVN PC BUILDER INTERACTIVE ENGINE
// ==========================================

const PCBuilder = {
    selectedParts: {
        cpu: null,
        mainboard: null,
        ram: null,
        vga: null,
        psu: null,
        case: null,
        cooler: null,
        storage: null,
        monitor: null
    },

    currentPartType: null,

    async openSelectorModal(partType) {
        this.currentPartType = partType;
        const modal = document.getElementById("partSelectorModal");
        const listEl = document.getElementById("modalProductList");
        const titleEl = document.getElementById("modalPartTitle");
        
        if (titleEl) titleEl.innerText = `Chọn ${partType.toUpperCase()} cho cấu hình PC`;
        if (listEl) listEl.innerHTML = `<div style="padding:20px;text-align:center;">Đang tải danh sách linh kiện...</div>`;
        if (modal) modal.style.display = "flex";

        try {
            const res = await fetch(`/api/v1/products/?pc_part_type=${partType}`);
            const products = await res.json();

            if (!products || products.length === 0) {
                listEl.innerHTML = `<div style="padding:20px;text-align:center;">Chưa có linh kiện cho mục này.</div>`;
                return;
            }

            listEl.innerHTML = products.map(p => `
                <div style="display:flex;align-items:center;justify-content:space-between;padding:12px;border-bottom:1px solid #eee;">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <img src="${p.thumbnail || 'https://via.placeholder.com/60'}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;">
                        <div>
                            <div style="font-weight:600;font-size:13px;max-width:380px;">${p.name}</div>
                            <div style="color:#e30019;font-weight:700;font-size:13px;">${p.promo_price.toLocaleString()} đ</div>
                        </div>
                    </div>
                    <button class="btn btn-primary" onclick="PCBuilder.selectPart('${partType}', ${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.promo_price}, '${p.thumbnail || ''}')">
                        <i class="fa-solid fa-plus"></i> Chọn
                    </button>
                </div>
            `).join("");

        } catch (e) {
            listEl.innerHTML = `<div style="padding:20px;color:red;text-align:center;">Lỗi tải dữ liệu.</div>`;
        }
    },

    closeModal() {
        const modal = document.getElementById("partSelectorModal");
        if (modal) modal.style.display = "none";
    },

    selectPart(partType, id, name, price, thumbnail) {
        this.selectedParts[partType] = { id, name, price, thumbnail };
        this.closeModal();
        this.renderRow(partType);
        this.checkCompatibilityAndTotals();
    },

    removePart(partType) {
        this.selectedParts[partType] = null;
        this.renderRow(partType);
        this.checkCompatibilityAndTotals();
    },

    renderRow(partType) {
        const item = this.selectedParts[partType];
        const rowEl = document.getElementById(`row-${partType}`);
        if (!rowEl) return;

        if (item) {
            rowEl.innerHTML = `
                <div class="part-info">
                    <img src="${item.thumbnail || 'https://via.placeholder.com/50'}" style="width:44px;height:44px;object-fit:cover;border-radius:6px;">
                    <div>
                        <div style="font-weight:700;font-size:14px;color:#1e293b;">${item.name}</div>
                        <div style="color:#e30019;font-weight:800;font-size:14px;">${item.price.toLocaleString()} đ</div>
                    </div>
                </div>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-outline" onclick="PCBuilder.openSelectorModal('${partType}')">Đổi</button>
                    <button class="btn btn-outline" style="color:red;" onclick="PCBuilder.removePart('${partType}')"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;
        } else {
            rowEl.innerHTML = `
                <div class="part-info">
                    <div class="part-icon"><i class="fa-solid fa-microchip"></i></div>
                    <div>
                        <div style="font-weight:700;font-size:14px;">${partType.toUpperCase()}</div>
                        <div style="color:#64748b;font-size:12px;">Chưa chọn linh kiện</div>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="PCBuilder.openSelectorModal('${partType}')">
                    <i class="fa-solid fa-plus"></i> Chọn linh kiện
                </button>
            `;
        }
    },

    async checkCompatibilityAndTotals() {
        const payload = {
            cpu_id: this.selectedParts.cpu?.id,
            mainboard_id: this.selectedParts.mainboard?.id,
            ram_id: this.selectedParts.ram?.id,
            vga_id: this.selectedParts.vga?.id,
            psu_id: this.selectedParts.psu?.id,
            cooler_id: this.selectedParts.cooler?.id,
            storage_id: this.selectedParts.storage?.id,
            case_id: this.selectedParts.case?.id
        };

        let totalPrice = 0;
        Object.values(this.selectedParts).forEach(p => {
            if (p) totalPrice += p.price;
        });

        const totalEl = document.getElementById("builderTotalPrice");
        if (totalEl) totalEl.innerText = `${totalPrice.toLocaleString()} đ`;

        try {
            const res = await fetch("/api/v1/ai/pc-builder-check", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            const statusBox = document.getElementById("compatStatusBox");
            if (!statusBox) return;

            if (data.is_compatible) {
                let html = `<div style="color:#10b981;font-weight:700;"><i class="fa-solid fa-circle-check"></i> Các linh kiện hoàn toàn tương thích!</div>`;
                html += `<div style="font-size:12px;color:#64748b;margin-top:4px;">Công suất ước tính: <strong>${data.estimated_wattage}W</strong> | Nguồn khuyến nghị: <strong>${data.recommended_psu_wattage}W</strong></div>`;
                if (data.warnings.length > 0) {
                    html += `<div style="margin-top:6px;font-size:12px;color:#f59e0b;">${data.warnings.join("<br>")}</div>`;
                }
                statusBox.innerHTML = html;
            } else {
                statusBox.innerHTML = `
                    <div style="color:#ef4444;font-weight:700;"><i class="fa-solid fa-triangle-exclamation"></i> Phát hiện xung đột linh kiện:</div>
                    <div style="font-size:12px;color:#dc2626;margin-top:4px;">${data.issues.join("<br>")}</div>
                `;
            }
        } catch (e) {
            console.error(e);
        }
    },

    addAllToCart() {
        const token = localStorage.getItem("gearvn_token");
        if (!token) {
            showToast("Vui lòng đăng nhập tài khoản để thêm cấu hình PC vào giỏ hàng!", "error");
            sessionStorage.setItem("gearvn_redirect_after_login", window.location.href);
            setTimeout(() => window.location.href = "/login", 800);
            return;
        }

        let count = 0;
        Object.values(this.selectedParts).forEach(p => {
            if (p) {
                Cart.addItem({
                    id: p.id,
                    name: p.name,
                    slug: "pc-part",
                    promo_price: p.price,
                    original_price: p.price,
                    thumbnail: p.thumbnail
                }, 1);
                count++;
            }
        });

        if (count > 0) {
            showToast(`Đã thêm ${count} linh kiện của cấu hình PC vào giỏ hàng!`);
            setTimeout(() => window.location.href = "/cart", 1000);
        } else {
            showToast("Vui lòng chọn ít nhất 1 linh kiện trước khi thêm vào giỏ hàng.", "error");
        }
    }
};
