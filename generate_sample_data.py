from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd


def build_mock_data(rows: int = 2000) -> pd.DataFrame:
    random.seed(42)

    products = [
        "Laptop Pro 14",
        "Laptop Air 13",
        "Gaming Mouse X",
        "Mechanical Keyboard K7",
        "4K Monitor 27",
        "USB-C Dock D10",
        "Noise Cancel Headphones",
        "Webcam HD 1080p",
        "External SSD 1TB",
        "WiFi Router AX3000",
        "Office Chair Ergo",
        "Smartphone S22",
        "Tablet T11",
        "Printer Laser L5",
        "Power Bank 20K",
    ]

    categories = {
        "Laptop Pro 14": "Computers",
        "Laptop Air 13": "Computers",
        "Gaming Mouse X": "Accessories",
        "Mechanical Keyboard K7": "Accessories",
        "4K Monitor 27": "Monitors",
        "USB-C Dock D10": "Accessories",
        "Noise Cancel Headphones": "Audio",
        "Webcam HD 1080p": "Accessories",
        "External SSD 1TB": "Storage",
        "WiFi Router AX3000": "Networking",
        "Office Chair Ergo": "Furniture",
        "Smartphone S22": "Mobile",
        "Tablet T11": "Mobile",
        "Printer Laser L5": "Office",
        "Power Bank 20K": "Mobile",
    }

    regions = ["Tashkent", "Samarkand", "Bukhara", "Andijan", "Namangan", "Fergana", "Nukus", "Khiva"]
    channels = ["Online", "Retail", "Partner"]
    payment_methods = ["Card", "Cash", "Bank Transfer", "Payme", "Click"]
    sales_reps = ["Ali", "Vali", "Madina", "Sardor", "Aziza", "Jasur", "Malika", "Nodir"]

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 3, 31)
    date_span_days = (end_date - start_date).days

    unit_price = {
        "Laptop Pro 14": 1450,
        "Laptop Air 13": 980,
        "Gaming Mouse X": 45,
        "Mechanical Keyboard K7": 95,
        "4K Monitor 27": 380,
        "USB-C Dock D10": 120,
        "Noise Cancel Headphones": 180,
        "Webcam HD 1080p": 70,
        "External SSD 1TB": 135,
        "WiFi Router AX3000": 165,
        "Office Chair Ergo": 230,
        "Smartphone S22": 720,
        "Tablet T11": 410,
        "Printer Laser L5": 260,
        "Power Bank 20K": 40,
    }

    records = []
    for i in range(1, rows + 1):
        product = random.choice(products)
        qty = random.randint(1, 8)
        base = unit_price[product]

        # Region and channel affect realistic pricing slightly.
        price_multiplier = random.uniform(0.92, 1.12)
        discount = random.choice([0, 0, 0, 0, 5, 10, 12, 15])

        gross = base * qty * price_multiplier
        discount_amount = gross * (discount / 100)
        net_sales = round(gross - discount_amount, 2)

        order_date = start_date + timedelta(days=random.randint(0, date_span_days))
        record = {
            "order_id": f"ORD-{i:06d}",
            "order_date": order_date.strftime("%Y-%m-%d"),
            "product": product,
            "category": categories[product],
            "region": random.choice(regions),
            "channel": random.choice(channels),
            "sales_rep": random.choice(sales_reps),
            "payment_method": random.choice(payment_methods),
            "quantity": qty,
            "unit_price": round(base * price_multiplier, 2),
            "discount_percent": discount,
            "sales": net_sales,
        }
        records.append(record)

    return pd.DataFrame(records)


def main() -> None:
    df = build_mock_data(rows=2000)
    out_file = "sample_sales_data.xlsx"
    df.to_excel(out_file, index=False)
    print(f"Created {out_file} with {len(df)} rows and {len(df.columns)} columns.")


if __name__ == "__main__":
    main()
