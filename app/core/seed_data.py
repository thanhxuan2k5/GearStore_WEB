import os
import json
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.product import Product
from app.models.review import Review
from app.models.internal_doc import InternalDoc
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod
from app.models.sales_log import SalesLog
from app.core.security import get_password_hash
from app.services.csv_sync_service import append_sales_record, init_csv_file

def seed_database(db: Session):
    # Check if data already seeded
    if db.query(User).first() is not None:
        return

    print("🌱 Đang khởi tạo dữ liệu mẫu cho hệ thống GearVN Tech Store...")

    # 1. USERS
    users = [
        User(
            email="admin@gearvn.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Quản Trị Viên Hệ Thống",
            phone="0901234567",
            address="Showroom GearVN 78-80 Hoàng Hoa Thám, P.12, Q.Tân Bình, TP.HCM",
            role=UserRole.ADMIN,
            is_active=True
        ),
        User(
            email="staff@gearvn.com",
            hashed_password=get_password_hash("staff123"),
            full_name="Nguyễn Văn Nhân Viên",
            phone="0909888999",
            address="Chi nhánh GearVN Trần Hưng Đạo, Q.1, TP.HCM",
            role=UserRole.STAFF,
            is_active=True
        ),
        User(
            email="customer@gmail.com",
            hashed_password=get_password_hash("user123"),
            full_name="Trần Minh Khách Hàng",
            phone="0918777666",
            address="Số 45 Lê Lợi, P.Bến Nghé, Quận 1, TP.HCM",
            role=UserRole.CUSTOMER,
            is_active=True
        )
    ]
    db.add_all(users)
    db.commit()

    # 2. CATEGORIES
    cats = [
        Category(name="Laptop Gaming", slug="laptop-gaming", icon="fa-laptop", description="Laptop gaming cấu hình cao, đồ họa mạnh mẽ"),
        Category(name="Laptop Văn Phòng", slug="laptop-van-phong", icon="fa-laptop-code", description="Laptop mỏng nhẹ, pin trâu cho học sinh sinh viên"),
        Category(name="PC G-Studio / PC Gaming", slug="pc-gaming", icon="fa-desktop", description="Dàn PC Gaming & Đồ họa chuyên nghiệp lắp sẵn"),
        Category(name="Card Màn Hình (VGA)", slug="vga-card-man-hinh", icon="fa-microchip", description="Nvidia GeForce RTX 40 Series, AMD Radeon RX"),
        Category(name="Bộ Vi Xử Lý (CPU)", slug="cpu-bo-vi-xu-ly", icon="fa-memory", description="Intel Core Gen 14, AMD Ryzen 7000/9000 Series"),
        Category(name="Bo Mạch Chủ (Mainboard)", slug="mainboard-bo-mach-chu", icon="fa-server", description="Mainboard ASUS, MSI, Gigabyte Z790/B760/X670"),
        Category(name="Bộ Nhớ RAM", slug="ram-bo-nho", icon="fa-ticket-alt", description="RAM DDR4, DDR5 Kingston Fury, Corsair Vengeance"),
        Category(name="Ổ Cứng SSD / HDD", slug="o-cung-ssd", icon="fa-hdd", description="SSD M.2 NVMe PCIe Gen 4x4 tốc độ cao"),
        Category(name="Nguồn Máy Tính (PSU)", slug="nguon-may-tinh-psu", icon="fa-bolt", description="Nguồn chuẩn 80 Plus Bronze, Gold, Platinum"),
        Category(name="Vỏ Case Máy Tính", slug="case-may-tinh", icon="fa-box", description="Vỏ case kính cường lực LED RGB tản nhiệt tốt"),
        Category(name="Tản Nhiệt CPU", slug="tan-nhiet-cpu", icon="fa-fan", description="Tản nhiệt nước AIO 240/360, tản tháp khí"),
        Category(name="Màn Hình Máy Tính", slug="man-hinh-may-tinh", icon="fa-tv", description="Màn hình gaming 144Hz - 240Hz, màn hình đồ họa 4K IPS"),
        Category(name="Bàn Phím Cơ", slug="ban-phim-co", icon="fa-keyboard", description="Bàn phím cơ custom, switch nảy, hot-swap, RGB"),
        Category(name="Chuột Gaming", slug="chuot-gaming", icon="fa-mouse", description="Chuột không dây siêu nhẹ, mắt đọc quang học chuẩn Esports")
    ]
    db.add_all(cats)
    db.commit()

    cat_map = {c.slug: c.id for c in db.query(Category).all()}

    # 3. PRODUCTS (GearVN Style Tech Products)
    products = [
        # Laptop Gaming
        Product(
            category_id=cat_map["laptop-gaming"],
            name="Laptop Gaming ASUS ROG Strix G16 G614JVR-N4011W (i9-14900HX / RTX 4080 12GB / 32GB RAM / 1TB SSD / 16' 2.5K 240Hz)",
            slug="asus-rog-strix-g16-g614jvr",
            brand="ASUS",
            original_price=69990000,
            promo_price=64990000,
            stock_quantity=15,
            thumbnail="https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80",
            short_desc="Siêu phẩm laptop gaming đỉnh cao với Intel Core i9 Gen 14th cùng Card đồ họa RTX 4080 12GB TGP 175W. Màn hình ROG Nebula 2.5K 240Hz cực đỉnh.",
            full_desc="ASUS ROG Strix G16 mang đến sức mạnh không giới hạn cho các game thủ và streamer chuyên nghiệp. Công nghệ tản nhiệt 3 quạt Tri-Fan, keo tản nhiệt kim loại lỏng Conductonaut Extreme giúp duy trì mức nhiệt mát mẻ.",
            specs_json=json.dumps({
                "cpu": "Intel Core i9-14900HX (24 nhân, 32 luồng, up to 5.8GHz)",
                "gpu": "NVIDIA GeForce RTX 4080 12GB GDDR6 (175W TGP)",
                "ram": "32GB DDR5 5600MHz (2x16GB)",
                "storage": "1TB M.2 NVMe PCIe 4.0 SSD",
                "screen": "16 inch 2.5K (2560x1600) IPS 240Hz, 100% DCI-P3, G-Sync",
                "battery": "90WHrs, 4-cell Li-ion",
                "weight": "2.50 kg"
            }),
            is_flash_sale=True,
            is_featured=True,
            rating_avg=5.0,
            rating_count=28,
            sales_count=45
        ),
        Product(
            category_id=cat_map["laptop-gaming"],
            name="Laptop Gaming Acer Nitro V 15 ANV15-51-57B2 (i5-13420H / RTX 4050 6GB / 16GB RAM / 512GB SSD / 15.6' FHD 144Hz)",
            slug="acer-nitro-v-15-anv15",
            brand="Acer",
            original_price=24990000,
            promo_price=20990000,
            stock_quantity=35,
            thumbnail="https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
            short_desc="Laptop gaming quốc dân phân khúc 20 triệu. Chiến mượt mà mọi tựa game Esport và game AAA với RTX 4050 6GB hỗ trợ DLSS 3.",
            specs_json=json.dumps({
                "cpu": "Intel Core i5-13420H (8 nhân, 12 luồng)",
                "gpu": "NVIDIA GeForce RTX 4050 6GB GDDR6",
                "ram": "16GB DDR5 5200MHz",
                "storage": "512GB PCIe NVMe SSD",
                "screen": "15.6 inch FHD (1920x1080) IPS 144Hz SlimBezel"
            }),
            is_flash_sale=True,
            is_featured=True,
            rating_avg=4.8,
            rating_count=52,
            sales_count=120
        ),
        Product(
            category_id=cat_map["laptop-van-phong"],
            name="Laptop ASUS Zenbook 14 OLED UX3405MA (Intel Core Ultra 7 155H / Intel Arc Graphics / 32GB RAM / 1TB SSD / 14' 3K 120Hz OLED)",
            slug="asus-zenbook-14-oled-ux3405",
            brand="ASUS",
            original_price=34990000,
            promo_price=31990000,
            stock_quantity=20,
            thumbnail="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80",
            short_desc="Laptop AI siêu mỏng nhẹ cao cấp chỉ 1.2kg. Màn hình Lumina OLED 3K 120Hz chuẩn màu điện ảnh. Chip NPU Intel AI Boost tích hợp.",
            specs_json=json.dumps({
                "cpu": "Intel Core Ultra 7 155H tích hợp NPU AI",
                "gpu": "Intel Arc Graphics",
                "ram": "32GB LPDDR5X on board",
                "storage": "1TB M.2 NVMe PCIe 4.0 SSD",
                "screen": "14.0 inch 3K (2880 x 1800) OLED 16:10 120Hz 100% DCI-P3",
                "weight": "1.20 kg"
            }),
            is_featured=True,
            rating_avg=4.9,
            rating_count=19,
            sales_count=38
        ),

        # PC Gaming G-Series
        Product(
            category_id=cat_map["pc-gaming"],
            name="PC G-Studio Intel Core i5-14400F / RTX 4060 8GB / 16GB DDR5 / 500GB NVMe / Nguồn 650W",
            slug="pc-g-studio-i5-14400f-rtx4060",
            brand="GearVN",
            original_price=23500000,
            promo_price=19990000,
            stock_quantity=25,
            thumbnail="https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80",
            short_desc="Cỗ máy Gaming & Đồ họa Best Seller tại GearVN. Cân tốt PUBG, GTA V, Valorant, Adobe Premiere, CapCut 4K.",
            specs_json=json.dumps({
                "cpu": "Intel Core i5-14400F (10 nhân, 16 luồng)",
                "mainboard": "MSI PRO B760M-A WIFI DDR5",
                "ram": "16GB (2x8GB) Kingston Fury Beast DDR5 5600MHz",
                "vga": "MSI GeForce RTX 4060 VENTUS 2X 8GB OC",
                "storage": "SSD Kingston NV2 500GB PCIe 4.0 NVMe",
                "psu": "DeepCool PK650D 650W 80 Plus Bronze",
                "case": "Xigmatek Gaming RGB Kính cường lực",
                "cooler": "Tản nhiệt khí Thermalright Assassin X 120 Refined SE"
            }),
            is_flash_sale=True,
            is_featured=True,
            rating_avg=5.0,
            rating_count=45,
            sales_count=89
        ),

        # Linh kiện PC Builder: CPU
        Product(
            category_id=cat_map["cpu-bo-vi-xu-ly"],
            name="CPU Intel Core i5 14400F (Up to 4.7GHz, 10 Cores 16 Threads, 20MB Cache, LGA 1700)",
            slug="cpu-intel-core-i5-14400f",
            brand="Intel",
            original_price=5490000,
            promo_price=4890000,
            stock_quantity=60,
            thumbnail="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"socket": "LGA1700", "wattage": 65, "cores": 10, "threads": 16}),
            pc_part_type="cpu",
            rating_avg=4.9,
            rating_count=32,
            sales_count=140
        ),
        Product(
            category_id=cat_map["cpu-bo-vi-xu-ly"],
            name="CPU AMD Ryzen 7 7800X3D (Up to 5.0GHz, 8 Cores 16 Threads, 104MB Cache, AM5)",
            slug="cpu-amd-ryzen-7-7800x3d",
            brand="AMD",
            original_price=11990000,
            promo_price=10490000,
            stock_quantity=30,
            thumbnail="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"socket": "AM5", "wattage": 120, "cores": 8, "threads": 16}),
            pc_part_type="cpu",
            rating_avg=5.0,
            rating_count=40,
            sales_count=95
        ),

        # Linh kiện PC Builder: Mainboard
        Product(
            category_id=cat_map["mainboard-bo-mach-chu"],
            name="Mainboard ASUS TUF GAMING B760-PLUS WIFI DDR5 (LGA 1700, ATX, PCIe 5.0)",
            slug="mainboard-asus-tuf-b760-plus-wifi-ddr5",
            brand="ASUS",
            original_price=4890000,
            promo_price=4390000,
            stock_quantity=40,
            thumbnail="https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"socket": "LGA1700", "ram_type": "DDR5", "form_factor": "ATX"}),
            pc_part_type="mainboard",
            rating_avg=4.9,
            rating_count=21,
            sales_count=60
        ),
        Product(
            category_id=cat_map["mainboard-bo-mach-chu"],
            name="Mainboard MSI MAG B650 TOMAHAWK WIFI (Socket AM5, ATX, DDR5)",
            slug="mainboard-msi-mag-b650-tomahawk-wifi",
            brand="MSI",
            original_price=6200000,
            promo_price=5690000,
            stock_quantity=25,
            thumbnail="https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"socket": "AM5", "ram_type": "DDR5", "form_factor": "ATX"}),
            pc_part_type="mainboard",
            rating_avg=4.8,
            rating_count=15,
            sales_count=45
        ),

        # Linh kiện PC Builder: RAM
        Product(
            category_id=cat_map["ram-bo-nho"],
            name="RAM Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz Black",
            slug="ram-corsair-vengeance-rgb-32gb-ddr5-6000mhz",
            brand="Corsair",
            original_price=3590000,
            promo_price=2990000,
            stock_quantity=50,
            thumbnail="https://images.unsplash.com/photo-1562976540-1502c2145186?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"ram_type": "DDR5", "capacity": "32GB (2x16GB)", "bus": "6000MHz"}),
            pc_part_type="ram",
            rating_avg=5.0,
            rating_count=35,
            sales_count=110
        ),

        # Linh kiện PC Builder: VGA Card màn hình
        Product(
            category_id=cat_map["vga-card-man-hinh"],
            name="Card màn hình ASUS TUF Gaming GeForce RTX 4070 SUPER 12GB GDDR6X OC Edition",
            slug="vga-asus-tuf-rtx-4070-super-12gb",
            brand="ASUS",
            original_price=21990000,
            promo_price=18990000,
            stock_quantity=20,
            thumbnail="https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"gpu_chip": "RTX 4070 SUPER", "vram": "12GB GDDR6X", "wattage": 220}),
            pc_part_type="vga",
            is_flash_sale=True,
            is_featured=True,
            rating_avg=5.0,
            rating_count=42,
            sales_count=75
        ),

        # Linh kiện PC Builder: Nguồn PSU
        Product(
            category_id=cat_map["nguon-may-tinh-psu"],
            name="Nguồn máy tính Corsair RM750e 750W 80 Plus Gold - Full Modular (ATX 3.0 / PCIe 5.0)",
            slug="psu-corsair-rm750e-750w-gold",
            brand="Corsair",
            original_price=3190000,
            promo_price=2690000,
            stock_quantity=45,
            thumbnail="https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"wattage": 750, "efficiency": "80 Plus Gold", "modular": "Full Modular"}),
            pc_part_type="psu",
            rating_avg=4.9,
            rating_count=29,
            sales_count=80
        ),

        # Màn hình
        Product(
            category_id=cat_map["man-hinh-may-tinh"],
            name="Màn hình Gaming ASUS TUF VG27AQ3A 27' 2K IPS 180Hz 1ms G-Sync",
            slug="man-hinh-asus-tuf-vg27aq3a-27-2k-180hz",
            brand="ASUS",
            original_price=7490000,
            promo_price=5990000,
            stock_quantity=30,
            thumbnail="https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"size": "27 inch", "resolution": "2K QHD (2560 x 1440)", "panel": "Fast IPS", "refresh_rate": "180Hz"}),
            pc_part_type="monitor",
            is_flash_sale=True,
            is_featured=True,
            rating_avg=4.9,
            rating_count=50,
            sales_count=130
        ),

        # Bàn phím cơ & Chuột
        Product(
            category_id=cat_map["ban-phim-co"],
            name="Bàn phím cơ không dây AKKO 5075B Plus Dracula Castle (Multi-modes / Gasket mount / Hot-swap)",
            slug="ban-phim-akko-5075b-plus-dracula",
            brand="AKKO",
            original_price=2490000,
            promo_price=1890000,
            stock_quantity=40,
            thumbnail="https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"switch": "Akko V3 Piano Pro", "connection": "Bluetooth 5.0 / 2.4GHz / Type-C", "led": "RGB"}),
            rating_avg=4.8,
            rating_count=65,
            sales_count=160
        ),
        Product(
            category_id=cat_map["chuot-gaming"],
            name="Chuột Gaming không dây Logitech G Pro X Superlight 2 Wireless Black (HERO 2 Sensor / 60g / 32.000 DPI)",
            slug="chuot-logitech-g-pro-x-superlight-2-black",
            brand="Logitech",
            original_price=3890000,
            promo_price=3290000,
            stock_quantity=50,
            thumbnail="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
            specs_json=json.dumps({"weight": "60g", "sensor": "HERO 2 32000 DPI", "polling_rate": "4000Hz", "battery": "95 hours"}),
            is_flash_sale=True,
            is_featured=True,
            rating_avg=5.0,
            rating_count=88,
            sales_count=210
        )
    ]
    db.add_all(products)
    db.commit()

    # 4. INTERNAL DOCUMENTS FOR RAG (Tài liệu nội bộ quy trình GearVN)
    internal_docs = [
        InternalDoc(
            title="Chính Sách Bảo Hành & Đổi Trả Sản Phẩm Công Nghệ GearVN 2026",
            category="Chính sách bảo hành",
            tags="bao hanh, doi tra, 1 doi 1, loi nha san xuat",
            content_text="""1. QUY ĐỊNH ĐỔI TRẢ 1 ĐỔI 1 TRONG 30 NGÀY ĐẦU:
- Áp dụng cho tất cả các sản phẩm Laptop, PC Gaming, Linh kiện phần cứng (CPU, VGA, Mainboard, RAM, SSD, Nguồn) phát sinh lỗi kỹ thuật phần cứng do nhà sản xuất.
- Điều kiện: Sản phẩm còn nguyên vẹn, không móp méo, trầy xước nặng, không có dấu hiệu vào nước hay can thiệp sửa chữa ngoài, đầy đủ hộp (box), sách hướng dẫn và phụ kiện đi kèm.

2. QUY TRÌNH TIẾP NHẬN BẢO HÀNH:
- Bước 1: Nhân viên kỹ thuật kiểm tra ngoại quan và xác nhận số Serial Number (S/N) trên hệ thống ERP GearVN.
- Bước 2: Thời gian kiểm tra lỗi nhanh tại quầy từ 15 - 30 phút.
- Bước 3: Nếu xác định lỗi phần cứng rõ ràng trong 30 ngày đầu, xuất kho đổi ngay sản phẩm mới 100% cùng model cho khách. Trường hợp hết hàng cùng model, khách hàng được đổi sang model tương đương hoặc hoàn tiền 100%."""
        ),
        InternalDoc(
            title="Quy Định Bảo Hành Màn Hình và Tiêu Chuẩn Điểm Chết (Dead Pixel)",
            category="Tiêu chuẩn kỹ thuật",
            tags="man hinh, diem chet, dead pixel, asus, lg, samsung",
            content_text="""TIÊU CHUẨN XỬ LÝ ĐIỂM CHẾT MÀN HÌNH CỦA CÁC HÃNG:
- Hãng ASUS: Đổi mới màn hình nếu có từ 3 điểm chết sáng (Bright dot) hoặc 5 điểm chết tối (Dark dot) trở lên trong vòng 3 năm. Riêng dòng ROG/TUF cao cấp hỗ trợ Zero Bright Dot trong 1 năm đầu.
- Hãng LG: Áp dụng đổi mới/thay panel nếu phát hiện từ 3 điểm chết trở lên đối với màn hình UltraGear và UltraFine.
- Hãng Samsung: Áp dụng theo tiêu chuẩn tối thiểu 5 điểm chết đối với các dòng Odyssey Gaming.
- Khách hàng mua kèm gói 'Bảo Hành VIP GearVN' được hỗ trợ 1 đổi 1 ngay lập tức nếu xuất hiện từ 1 điểm chết bất kỳ trong 3 tháng đầu."""
        ),
        InternalDoc(
            title="Chính Sách Chiết Khấu Mua Hàng & Phúc Lợi Cho Nhân Viên GearVN",
            category="Chính sách nội bộ",
            tags="chiet khau nhan vien, mua hang noi bo, tra gop 0%",
            content_text="""CHÍNH SÁCH MUA HÀNG NỘI BỘ DÀNH CHO NHÂN VIÊN CHÍNH THỨC:
1. Mức giảm giá chiết khấu:
- Linh kiện PC (CPU, Mainboard, VGA, RAM, SSD): Giảm trực tiếp 8% trên giá bán niêm yết hoặc tính theo giá vốn nhập kho + 2% chi phí vận hành (tùy mức nào thấp hơn).
- Gaming Gear (Bàn phím, Chuột, Tai nghe): Giảm 12% - 15%.
- Laptop Gaming & PC Lắp sẵn: Giảm 7% tối đa 3.000.000 VNĐ/sản phẩm.

2. Hạn mức mua hàng: Mỗi nhân viên được hưởng hạn mức tối đa 50.000.000 VNĐ/năm cho người thân và bản thân. Cần đăng ký qua cổng Portal HR trước 24h."""
        )
    ]
    db.add_all(internal_docs)
    db.commit()

    # 5. REVIEWS & SENTIMENT SAMPLES
    reviews = [
        Review(
            product_id=products[0].id,
            customer_name="Hoàng Nam",
            rating=5,
            comment="Laptop ROG Strix G16 chạy cực bốc, màn hình 240Hz bắn CS2 không có độ trễ luôn. Đóng gói rất kỹ càng!",
            sentiment_label="positive",
            sentiment_score=0.98
        ),
        Review(
            product_id=products[1].id,
            customer_name="Văn Tùng",
            rating=5,
            comment="Giá 20 củ mà có RTX 4050 kèm chip i5 gen 13 quá hời. Shop giao hàng hỏa tốc trong 2 tiếng rất ưng ý.",
            sentiment_label="positive",
            sentiment_score=0.95
        ),
        Review(
            product_id=products[3].id,
            customer_name="Lê Minh",
            rating=5,
            comment="Dàn PC G-Studio đi dây gọn gàng, LED RGB đồng bộ đẹp mắt. Test game nhiệt độ CPU chỉ 65 độ.",
            sentiment_label="positive",
            sentiment_score=0.96
        ),
        Review(
            product_id=products[1].id,
            customer_name="Trần Đức",
            rating=3,
            comment="Máy dùng tốt nhưng quạt tản nhiệt khi max tải hơi ồn một chút, tạm chấp nhận trong tầm giá.",
            sentiment_label="neutral",
            sentiment_score=0.75
        ),
        Review(
            product_id=products[0].id,
            customer_name="Minh Quang",
            rating=1,
            comment="Hộp bên ngoài bị móp nhẹ do shipper vận chuyển, may mà bên trong máy không sao nhưng cần cải thiện vận chuyển.",
            sentiment_label="negative",
            sentiment_score=0.88
        )
    ]
    db.add_all(reviews)
    db.commit()

    # 6. GENERATE REALTIME HOURLY SALES LOGS (.CSV) FOR ML MODEL TRAINING & CHARTS
    init_csv_file()
    now = datetime.utcnow()
    
    # Generate 48 hours of historical hourly sales
    for h in range(48, 0, -1):
        dt = now - timedelta(hours=h)
        # 1 to 4 orders per hour
        hour = dt.hour
        # Peak hours during 10-12 and 19-22
        multiplier = 3 if (10 <= hour <= 12 or 19 <= hour <= 22) else 1
        num_sales = np.random.randint(1 * multiplier, 4 * multiplier + 1)
        
        for _ in range(num_sales):
            p = products[np.random.randint(0, len(products))]
            qty = np.random.choice([1, 1, 1, 2])
            revenue = p.promo_price * qty
            code = f"GVN-{dt.strftime('%y%m%d%H')}-{np.random.randint(100, 999)}"
            
            append_sales_record(
                order_code=code,
                product_id=p.id,
                product_name=p.name,
                category_id=p.category_id,
                category_name="Công nghệ",
                quantity=qty,
                unit_price=p.promo_price,
                total_revenue=revenue,
                customer_name="Khách Hàng GearVN",
                custom_dt=dt
            )

    print("✅ Khởi tạo dữ liệu mẫu và file CSV bán hàng realtime thành công!")
