import sys
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.product import Product

PRODUCT_IMAGES_MAP = {
    # LAPTOP GAMING
    "asus-rog-strix-g16-g614jvr": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&auto=format&fit=crop&q=80",
    "lenovo-legion-pro-5-16irx9": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80",
    "asus-tuf-gaming-a15-fa507uv": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&auto=format&fit=crop&q=80",
    "msi-katana-15-b13vfk": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80",
    "acer-nitro-v-15-anv15": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&auto=format&fit=crop&q=80",

    # LAPTOP DOANH NHÂN & VĂN PHÒNG
    "macbook-air-13-m3-16gb-512gb": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
    "dell-xps-13-9340": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&auto=format&fit=crop&q=80",
    "asus-zenbook-14-oled-ux3405": "https://images.unsplash.com/photo-1544731612-de292439cc67?w=800&auto=format&fit=crop&q=80",

    # PC GAMING G-SERIES
    "pc-g-studio-r7-7800x3d-rtx4070ti-super": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=80",
    "pc-g-studio-i5-14400f-rtx4060": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",
    "pc-gaming-entry-i3-14100f-gtx1650": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=800&auto=format&fit=crop&q=80",

    # CARD MÀN HÌNH (VGA)
    "vga-asus-rog-strix-rtx-4090-24gb": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=800&auto=format&fit=crop&q=80",
    "vga-gigabyte-rtx-4080-super-gaming-oc-16gb": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=800&auto=format&fit=crop&q=80",
    "vga-asus-tuf-rtx-4070-super-12gb": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=800&auto=format&fit=crop&q=80",
    "vga-gigabyte-rx-7800-xt-gaming-oc-16gb": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=800&auto=format&fit=crop&q=80",
    "vga-msi-rtx-4060-ventus-2x-8gb": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=800&auto=format&fit=crop&q=80",

    # CPU VI XỬ LÝ
    "cpu-intel-core-i7-14700k": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&auto=format&fit=crop&q=80",
    "cpu-intel-core-i5-14400f": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&auto=format&fit=crop&q=80",
    "cpu-amd-ryzen-7-7800x3d": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&auto=format&fit=crop&q=80",
    "cpu-amd-ryzen-5-7600x": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&auto=format&fit=crop&q=80",

    # MAINBOARD BO MẠCH CHỦ
    "mainboard-msi-mag-z790-tomahawk-max-wifi": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
    "mainboard-gigabyte-b650-aorus-elite-ax-v2": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
    "mainboard-asus-tuf-b760-plus-wifi-ddr5": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
    "mainboard-msi-mag-b650-tomahawk-wifi": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",
    "mainboard-asus-rog-strix-b760-a-wifi-d4": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=80",

    # BỘ NHỚ RAM
    "ram-corsair-vengeance-rgb-32gb-ddr5-6000mhz": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=800&auto=format&fit=crop&q=80",
    "ram-gskill-trident-z5-rgb-64gb-ddr5-6000": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=800&auto=format&fit=crop&q=80",
    "ram-kingston-fury-beast-rgb-16gb-ddr4-3200": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=800&auto=format&fit=crop&q=80",

    # Ổ CỨNG SSD
    "ssd-samsung-990-pro-1tb": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=800&auto=format&fit=crop&q=80",

    # TẢN NHIỆT CPU
    "tan-nhiet-aio-deepcool-lt720-360mm": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=80",
    "tan-nhiet-thermalright-assassin-x-120-se": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=80",

    # VỎ CASE MÁY TÍNH
    "case-nzxt-h5-flow-rgb-black": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=80",

    # NGUỒN PSU
    "psu-asus-rog-thor-1000w-platinum-ii": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",
    "psu-corsair-rm750e-750w-gold": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",

    # MÀN HÌNH
    "man-hinh-samsung-odyssey-g7-32-2k-240hz": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
    "man-hinh-dell-ultrasharp-u2724d-27-2k": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
    "man-hinh-asus-tuf-vg27aq3a-27-2k-180hz": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
    "man-hinh-lg-ultragear-24gs60f-b-24-180hz": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",

    # GAMING GEAR
    "ban-phim-corsair-k70-max-rgb": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
    "ban-phim-akko-5075b-plus-dracula": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
    "chuot-razer-deathadder-v3-pro-white": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
    "chuot-logitech-g-pro-x-superlight-2-black": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80"
}

def update_images():
    db: Session = SessionLocal()
    try:
        updated_count = 0
        for slug, img_url in PRODUCT_IMAGES_MAP.items():
            product = db.query(Product).filter(Product.slug == slug).first()
            if product:
                product.thumbnail = img_url
                updated_count += 1

        db.commit()
        print(f"[*] Da cap nhat hinh anh chuan xac cho {updated_count} san pham thanh cong!")
    finally:
        db.close()

if __name__ == "__main__":
    update_images()
