import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.ai import PCBuilderCompatibilityRequest, PCBuilderCompatibilityResponse

class PCBuilderService:
    def check_compatibility(self, db: Session, req: PCBuilderCompatibilityRequest) -> PCBuilderCompatibilityResponse:
        issues = []
        warnings = []
        estimated_wattage = 150 # Base motherboard + fans + system
        total_price = 0.0

        # Load selected products
        cpu = db.query(Product).filter(Product.id == req.cpu_id).first() if req.cpu_id else None
        mainboard = db.query(Product).filter(Product.id == req.mainboard_id).first() if req.mainboard_id else None
        ram = db.query(Product).filter(Product.id == req.ram_id).first() if req.ram_id else None
        vga = db.query(Product).filter(Product.id == req.vga_id).first() if req.vga_id else None
        psu = db.query(Product).filter(Product.id == req.psu_id).first() if req.psu_id else None
        cooler = db.query(Product).filter(Product.id == req.cooler_id).first() if req.cooler_id else None
        storage = db.query(Product).filter(Product.id == req.storage_id).first() if req.storage_id else None
        case = db.query(Product).filter(Product.id == req.case_id).first() if req.case_id else None

        parts = [cpu, mainboard, ram, vga, psu, cooler, storage, case]
        for p in parts:
            if p:
                total_price += p.promo_price

        # Extract specs
        def get_specs(prod):
            if not prod or not prod.specs_json:
                return {}
            try:
                return json.loads(prod.specs_json)
            except Exception:
                return {}

        cpu_specs = get_specs(cpu)
        main_specs = get_specs(mainboard)
        ram_specs = get_specs(ram)
        vga_specs = get_specs(vga)
        psu_specs = get_specs(psu)

        # 1. Check CPU vs Mainboard Socket
        if cpu and mainboard:
            cpu_socket = cpu_specs.get("socket", "").upper()
            main_socket = main_specs.get("socket", "").upper()
            if cpu_socket and main_socket and cpu_socket != main_socket:
                issues.append(f"❌ Không tương thích Socket: CPU dùng socket [{cpu_socket}] nhưng Mainboard là socket [{main_socket}].")

        # 2. Check RAM DDR4 / DDR5 compatibility with Mainboard
        if ram and mainboard:
            ram_type = "DDR5" if "DDR5" in ram.name.upper() or ram_specs.get("ram_type", "").upper() == "DDR5" else "DDR4"
            main_ram_type = "DDR5" if "DDR5" in mainboard.name.upper() or main_specs.get("ram_type", "").upper() == "DDR5" else "DDR4"
            if ram_type != main_ram_type:
                issues.append(f"❌ Không tương thích chuẩn RAM: Mainboard hỗ trợ [{main_ram_type}] nhưng bạn đang chọn thanh RAM [{ram_type}].")

        # 3. Power Consumption & PSU Wattage
        cpu_watt = int(cpu_specs.get("wattage", 125)) if cpu else 65
        vga_watt = int(vga_specs.get("wattage", 220)) if vga else 0
        estimated_wattage += (cpu_watt + vga_watt)
        
        # Recommended PSU should have at least 25% overhead headroom
        recommended_psu = int(estimated_wattage * 1.35 / 50) * 50
        recommended_psu = max(recommended_psu, 550)

        if psu:
            psu_watt = int(psu_specs.get("wattage", 0))
            if psu_watt > 0 and psu_watt < estimated_wattage:
                issues.append(f"❌ Nguồn không đủ tải: Dàn máy cần tối thiểu {estimated_wattage}W nhưng nguồn hiện tại chỉ có {psu_watt}W.")
            elif psu_watt > 0 and psu_watt < recommended_psu:
                warnings.append(f"⚠️ Cảnh báo nguồn: Nguồn {psu_watt}W vừa đủ nhưng khuyến nghị nên dùng từ {recommended_psu}W để hệ thống hoạt động ổn định nhất khi tải nặng.")

        if cpu and not cooler and "i7" in cpu.name.lower() or cpu and not cooler and "i9" in cpu.name.lower() or cpu and not cooler and "ryzen 7" in cpu.name.lower():
            warnings.append("⚠️ CPU hiệu năng cao tỏa nhiệt nhiều, bạn nên thêm Tản nhiệt khí hoặc Tản nhiệt nước để duy trì nhiệt độ tối ưu.")

        is_compatible = len(issues) == 0

        return PCBuilderCompatibilityResponse(
            is_compatible=is_compatible,
            issues=issues,
            warnings=warnings,
            estimated_wattage=estimated_wattage,
            recommended_psu_wattage=recommended_psu,
            total_price=total_price
        )

pc_builder_service = PCBuilderService()
