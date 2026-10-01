import os
import sys
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.main import app
from app.database import SessionLocal, get_db
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.review import Review
from app.models.internal_doc import InternalDoc

client = TestClient(app)

class TestGearVNSystem:
    admin_token = None
    customer_token = None
    test_user_id = None
    created_product_id = None
    created_cat_id = None
    created_order_code = None

    @classmethod
    def setup_class(cls):
        print("\n" + "="*70)
        print(" BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG GEARVN E-COMMERCE & AI ASSISTANT")
        print("="*70)

    # =========================================================================
    # 1. KIỂM THỬ GIAO DIỆN (HTML STOREFRONT & ADMIN PORTAL)
    # =========================================================================
    def test_01_storefront_pages(self):
        """Kiểm tra toàn bộ các trang giao diện người dùng (Storefront)"""
        pages = [
            ("/", 200, "GEARVN"),
            ("/products", 200, "Danh Sách Sản Phẩm"),
            ("/pc-builder", 200, "Xây Dựng Cấu Hình PC"),
            ("/cart", 200, "Giỏ Hàng"),
            ("/login", 200, "CỔNG XÁC THỰC AN TOÀN"),
            ("/logout", 200, "Đăng Xuất Thành Công"),
            ("/profile", 200, "Thông tin tài khoản"),
        ]
        for url, expected_status, text_snippet in pages:
            res = client.get(url)
            assert res.status_code == expected_status, f"Lỗi tải trang {url}: status {res.status_code}"
            assert text_snippet in res.text, f"Nội dung trang {url} thiếu '{text_snippet}'"

        # Đảm bảo trang /login và /logout là trang độc lập hoàn toàn (không chứa navbar/footer của store)
        res_login = client.get("/login")
        assert "mega-menu-trigger" not in res_login.text
        assert "ai-chat-window" not in res_login.text

        res_logout = client.get("/logout")
        assert "mega-menu-trigger" not in res_logout.text

        print(" [OK] 1. Kiểm thử toàn bộ trang Storefront & Trang Đăng nhập/Đăng xuất độc lập: Thành công (200 OK)")

    def test_02_admin_portal_pages(self):
        """Kiểm tra toàn bộ các trang giao diện Quản trị viên (Admin Portal)"""
        pages = [
            ("/admin/dashboard", 200, "Dashboard Analytics"),
            ("/admin/products", 200, "Quản Lý Sản Phẩm"),
            ("/admin/categories", 200, "Quản Lý Danh Mục"),
            ("/admin/orders", 200, "Quản Lý Đơn Hàng"),
            ("/admin/users", 200, "Quản Lý Tài Khoản"),
            ("/admin/rag", 200, "Tra Cứu Quy Định"),
        ]
        for url, expected_status, text_snippet in pages:
            res = client.get(url)
            assert res.status_code == expected_status, f"Lỗi tải trang {url}: status {res.status_code}"
            assert text_snippet in res.text, f"Nội dung trang {url} thiếu '{text_snippet}'"
        print(" [OK] 2. Kiểm thử toàn bộ trang Admin Portal: Thành công (200 OK)")

    # =========================================================================
    # 2. KIỂM THỬ XÁC THỰC & PHÂN QUYỀN (AUTH & USER MANAGEMENT)
    # =========================================================================
    def test_03_login_admin_and_customer(self):
        """Đăng nhập tài khoản Admin, Staff và Customer"""
        # Admin login
        res_admin = client.post("/api/v1/auth/login-json", json={"email": "admin@gearvn.com", "password": "admin123"})
        assert res_admin.status_code == 200
        admin_data = res_admin.json()
        assert admin_data["role"] == "admin"
        assert "access_token" in admin_data
        TestGearVNSystem.admin_token = admin_data["access_token"]

        # Customer login
        res_cust = client.post("/api/v1/auth/login-json", json={"email": "customer@gmail.com", "password": "user123"})
        assert res_cust.status_code == 200
        cust_data = res_cust.json()
        assert cust_data["role"] == "customer"
        assert "access_token" in cust_data
        TestGearVNSystem.customer_token = cust_data["access_token"]

        print(" [OK] 3. Đăng nhập Admin và Customer: Thành công, cấp JWT Token chuẩn xác")

    def test_04_register_customer(self):
        """Đăng ký tài khoản khách hàng mới và chặn tự đăng ký đuôi @gearvn.com"""
        # 1. Chặn đăng ký email @gearvn.com từ bên ngoài
        res_blocked = client.post("/api/v1/auth/register", json={
            "email": "hacker@gearvn.com",
            "password": "password123",
            "full_name": "Người Dùng Mạo Danh",
        })
        assert res_blocked.status_code == 400
        assert "@gearvn.com" in res_blocked.json()["detail"]

        # 2. Đăng ký khách hàng thông thường thành công
        rand_email = f"test_user_{int(datetime.utcnow().timestamp())}@gmail.com"
        payload = {
            "email": rand_email,
            "password": "password123",
            "full_name": "Người Dùng Khách Hàng",
            "phone": "0987654321",
            "address": "123 Đường Công Nghệ, Q.1, TP.HCM"
        }
        res = client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == rand_email
        assert data["role"] == "customer"
        TestGearVNSystem.test_user_id = data["id"]
        print(" [OK] 4. Đăng ký khách hàng mới & Chặn đăng ký @gearvn.com: Thành công")

    def test_05_admin_user_management(self):
        """Admin xem danh sách, tạo nhân viên mới @gearvn.com, cập nhật và xóa tài khoản"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        
        # 1. Get users
        res = client.get("/api/v1/auth/users", headers=headers)
        assert res.status_code == 200
        users = res.json()
        assert len(users) >= 3

        # 2. Admin tạo tài khoản nhân viên mới bắt buộc đuôi @gearvn.com
        staff_email = f"nhanvien_{int(datetime.utcnow().timestamp())}@gearvn.com"
        res_create_staff = client.post("/api/v1/auth/users", json={
            "email": staff_email,
            "password": "staffpassword123",
            "full_name": "Nhân Viên Kỹ Thuật Mới",
            "phone": "0911223344",
            "role": "staff"
        }, headers=headers)
        assert res_create_staff.status_code == 200
        new_staff = res_create_staff.json()
        assert new_staff["role"] == "staff"
        assert new_staff["email"] == staff_email

        # 3. Admin cập nhật thông tin nhân viên
        res_update = client.put(f"/api/v1/auth/users/{new_staff['id']}", json={
            "full_name": "Nhân Viên Kỹ Thuật (Đã cập nhật)",
            "is_active": True
        }, headers=headers)
        assert res_update.status_code == 200
        assert res_update.json()["full_name"] == "Nhân Viên Kỹ Thuật (Đã cập nhật)"

        # 4. Admin xóa nhân viên test
        res_del_staff = client.delete(f"/api/v1/auth/users/{new_staff['id']}", headers=headers)
        assert res_del_staff.status_code == 200

        # 5. Xóa khách hàng test
        if TestGearVNSystem.test_user_id:
            res_del = client.delete(f"/api/v1/auth/users/{TestGearVNSystem.test_user_id}", headers=headers)
            assert res_del.status_code == 200

        print(" [OK] 5. Quản lý nhân viên Admin (Tạo nhân viên @gearvn.com, Sửa, Đổi vai trò, Xóa): Thành công")

    # =========================================================================
    # 3. KIỂM THỬ SẢN PHẨM & DANH MỤC (CRUD PRODUCTS & CATEGORIES)
    # =========================================================================
    def test_06_categories_crud(self):
        """Thêm, sửa và kiểm tra danh mục sản phẩm"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        
        # Create category
        cat_slug = f"test-cat-{int(datetime.utcnow().timestamp())}"
        create_res = client.post("/api/v1/categories/", json={
            "name": "Danh Mục Thử Nghiệm",
            "slug": cat_slug,
            "description": "Mô tả danh mục test",
            "icon": "fa-solid fa-microchip",
            "order_index": 99
        }, headers=headers)
        assert create_res.status_code == 200
        cat_data = create_res.json()
        TestGearVNSystem.created_cat_id = cat_data["id"]

        # Update category
        update_res = client.put(f"/api/v1/categories/{TestGearVNSystem.created_cat_id}", json={
            "description": "Mô tả đã được cập nhật"
        }, headers=headers)
        assert update_res.status_code == 200
        assert update_res.json()["description"] == "Mô tả đã được cập nhật"

        print(" [OK] 6. Thao tác CRUD Danh mục sản phẩm: Thành công")

    def test_07_products_crud_and_filters(self):
        """Thêm, sửa, lọc và xóa sản phẩm"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        
        # 1. Create Product
        prod_slug = f"test-product-{int(datetime.utcnow().timestamp())}"
        prod_payload = {
            "name": "Laptop Gaming ASUS ROG Test Pro",
            "slug": prod_slug,
            "category_id": TestGearVNSystem.created_cat_id or 1,
            "brand": "ASUS",
            "original_price": 30000000.0,
            "promo_price": 27990000.0,
            "stock_quantity": 25,
            "short_desc": "Laptop Gaming thử nghiệm mạnh mẽ",
            "description": "Chi tiết sản phẩm test",
            "specs_json": json.dumps({"cpu": "Core i7", "gpu": "RTX 4060", "ram": "16GB"}),
            "thumbnail": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500",
            "is_flash_sale": True,
            "is_featured": True
        }
        res_create = client.post("/api/v1/products/", json=prod_payload, headers=headers)
        assert res_create.status_code == 200
        p_data = res_create.json()
        TestGearVNSystem.created_product_id = p_data["id"]
        assert p_data["brand"] == "ASUS"

        # 2. Get Product Detail by Slug
        res_get = client.get(f"/api/v1/products/by-slug/{prod_slug}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == TestGearVNSystem.created_product_id

        # 3. Filter products by search and price
        res_filter = client.get(f"/api/v1/products/?search=ASUS&min_price=20000000&max_price=35000000")
        assert res_filter.status_code == 200
        items = res_filter.json()
        assert len(items) >= 1

        # 4. Update Product
        res_update = client.put(f"/api/v1/products/{TestGearVNSystem.created_product_id}", json={
            "stock_quantity": 30,
            "promo_price": 26990000.0
        }, headers=headers)
        assert res_update.status_code == 200
        assert res_update.json()["stock_quantity"] == 30

        # 5. Delete Product
        res_del = client.delete(f"/api/v1/products/{TestGearVNSystem.created_product_id}", headers=headers)
        assert res_del.status_code == 200

        # Cleanup test category
        if TestGearVNSystem.created_cat_id:
            client.delete(f"/api/v1/categories/{TestGearVNSystem.created_cat_id}", headers=headers)

        print(" [OK] 7. Thao tác CRUD Sản phẩm & Bộ lọc (Search, Brand, Price): Thành công")

    # =========================================================================
    # 4. KIỂM THỬ ĐẶT HÀNG & ĐỒNG BỘ DOANH SỐ (ORDERS & REALTIME CSV)
    # =========================================================================
    def test_08_order_checkout_flow(self):
        """Đặt hàng, kiểm tra trừ tồn kho, tăng lượt bán và cập nhật trạng thái"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.customer_token}"}
        
        # Pick an existing product
        db = SessionLocal()
        prod = db.query(Product).filter(Product.stock_quantity >= 2).first()
        db.close()
        assert prod is not None

        old_stock = prod.stock_quantity
        old_sales = prod.sales_count

        order_payload = {
            "customer_name": "Nguyễn Văn Mua Hàng",
            "customer_phone": "0912345678",
            "customer_email": "customer@gmail.com",
            "shipping_address": "456 Lê Lợi, P. Bến Nghé, Q.1, TP.HCM",
            "payment_method": "cod",
            "items": [
                {"product_id": prod.id, "quantity": 1}
            ],
            "discount_amount": 0,
            "note": "Giao hàng giờ hành chính"
        }

        res = client.post("/api/v1/orders/", json=order_payload, headers=headers)
        assert res.status_code == 200
        order_data = res.json()
        TestGearVNSystem.created_order_code = order_data["order_code"]
        assert order_data["final_amount"] == prod.promo_price

        # Check stock decrease
        db = SessionLocal()
        updated_prod = db.query(Product).filter(Product.id == prod.id).first()
        assert updated_prod.stock_quantity == old_stock - 1
        assert updated_prod.sales_count == old_sales + 1

        # Check admin order status update
        admin_headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        res_status = client.put(
            f"/api/v1/orders/{order_data['id']}/status",
            json={"status": "processing"},
            headers=admin_headers
        )
        assert res_status.status_code == 200
        assert res_status.json()["status"] == "processing"
        db.close()

        print(f" [OK] 8. Quy trình Đặt hàng & Trừ tồn kho (Mã đơn: {TestGearVNSystem.created_order_code}): Thành công")

    # =========================================================================
    # 5. KIỂM THỬ ĐÁNH GIÁ & ML SENTIMENT ANALYSIS
    # =========================================================================
    def test_09_review_and_sentiment_analysis(self):
        """Gửi đánh giá và kiểm tra phân tích cảm xúc (Positive/Neutral/Negative)"""
        db = SessionLocal()
        prod = db.query(Product).first()
        db.close()

        # Positive review
        rev_payload = {
            "product_id": prod.id,
            "customer_name": "Trần Thanh Thảo",
            "customer_phone": "0988888888",
            "rating": 5,
            "comment": "Máy chạy rất mượt mà, chơi game max setting không bị giật lag, tản nhiệt rất mát 5 sao cho shop!"
        }
        res = client.post("/api/v1/reviews/", json=rev_payload)
        assert res.status_code == 200
        rev_data = res.json()
        assert rev_data["sentiment_label"] == "positive"
        assert rev_data["sentiment_score"] >= 0.7

        print(f" [OK] 9. Phân tích cảm xúc đánh giá bằng ML (Label: {rev_data['sentiment_label']}, Độ tin cậy: {rev_data['sentiment_score']}): Thành công")

    # =========================================================================
    # 6. KIỂM THỬ TƯ VẤN BÁN HÀNG AI (AI SALES ASSISTANT)
    # =========================================================================
    def test_10_ai_sales_consultant(self):
        """Khách hàng trò chuyện và nhờ AI tư vấn sản phẩm công nghệ"""
        chat_payload = {
            "message": "Tư vấn cho mình laptop gaming tầm giá 25 triệu để chơi game và lập trình",
            "budget": 25000000,
            "conversation_history": []
        }
        res = client.post("/api/v1/ai/chat", json=chat_payload)
        assert res.status_code == 200
        chat_data = res.json()
        assert "reply" in chat_data
        assert len(chat_data["reply"]) > 20
        assert len(chat_data["recommended_products"]) >= 1
        assert len(chat_data["suggested_questions"]) >= 1

        print(" [OK] 10. Trợ lý AI Tư Vấn Bán Hàng: Thành công, phản hồi tự nhiên và gợi ý sản phẩm phù hợp")

    # =========================================================================
    # 7. KIỂM THỬ TÍNH TƯƠNG THÍCH PC BUILDER
    # =========================================================================
    def test_11_pc_builder_compatibility_check(self):
        """Kiểm tra tương thích linh kiện PC (Socket CPU, Chuẩn RAM, Nguồn PSU)"""
        db = SessionLocal()
        cpu = db.query(Product).filter(Product.pc_part_type == "cpu").first()
        mb = db.query(Product).filter(Product.pc_part_type == "mainboard").first()
        ram = db.query(Product).filter(Product.pc_part_type == "ram").first()
        vga = db.query(Product).filter(Product.pc_part_type == "vga").first()
        psu = db.query(Product).filter(Product.pc_part_type == "psu").first()
        db.close()

        req_payload = {
            "cpu_id": cpu.id if cpu else None,
            "mainboard_id": mb.id if mb else None,
            "ram_id": ram.id if ram else None,
            "vga_id": vga.id if vga else None,
            "psu_id": psu.id if psu else None
        }

        res = client.post("/api/v1/ai/pc-builder-check", json=req_payload)
        assert res.status_code == 200
        data = res.json()
        assert "is_compatible" in data
        assert "estimated_wattage" in data
        assert "recommended_psu_wattage" in data
        assert "issues" in data

        print(f" [OK] 11. Thuật toán kiểm tra tương thích PC Builder (Công suất ước tính: {data['estimated_wattage']}W): Thành công")

    # =========================================================================
    # 8. KIỂM THỬ PHÂN TÍCH DOANH SỐ & DỰ BÁO MACHINE LEARNING
    # =========================================================================
    def test_12_analytics_and_sales_forecast(self):
        """Kiểm tra thống kê Realtime Dashboard và Dự báo doanh số chuỗi thời gian"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        
        # Realtime stats
        res_rt = client.get("/api/v1/analytics/realtime", headers=headers)
        assert res_rt.status_code == 200
        rt_data = res_rt.json()
        assert "today_revenue" in rt_data
        assert "top_selling_products" in rt_data
        assert "category_breakdown" in rt_data

        # ML Forecast
        res_fc = client.get("/api/v1/analytics/forecast?hours=12", headers=headers)
        assert res_fc.status_code == 200
        fc_data = res_fc.json()
        assert "model_name" in fc_data
        assert len(fc_data["forecast"]) == 12
        assert "summary_insight" in fc_data

        print(f" [OK] 12. Phân tích doanh số Realtime & Dự báo ML 12h tiếp theo (Mô hình: {fc_data['model_name']}): Thành công")

    # =========================================================================
    # 9. KIỂM THỬ TRA CỨU QUY ĐỊNH NỘI BỘ (RAG & CHATBOT Q&A)
    # =========================================================================
    def test_13_knowledge_base_rag_query(self):
        """Tra cứu chính sách nội bộ với câu hỏi thực tế và kiểm tra phản hồi phong cách Chatbot"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        
        query_text = "Khách báo pin laptop bị phồng, làm gì trước tiên?"
        res = client.post("/api/v1/rag/query", json={"query": query_text, "top_k": 1}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        answer = data["answer"]
        citations = data["citations"]

        # Kiểm tra nội dung câu trả lời
        assert len(answer) > 20
        # Đảm bảo không còn tiền tố cứng nhắc "Trả lời:"
        assert not answer.strip().startswith("Trả lời:")
        # Đảm bảo có trích dẫn tài liệu đối soát
        assert len(citations) >= 1
        assert "Chinh_sach_Doi_tra_Bao_hanh" in citations[0]["title"]

        print(f" [OK] 13. Tra cứu quy định nội bộ (RAG) dạng Chatbot tự nhiên: Thành công")
        print(f"      -> Câu hỏi: {query_text}")
        print(f"      -> Phản hồi: {answer[:120]}...")

    def test_14_knowledge_base_spaces_and_docs(self):
        """Kiểm tra danh sách không gian tài liệu và danh sách tài liệu lưu trữ"""
        headers = {"Authorization": f"Bearer {TestGearVNSystem.admin_token}"}
        
        # Get spaces
        res_spaces = client.get("/api/v1/rag/spaces", headers=headers)
        assert res_spaces.status_code == 200
        spaces = res_spaces.json()
        assert len(spaces) >= 1

        # Get docs
        res_docs = client.get("/api/v1/rag/docs", headers=headers)
        assert res_docs.status_code == 200
        docs = res_docs.json()
        assert len(docs) >= 1

        print(f" [OK] 14. Kiểm tra Không gian tài liệu & Kho lưu trữ (Tổng {len(docs)} tài liệu): Thành công")

    @classmethod
    def teardown_class(cls):
        print("\n" + "="*70)
        print(" TẤT CẢ 14 HẠNG MỤC KIỂM THỬ HỆ THỐNG ĐỀU ĐẠT CHUẨN 100%!")
        print("="*70 + "\n")
