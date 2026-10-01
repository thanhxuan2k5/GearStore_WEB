import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from app.config import settings

CSV_HEADERS = [
    "timestamp",
    "date",
    "hour",
    "day_of_week",
    "month",
    "order_code",
    "product_id",
    "product_name",
    "category_id",
    "category_name",
    "quantity",
    "unit_price",
    "total_revenue",
    "customer_name"
]

def init_csv_file():
    """Tạo file CSV nếu chưa tồn tại"""
    if not os.path.exists(settings.CSV_SALES_PATH):
        os.makedirs(os.path.dirname(settings.CSV_SALES_PATH), exist_ok=True)
        with open(settings.CSV_SALES_PATH, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def append_sales_record(
    order_code: str,
    product_id: int,
    product_name: str,
    category_id: int,
    category_name: str,
    quantity: int,
    unit_price: float,
    total_revenue: float,
    customer_name: str,
    custom_dt: Optional[datetime] = None
):
    """Ghi nhận 1 dòng giao dịch bán hàng realtime vào file CSV"""
    init_csv_file()
    now = custom_dt or datetime.utcnow()
    row = [
        now.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d"),
        now.hour,
        now.weekday(), # 0=Monday, 6=Sunday
        now.month,
        order_code,
        product_id,
        product_name,
        category_id,
        category_name,
        quantity,
        unit_price,
        total_revenue,
        customer_name
    ]
    with open(settings.CSV_SALES_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def get_sales_dataframe() -> pd.DataFrame:
    """Đọc dữ liệu CSV thành Pandas DataFrame phục vụ phân tích và ML"""
    init_csv_file()
    try:
        df = pd.read_csv(settings.CSV_SALES_PATH, encoding="utf-8-sig")
        if df.empty:
            return pd.DataFrame(columns=CSV_HEADERS)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce').fillna(0)
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1)
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return pd.DataFrame(columns=CSV_HEADERS)
