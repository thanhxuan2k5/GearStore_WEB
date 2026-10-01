# HỆ THỐNG BÁN HÀNG CÔNG NGHỆ GEARVN & AI/ML ECOSYSTEM

Hệ thống thương mại điện tử chuyên biệt cho sản phẩm công nghệ (Laptop Gaming, PC Builder, Linh kiện phần cứng, Gaming Gear) xây dựng bằng **FastAPI (Python)**, giao diện **HTML5/CSS3/JavaScript phong cách GearVN**, tích hợp **Trợ lý AI tư vấn bán hàng**, **RAG Chatbot tra cứu nội bộ** và **Mô hình Machine Learning phân loại đánh giá & dự báo doanh số bán hàng Realtime với file `.csv`**.

---

## 🌟 CÁC TÍNH NĂNG NỔI BẬT

### 1. Storefront Khách Hàng (Chuẩn phong cách GearVN)
- **Mega Menu thông minh:** Danh mục đa cấp laptop, PC gaming, VGA, CPU, RAM, màn hình kèm icon trực quan.
- **Flash Sale Giờ Vàng:** Đồng hồ đếm ngược, nhãn giảm giá và thanh trạng thái còn hàng.
- **Bộ lọc thông số chuyên sâu (Specs Filter):** Lọc theo CPU (i5, i7, i9, Ryzen), GPU (RTX 4050, 4060, 4070, 4080), RAM, thương hiệu và mức giá.
- **Công cụ PC Builder:** Tự do chọn CPU, Mainboard, RAM, VGA, Nguồn... Hệ thống tự động kiểm tra tương thích Socket và tính toán công suất nguồn (PSU Wattage).
- **Trang Chi tiết sản phẩm:** Thư viện ảnh, bảng thông số kỹ thuật, quà tặng kèm, và hệ thống đánh giá sản phẩm.
- **Giỏ hàng & Đặt hàng (Checkout):** Mua nhanh, thanh toán COD / QR Bank / VNPAY.

### 2. Trợ Lý AI Tư Vấn Bán Hàng 24/7 (AI Sales Assistant)
- Widget chat nổi góc phải màn hình, hỗ trợ tư vấn bằng tiếng Việt tự nhiên.
- Tự động bóc tách ngân sách và mục đích sử dụng (Gaming, Đồ họa 4K, Văn phòng sinh viên...) để query database và đề xuất 2-3 sản phẩm tối ưu nhất kèm link xem nhanh.

### 3. Cổng Quản Trị (Admin Portal) & RAG Chatbot Nội Bộ
- **CRUD Quản lý:** Thêm, sửa, xóa Sản phẩm, Danh mục, Đơn hàng và cập nhật trạng thái đơn hàng.
- **RAG Chatbot Nội bộ (Internal Knowledge Base):** Cho phép nhân viên/kỹ thuật hỏi đáp tự động về chính sách bảo hành 30 ngày, tiêu chuẩn điểm chết màn hình ASUS/LG, quy trình đổi trả và chính sách chiết khấu nhân viên. Kèm trích dẫn tài liệu nguồn chính xác.

### 4. Machine Learning & Realtime Sales Data Pipeline
- **Realtime CSV Sync:** Mọi đơn hàng mới phát sinh đều được tự động ghi nhận theo thời gian thực vào file `data/sales_realtime.csv` phân chia theo ngày/giờ.
- **Sentiment Analysis:** Phân loại cảm xúc đánh giá của khách hàng (Tích cực, Trung tính, Tiêu cực) tự động khi có review mới.
- **Time-Series Sales Forecasting:** Mô hình hồi quy chuỗi thời gian kết hợp đặc trưng chu kỳ giờ trong ngày (Hourly Cyclical Sine/Cosine Features) dự báo doanh số cho các khung giờ tiếp theo, hiển thị trực quan trên biểu đồ Chart.js.

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY DỰ ÁN

### 1. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy Server:
```bash
python run.py
```
Hoặc:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Truy cập các cổng giao diện:
- 🌐 **Trang chủ Khách hàng (GearVN Store):** `http://127.0.0.1:8000/`
- 🛠️ **Công cụ PC Builder:** `http://127.0.0.1:8000/pc-builder`
- 📊 **Admin Dashboard & ML Forecast:** `http://127.0.0.1:8000/admin/dashboard`
- 🤖 **RAG Chatbot Tra Cứu Nội Bộ:** `http://127.0.0.1:8000/admin/rag`
- 📦 **Quản lý Sản phẩm (Admin):** `http://127.0.0.1:8000/admin/products`
- 📖 **Tài liệu API Swagger (OpenAPI):** `http://127.0.0.1:8000/docs`

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN

```
d:\BTCK\
├── app/
│   ├── main.py                  # Điểm khởi chạy FastAPI, cấu hình template & static
│   ├── config.py                # Cấu hình biến môi trường, đường dẫn file dữ liệu
│   ├── database.py              # Kết nối SQLAlchemy
│   ├── models/                  # Database Models (User, Product, Category, Order, Review, Doc)
│   ├── schemas/                 # Pydantic Schemas xác thực dữ liệu API
│   ├── api/                     # REST API Routers (Auth, Products, Categories, Orders, AI, RAG, Analytics)
│   ├── services/                # Business Logic, AI Assistant, RAG Engine, ML Forecast, CSV Sync
│   ├── core/                    # Security JWT, Seed Data mẫu
│   ├── static/                  # CSS (GearVN Theme), JS (Cart, AI Chat, PC Builder, Admin Charts)
│   └── templates/               # Jinja2 HTML Templates (Storefront & Admin)
├── data/                        # File DB SQLite và file log sales_realtime.csv
├── requirements.txt             # Danh sách thư viện Python
├── run.py                       # Script khởi động server
└── README.md                    # Hướng dẫn chi tiết
```
