import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.category import Category
from app.models.product import Product

NEW_PRODUCTS = [
    # LAPTOP GAMING CAO CẤP & PHỔ THÔNG
    {
        "cat_slug": "laptop-gaming",
        "name": "Laptop Gaming Lenovo Legion Pro 5 16IRX9 (i7-14650HX / RTX 4060 8GB / 32GB RAM / 1TB SSD / 16' WQXGA 240Hz 500nits)",
        "slug": "lenovo-legion-pro-5-16irx9",
        "brand": "Lenovo",
        "original_price": 45990000,
        "promo_price": 41990000,
        "stock_quantity": 25,
        "thumbnail": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Laptop gaming quốc dân cao cấp với hệ thống tản nhiệt Legion Coldfront 5.0, màn hình chuẩn đồ họa 500nits 240Hz, chip AI Lenovo LA1.",
        "specs_json": {
            "cpu": "Intel Core i7-14650HX (16 nhân, 24 luồng, up to 5.2GHz)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 140W TGP",
            "ram": "32GB DDR5 5600MHz",
            "storage": "1TB SSD M.2 2280 PCIe 4.0x4 NVMe",
            "screen": "16 inch WQXGA (2560x1600) IPS 240Hz 500nits 100% sRGB",
            "weight": "2.50 kg"
        },
        "is_flash_sale": True,
        "is_featured": True,
        "rating_avg": 5.0,
        "rating_count": 68,
        "sales_count": 142
    },
    {
        "cat_slug": "laptop-gaming",
        "name": "Laptop Gaming ASUS TUF Gaming A15 FA507UV (Ryzen 7 8845HS / RTX 4060 8GB / 16GB RAM / 512GB SSD / 15.6' FHD 144Hz 100% sRGB)",
        "slug": "asus-tuf-gaming-a15-fa507uv",
        "brand": "ASUS",
        "original_price": 32990000,
        "promo_price": 28490000,
        "stock_quantity": 30,
        "thumbnail": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Độ bền chuẩn quân đội MIL-STD-810H, chip Ryzen 7 tích hợp AI Ryzen NPU và Card đồ họa RTX 4060 cân mọi game Esport và AAA.",
        "specs_json": {
            "cpu": "AMD Ryzen 7 8845HS tích hợp Ryzen AI",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6 (140W)",
            "ram": "16GB DDR5 5600MHz",
            "storage": "512GB PCIe 4.0 NVMe M.2 SSD",
            "screen": "15.6 inch FHD (1920x1080) 144Hz 100% sRGB G-Sync",
            "weight": "2.20 kg"
        },
        "is_flash_sale": False,
        "is_featured": True,
        "rating_avg": 4.9,
        "rating_count": 44,
        "sales_count": 98
    },
    {
        "cat_slug": "laptop-gaming",
        "name": "Laptop Gaming MSI Katana 15 B13VFK (i7-13620H / RTX 4060 8GB / 16GB RAM / 1TB SSD / 15.6' FHD 144Hz IPS)",
        "slug": "msi-katana-15-b13vfk",
        "brand": "MSI",
        "original_price": 31490000,
        "promo_price": 26990000,
        "stock_quantity": 20,
        "thumbnail": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Thanh kiếm sắc bén của game thủ với bàn phím LED RGB 4 vùng, tản nhiệt Cooler Boost 5 2 quạt 6 ống dẫn nhiệt.",
        "specs_json": {
            "cpu": "Intel Core i7-13620H (10 nhân, 16 luồng)",
            "gpu": "NVIDIA GeForce RTX 4060 8GB GDDR6",
            "ram": "16GB DDR5 (2x8GB)",
            "storage": "1TB NVMe PCIe Gen4 SSD",
            "screen": "15.6 inch FHD (1920x1080) IPS 144Hz"
        },
        "is_flash_sale": True,
        "is_featured": False,
        "rating_avg": 4.7,
        "rating_count": 31,
        "sales_count": 85
    },

    # LAPTOP VĂN PHÒNG & MỎNG NHẸ DOANH NHÂN
    {
        "cat_slug": "laptop-van-phong",
        "name": "Laptop Dell XPS 13 9340 (Intel Core Ultra 7 155H / 16GB RAM / 512GB SSD / 13.4' FHD+ InfinityEdge 120Hz 500nits)",
        "slug": "dell-xps-13-9340",
        "brand": "Dell",
        "original_price": 49990000,
        "promo_price": 44990000,
        "stock_quantity": 15,
        "thumbnail": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Kiệt tác laptop cao cấp nhất của Dell với khung nhôm nguyên khối CNC, bàn phím liền mạch và touchpad kính ẩn hiện đại.",
        "specs_json": {
            "cpu": "Intel Core Ultra 7 155H (16 nhân, 22 luồng, Intel AI Boost)",
            "gpu": "Intel Arc Graphics",
            "ram": "16GB LPDDR5x 7467MT/s",
            "storage": "512GB M.2 PCIe NVMe SSD",
            "screen": "13.4 inch FHD+ (1920x1200) 120Hz 500nits 100% sRGB",
            "weight": "1.19 kg"
        },
        "is_featured": True,
        "rating_avg": 5.0,
        "rating_count": 22,
        "sales_count": 40
    },
    {
        "cat_slug": "laptop-van-phong",
        "name": "Laptop Apple MacBook Air 13 M3 2024 (8-Core CPU / 10-Core GPU / 16GB Unified Memory / 512GB SSD Space Gray)",
        "slug": "macbook-air-13-m3-16gb-512gb",
        "brand": "Apple",
        "original_price": 37990000,
        "promo_price": 34490000,
        "stock_quantity": 30,
        "thumbnail": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Mỏng nhẹ kinh ngạc, thời lượng pin lên đến 18 tiếng, chip Apple Silicon M3 với Neural Engine 16 lõi xử lý AI tốc độ cao.",
        "specs_json": {
            "cpu": "Apple M3 chip (8 nhân CPU, 10 nhân GPU, 16 nhân Neural Engine)",
            "ram": "16GB Unified Memory",
            "storage": "512GB SSD",
            "screen": "13.6 inch Liquid Retina (2560x1664) True Tone 500nits",
            "weight": "1.24 kg"
        },
        "is_featured": True,
        "rating_avg": 5.0,
        "rating_count": 55,
        "sales_count": 160
    },

    # PC GAMING G-SERIES ĐỈNH CAO
    {
        "cat_slug": "pc-gaming",
        "name": "PC G-Studio Ultra AMD Ryzen 7 7800X3D / RTX 4070 Ti SUPER 16GB / 32GB DDR5 / 1TB Gen4 / Tản Nước 360 / Nguồn 850W Gold",
        "slug": "pc-g-studio-r7-7800x3d-rtx4070ti-super",
        "brand": "GearVN",
        "original_price": 54990000,
        "promo_price": 49990000,
        "stock_quantity": 12,
        "thumbnail": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Dàn PC Gaming Flagship trang bị 'Vua gaming' Ryzen 7 7800X3D cùng RTX 4070 Ti Super 16GB VRAM. Max setting 4K mọi tựa game AAA.",
        "specs_json": {
            "cpu": "AMD Ryzen 7 7800X3D (8 Cores, 16 Threads, 104MB Cache)",
            "mainboard": "ASUS TUF GAMING B650-PLUS WIFI DDR5",
            "ram": "32GB (2x16GB) Corsair Vengeance RGB DDR5 6000MHz",
            "vga": "ASUS TUF Gaming GeForce RTX 4070 Ti SUPER 16GB GDDR6X",
            "storage": "SSD Samsung 990 PRO 1TB PCIe 4.0 NVMe",
            "psu": "Corsair RM850e 850W 80 Plus Gold ATX 3.0",
            "cooler": "Tản nước AIO DeepCool LT720 360mm ARGB",
            "case": "NZXT H9 Flow Dual-Chamber Kính cường lực"
        },
        "is_flash_sale": True,
        "is_featured": True,
        "rating_avg": 5.0,
        "rating_count": 48,
        "sales_count": 76
    },
    {
        "cat_slug": "pc-gaming",
        "name": "PC Gaming Entry Intel Core i3-14100F / GTX 1650 4GB / 16GB RAM / 500GB SSD / Nguồn 550W (PC Giá Rẻ Học Tập & LOL/Valorant)",
        "slug": "pc-gaming-entry-i3-14100f-gtx1650",
        "brand": "GearVN",
        "original_price": 12500000,
        "promo_price": 9990000,
        "stock_quantity": 40,
        "thumbnail": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600&auto=format&fit=crop&q=80",
        "short_desc": "Cỗ máy tính giá mềm cho học sinh sinh viên chơi mượt Liên Minh Huyền Thoại, FO4, Valorant, CS2 và học tập tin học văn phòng.",
        "specs_json": {
            "cpu": "Intel Core i3-14100F (4 nhân 8 luồng, up to 4.7GHz)",
            "mainboard": "MSI PRO H610M-E DDR4",
            "ram": "16GB (2x8GB) Kingston Fury DDR4 3200MHz",
            "vga": "MSI GeForce GTX 1650 D6 VENTUS XS 4GB OCV3",
            "storage": "SSD Kingston NV2 500GB PCIe NVMe",
            "psu": "DeepCool PK550D 550W 80 Plus Bronze"
        },
        "is_flash_sale": True,
        "is_featured": False,
        "rating_avg": 4.8,
        "rating_count": 39,
        "sales_count": 180
    },

    # CARD MÀN HÌNH (VGA)
    {
        "cat_slug": "vga-card-man-hinh",
        "name": "Card màn hình MSI GeForce RTX 4060 VENTUS 2X BLACK 8GB OC GDDR6",
        "slug": "vga-msi-rtx-4060-ventus-2x-8gb",
        "brand": "MSI",
        "original_price": 8990000,
        "promo_price": 7890000,
        "stock_quantity": 35,
        "thumbnail": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"gpu_chip": "RTX 4060", "vram": "8GB GDDR6", "wattage": 115, "length": "199mm"},
        "pc_part_type": "vga",
        "rating_avg": 4.9,
        "rating_count": 52,
        "sales_count": 190
    },
    {
        "cat_slug": "vga-card-man-hinh",
        "name": "Card màn hình GIGABYTE GeForce RTX 4080 SUPER GAMING OC 16GB GDDR6X",
        "slug": "vga-gigabyte-rtx-4080-super-gaming-oc-16gb",
        "brand": "Gigabyte",
        "original_price": 33990000,
        "promo_price": 30490000,
        "stock_quantity": 10,
        "thumbnail": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"gpu_chip": "RTX 4080 SUPER", "vram": "16GB GDDR6X", "wattage": 320, "length": "342mm"},
        "pc_part_type": "vga",
        "rating_avg": 5.0,
        "rating_count": 18,
        "sales_count": 35
    },

    # CPU VI XỬ LÝ
    {
        "cat_slug": "cpu-bo-vi-xu-ly",
        "name": "CPU Intel Core i7 14700K (Up to 5.6GHz, 20 Cores 28 Threads, 33MB Cache, LGA 1700)",
        "slug": "cpu-intel-core-i7-14700k",
        "brand": "Intel",
        "original_price": 11490000,
        "promo_price": 10290000,
        "stock_quantity": 25,
        "thumbnail": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"socket": "LGA1700", "wattage": 125, "cores": 20, "threads": 28},
        "pc_part_type": "cpu",
        "rating_avg": 5.0,
        "rating_count": 33,
        "sales_count": 88
    },
    {
        "cat_slug": "cpu-bo-vi-xu-ly",
        "name": "CPU AMD Ryzen 5 7600X (Up to 5.3GHz, 6 Cores 12 Threads, 38MB Cache, Socket AM5)",
        "slug": "cpu-amd-ryzen-5-7600x",
        "brand": "AMD",
        "original_price": 6490000,
        "promo_price": 5490000,
        "stock_quantity": 40,
        "thumbnail": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"socket": "AM5", "wattage": 105, "cores": 6, "threads": 12},
        "pc_part_type": "cpu",
        "rating_avg": 4.8,
        "rating_count": 27,
        "sales_count": 115
    },

    # Ổ CỨNG SSD
    {
        "cat_slug": "o-cung-ssd",
        "name": "Ổ cứng SSD Samsung 990 PRO 1TB M.2 PCIe Gen 4.0 x4 NVMe (Đọc 7450MB/s - Ghi 6900MB/s)",
        "slug": "ssd-samsung-990-pro-1tb",
        "brand": "Samsung",
        "original_price": 3290000,
        "promo_price": 2790000,
        "stock_quantity": 50,
        "thumbnail": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"capacity": "1TB", "interface": "PCIe Gen 4.0 x4", "read_speed": "7450 MB/s", "write_speed": "6900 MB/s"},
        "pc_part_type": "storage",
        "rating_avg": 5.0,
        "rating_count": 62,
        "sales_count": 230
    },

    # TẢN NHIỆT CPU
    {
        "cat_slug": "tan-nhiet-cpu",
        "name": "Tản nhiệt nước AIO DeepCool LT720 360mm ARGB Black",
        "slug": "tan-nhiet-aio-deepcool-lt720-360mm",
        "brand": "DeepCool",
        "original_price": 3490000,
        "promo_price": 2990000,
        "stock_quantity": 30,
        "thumbnail": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"type": "AIO 360mm", "fans": "3x 120mm PWM", "compatibility": "LGA1700 / AM5"},
        "pc_part_type": "cooler",
        "rating_avg": 4.9,
        "rating_count": 28,
        "sales_count": 82
    },

    # VỎ CASE
    {
        "cat_slug": "case-may-tinh",
        "name": "Vỏ Case NZXT H5 Flow RGB Black (Mid-Tower / 2 Fan F140 RGB Core / Kính cường lực)",
        "slug": "case-nzxt-h5-flow-rgb-black",
        "brand": "NZXT",
        "original_price": 2890000,
        "promo_price": 2490000,
        "stock_quantity": 25,
        "thumbnail": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"form_factor": "Mid-Tower", "motherboard_support": "ATX / Micro-ATX / Mini-ITX"},
        "pc_part_type": "case",
        "rating_avg": 4.9,
        "rating_count": 35,
        "sales_count": 95
    },

    # MÀN HÌNH ĐỒ HỌA & GAMING CONG
    {
        "cat_slug": "man-hinh-may-tinh",
        "name": "Màn hình Đồ họa Dell UltraSharp U2724D 27' 2K IPS Black 120Hz 100% sRGB Type-C",
        "slug": "man-hinh-dell-ultrasharp-u2724d-27-2k",
        "brand": "Dell",
        "original_price": 11990000,
        "promo_price": 10490000,
        "stock_quantity": 20,
        "thumbnail": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"size": "27 inch", "resolution": "2K QHD (2560x1440)", "panel": "IPS Black", "refresh_rate": "120Hz", "color": "100% sRGB, 98% DCI-P3"},
        "pc_part_type": "monitor",
        "rating_avg": 5.0,
        "rating_count": 41,
        "sales_count": 78
    },

    # GAMING GEAR
    {
        "cat_slug": "ban-phim-co",
        "name": "Bàn phím cơ Corsair K70 MAX RGB Magnetic-Mechanical (CORSAIR MGX Switches / Rapid Trigger / 8000Hz)",
        "slug": "ban-phim-corsair-k70-max-rgb",
        "brand": "Corsair",
        "original_price": 5990000,
        "promo_price": 5190000,
        "stock_quantity": 25,
        "thumbnail": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"switch": "Corsair MGX Magnetic Switch", "polling_rate": "8000Hz", "keycaps": "PBT Double-Shot", "led": "RGB Per-key"},
        "rating_avg": 5.0,
        "rating_count": 34,
        "sales_count": 62
    },
    {
        "cat_slug": "chuot-gaming",
        "name": "Chuột Gaming Razer DeathAdder V3 Pro Wireless White (Focus Pro 30K Sensor / 63g / Optical Gen-3)",
        "slug": "chuot-razer-deathadder-v3-pro-white",
        "brand": "Razer",
        "original_price": 3990000,
        "promo_price": 3390000,
        "stock_quantity": 30,
        "thumbnail": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"weight": "63g", "sensor": "Focus Pro 30K Optical", "switches": "Optical Mouse Switches Gen-3", "battery": "90 hours"},
        "rating_avg": 4.9,
        "rating_count": 46,
        "sales_count": 120
    }
]

