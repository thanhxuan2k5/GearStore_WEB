import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.category import Category
from app.models.product import Product

MORE_PRODUCTS = [
    # MAINBOARD
    {
        "cat_slug": "mainboard-bo-mach-chu",
        "name": "Mainboard MSI MAG Z790 TOMAHAWK MAX WIFI DDR5 (LGA1700 / ATX / PCIe 5.0 / Wi-Fi 7)",
        "slug": "mainboard-msi-mag-z790-tomahawk-max-wifi",
        "brand": "MSI",
        "original_price": 8990000,
        "promo_price": 7990000,
        "stock_quantity": 25,
        "thumbnail": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"socket": "LGA1700", "ram_type": "DDR5", "form_factor": "ATX", "pcie": "PCIe 5.0"},
        "pc_part_type": "mainboard",
        "rating_avg": 5.0,
        "rating_count": 30,
        "sales_count": 65
    },
    {
        "cat_slug": "mainboard-bo-mach-chu",
        "name": "Mainboard GIGABYTE B650 AORUS ELITE AX V2 (Socket AM5 / ATX / DDR5 / PCIe 5.0 M.2)",
        "slug": "mainboard-gigabyte-b650-aorus-elite-ax-v2",
        "brand": "Gigabyte",
        "original_price": 6490000,
        "promo_price": 5790000,
        "stock_quantity": 30,
        "thumbnail": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"socket": "AM5", "ram_type": "DDR5", "form_factor": "ATX"},
        "pc_part_type": "mainboard",
        "rating_avg": 4.9,
        "rating_count": 25,
        "sales_count": 70
    },
    {
        "cat_slug": "mainboard-bo-mach-chu",
        "name": "Mainboard ASUS ROG STRIX B760-A GAMING WIFI D4 (LGA1700 / ATX / DDR4 White Edition)",
        "slug": "mainboard-asus-rog-strix-b760-a-wifi-d4",
        "brand": "ASUS",
        "original_price": 5890000,
        "promo_price": 5290000,
        "stock_quantity": 20,
        "thumbnail": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"socket": "LGA1700", "ram_type": "DDR4", "form_factor": "ATX"},
        "pc_part_type": "mainboard",
        "rating_avg": 4.9,
        "rating_count": 19,
        "sales_count": 48
    },

    # RAM
    {
        "cat_slug": "ram-bo-nho",
        "name": "RAM Kingston Fury Beast RGB 16GB (2x8GB) DDR4 3200MHz Black",
        "slug": "ram-kingston-fury-beast-rgb-16gb-ddr4-3200",
        "brand": "Kingston",
        "original_price": 1490000,
        "promo_price": 1190000,
        "stock_quantity": 60,
        "thumbnail": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"ram_type": "DDR4", "capacity": "16GB (2x8GB)", "bus": "3200MHz"},
        "pc_part_type": "ram",
        "rating_avg": 4.9,
        "rating_count": 80,
        "sales_count": 320
    },
    {
        "cat_slug": "ram-bo-nho",
        "name": "RAM G.Skill Trident Z5 RGB 64GB (2x32GB) DDR5 6000MHz Black",
        "slug": "ram-gskill-trident-z5-rgb-64gb-ddr5-6000",
        "brand": "G.Skill",
        "original_price": 6890000,
        "promo_price": 5990000,
        "stock_quantity": 20,
        "thumbnail": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"ram_type": "DDR5", "capacity": "64GB (2x32GB)", "bus": "6000MHz"},
        "pc_part_type": "ram",
        "rating_avg": 5.0,
        "rating_count": 28,
        "sales_count": 45
    },

    # VGA
    {
        "cat_slug": "vga-card-man-hinh",
        "name": "Card màn hình ASUS ROG Strix GeForce RTX 4090 24GB GDDR6X OC Edition",
        "slug": "vga-asus-rog-strix-rtx-4090-24gb",
        "brand": "ASUS",
        "original_price": 62990000,
        "promo_price": 57990000,
        "stock_quantity": 8,
        "thumbnail": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"gpu_chip": "RTX 4090", "vram": "24GB GDDR6X", "wattage": 450, "length": "357mm"},
        "pc_part_type": "vga",
        "is_featured": True,
        "rating_avg": 5.0,
        "rating_count": 15,
        "sales_count": 22
    },
    {
        "cat_slug": "vga-card-man-hinh",
        "name": "Card màn hình GIGABYTE Radeon RX 7800 XT GAMING OC 16GB GDDR6",
        "slug": "vga-gigabyte-rx-7800-xt-gaming-oc-16gb",
        "brand": "Gigabyte",
        "original_price": 16990000,
        "promo_price": 14890000,
        "stock_quantity": 18,
        "thumbnail": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"gpu_chip": "RX 7800 XT", "vram": "16GB GDDR6", "wattage": 263},
        "pc_part_type": "vga",
        "rating_avg": 4.9,
        "rating_count": 21,
        "sales_count": 54
    },

    # NGUỒN PSU
    {
        "cat_slug": "nguon-may-tinh-psu",
        "name": "Nguồn máy tính ASUS ROG Thor 1000W Platinum II (1000W / 80 Plus Platinum / Màn hình OLED / PCIe 5.0)",
        "slug": "psu-asus-rog-thor-1000w-platinum-ii",
        "brand": "ASUS",
        "original_price": 8990000,
        "promo_price": 7990000,
        "stock_quantity": 15,
        "thumbnail": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"wattage": 1000, "efficiency": "80 Plus Platinum", "modular": "Full Modular"},
        "pc_part_type": "psu",
        "rating_avg": 5.0,
        "rating_count": 18,
        "sales_count": 30
    },

    # TẢN NHIỆT CPU
    {
        "cat_slug": "tan-nhiet-cpu",
        "name": "Tản nhiệt khí Thermalright Assassin X 120 Refined SE ARGB",
        "slug": "tan-nhiet-thermalright-assassin-x-120-se",
        "brand": "Thermalright",
        "original_price": 550000,
        "promo_price": 420000,
        "stock_quantity": 60,
        "thumbnail": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"type": "Air Cooler", "tdp_support": "180W", "compatibility": "LGA1700 / AM5"},
        "pc_part_type": "cooler",
        "rating_avg": 4.9,
        "rating_count": 95,
        "sales_count": 420
    },

    # MÀN HÌNH GAMING
    {
        "cat_slug": "man-hinh-may-tinh",
        "name": "Màn hình Cong Gaming Samsung Odyssey G7 32' 2K QHD 240Hz 1ms 1000R HDR600 G-Sync",
        "slug": "man-hinh-samsung-odyssey-g7-32-2k-240hz",
        "brand": "Samsung",
        "original_price": 14990000,
        "promo_price": 12490000,
        "stock_quantity": 20,
        "thumbnail": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"size": "32 inch", "resolution": "2K (2560x1440)", "panel": "VA Cong 1000R", "refresh_rate": "240Hz"},
        "pc_part_type": "monitor",
        "rating_avg": 5.0,
        "rating_count": 38,
        "sales_count": 86
    },
    {
        "cat_slug": "man-hinh-may-tinh",
        "name": "Màn hình Gaming LG UltraGear 24GS60F-B 24' FHD IPS 180Hz 1ms HDR10",
        "slug": "man-hinh-lg-ultragear-24gs60f-b-24-180hz",
        "brand": "LG",
        "original_price": 3890000,
        "promo_price": 3190000,
        "stock_quantity": 40,
        "thumbnail": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
        "specs_json": {"size": "24 inch", "resolution": "FHD (1920x1080)", "panel": "IPS", "refresh_rate": "180Hz"},
        "pc_part_type": "monitor",
        "rating_avg": 4.9,
        "rating_count": 64,
        "sales_count": 210
    }
]

def add_more_products():
    db: Session = SessionLocal()
    try:
        cats = {c.slug: c.id for c in db.query(Category).all()}
        added_count = 0

        for p_data in MORE_PRODUCTS:
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
        print(f"Added {added_count} additional products to database successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    add_more_products()