def add_new_products():
    db: Session = SessionLocal()
    try:
        cats = {c.slug: c.id for c in db.query(Category).all()}
        added_count = 0

        for p_data in NEW_PRODUCTS:
            cat_id = cats.get(p_data["cat_slug"])
            if not cat_id:
                continue

            existing = db.query(Product).filter(Product.slug == p_data["slug"]).first()
            if existing:
                continue

            prod = Product(
                category_id=cat_id,
                name=p_data["name"],
                slug=p_data["slug"],
                brand=p_data["brand"],
                original_price=p_data["original_price"],
                promo_price=p_data["promo_price"],
                stock_quantity=p_data.get("stock_quantity", 30),
                thumbnail=p_data["thumbnail"],
                short_desc=p_data.get("short_desc", ""),
                specs_json=json.dumps(p_data.get("specs_json", {})),
                is_flash_sale=p_data.get("is_flash_sale", False),
                is_featured=p_data.get("is_featured", False),
                pc_part_type=p_data.get("pc_part_type", None),
                rating_avg=p_data.get("rating_avg", 5.0),
                rating_count=p_data.get("rating_count", 20),
                sales_count=p_data.get("sales_count", 50)
            )
            db.add(prod)
            added_count += 1

        db.commit()
        print(f"✅ Đã nạp thành công thêm {added_count} sản phẩm công nghệ GearVN mới vào Database!")
    finally:
        db.close()

if __name__ == "__main__":
    add_new_products()
